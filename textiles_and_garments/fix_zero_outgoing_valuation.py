import frappe
from frappe.utils import flt


def fix_zero_outgoing_valuation(doc, method=None):
    """
    Stock Entry 'validate' hook - DEFENSIVE SAFETY NET, not a root-cause fix.

    Symptom this catches: an outgoing/consumed row (s_warehouse set) comes
    out of core's set_rate_for_outgoing_items() at basic_rate = 0, even
    though a valid, nonzero valuation clearly existed for that exact
    item+warehouse immediately beforehand (confirmed by hand on real
    documents - MF/26/24098 and others). The exact code path causing core
    to miss that valid prior rate has NOT been identified yet; this hook
    does not fix that path, it only catches and corrects the result.

    Must run in 'validate' (after core), because
    set_rate_for_outgoing_items() unconditionally recalculates any row
    with s_warehouse set - it does not honour set_basic_rate_manually the
    way incoming/scrap rows do, so pre-setting the rate in before_validate
    would just get overwritten again by core a moment later.

    Because the outgoing row's cost also feeds get_basic_rate_for_manufactured_item()
    within the SAME validate() call (which already ran, using the wrong
    zero), this hook must also redo that netting itself for any
    is_finished_item row in the same document - otherwise the raw
    material gets corrected but the finished item silently stays wrong.
    """
    if doc.purpose not in ("Manufacture", "Material Transfer", "Material Issue", "Repack"):
        return

    outgoing_rows = [d for d in doc.items if d.s_warehouse and not d.is_scrap_item]
    suspect_rows = [d for d in outgoing_rows if not flt(d.basic_rate)]
    if not suspect_rows:
        return

    corrected_value = 0.0
    corrected_items = []
    still_zero = []

    for d in suspect_rows:
        true_rate = _get_last_known_valuation(d.item_code, d.s_warehouse, doc.posting_date, doc.posting_time)

        if true_rate:
            old_amount = flt(d.basic_amount)
            d.basic_rate = true_rate
            d.basic_amount = flt(flt(d.transfer_qty) * true_rate, d.precision("basic_amount"))
            corrected_value += flt(d.basic_amount) - old_amount
            corrected_items.append(d.item_code)
        else:
            # No prior valuation found anywhere - genuinely nothing to correct against.
            still_zero.append(d.item_code)

    if not corrected_items:
        return

    # Redo the finished-item netting for this document using the corrected
    # outgoing cost, mirroring get_basic_rate_for_manufactured_item()'s own
    # formula, since core already ran it once with the wrong (zero) inputs.
    if doc.purpose == "Manufacture":
        finished_rows = [d for d in doc.items if d.is_finished_item]
        finished_qty = sum(flt(d.transfer_qty) for d in finished_rows)
        if finished_rows and finished_qty:
            for d in finished_rows:
                old_rate = flt(d.basic_rate)
                new_amount = flt(d.basic_amount) + corrected_value * (flt(d.transfer_qty) / finished_qty)
                d.basic_rate = flt(new_amount / d.transfer_qty) if d.transfer_qty else old_rate
                d.basic_amount = flt(new_amount, d.precision("basic_amount"))

    # Recompute doc-level aggregates so totals reflect the corrections above.
    doc.update_valuation_rate()
    doc.set_total_incoming_outgoing_value()
    doc.set_total_amount()

    frappe.msgprint(
        frappe._(
            "Corrected zero valuation on: {0}. This is a safety-net fix - "
            "the underlying reason core computed a zero rate here has not "
            "been identified, only the symptom."
        ).format(", ".join(frappe.bold(i) for i in corrected_items)),
        indicator="orange",
        alert=True,
    )

    if still_zero:
        frappe.msgprint(
            frappe._(
                "No prior valuation found at all for: {0} - these are still zero "
                "and could not be corrected."
            ).format(", ".join(frappe.bold(i) for i in set(still_zero))),
            indicator="red",
            alert=True,
        )


def _get_last_known_valuation(item_code, warehouse, posting_date, posting_time):
    """Most recent valuation_rate on record for this item+warehouse strictly
    before this document's posting datetime - same lookup core is supposed
    to use, done independently as a cross-check."""
    row = frappe.db.sql(
        """
        select valuation_rate
        from `tabStock Ledger Entry`
        where item_code = %(item_code)s
            and warehouse = %(warehouse)s
            and is_cancelled = 0
            and valuation_rate > 0
            and timestamp(posting_date, posting_time) <= timestamp(%(posting_date)s, %(posting_time)s)
        order by posting_date desc, posting_time desc
        limit 1
        """,
        {
            "item_code": item_code,
            "warehouse": warehouse,
            "posting_date": posting_date,
            "posting_time": posting_time,
        },
        as_dict=True,
    )
    return flt(row[0].valuation_rate) if row else 0.0
