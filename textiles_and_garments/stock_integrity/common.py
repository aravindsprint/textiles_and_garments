"""
Shared settings, ledger queries and alerting for stock_integrity.

site_config.json keys (all optional; changing them needs no deploy):

    "stock_integrity_enabled": 1,
    "stock_integrity_missing_leg": "block",     # block | alert | off
    "stock_integrity_chain": "block",           # block | alert | off
    "stock_integrity_negative_batch": "block",  # block | alert | off
    "stock_integrity_zero_rate_receipt": "alert",  # block | alert | off
    "stock_integrity_fill_sr_actual_qty": 1,
    "stock_integrity_snap_remainder": 0.005,    # stock UOM; 0 disables
    "stock_integrity_protect": 1,
    "stock_integrity_alert_to": ["aravindsprint@gmail.com"]

If stock_integrity_alert_to is not set, stock_guard_alert_to is used.
"""

import frappe
from frappe.utils import cint, flt


MODES = ("block", "alert", "off")


def settings():
    c = frappe.conf

    def mode(key, default):
        v = (c.get(key) or default).lower()
        return v if v in MODES else default

    return frappe._dict(
        enabled=cint(c.get("stock_integrity_enabled", 1)),
        missing_leg=mode("stock_integrity_missing_leg", "block"),
        chain=mode("stock_integrity_chain", "block"),
        negative_batch=mode("stock_integrity_negative_batch", "block"),
        zero_rate_receipt=mode("stock_integrity_zero_rate_receipt", "alert"),
        fill_sr_actual_qty=cint(c.get("stock_integrity_fill_sr_actual_qty", 1)),
        snap_remainder=flt(c.get("stock_integrity_snap_remainder", 0.005)),
        protect=cint(c.get("stock_integrity_protect", 1)),
        alert_to=c.get("stock_integrity_alert_to") or c.get("stock_guard_alert_to") or ["aravindsprint@gmail.com"],
    )


_HAS_PDT = None


def sle_dt():
    """SQL expression for an SLE's posting moment (posting_datetime when the column exists)."""
    global _HAS_PDT
    if _HAS_PDT is None:
        _HAS_PDT = frappe.db.has_column("Stock Ledger Entry", "posting_datetime")
    return "posting_datetime" if _HAS_PDT else "TIMESTAMP(posting_date, posting_time)"


def previous_qty_after(item_code, warehouse, at, creation):
    """qty_after_transaction of the ledger line just before (at, creation), or 0."""
    dt = sle_dt()
    r = frappe.db.sql(
        f"""SELECT qty_after_transaction FROM `tabStock Ledger Entry`
            WHERE item_code=%(i)s AND warehouse=%(w)s AND is_cancelled=0
              AND ({dt} < %(at)s OR ({dt} = %(at)s AND creation < %(cr)s))
            ORDER BY {dt} DESC, creation DESC LIMIT 1""",
        {"i": item_code, "w": warehouse, "at": at, "cr": creation},
    )
    return flt(r[0][0]) if r else 0.0


def ledger_state(item_code, warehouse):
    """(sum qty, sum value, bin qty, bin value) - the same four numbers the clean-up used."""
    s = frappe.db.sql(
        """SELECT ROUND(SUM(actual_qty), 6), ROUND(SUM(stock_value_difference), 2)
           FROM `tabStock Ledger Entry` WHERE item_code=%s AND warehouse=%s AND is_cancelled=0""",
        (item_code, warehouse),
    )[0]
    b = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse},
                            ["actual_qty", "stock_value"]) or (None, None)
    return flt(s[0]), flt(s[1]), flt(b[0]), flt(b[1])


def batch_balances(item_code, warehouse):
    """
    Per-batch (qty, value) in one warehouse, combining bundle-based lines and
    old-style lines that carry batch_no directly. Two indexed queries instead of
    one COALESCE join (that join scans the whole ledger).
    """
    out = {}
    for b, q, v in frappe.db.sql(
        """SELECT e.batch_no, SUM(e.qty), SUM(e.stock_value_difference)
           FROM `tabStock Ledger Entry` s
           JOIN `tabSerial and Batch Entry` e ON e.parent = s.serial_and_batch_bundle
           WHERE s.item_code=%s AND s.warehouse=%s AND s.is_cancelled=0 AND IFNULL(e.batch_no,'')!=''
           GROUP BY e.batch_no""",
        (item_code, warehouse),
    ):
        out[b] = [flt(q), flt(v)]
    for b, q, v in frappe.db.sql(
        """SELECT batch_no, SUM(actual_qty), SUM(stock_value_difference)
           FROM `tabStock Ledger Entry`
           WHERE item_code=%s AND warehouse=%s AND is_cancelled=0
             AND IFNULL(serial_and_batch_bundle,'')='' AND IFNULL(batch_no,'')!=''
           GROUP BY batch_no""",
        (item_code, warehouse),
    ):
        cur = out.setdefault(b, [0.0, 0.0])
        cur[0] += flt(q)
        cur[1] += flt(v)
    return [frappe._dict(b=b, q=round(q, 6), v=round(v, 2)) for b, (q, v) in out.items()]


def batch_qty_in_warehouse(batch_no, warehouse):
    """Ledger quantity of one batch in one warehouse (submitted, not cancelled)."""
    q1 = frappe.db.sql(
        """SELECT SUM(e.qty) FROM `tabSerial and Batch Entry` e
           JOIN `tabSerial and Batch Bundle` b ON b.name = e.parent
           WHERE e.batch_no=%s AND b.warehouse=%s AND b.docstatus=1 AND IFNULL(b.is_cancelled,0)=0""",
        (batch_no, warehouse),
    )[0][0]
    q2 = frappe.db.sql(
        """SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
           WHERE batch_no=%s AND warehouse=%s AND is_cancelled=0 AND IFNULL(serial_and_batch_bundle,'')=''""",
        (batch_no, warehouse),
    )[0][0]
    return flt(q1) + flt(q2)


def alert(subject, html):
    subject = "[{0}] {1}".format(frappe.local.site, subject)
    frappe.log_error(title=subject[:140], message=html)
    try:
        frappe.sendmail(recipients=settings().alert_to, subject=subject, message=html, now=True)
    except Exception:
        frappe.log_error(title="Stock Integrity: alert email failed")


def html_list(lines):
    return "<ul>{0}</ul>".format("".join("<li>{0}</li>".format(frappe.utils.escape_html(l)) for l in lines))
