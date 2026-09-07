import frappe
from frappe.utils import flt


def fix_scrap_item_valuation(doc, method=None):
    """
    Stock Entry 'before_validate' hook.

    Must run BEFORE core's own validate() -> calculate_rate_and_amount() ->
    set_basic_rate(), because get_basic_rate_for_manufactured_item() nets
    scrap_items_cost (read from each scrap row's CURRENT basic_amount) off
    the consumed material cost before dividing it among finished items.

    If scrap rows still carry their previous/blank basic_amount when that
    calculation runs, the finished item silently absorbs 100% of the
    consumed cost and scrap gets valued at 0 - even if scrap's own rate
    gets patched afterwards, the two numbers no longer reconcile.

    This sets scrap rows' rate from BOM Scrap Item (falling back to the
    Item master) and marks them set_basic_rate_manually=1 so core's own
    incoming-item loop leaves them untouched later in the same validate.
    """
    if doc.purpose != "Manufacture" or not doc.bom_no:
        return

    scrap_rows = [d for d in doc.items if d.is_scrap_item]
    if not scrap_rows:
        return

    # BOM Scrap Item rates for this BOM, keyed by item_code
    bom_scrap_rates = frappe._dict(
        frappe.get_all(
            "BOM Scrap Item",
            filters={"parent": doc.bom_no},
            fields=["item_code", "rate"],
            as_list=True,
        )
    )

    corrected = []
    still_zero = []

    for d in scrap_rows:
        rate = flt(bom_scrap_rates.get(d.item_code))

        if not rate:
            rate = flt(
                frappe.db.get_value("Item", d.item_code, "valuation_rate")
            ) or flt(frappe.db.get_value("Item", d.item_code, "standard_rate"))

        if rate:
            d.basic_rate = rate
            d.set_basic_rate_manually = 1  # stops core's incoming-item loop from overwriting this
            d.basic_amount = flt(flt(d.transfer_qty) * rate, d.precision("basic_amount"))
            corrected.append(d.item_code)
        else:
            # No BOM rate AND no Item fallback - leave at 0. Core will then
            # net off 0 (same as today) and the finished item absorbs the
            # full cost, which is at least consistent rather than silently
            # wrong in two different rows.
            still_zero.append(d.item_code)

    if still_zero:
        frappe.msgprint(
            frappe._(
                "No BOM Scrap Item rate or Item valuation/standard rate found for: {0}. "
                "These will post at zero and the finished item will absorb their full cost share."
            ).format(", ".join(frappe.bold(i) for i in set(still_zero))),
            indicator="orange",
            alert=True,
        )
