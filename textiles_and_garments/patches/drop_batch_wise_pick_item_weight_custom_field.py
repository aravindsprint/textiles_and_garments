import frappe


def execute():
    """The 'weight' field on Batch Wise Pick Item was created as a live
    Custom Field before it was added to the doctype's own JSON as a
    standard field. Since this patch runs post_model_sync (after the
    standard field has already been migrated in), a leftover Custom
    Field of the same name is now redundant and would otherwise sit
    unused (or shadow the standard one) — remove it."""
    if frappe.db.exists("Custom Field", "Batch Wise Pick Item-weight"):
        frappe.delete_doc("Custom Field", "Batch Wise Pick Item-weight", ignore_permissions=True)
        frappe.db.commit()
