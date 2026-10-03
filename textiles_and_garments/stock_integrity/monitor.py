"""
Scheduled stock integrity checks.

  check_failed_reposts   hourly. 16 Repost Item Valuations had sat in "Failed" unnoticed,
                         one since Aug 2024. A failed repost leaves every later line of its
                         items stale (YRFPP090's Rs 5,044.50 came from 3vgev9sl2l failing on
                         16 Jun 2026). Alerts each new failure once, with the error tail.
  refill_after_reposts   hourly. A repost can change the balance before a non-batch Stock
                         Reconciliation, so its actual_qty is recomputed for the items the
                         completed reposts touched (protected vouchers are left alone).
  nightly_scan           daily. The same aggregation as the Stock_balance_checking report:
                         every item/warehouse that is red (value <= -1 or qty < -0.001) or
                         whose ledger total disagrees with its stored (Bin) balance.

Manual run:
    bench --site pranera.erpnext.com execute textiles_and_garments.stock_integrity.monitor.nightly_scan --kwargs "{'send': 0}"
"""

import frappe
from frappe.utils import add_to_date, flt, now_datetime

from textiles_and_garments.stock_integrity.common import alert, settings
from textiles_and_garments.stock_integrity.guard import fill_sr_actual_qty
from textiles_and_garments.stock_integrity.protect import get_protected
from textiles_and_garments.stock_integrity.pure import is_red, out_of_sync

FAILED_CACHE_KEY = "stock_integrity_alerted_failed_reposts"
REFILL_CACHE_KEY = "stock_integrity_refilled_reposts"


def check_failed_reposts():
    if not settings().enabled:
        return
    seen = set(frappe.cache().get_value(FAILED_CACHE_KEY) or [])
    rows = frappe.get_all(
        "Repost Item Valuation",
        filters={"docstatus": 1, "status": "Failed", "modified": (">=", add_to_date(now_datetime(), hours=-26))},
        fields=["name", "based_on", "item_code", "warehouse", "voucher_type", "voucher_no", "posting_date", "error_log"],
    )
    new = [r for r in rows if r.name not in seen]
    if not new:
        return
    body = "".join(
        "<h4>{0}</h4><p>{1} {2} {3} | {4} | from {5}</p><pre>{6}</pre>".format(
            r.name, r.based_on, r.item_code or r.voucher_type or "", r.voucher_no or "", r.warehouse or "",
            r.posting_date, frappe.utils.escape_html((r.error_log or "")[-800:]))
        for r in new
    )
    body += ("<p>Until a failed repost is fixed and restarted, every later ledger line of its items keeps "
             "stale values. Check the error, fix the cause, then use Restart on the Repost Item Valuation.</p>")
    alert("Repost Item Valuation failed ({0})".format(len(new)), body)
    seen.update(r.name for r in new)
    frappe.cache().set_value(FAILED_CACHE_KEY, list(seen), expires_in_sec=7 * 86400)


def refill_after_reposts():
    s = settings()
    if not s.enabled or not s.fill_sr_actual_qty:
        return
    done = set(frappe.cache().get_value(REFILL_CACHE_KEY) or [])
    skip = [vn for vt, vn in get_protected() if vt == "Stock Reconciliation"]
    rivs = frappe.get_all(
        "Repost Item Valuation",
        filters={"docstatus": 1, "status": "Completed", "modified": (">=", add_to_date(now_datetime(), hours=-2))},
        fields=["name", "based_on", "item_code", "warehouse", "voucher_type", "voucher_no", "posting_date"],
    )
    for riv in rivs:
        if riv.name in done:
            continue
        if riv.based_on == "Transaction" and riv.voucher_no:
            pairs = frappe.db.sql(
                """SELECT DISTINCT item_code, warehouse FROM `tabStock Ledger Entry`
                   WHERE voucher_type=%s AND voucher_no=%s""",
                (riv.voucher_type, riv.voucher_no),
            )
        else:
            pairs = [(riv.item_code, riv.warehouse)]
        for item, wh in pairs:
            fill_sr_actual_qty(item_code=item, warehouse=wh, from_date=riv.posting_date, skip_vouchers=skip)
        done.add(riv.name)
    frappe.cache().set_value(REFILL_CACHE_KEY, list(done), expires_in_sec=3 * 86400)


def scan_rows(company=None):
    """Item/warehouses that are red or out of sync. Read-only."""
    cond, vals = "", {}
    if company:
        cond, vals = "AND sle.company=%(c)s", {"c": company}
    rows = frappe.db.sql(
        f"""SELECT sle.item_code, sle.warehouse,
                ROUND(SUM(sle.actual_qty), 6) AS q, ROUND(SUM(sle.stock_value_difference), 2) AS v,
                MAX(b.actual_qty) AS bq, MAX(b.stock_value) AS bv
            FROM `tabStock Ledger Entry` sle
            LEFT JOIN `tabBin` b ON b.item_code = sle.item_code AND b.warehouse = sle.warehouse
            WHERE sle.is_cancelled = 0 {cond}
            GROUP BY sle.item_code, sle.warehouse""",
        vals,
        as_dict=True,
    )
    red, sync = [], []
    for r in rows:
        if is_red(r.q, r.v):
            red.append(r)
        elif out_of_sync(r.q, r.v, r.bq, r.bv):
            sync.append(r)
    return red, sync


def nightly_scan(send=1):
    if not settings().enabled:
        return
    red, sync = scan_rows()
    for r in red[:50]:
        print("RED ", r.item_code, "|", r.warehouse, flt(r.q, 3), flt(r.v, 2), "| bin", flt(r.bq, 3), flt(r.bv, 2))
    for r in sync[:50]:
        print("SYNC", r.item_code, "|", r.warehouse, flt(r.q, 3), flt(r.v, 2), "| bin", flt(r.bq, 3), flt(r.bv, 2))
    print("{0} red, {1} out of sync".format(len(red), len(sync)))
    if (red or sync) and int(send):
        alert(
            "Stock ledger: {0} red rows, {1} out of sync".format(len(red), len(sync)),
            _table("Red (value <= -1 or qty < -0.001)", red) + _table("Ledger total differs from stored balance", sync)
            + "<p>Repair: bench --site {0} execute textiles_and_garments.stock_integrity.repair.run "
              "(dry run by default).</p>".format(frappe.local.site),
        )
    return {"red": len(red), "out_of_sync": len(sync)}


def _table(title, rows):
    if not rows:
        return ""
    trs = "".join(
        "<tr><td>{0}</td><td>{1}</td><td align='right'>{2}</td><td align='right'>{3}</td>"
        "<td align='right'>{4}</td><td align='right'>{5}</td></tr>".format(
            frappe.utils.escape_html(r.item_code), frappe.utils.escape_html(r.warehouse),
            flt(r.q, 3), flt(r.v, 2), flt(r.bq, 3), flt(r.bv, 2))
        for r in rows[:100]
    )
    more = "<p>... and {0} more</p>".format(len(rows) - 100) if len(rows) > 100 else ""
    return ("<h4>{0}: {1}</h4><table border='1' cellpadding='4' cellspacing='0'><tr><th>Item</th><th>Warehouse</th>"
            "<th>Ledger qty</th><th>Ledger value</th><th>Stored qty</th><th>Stored value</th></tr>{2}</table>{3}<br>"
            ).format(title, len(rows), trs, more)
