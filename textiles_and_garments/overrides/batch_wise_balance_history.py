# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from frappe import _

# =============================================================================
# CONFIGURATION: Block ALL Sales Users (Strict Mode)
# =============================================================================

# Roles to block (users with ANY of these roles will be blocked)
RESTRICTED_ROLES = ["Sales User"]

# STRICT MODE: Block users with restricted roles even if they have other roles
STRICT_MODE = True

# These roles are still defined but won't override the restriction in STRICT_MODE
UNRESTRICTED_ROLES = ["Stock Manager", "System Manager", "Accounts Manager"]

# Optional: Block/Allow specific users by email
RESTRICTED_USERS = []
UNRESTRICTED_USERS = []

def is_user_restricted():
    """
    Check if current user is restricted from accessing Batch-Wise Balance History
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
    Override Batch-Wise Balance History report to restrict access for Sales Users
    STRICT MODE: Blocks ALL users with Sales User role
    """
    user_restricted = is_user_restricted()
    user_roles = frappe.get_roles(frappe.session.user)
    
    # Filter relevant roles for logging
    relevant_roles = [r for r in user_roles if r in RESTRICTED_ROLES + UNRESTRICTED_ROLES]
    
    # DEBUG: Log access check
    print(f"\n{'='*60}")
    print(f"BATCH REPORT ACCESS CHECK (STRICT MODE)")
    print(f"User: {frappe.session.user}")
    print(f"Relevant Roles: {relevant_roles}")
    print(f"Has Sales User Role: {'Sales User' in user_roles}")
    print(f"Restricted: {user_restricted}")
    print(f"{'='*60}\n")
    
    # Block access if user is restricted
    if user_restricted:
        print("=== BLOCKING ACCESS - USER HAS SALES USER ROLE ===")
        
        frappe.throw(
            _("You do not have permission to access the <b>Batch-Wise Balance History</b> report.<br><br>"
              "This report contains sensitive inventory and batch tracking information.<br><br>"
              "<b>Note:</b> Access is restricted for all users with the Sales User role.<br><br>"
              "Please contact your System Manager or Stock Manager if you need access to this report."),
            title=_("Access Restricted"),
            exc=frappe.PermissionError
        )
    
    # Get original execute from main app module
    import textiles_and_garments
    
    original_execute = textiles_and_garments.ORIGINAL_BATCH_EXECUTE
    
    if not original_execute:
        frappe.throw(
            _("System Error: Original batch report function not found.<br><br>"
              "Please restart bench: <code>bench restart</code>"),
            title=_("Configuration Error")
        )
    
    # Convert filters to frappe._dict if it's a plain dict
    if filters and isinstance(filters, dict) and not isinstance(filters, frappe._dict):
        filters = frappe._dict(filters)
    
    # Call original execute
    print("=== CALLING ORIGINAL EXECUTE - USER ALLOWED ===")
    result = original_execute(filters)
    
    if result and len(result) > 1:
        print(f"=== RETURNED {len(result[1])} ROWS ===\n")
    
    return result