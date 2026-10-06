"""
Submit-time stock ledger integrity checks.

Each check maps to a failure found in the Stock_balance_checking clean-up of 3 Oct 2026:

  missing_leg     BM/25/89360 (10 Feb 2026) posted its 25.12 kg out of NAP_E1/GF/A04 but its
                  arrival line in DYE/UNDER DYEING (WIP) was cancelled while the entry stayed
                  submitted. Every Stock Entry row must have a ledger line for each warehouse.
  chain           MF/25/10763 (21 Aug 2025) added 24.84 kg to JV/KNITTING, but the running
                  balance never included it; the stored balance stayed 24.84 kg short for 14
                  months. Each new line must continue the running balance of the line before it,
                  and the Bin must equal the last line.
  negative_batch  BM/25/89360 issued batch JOB11723 from a warehouse that never received it.
                  No outgoing movement may leave a batch below zero in its warehouse.

All three run in on_submit, after ERPNext has written the ledger, inside the same transaction:
"block" rolls the submit back with a message, "alert" lets it through and e-mails/logs.

  zero_rate_receipt  MR/25/00909 (4 Aug 2025) brought 1,672 kg NOBO and 7,000 kg COMFORTEC into
                  Pranera Marketing at rate 0 (Rs 50 lakh of stock at no value until SR/00035).
                  A Material Receipt of a stock item must carry a rate unless the row has
                  "Allow Zero Valuation Rate" ticked on purpose. Runs before_submit, so drafts
                  can still be saved. Defaults to "alert".

Also here:
  fill_sr_actual_qty  ERPNext stores a non-batch Stock Reconciliation line with actual_qty = 0
                      and only qty_after_transaction. Reports that SUM(actual_qty) (including
                      the Stock_balance_checking report) then disagree with the stored balance.
                      This fills actual_qty with the real change.
  snap_remainders     Stock Entry before_validate: an outgoing row that would leave a weighing
                      crumb (<= 5 g by default) of a batch behind takes the whole batch instead,
                      so 0.001 kg fragments carrying value stop being created.
"""

import frappe
from frappe import _
from frappe.utils import cint, flt

from textiles_and_garments.stock_integrity.common import (
    alert,
    batch_qty_in_warehouse,
    html_list,
    previous_qty_after,
    settings,
    sle_dt,
)
from textiles_and_garments.stock_integrity.pure import QTY_TOL, chain_ok, snap_remainder


# --------------------------------------------------------------------------
# on_submit
# --------------------------------------------------------------------------
def on_submit(doc, method=None):
    s = settings()
    if not s.enabled or doc.flags.ignore_stock_integrity:
        return
    if doc.doctype in ("Sales Invoice", "Purchase Invoice") and not cint(doc.get("update_stock")):
        return

    if doc.doctype == "Stock Reconciliation" and s.fill_sr_actual_qty:
        fill_sr_actual_qty(voucher_no=doc.name)

    found = {"missing_leg": [], "chain": [], "negative_batch": []}
    if doc.doctype == "Stock Entry" and s.missing_leg != "off":
        found["missing_leg"] = _missing_legs(doc)
    if s.chain != "off":
        found["chain"] = _chain_breaks(doc)
    if s.negative_batch != "off":
        found["negative_batch"] = _negative_batches(doc)

    block, warn = [], []
    allow_negative = cint(frappe.db.get_single_value("Stock Settings", "allow_negative_stock"))
    for key, lines in found.items():
        if not lines:
            continue
        mode = s[key]
        if key == "negative_batch" and allow_negative and mode == "block":
            mode = "alert"
        (block if mode == "block" else warn).extend(lines)

    if warn:
        alert(_("Stock integrity warning on {0} {1}").format(doc.doctype, doc.name), html_list(warn))
    if block:
        frappe.throw(
            _("This document would leave the stock ledger inconsistent, so it was not submitted. "
              "Nothing has been posted. Please send a screenshot to the ERP team.{0}").format(html_list(block)),
            title=_("Stock Ledger Integrity"),
        )


def _missing_legs(doc):
    present = set(
        frappe.db.sql(
            """SELECT voucher_detail_no, warehouse FROM `tabStock Ledger Entry`
               WHERE voucher_type='Stock Entry' AND voucher_no=%s AND is_cancelled=0""",
            doc.name,
        )
    )
    out = []
    for d in doc.items:
        if not flt(d.get("transfer_qty") or d.qty):
            continue
        if not frappe.get_cached_value("Item", d.item_code, "is_stock_item"):
            continue
        for wh in (d.s_warehouse, d.t_warehouse):
            if wh and (d.name, wh) not in present:
                out.append(_("Row {0}: {1} has no stock ledger line for {2}").format(d.idx, d.item_code, wh))
    return out


def _chain_breaks(doc):
    dt = sle_dt()
    sles = frappe.db.sql(
        f"""SELECT name, item_code, warehouse, actual_qty, qty_after_transaction, {dt} AS at, creation
            FROM `tabStock Ledger Entry`
            WHERE voucher_type=%s AND voucher_no=%s AND is_cancelled=0
            ORDER BY {dt}, creation""",
        (doc.doctype, doc.name),
        as_dict=True,
    )
    out, touched = [], set()
    for sle in sles:
        touched.add((sle.item_code, sle.warehouse))
        prev = previous_qty_after(sle.item_code, sle.warehouse, sle.at, sle.creation)
        if not chain_ok(prev, sle.actual_qty, sle.qty_after_transaction):
            out.append(_("{0} @ {1}: balance before {2} + movement {3} does not give {4}").format(
                sle.item_code, sle.warehouse, flt(prev, 3), flt(sle.actual_qty, 3), flt(sle.qty_after_transaction, 3)))

    for item_code, warehouse in touched:
        last = frappe.db.sql(
            f"""SELECT qty_after_transaction FROM `tabStock Ledger Entry`
                WHERE item_code=%s AND warehouse=%s AND is_cancelled=0
                ORDER BY {dt} DESC, creation DESC LIMIT 1""",
            (item_code, warehouse),
        )
        bin_qty = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty")
        if last and abs(flt(last[0][0]) - flt(bin_qty)) > QTY_TOL:
            out.append(_("{0} @ {1}: stored balance {2} differs from ledger balance {3}").format(
                item_code, warehouse, flt(bin_qty, 3), flt(last[0][0], 3)))
    return out


def _negative_batches(doc):
    pairs = set(
        frappe.db.sql(
            """SELECT e.batch_no, b.warehouse
               FROM `tabSerial and Batch Bundle` b JOIN `tabSerial and Batch Entry` e ON e.parent = b.name
               WHERE b.voucher_type=%s AND b.voucher_no=%s AND b.docstatus=1
                 AND b.type_of_transaction='Outward' AND IFNULL(e.batch_no,'')!=''""",
            (doc.doctype, doc.name),
        )
    )
    pairs |= set(
        frappe.db.sql(
            """SELECT batch_no, warehouse FROM `tabStock Ledger Entry`
               WHERE voucher_type=%s AND voucher_no=%s AND is_cancelled=0 AND actual_qty < 0
                 AND IFNULL(batch_no,'')!='' AND IFNULL(serial_and_batch_bundle,'')=''""",
            (doc.doctype, doc.name),
        )
    )
    out = []
    for batch_no, warehouse in pairs:
        q = batch_qty_in_warehouse(batch_no, warehouse)
        if q < -QTY_TOL:
            out.append(_("Batch {0} would be at {1} in {2}; the warehouse does not hold that much of it").format(
                batch_no, flt(q, 3), warehouse))
    return out


# --------------------------------------------------------------------------
# Stock Entry before_submit: no stock may arrive at zero value by accident
# --------------------------------------------------------------------------
def check_zero_rate_receipt(doc, method=None):
    s = settings()
    if not s.enabled or s.zero_rate_receipt == "off" or doc.flags.ignore_stock_integrity:
        return
    if doc.purpose != "Material Receipt":
        return
    lines = []
    for d in doc.items:
        if not d.t_warehouse or not flt(d.get("transfer_qty") or d.qty):
            continue
        if cint(d.get("allow_zero_valuation_rate")):
            continue
        if not frappe.get_cached_value("Item", d.item_code, "is_stock_item"):
            continue
        if flt(d.get("valuation_rate")) or flt(d.get("basic_rate")):
            continue
        lines.append(_("Row {0}: {1}, {2} into {3} has no rate").format(
            d.idx, d.item_code, flt(d.get("transfer_qty") or d.qty, 3), d.t_warehouse))
    if not lines:
        return
    if s.zero_rate_receipt == "alert":
        alert(_("Zero-rate Material Receipt {0}").format(doc.name), html_list(lines))
        return
    frappe.throw(
        _("This Material Receipt brings stock in at no value. Enter the purchase/transfer rate, or tick "
          "\"Allow Zero Valuation Rate\" on the row if the stock really is free.{0}").format(html_list(lines)),
        title=_("Stock Ledger Integrity"),
    )


# --------------------------------------------------------------------------
# Stock Reconciliation: real quantity change on non-batch lines
# --------------------------------------------------------------------------
def fill_sr_actual_qty(voucher_no=None, item_code=None, warehouse=None, from_date=None, skip_vouchers=()):
    """
    Set actual_qty on non-batch Stock Reconciliation ledger lines to
    qty_after_transaction minus the balance before them.

    Pass voucher_no for one reconciliation, or item_code/warehouse/from_date
    after a repost has rewritten balances. Lines of `skip_vouchers` are left alone.
    Returns the number of lines changed.
    """
    dt = sle_dt()
    cond, vals = ["voucher_type='Stock Reconciliation'", "is_cancelled=0",
                  "IFNULL(serial_and_batch_bundle,'')=''", "IFNULL(batch_no,'')=''"], {}
    if voucher_no:
        cond.append("voucher_no=%(v)s"); vals["v"] = voucher_no
    if item_code:
        cond.append("item_code=%(i)s"); vals["i"] = item_code
    if warehouse:
        cond.append("warehouse=%(w)s"); vals["w"] = warehouse
    if from_date:
        cond.append("posting_date >= %(d)s"); vals["d"] = from_date
    if skip_vouchers:
        cond.append("voucher_no NOT IN %(skip)s"); vals["skip"] = tuple(skip_vouchers)

    changed = 0
    for r in frappe.db.sql(
        f"""SELECT name, item_code, warehouse, actual_qty, qty_after_transaction, {dt} AS at, creation
            FROM `tabStock Ledger Entry` WHERE {' AND '.join(cond)} ORDER BY {dt}, creation""",
        vals,
        as_dict=True,
    ):
        prev = previous_qty_after(r.item_code, r.warehouse, r.at, r.creation)
        want = round(flt(r.qty_after_transaction) - prev, 6)
        if abs(want - flt(r.actual_qty)) > QTY_TOL / 10:
            frappe.db.set_value("Stock Ledger Entry", r.name, "actual_qty", want, update_modified=False)
            changed += 1
    return changed


# --------------------------------------------------------------------------
# Stock Entry before_validate: take the whole batch instead of leaving a crumb
# --------------------------------------------------------------------------
def snap_remainders(doc, method=None):
    s = settings()
    if not s.enabled or s.snap_remainder <= 0 or doc.docstatus != 0 or doc.flags.ignore_stock_integrity:
        return
    try:
        from erpnext.stock.doctype.batch.batch import get_batch_qty
    except ImportError:
        return

    groups = {}
    for d in doc.items:
        if not (d.s_warehouse and d.get("batch_no")):
            continue
        if d.get("serial_and_batch_bundle") and not cint(d.get("use_serial_batch_fields")):
            continue
        uom = frappe.get_cached_value("Item", d.item_code, "stock_uom")
        if uom and cint(frappe.get_cached_value("UOM", uom, "must_be_whole_number")):
            continue
        groups.setdefault((d.batch_no, d.s_warehouse, d.item_code), []).append(d)

    snapped = []
    for (batch_no, warehouse, item_code), rows in groups.items():
        try:
            available = flt(get_batch_qty(batch_no=batch_no, warehouse=warehouse, item_code=item_code))
        except Exception:
            continue
        taking = sum(flt(r.qty) * flt(r.conversion_factor or 1) for r in rows)
        rem = snap_remainder(available, taking, s.snap_remainder)
        if not rem:
            continue
        last = rows[-1]
        cf = flt(last.conversion_factor or 1)
        last.qty = flt(last.qty) + rem / cf
        last.transfer_qty = flt(last.qty) * cf
        snapped.append(_("Row {0}: {1} batch {2} +{3} so no {3} is left behind in {4}").format(
            last.idx, item_code, batch_no, flt(rem, 3), warehouse))

    if snapped:
        frappe.msgprint(html_list(snapped), title=_("Whole batch taken"), indicator="blue", alert=True)
