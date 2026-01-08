# your_custom_app/your_custom_app/custom_scripts/purchase_receipt.py

import frappe
from frappe import _

def update_awaiting_grn_on_submit(doc, method):
    """Update Awaiting GRN with Purchase Receipt reference on submission"""
    if doc.custom_awaiting_grn:
        try:
            # Fetch the Awaiting GRN document
            awaiting_grn = frappe.get_doc("Awaiting GRN", doc.custom_awaiting_grn)
            
            # Validate: Check if already linked to another Purchase Receipt
            if awaiting_grn.purchase_receipt and awaiting_grn.purchase_receipt != doc.name:
                frappe.throw(_(
                    f"Awaiting GRN {doc.custom_awaiting_grn} is already linked to "
                    f"Purchase Receipt <a href='/app/purchase-receipt/{awaiting_grn.purchase_receipt}'>{awaiting_grn.purchase_receipt}</a>"
                ))
            
            # Update the purchase_receipt field
            awaiting_grn.db_set('purchase_receipt', doc.name, update_modified=True)
            
            # Optional: Add comment for tracking
            awaiting_grn.add_comment(
                'Info', 
                f'Linked to Purchase Receipt: <a href="/app/purchase-receipt/{doc.name}">{doc.name}</a>'
            )
            
            frappe.msgprint(
                _(f"Successfully linked Awaiting GRN {doc.custom_awaiting_grn}"), 
                alert=True,
                indicator='green'
            )
            
        except frappe.DoesNotExistError:
            frappe.throw(_(f"Awaiting GRN {doc.custom_awaiting_grn} not found"))
        except Exception as e:
            frappe.log_error(
                message=frappe.get_traceback(),
                title=f"Error updating Awaiting GRN {doc.custom_awaiting_grn}"
            )
            frappe.throw(_(f"Failed to update Awaiting GRN: {str(e)}"))


def clear_awaiting_grn_on_cancel(doc, method):
    """Clear Purchase Receipt reference from Awaiting GRN on cancellation"""
    if doc.custom_awaiting_grn:
        try:
            awaiting_grn = frappe.get_doc("Awaiting GRN", doc.custom_awaiting_grn)
            
            # Only clear if it's linked to this Purchase Receipt
            if awaiting_grn.purchase_receipt == doc.name:
                awaiting_grn.db_set('purchase_receipt', None, update_modified=True)
                
                awaiting_grn.add_comment(
                    'Info',
                    f'Unlinked from cancelled Purchase Receipt: {doc.name}'
                )
                
                frappe.msgprint(
                    _(f"Cleared link from Awaiting GRN {doc.custom_awaiting_grn}"),
                    alert=True,
                    indicator='orange'
                )
                
        except Exception as e:
            frappe.log_error(
                message=frappe.get_traceback(),
                title=f"Error clearing Awaiting GRN {doc.custom_awaiting_grn}"
            )