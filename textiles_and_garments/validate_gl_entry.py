import frappe
from frappe import _

def validate_gl_entry(doc, method):
    """Prevent GL Entry creation for Employee party type"""
    print(f"\n\nvalidate_gl_entry called - Party Type: {doc.party_type}\n\n")
    
    if doc.party_type == "Employee":
        frappe.throw(
            _("General Ledger entries cannot be created for Employee party type. "
              "Please use Employee Advance or Expense Claim instead."),
            title=_("Invalid Party Type")
        )