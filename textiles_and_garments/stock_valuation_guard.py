"""
Stock valuation guard for erp.pranera.in

Incident (Feb 2026): Stock Entry BM/25/90012 moved one batch out of
JV/1stFloor(TEMP-2) in 14 rows. Batch-wise valuation saw ~0.02 kg available
instead of 333.9 kg, so the rows went out at Rs 19 lakh .. Rs 1,434 crore per kg
and the company stock value showed -Rs 7.48 lakh crore for seven months.

Three layers, so this cannot go unnoticed again:

1. check_voucher        doc_events on_submit of every stock voucher. Runs after
                        ERPNext has posted and valued the voucher's SLEs, inside
                        the same transaction -> frappe.throw rolls the submit back.
2. check_recent_reposts hourly. Reposts rewrite SLEs without passing through
                        on_submit, so completed Repost Item Valuations are
                        re-checked for the items they touched.
3. daily_monitor        daily scan of Bins + recent SLEs, alert by email + Error Log.

Each SLE is judged on its own transaction rate |stock_value_difference / actual_qty|
and |stock_value_difference|, never on the warehouse running valuation_rate (a tiny
leftover qty gives a meaningless running rate that must not block normal work).

Two tiers, back-tested against the live ledger Oct 2024 - Oct 2026:
  BLOCK (submit is rolled back)   value > Rs 5 cr
                                  OR (value > Rs 5 lakh AND rate > Rs 5 lakh/unit)
      -> 0 legitimate entries hit in 2 years; every row of BM/25/90012 is hit.
  ALERT (email + Error Log only)  value > Rs 1,000 AND rate > Rs 1 lakh/unit
      -> catches small leaks such as DYE/LOT SECTION manufactures posting
         0.001 kg of fabric at Rs 2.4 lakh, plus expensive spares (review once,
         then exempt their item groups).

site_config.json overrides (all optional, no deploy needed to change):
    "stock_guard_enabled": 1,
    "stock_guard_block_max_value": 50000000,   # Rs 5 crore per SLE
    "stock_guard_block_min_value": 500000,     # Rs 5 lakh
    "stock_guard_block_max_rate": 500000,      # Rs 5 lakh per stock UOM
    "stock_guard_alert_min_value": 1000,
    "stock_guard_alert_max_rate": 100000,
    "stock_guard_max_bin_value": 100000000,    # Rs 10 crore in one item-warehouse
    "stock_guard_exempt_item_groups": ["SPARES/SUBLIMATION PRINTER"],
    "stock_guard_alert_to": ["aravindsprint@gmail.com"]

Manual scan:
    bench --site pranera.erpnext.com execute textiles_and_garments.stock_valuation_guard.scan --kwargs "{'days': 400}"
"""

import frappe
from frappe import _
from frappe.utils import add_days, add_to_date, cint, flt, fmt_money, now_datetime, nowdate

GUARDED_DOCTYPES = (
    "Stock Entry",
    "Purchase Receipt",
    "Subcontracting Receipt",
    "Delivery Note",
    "Sales Invoice",
    "Purchase Invoice",
    "Stock Reconciliation",
)

ALERTED_REPOSTS_CACHE_KEY = "stock_guard_alerted_reposts"


# --------------------------------------------------------------------------
# settings + shared query
# --------------------------------------------------------------------------
def _settings():
    conf = frappe.conf
    return frappe._dict(
        enabled=cint(conf.get("stock_guard_enabled", 1)),
        block=frappe._dict(
            max_value=flt(conf.get("stock_guard_block_max_value") or 50000000),
            min_value=flt(conf.get("stock_guard_block_min_value") or 500000),
            max_rate=flt(conf.get("stock_guard_block_max_rate") or 500000),
        ),
        alert=frappe._dict(
            max_value=flt(conf.get("stock_guard_block_max_value") or 50000000),
            min_value=flt(conf.get("stock_guard_alert_min_value") or 1000),
            max_rate=flt(conf.get("stock_guard_alert_max_rate") or 100000),
        ),
        max_bin_value=flt(conf.get("stock_guard_max_bin_value") or 100000000),
        exempt_item_groups=tuple(conf.get("stock_guard_exempt_item_groups") or ()),
        alert_to=conf.get("stock_guard_alert_to") or ["aravindsprint@gmail.com"],
    )


def _bad_sles(s, where, values, tier="alert", limit=50):
    """SLEs matching `where` whose own movement is out of range for `tier`."""
    t = s[tier]
    exempt = ""
    if s.exempt_item_groups and tier == "alert":
        exempt = "AND IFNULL(i.item_group, '') NOT IN %(exempt)s"
        values["exempt"] = s.exempt_item_groups

    values.update({"max_rate": t.max_rate, "min_value": t.min_value, "max_value": t.max_value, "limit": limit})
    return frappe.db.sql(
        f"""
        SELECT sle.name, sle.posting_date, sle.voucher_type, sle.voucher_no, sle.item_code,
            sle.warehouse, sle.actual_qty, sle.stock_value_difference,
            ABS(sle.stock_value_difference / NULLIF(sle.actual_qty, 0)) AS txn_rate
        FROM `tabStock Ledger Entry` sle
        LEFT JOIN `tabItem` i ON i.name = sle.item_code
        WHERE sle.is_cancelled = 0
          AND {where}
          AND (
                ABS(sle.stock_value_difference) > %(max_value)s
             OR (sle.actual_qty != 0
                 AND ABS(sle.stock_value_difference) > %(min_value)s
                 AND ABS(sle.stock_value_difference / sle.actual_qty) > %(max_rate)s)
          )
          {exempt}
        ORDER BY sle.posting_date, sle.creation
        LIMIT %(limit)s
        """,
        values,
        as_dict=True,
    )


def _bad_bins(s, item_codes=None):
    cond, values = "", {"max_bin": s.max_bin_value}
    if item_codes:
        cond = "AND item_code IN %(items)s"
        values["items"] = tuple(item_codes)
    return frappe.db.sql(
        f"""
        SELECT item_code, warehouse, actual_qty, valuation_rate, stock_value
        FROM `tabBin`
        WHERE ABS(stock_value) > %(max_bin)s {cond}
        ORDER BY ABS(stock_value) DESC
        LIMIT 50
        """,
        values,
        as_dict=True,
    )


# --------------------------------------------------------------------------
# 1. submit-time guard
# --------------------------------------------------------------------------
def check_voucher(doc, method=None):
    s = _settings()
    if not s.enabled or doc.flags.ignore_stock_guard:
        return
    if doc.doctype not in GUARDED_DOCTYPES:
        return
    if doc.doctype in ("Sales Invoice", "Purchase Invoice") and not cint(doc.get("update_stock")):
        return

    bad = _bad_sles(
        s,
        "sle.voucher_type = %(vt)s AND sle.voucher_no = %(vn)s",
        {"vt": doc.doctype, "vn": doc.name},
        tier="block",
        limit=10,
    )
    if not bad:
        return

    lines = "".join(
        "<li><b>{0}</b> @ {1}: qty {2}, rate {3}/unit, value change {4}</li>".format(
            frappe.utils.escape_html(b.item_code),
            frappe.utils.escape_html(b.warehouse),
            flt(b.actual_qty, 3),
            fmt_money(b.txn_rate),
            fmt_money(b.stock_value_difference),
        )
        for b in bad
    )
    frappe.throw(
        _(
            "ERPNext calculated an impossible stock valuation for this document, so it was "
            "not submitted. Nothing has been posted. Please send a screenshot to the ERP team."
            "<ul>{0}</ul>"
        ).format(lines),
        title=_("Stock Valuation Guard"),
    )


# --------------------------------------------------------------------------
# 2. hourly: re-check what completed reposts touched
# --------------------------------------------------------------------------
def check_recent_reposts():
    s = _settings()
    if not s.enabled:
        return

    alerted = set(frappe.cache().get_value(ALERTED_REPOSTS_CACHE_KEY) or [])
    rivs = frappe.get_all(
        "Repost Item Valuation",
        filters={
            "docstatus": 1,
            "status": "Completed",
            "modified": (">=", add_to_date(now_datetime(), hours=-2)),
        },
        fields=["name", "item_code", "voucher_type", "voucher_no", "posting_date"],
    )

    findings = []
    for riv in rivs:
        if riv.name in alerted:
            continue
        items = [riv.item_code] if riv.item_code else frappe.get_all(
            "Stock Ledger Entry",
            filters={"voucher_type": riv.voucher_type, "voucher_no": riv.voucher_no, "is_cancelled": 0},
            pluck="item_code",
            distinct=True,
        )
        if not items:
            continue

        bad = _bad_sles(
            s,
            "sle.item_code IN %(items)s AND sle.posting_date >= %(from_date)s",
            {"items": tuple(items), "from_date": riv.posting_date},
            tier="block",
            limit=20,
        )
        bins = _bad_bins(s, items)
        if bad or bins:
            findings.append((riv, bad, bins))
            alerted.add(riv.name)

    if findings:
        frappe.cache().set_value(ALERTED_REPOSTS_CACHE_KEY, list(alerted), expires_in_sec=3 * 86400)
        body = "".join(
            "<h4>Repost {0} ({1})</h4>{2}{3}".format(
                riv.name, riv.item_code or riv.voucher_no, _sle_table(bad), _bin_table(bins)
            )
            for riv, bad, bins in findings
        )
        _alert("Repost produced out-of-range stock valuation ({0})".format(len(findings)), body)


# --------------------------------------------------------------------------
# 3. daily monitor + manual scan
# --------------------------------------------------------------------------
def daily_monitor():
    s = _settings()
    if not s.enabled:
        return
    bad = _bad_sles(s, "sle.posting_date >= %(from_date)s", {"from_date": add_days(nowdate(), -3)}, tier="alert")
    bins = _bad_bins(s)
    if bad or bins:
        _alert(
            "Stock valuation anomalies: {0} ledger rows, {1} bins".format(len(bad), len(bins)),
            _sle_table(bad) + _bin_table(bins),
        )


@frappe.whitelist()
def scan(days=30, tier="alert"):
    """Read-only scan of the last `days` days. tier = "alert" (sensitive) or "block"."""
    frappe.only_for("System Manager")
    if tier not in ("alert", "block"):
        frappe.throw(_("tier must be 'alert' or 'block'"))
    s = _settings()
    bad = _bad_sles(s, "sle.posting_date >= %(from_date)s",
                    {"from_date": add_days(nowdate(), -cint(days))}, tier=tier, limit=500)
    bins = _bad_bins(s)
    for r in bad:
        print("SLE", r.posting_date, r.voucher_no, r.item_code, r.warehouse,
              flt(r.actual_qty, 3), flt(r.txn_rate, 2), flt(r.stock_value_difference, 2))
    for b in bins:
        print("BIN", b.item_code, b.warehouse, flt(b.actual_qty, 3), flt(b.stock_value, 2))
    print("{0} ledger rows, {1} bins out of range".format(len(bad), len(bins)))
    return {"sles": bad, "bins": bins}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _sle_table(rows):
    if not rows:
        return ""
    trs = "".join(
        "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td align='right'>{4}</td>"
        "<td align='right'>{5}</td><td align='right'>{6}</td></tr>".format(
            r.posting_date, r.voucher_no, frappe.utils.escape_html(r.item_code),
            frappe.utils.escape_html(r.warehouse), flt(r.actual_qty, 3),
            fmt_money(r.txn_rate), fmt_money(r.stock_value_difference))
        for r in rows
    )
    return ("<table border='1' cellpadding='4' cellspacing='0'><tr><th>Date</th><th>Voucher</th>"
            "<th>Item</th><th>Warehouse</th><th>Qty</th><th>Rate</th><th>Value change</th></tr>"
            "{0}</table><br>").format(trs)


def _bin_table(rows):
    if not rows:
        return ""
    trs = "".join(
        "<tr><td>{0}</td><td>{1}</td><td align='right'>{2}</td><td align='right'>{3}</td></tr>".format(
            frappe.utils.escape_html(b.item_code), frappe.utils.escape_html(b.warehouse),
            flt(b.actual_qty, 3), fmt_money(b.stock_value))
        for b in rows
    )
    return ("<table border='1' cellpadding='4' cellspacing='0'><tr><th>Item</th><th>Warehouse</th>"
            "<th>Qty</th><th>Stock value</th></tr>{0}</table><br>").format(trs)


def _alert(subject, html):
    subject = "[{0}] {1}".format(frappe.local.site, subject)
    frappe.log_error(title=subject[:140], message=html)
    try:
        frappe.sendmail(recipients=_settings().alert_to, subject=subject, message=html, now=True)
    except Exception:
        frappe.log_error(title="Stock Valuation Guard: alert email failed")
