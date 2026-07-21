import frappe
from frappe import _


@frappe.whitelist()
def get_rm_batch_details(subcontracting_order, rm_item_codes):
    """
    Fetch (parent, item_code, batch_no) from Stock Entry Detail for submitted
    Stock Entries linked to the given Subcontracting Order, restricted to the
    given raw material item codes.

    Runs with ignore_permissions=True to bypass field-level permission masking
    on Stock Entry Detail (parent/batch_no are silently dropped by frappe.db.get_list
    for roles without read permission at their permlevel). Caller-level access is
    still gated via the explicit has_permission check below - this does NOT expose
    Stock Entry Detail data to unauthenticated or unrelated users.
    """
    if isinstance(rm_item_codes, str):
        rm_item_codes = frappe.parse_json(rm_item_codes)

    if not subcontracting_order or not rm_item_codes:
        return []

    if not frappe.has_permission("Subcontracting Receipt", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    stock_entries = frappe.get_all(
        "Stock Entry",
        filters={"subcontracting_order": subcontracting_order, "docstatus": 1},
        pluck="name",
        ignore_permissions=True,
    )

    if not stock_entries:
        return []

    rows = frappe.get_all(
        "Stock Entry Detail",
        filters={
            "parent": ["in", stock_entries],
            "item_code": ["in", rm_item_codes],
        },
        fields=["parent", "item_code", "batch_no"],
        ignore_permissions=True,
    )

    return rows
