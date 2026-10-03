"""
Protect vouchers whose ledger lines were adjusted by the clean-up / repair tool.

Why: on 3 Oct 2026 SR/00024's adjusted lines were silently undone 12 minutes after
commit, because its own automatic Repost Item Valuation recalculated them. Any later
repost that starts at or before an adjusted line does the same - typically one caused
by a backdated stock entry, or by cancelling an old document.

Protected vouchers are kept in the global default `stock_integrity_protected_vouchers`
(a JSON list of [voucher_type, voucher_no]). For every item/warehouse they touch, the
earliest protected ledger moment is cached. Then:

  guard_repost   Repost Item Valuation validate: refuse a repost that would start at or
                 before a protected line of an item/warehouse it touches. The repost is
                 created inside the submit/cancel of the document that caused it, so the
                 throw rolls that document back with an explanation.
  guard_cancel   before_cancel on Stock Entry / Stock Reconciliation: refuse to cancel a
                 protected voucher.

Escape hatch for a deliberate, supervised repost:
    frappe.flags.allow_protected_repost = True
or site_config "stock_integrity_protect": 0.
"""

import json

import frappe
from frappe import _
from frappe.utils import get_datetime

from textiles_and_garments.stock_integrity.common import settings, sle_dt
from textiles_and_garments.stock_integrity.pure import repost_hits_protected

DEFAULT_KEY = "stock_integrity_protected_vouchers"
CACHE_KEY = "stock_integrity_protected_index"


def get_protected():
    raw = frappe.db.get_default(DEFAULT_KEY)
    try:
        return [tuple(x) for x in json.loads(raw)] if raw else []
    except Exception:
        return []


def protect(voucher_type, voucher_no):
    """Add one voucher to the protected list (idempotent)."""
    cur = get_protected()
    key = (voucher_type, voucher_no)
    if key not in cur:
        cur.append(key)
        frappe.db.set_default(DEFAULT_KEY, json.dumps([list(x) for x in cur]))
    frappe.cache().delete_value(CACHE_KEY)


def unprotect(voucher_type, voucher_no):
    cur = [x for x in get_protected() if x != (voucher_type, voucher_no)]
    frappe.db.set_default(DEFAULT_KEY, json.dumps([list(x) for x in cur]))
    frappe.cache().delete_value(CACHE_KEY)


def is_protected(voucher_type, voucher_no):
    return (voucher_type, voucher_no) in get_protected()


def protected_index():
    """{"item||warehouse": [earliest protected moment (ISO str), voucher_no]}"""
    idx = frappe.cache().get_value(CACHE_KEY)
    if idx is not None:
        return idx
    idx = {}
    dt = sle_dt()
    for vt, vn in get_protected():
        for item, wh, at in frappe.db.sql(
            f"""SELECT item_code, warehouse, MIN({dt}) FROM `tabStock Ledger Entry`
                WHERE voucher_type=%s AND voucher_no=%s AND is_cancelled=0
                GROUP BY item_code, warehouse""",
            (vt, vn),
        ):
            k = f"{item}||{wh}"
            at = str(at)
            if k not in idx or at < idx[k][0]:
                idx[k] = [at, vn]
    frappe.cache().set_value(CACHE_KEY, idx, expires_in_sec=6 * 3600)
    return idx


def _repost_pairs(doc):
    """Item/warehouse pairs a Repost Item Valuation will recalculate (None = wildcard)."""
    if doc.based_on == "Transaction" and doc.voucher_type and doc.voucher_no:
        return frappe.db.sql(
            """SELECT DISTINCT item_code, warehouse FROM `tabStock Ledger Entry`
               WHERE voucher_type=%s AND voucher_no=%s""",
            (doc.voucher_type, doc.voucher_no),
        )
    return [(doc.item_code or None, doc.warehouse or None)]


def guard_repost(doc, method=None):
    s = settings()
    if not s.enabled or not s.protect or frappe.flags.allow_protected_repost:
        return
    if doc.docstatus == 2 or doc.get("status") in ("Skipped", "Completed"):
        return
    idx = protected_index()
    if not idx:
        return

    start = str(get_datetime("{0} {1}".format(doc.posting_date, doc.posting_time or "00:00:00")))
    hits = []
    for item, wh in _repost_pairs(doc):
        for k, (at, vn) in idx.items():
            i, w = k.split("||", 1)
            if (item is None or item == i) and (wh is None or wh == w) and repost_hits_protected(start, at):
                hits.append(_("{0} @ {1} (reconciled by {2} on {3})").format(i, w, vn, at[:16]))
    if hits:
        frappe.throw(
            _("This would recalculate stock that was reconciled and locked. Post the document with "
              "today's date instead of a past date, or ask the ERP team.<ul>{0}</ul>").format(
                "".join("<li>{0}</li>".format(frappe.utils.escape_html(h)) for h in hits[:10])),
            title=_("Protected stock reconciliation"),
        )


def guard_cancel(doc, method=None):
    s = settings()
    if not s.enabled or not s.protect or frappe.flags.allow_protected_repost:
        return
    if is_protected(doc.doctype, doc.name):
        frappe.throw(
            _("{0} {1} was adjusted during a stock ledger clean-up and cannot be cancelled. "
              "Cancelling it would bring the old stock differences back. Ask the ERP team.").format(
                doc.doctype, doc.name),
            title=_("Protected stock reconciliation"),
        )
