# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.accounts.report.general_ledger import general_ledger

# Store original execute function
_original_execute = general_ledger.execute

# =============================================================================
# CONFIGURATION: Define which users/roles are restricted
# =============================================================================

# Option 1: Restrict specific roles
RESTRICTED_ROLES = [
    "Accounts User",
    "Sales User",
    # Add more roles here
]

# Option 2: Unrestricted roles (can see Employee data)
UNRESTRICTED_ROLES = [
    "Accounts Manager",
    "System Manager",
    "HR Manager",
    # Add more roles here
]

# Option 3: Restrict specific users (optional)
RESTRICTED_USERS = [
    # "user1@example.com",
    # "user2@example.com",
]

# Option 4: Unrestricted users (optional)
UNRESTRICTED_USERS = [
    # "admin@example.com",
    # "manager@example.com",
]

def is_user_restricted():
    """
    Check if current user is restricted from viewing Employee data
    Returns True if user IS restricted
    """
    user = frappe.session.user
    
    # Administrator is never restricted
    if user == "Administrator":
        return False
    
    # Check unrestricted users first (whitelist)
    if UNRESTRICTED_USERS and user in UNRESTRICTED_USERS:
        return False
    
    # Check restricted users (blacklist)
    if RESTRICTED_USERS and user in RESTRICTED_USERS:
        return True
    
    # Check user roles
    user_roles = frappe.get_roles(user)
    
    # If user has any unrestricted role, allow access
    if UNRESTRICTED_ROLES:
        for role in UNRESTRICTED_ROLES:
            if role in user_roles:
                return False
    
    # If user has any restricted role, restrict access
    if RESTRICTED_ROLES:
        for role in RESTRICTED_ROLES:
            if role in user_roles:
                return True
    
    # Default: No restriction if not in any list
    return False

def custom_execute(filters=None):
    """
    Override General Ledger report to exclude Employee party type for restricted users
    """
    # Check if user is restricted
    user_restricted = is_user_restricted()
    
    # DEBUG: Log function call
    frappe.log_error(
        f"Custom GL Execute Called - User: {frappe.session.user}, Restricted: {user_restricted}",
        str(filters)
    )
    print(f"\n=== CUSTOM GL EXECUTE - User: {frappe.session.user}, Restricted: {user_restricted} ===\n")
    
    # Only apply restrictions if user is restricted
    if user_restricted:
        # Block if Employee party type is explicitly selected
        if filters and filters.get("party_type") == "Employee":
            print("=== BLOCKING EMPLOYEE PARTY TYPE FOR RESTRICTED USER ===")
            frappe.throw(
                _("You do not have permission to view General Ledger for Employee party type. "
                  "Please contact your administrator or use Employee Advance/Expense Claim reports."),
                title=_("Access Restricted")
            )
    
    # Call original execute function
    print("=== CALLING ORIGINAL EXECUTE ===")
    columns, data = _original_execute(filters)
    print(f"=== ORIGINAL EXECUTE RETURNED {len(data) if data else 0} ROWS ===")
    
    # Filter out Employee entries only for restricted users
    if user_restricted and data:
        original_count = len(data)
        filtered_data = []
        for row in data:
            # Check if row is a dict and has party_type field
            if isinstance(row, dict) and row.get("party_type") == "Employee":
                print(f"=== FILTERING OUT EMPLOYEE ROW FOR RESTRICTED USER: {row.get('party', 'N/A')} ===")
                continue
            filtered_data.append(row)
        
        print(f"=== FILTERED {original_count - len(filtered_data)} EMPLOYEE ROWS ===")
        return columns, filtered_data
    
    return columns, data

# Store original get_conditions function
_original_get_conditions = general_ledger.get_conditions

def custom_get_conditions(filters):
    """
    Add condition to exclude Employee party type from GL entries for restricted users
    """
    print(f"\n=== CUSTOM GET_CONDITIONS - User: {frappe.session.user} ===")
    
    # Get original conditions
    conditions = _original_get_conditions(filters)
    
    # Only add restriction for restricted users
    user_restricted = is_user_restricted()
    
    if user_restricted and not filters.get("party_type"):
        # If no party_type filter, exclude Employee by default
        additional_condition = " and (party_type IS NULL OR party_type != 'Employee')"
        conditions += additional_condition
        print(f"=== ADDED EMPLOYEE EXCLUSION CONDITION FOR RESTRICTED USER ===")
    
    print(f"Final conditions: {conditions}\n")
    return conditions