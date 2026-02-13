# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from frappe import _

# =============================================================================
# CONFIGURATION: Block users with restricted roles (STRICT MODE)
# =============================================================================

# Roles to block from viewing Employee data in General Ledger
RESTRICTED_ROLES = [
    "Accounts User",
    "Sales User",
]

# STRICT MODE: Block users with restricted roles even if they have other roles
STRICT_MODE = True

# These roles are defined but won't override restriction in STRICT_MODE
UNRESTRICTED_ROLES = [
    "Accounts Manager",
    "System Manager",
    "HR Manager",
]

# Optional: Block/Allow specific users by email
RESTRICTED_USERS = []
UNRESTRICTED_USERS = []

def is_user_restricted():
    """
    Check if current user is restricted from viewing Employee data
    STRICT MODE: Returns True if user has ANY restricted role
    """
    user = frappe.session.user
    
    # Administrator is never restricted
    if user == "Administrator":
        return False
    
    # Check unrestricted users whitelist (these can override STRICT_MODE)
    if UNRESTRICTED_USERS and user in UNRESTRICTED_USERS:
        return False
    
    # Check restricted users blacklist
    if RESTRICTED_USERS and user in RESTRICTED_USERS:
        return True
    
    # Get user roles
    user_roles = frappe.get_roles(user)
    
    # STRICT MODE: Block if user has ANY restricted role
    if STRICT_MODE:
        for role in RESTRICTED_ROLES:
            if role in user_roles:
                return True
        # If user doesn't have any restricted role, allow access
        return False
    
    # NORMAL MODE (STRICT_MODE = False):
    # Allow if user has any unrestricted role
    if UNRESTRICTED_ROLES:
        for role in UNRESTRICTED_ROLES:
            if role in user_roles:
                return False
    
    # Block if user has restricted role and no unrestricted role
    if RESTRICTED_ROLES:
        for role in RESTRICTED_ROLES:
            if role in user_roles:
                return True
    
    # Default: No restriction if not in any list
    return False

def custom_execute(filters=None):
    """
    Override General Ledger report to exclude Employee party type for restricted users
    STRICT MODE: Blocks ALL users with Accounts User or Sales User role
    """
    # Check if user is restricted
    user_restricted = is_user_restricted()
    user_roles = frappe.get_roles(frappe.session.user)
    
    # Filter relevant roles for logging
    relevant_roles = [r for r in user_roles if r in RESTRICTED_ROLES + UNRESTRICTED_ROLES]
    
    # DEBUG: Log function call
    print(f"\n{'='*60}")
    print(f"GENERAL LEDGER ACCESS CHECK (STRICT MODE)")
    print(f"User: {frappe.session.user}")
    print(f"Relevant Roles: {relevant_roles}")
    print(f"Has Restricted Role: {any(r in user_roles for r in RESTRICTED_ROLES)}")
    print(f"Restricted from Employee data: {user_restricted}")
    print(f"Party Type Filter: {filters.get('party_type') if filters else None}")
    print(f"{'='*60}\n")
    
    # Only apply restrictions if user is restricted
    if user_restricted:
        # Block if Employee party type is explicitly selected
        if filters and filters.get("party_type") == "Employee":
            print("=== BLOCKING EMPLOYEE PARTY TYPE FOR RESTRICTED USER (STRICT MODE) ===")
            frappe.throw(
                _("You do not have permission to view General Ledger for Employee party type.<br><br>"
                  "<b>Note:</b> Access is restricted for all users with Accounts User or Sales User role.<br><br>"
                  "Please contact your administrator or use Employee Advance/Expense Claim reports for employee-related transactions."),
                title=_("Access Restricted"),
                exc=frappe.PermissionError
            )
    
    # Get original execute from main app module
    import textiles_and_garments
    
    original_execute = textiles_and_garments.ORIGINAL_GL_EXECUTE
    
    if not original_execute:
        frappe.throw(
            _("System Error: Original General Ledger function not found.<br><br>"
              "Please restart bench: <code>bench restart</code>"),
            title=_("Configuration Error")
        )
    
    # Convert filters to frappe._dict if needed
    if filters and isinstance(filters, dict) and not isinstance(filters, frappe._dict):
        filters = frappe._dict(filters)
    
    # Call original execute function
    print("=== CALLING ORIGINAL GL EXECUTE ===")
    columns, data = original_execute(filters)
    print(f"=== ORIGINAL EXECUTE RETURNED {len(data) if data else 0} ROWS ===")
    
    # Filter out Employee entries only for restricted users
    if user_restricted and data:
        original_count = len(data)
        filtered_data = []
        
        for row in data:
            # Check if row is a dict and has party_type field
            if isinstance(row, dict) and row.get("party_type") == "Employee":
                # Silently filter out Employee entries
                continue
            filtered_data.append(row)
        
        filtered_count = original_count - len(filtered_data)
        if filtered_count > 0:
            print(f"=== FILTERED {filtered_count} EMPLOYEE ROWS (STRICT MODE) ===")
        
        return columns, filtered_data
    
    return columns, data

def custom_get_conditions(filters):
    """
    Add condition to exclude Employee party type from GL entries for restricted users
    STRICT MODE: Applies to all users with restricted roles
    """
    print(f"\n=== CUSTOM GET_CONDITIONS (STRICT MODE) - User: {frappe.session.user} ===")
    
    # Get original get_conditions from main app module
    import textiles_and_garments
    
    original_get_conditions = textiles_and_garments.ORIGINAL_GL_GET_CONDITIONS
    
    if not original_get_conditions:
        frappe.throw(
            _("System Error: Original get_conditions function not found.<br><br>"
              "Please restart bench: <code>bench restart</code>"),
            title=_("Configuration Error")
        )
    
    # Get original conditions
    conditions = original_get_conditions(filters)
    
    # Only add restriction for restricted users
    user_restricted = is_user_restricted()
    
    if user_restricted and not filters.get("party_type"):
        # If no party_type filter, exclude Employee by default at SQL level
        additional_condition = " and (party_type IS NULL OR party_type != 'Employee')"
        conditions += additional_condition
        print(f"=== ADDED EMPLOYEE EXCLUSION CONDITION (STRICT MODE) ===")
    
    print(f"Final conditions: {conditions}\n")
    return conditions