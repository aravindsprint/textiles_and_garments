# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals

# __version__ = '0.0.1'

# def apply_general_ledger_patches():
#     """Apply General Ledger monkey patches"""
#     try:
#         from erpnext.accounts.report.general_ledger import general_ledger
        
#         # Check if already patched
#         if hasattr(general_ledger.execute, '_is_custom_patched'):
#             return
            
#         from textiles_and_garments.overrides.general_ledger import (
#             custom_execute,
#             custom_get_conditions
#         )
        
#         # Apply patches
#         general_ledger.execute = custom_execute
#         general_ledger.get_conditions = custom_get_conditions
        
#         # Mark as patched to avoid re-patching
#         general_ledger.execute._is_custom_patched = True
        
#         print("✓ General Ledger patches applied via __init__.py")
        
#     except ImportError:
#         # ERPNext might not be installed yet
#         pass
#     except Exception as e:
#         print(f"✗ Error applying GL patches: {e}")

# # Apply patches when module is imported
# apply_general_ledger_patches()


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
        # ERPNext might not be installed yet
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

# Apply patches when module is imported
apply_general_ledger_patches()
apply_batch_report_patches()