import frappe

def execute():
    """Apply General Ledger monkey patch"""
    try:
        from erpnext.accounts.report.general_ledger import general_ledger
        from textiles_and_garments.overrides.general_ledger import custom_execute, custom_get_conditions
        
        general_ledger.execute = custom_execute
        general_ledger.get_conditions = custom_get_conditions
        
        print("\n✓ General Ledger patches applied via patch\n")
        frappe.log_error("Patches applied successfully", "GL Patch")
        
    except Exception as e:
        print(f"\n✗ Patch error: {e}\n")
        frappe.log_error(str(e), "GL Patch Error")