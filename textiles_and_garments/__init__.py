# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '0.0.1'

# =============================================================================
# GLOBAL STORAGE for original functions (before monkey patching)
# =============================================================================
ORIGINAL_BATCH_EXECUTE = None
ORIGINAL_GL_EXECUTE = None
ORIGINAL_GL_GET_CONDITIONS = None

def apply_general_ledger_patches():
    """Apply General Ledger monkey patches"""
    global ORIGINAL_GL_EXECUTE, ORIGINAL_GL_GET_CONDITIONS
    
    try:
        from erpnext.accounts.report.general_ledger import general_ledger
        
        # Check if already patched
        if hasattr(general_ledger.execute, '_is_custom_patched'):
            return
        
        # Store originals globally
        ORIGINAL_GL_EXECUTE = general_ledger.execute
        ORIGINAL_GL_GET_CONDITIONS = general_ledger.get_conditions
        
        from textiles_and_garments.overrides.general_ledger import (
            custom_execute,
            custom_get_conditions
        )
        
        # Apply patches
        general_ledger.execute = custom_execute
        general_ledger.get_conditions = custom_get_conditions
        
        # Mark as patched to avoid re-patching
        general_ledger.execute._is_custom_patched = True
        
        print("✓ General Ledger patches applied via __init__.py")
        
    except ImportError:
        pass
    except Exception as e:
        print(f"✗ Error applying GL patches: {e}")


def apply_batch_report_patches():
    """Apply Batch-Wise Balance History monkey patches"""
    global ORIGINAL_BATCH_EXECUTE
    
    try:
        from erpnext.stock.report.batch_wise_balance_history import batch_wise_balance_history
        
        # Check if already patched
        if hasattr(batch_wise_balance_history.execute, '_is_custom_patched'):
            print("✓ Batch report already patched, skipping...")
            return
        
        # Store original globally BEFORE importing custom function
        ORIGINAL_BATCH_EXECUTE = batch_wise_balance_history.execute
        
        from textiles_and_garments.overrides.batch_wise_balance_history import custom_execute
        
        # Apply patch
        batch_wise_balance_history.execute = custom_execute
        
        # Mark as patched
        batch_wise_balance_history.execute._is_custom_patched = True
        
        print("✓ Batch-Wise Balance History patches applied via __init__.py")
        
    except ImportError as e:
        print(f"✗ Import Error in Batch Report: {e}")
    except Exception as e:
        print(f"✗ Error applying Batch Report patches: {e}")
        import traceback
        traceback.print_exc()


# def apply_india_compliance_address_patch():
#     """Patch india_compliance validate_state to not throw when state is empty"""
#     try:
#         from india_compliance.gst_india.overrides import address as _ic_address
#         from india_compliance.gst_india.constants import STATE_NUMBERS
#         import frappe as _frappe

#         def _patched_validate_state(doc):
#             if doc.country != "India":
#                 doc.gst_state = None
#                 doc.gst_state_number = None
#                 return

#             # Auto-copy from states dropdown if state is empty
#             if not doc.state and doc.gst_state:
#                 doc.state = doc.gst_state
#             if not doc.state and getattr(doc, 'states', None):
#                 doc.state = doc.states

#             # Still empty — skip silently instead of throwing
#             if not doc.state:
#                 return

#             if doc.state not in STATE_NUMBERS:
#                 _frappe.throw(
#                     _frappe._("Please select a valid State from available options"),
#                     title=_frappe._("Invalid State"),
#                 )

#             doc.gst_state = doc.state
#             doc.gst_state_number = STATE_NUMBERS[doc.state]

#             if doc.gstin and doc.gst_state_number != doc.gstin[:2]:
#                 _frappe.throw(
#                     _frappe._(
#                         "First 2 digits of GSTIN should match with State Number for {0} ({1})"
#                     ).format(_frappe.bold(doc.gst_state), doc.gst_state_number),
#                     title=_frappe._("Invalid GSTIN or State"),
#                 )

#         _ic_address.validate_state = _patched_validate_state
#         print("✓ India Compliance Address patches applied via __init__.py")

#     except Exception as e:
#         print(f"✗ Error applying India Compliance Address patch: {e}")


# Apply all patches when module is imported
apply_general_ledger_patches()
apply_batch_report_patches()
# apply_india_compliance_address_patch()

