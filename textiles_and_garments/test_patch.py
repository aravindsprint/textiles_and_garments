import frappe
from frappe.utils import today, add_days

def test_batch_patch():
    """
    Test if batch report patch is applied
    """
    print("\n" + "="*80)
    print("TESTING BATCH-WISE BALANCE HISTORY PATCH")
    print("="*80 + "\n")
    
    try:
        # Import the report module
        from erpnext.stock.report.batch_wise_balance_history import batch_wise_balance_history
        
        # Check the execute function
        print(f"Execute function: {batch_wise_balance_history.execute}")
        print(f"Function name: {batch_wise_balance_history.execute.__name__}")
        print(f"Function module: {batch_wise_balance_history.execute.__module__}")
        
        # Check if it's our custom function
        is_custom = batch_wise_balance_history.execute.__name__ == "custom_execute"
        has_patch_marker = hasattr(batch_wise_balance_history.execute, '_is_custom_patched')
        
        print(f"\nIs custom execute? {is_custom}")
        print(f"Has patch marker? {has_patch_marker}")
        
        if is_custom or has_patch_marker:
            print("\n✓ PATCH IS APPLIED CORRECTLY")
        else:
            print("\n✗ PATCH IS NOT APPLIED")
            print("Make sure to restart bench after updating __init__.py")
            return
        
        # Test with different users
        print("\n" + "-"*80)
        print("TESTING WITH DIFFERENT USERS")
        print("-"*80 + "\n")
        
        # Prepare proper filters for the report
        filters = {
            "from_date": add_days(today(), -30),
            "to_date": today(),
            "item_code": None,
            "warehouse": None,
            "batch_no": None
        }
        
        test_users = [
            ("Administrator", False),
        ]
        
        # Try to find a Sales User
        sales_users = frappe.get_all("User", 
            filters={"enabled": 1},
            fields=["name"],
            limit=10
        )
        
        for user_doc in sales_users:
            user_roles = frappe.get_roles(user_doc.name)
            if "Sales User" in user_roles and "Stock Manager" not in user_roles:
                test_users.append((user_doc.name, True))
                break
        
        for test_user, should_block in test_users:
            print(f"\nTesting user: {test_user}")
            print(f"Should be blocked: {should_block}")
            user_roles = frappe.get_roles(test_user)
            print(f"Relevant roles: {[r for r in user_roles if r in ['Sales User', 'Stock Manager', 'Stock User', 'System Manager']]}")
            
            frappe.set_user(test_user)
            
            try:
                result = batch_wise_balance_history.execute(filters)
                if should_block:
                    print(f"  ✗ FAIL - User should be blocked but got access!")
                    print(f"  Got {len(result[1]) if result and len(result) > 1 else 0} rows")
                else:
                    print(f"  ✓ PASS - User has access as expected")
                    print(f"  Got {len(result[1]) if result and len(result) > 1 else 0} rows")
            except frappe.PermissionError as e:
                if should_block:
                    print(f"  ✓ PASS - User blocked as expected")
                    print(f"  Error: {str(e)[:100]}")
                else:
                    print(f"  ✗ FAIL - User should have access but was blocked!")
                    print(f"  Error: {str(e)}")
            except Exception as e:
                print(f"  ✗ ERROR - {type(e).__name__}: {str(e)[:200]}")
                import traceback
                traceback.print_exc()
            finally:
                frappe.set_user("Administrator")
        
    except ImportError as e:
        print(f"\n✗ IMPORT ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_batch_patch()