import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate
from frappe import _

def purchase_order(doc, method=None):
    """
    Purchase Order on_submit hook
    Update Time and Action milestones when PO is submitted
    """
    print("\n\non_submit\n\n")
    update_plans_milestones(doc)

def update_plans_milestones(doc):
    """Update PO Creation milestone for all linked plans"""
    for item in doc.items:
        if item.get('custom_plans'):
            try:
                # Reload the plan to get latest data
                plan = frappe.get_doc("Plans", item.custom_plans)
                print(f"\n\nUpdating PO Creation milestone for plan: {plan.name}")

                # Check if PO is subcontracted
                if doc.is_subcontracted == 0:
                    # Regular Purchase Order - use item_code
                    plan.update_milestone_status("PO Creation", "Completed", doc.name, item.item_code)
                else:
                    # Subcontracted Purchase Order - use fg_item
                    plan.update_milestone_status("PO Creation", "Completed", doc.name, item.fg_item)
                
            except Exception as e:
                frappe.log_error(f"Error updating plan {item.custom_plans}: {str(e)}")

@frappe.whitelist()
def remove_po_links_before_cancel(po_name, plan_names=None):
    """
    Remove PO links from Plans before cancellation (called from JS)
    """
    try:
        print(f"🔗 DEBUG: Removing links for PO: {po_name}")
        print(f"🔗 DEBUG: plan_names received: {plan_names} (type: {type(plan_names)})")
        
        # Handle the case where plan_names might be a string or list
        if isinstance(plan_names, str):
            try:
                # Try to parse as JSON if it's a string representation of a list
                import json
                plan_names = json.loads(plan_names)
            except:
                # If it's just a single plan name as string, convert to list
                plan_names = [plan_names]
        
        # If plan_names is still not provided or empty, find them from the PO
        if not plan_names:
            po = frappe.get_doc("Purchase Order", po_name)
            plan_names = set()
            for item in po.items:
                if item.get('custom_plans'):
                    plan_names.add(item.custom_plans)
            plan_names = list(plan_names)
        
        print(f"📋 Plans to process: {plan_names}")
        
        removed_count = 0
        
        for plan_name in plan_names:
            print(f"\n--- Processing plan: {plan_name} ---")
            
            if not frappe.db.exists("Plans", plan_name):
                print(f"❌ Plan {plan_name} does not exist")
                continue
                
            plan = frappe.get_doc("Plans", plan_name)
            print(f"📊 Plan loaded: {plan.name}, Milestones: {len(plan.time_and_action_milestones)}")
            
            links_cleared = 0
            # Check what references exist
            for idx, milestone in enumerate(plan.time_and_action_milestones):
                print(f"   Milestone {idx}: {milestone.milestone_name} -> {milestone.reference_document_name}")
                if milestone.reference_document_name == po_name:
                    print(f"   🎯 FOUND MATCH - clearing this one")
                    milestone.reference_document_name = None
                    milestone.status = 'Pending'
                    milestone.actual_date = None
                    milestone.delay_days = 0
                    links_cleared += 1
            
            if links_cleared > 0:
                # Save the changes
                plan.save(ignore_permissions=True)
                frappe.db.commit()
                print(f"✅ Cleared {links_cleared} links from plan {plan_name}")
                removed_count += 1
            else:
                print(f"ℹ️  No links found in plan {plan_name}")
        
        return {
            'success': True,
            'message': f'Removed links from {removed_count} plan(s)',
            'removed_count': removed_count
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        frappe.log_error(f"Error in remove_po_links_before_cancel: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }





def purchase_receipt_on_submit(doc, method=None):
    """
    Purchase Receipt on_submit hook
    Update Time and Action milestones when Purchase Receipt is submitted
    """
    try:
        updated_plans = []
        
        print(f"🔄 Processing Purchase Receipt: {doc.name}")
        print(f"📋 Is Subcontracted: {doc.is_subcontracted}")
        
        for item in doc.items:
            if item.purchase_order:
                # Get the Purchase Order
                po = frappe.get_doc("Purchase Order", item.purchase_order)
                print(f"📦 Processing Purchase Order: {po.name}")
                
                # Find the plan from PO items that match this PR item
                for po_item in po.items:
                    if po_item.name == item.purchase_order_item and po_item.get('custom_plans'):
                        plan_name = po_item.custom_plans
                        if frappe.db.exists("Plans", plan_name):
                            # Reload the plan document WITH custom methods
                            plan = frappe.get_doc("Plans", plan_name)
                            
                            # Check if this is a subcontracted purchase receipt
                            if doc.is_subcontracted == 0:
                                # ✅ Regular Purchase Receipt - match by item_code
                                print(f"🔧 Regular PO: Updating milestone with item_code: {item.item_code}")
                                plan.update_milestone_status("Purchase Receipt", "Completed", doc.name, item.item_code)
                                print(f"✅ Updated Purchase Receipt milestone for plan: {plan_name} (Regular PO)")
                            else:
                                # ✅ Subcontracted Purchase Receipt - update without item_code matching
                                print(f"🔧 Subcontracted PO: Updating milestone without item_code matching")
                                plan.update_milestone_status("Purchase Receipt", "Completed", doc.name)
                                print(f"✅ Updated Purchase Receipt milestone for plan: {plan_name} (Subcontracted)")
                            
                            updated_plans.append(plan_name)
                        else:
                            print(f"❌ Plan {plan_name} does not exist")
                    else:
                        print(f"ℹ️ PO Item {po_item.name} has no custom_plans or doesn't match PR item")
            else:
                print(f"ℹ️ PR Item {item.item_code} has no purchase_order")
        
        # Remove duplicates
        updated_plans = list(set(updated_plans))
        
        if updated_plans:
            frappe.msgprint(f"Updated Purchase Receipt milestone for {len(updated_plans)} plan(s): {', '.join(updated_plans)}")
        else:
            frappe.msgprint("No plans found to update Purchase Receipt milestone")
                            
    except Exception as e:
        frappe.log_error(f"Error in purchase_receipt_on_submit: {str(e)}")
        frappe.throw(f"Error updating plan milestones: {str(e)}")


@frappe.whitelist()
def remove_pr_links_before_cancel(pr_name, plan_names=None):
    """
    Remove Purchase Receipt links from Plans before cancellation (called from JS)
    """
    try:
        print(f"🔗 DEBUG: Removing PR links for Purchase Receipt: {pr_name}")
        print(f"🔗 DEBUG: plan_names received: {plan_names} (type: {type(plan_names)})")
        
        # Handle the case where plan_names might be a string or list
        if isinstance(plan_names, str):
            try:
                # Try to parse as JSON if it's a string representation of a list
                import json
                plan_names = json.loads(plan_names)
            except:
                # If it's just a single plan name as string, convert to list
                plan_names = [plan_names]
        
        # If plan_names is still not provided or empty, find them from the PR
        if not plan_names:
            pr = frappe.get_doc("Purchase Receipt", pr_name)
            plan_names = set()
            for item in pr.items:
                if item.get('custom_plans'):
                    plan_names.add(item.custom_plans)
            plan_names = list(plan_names)
        
        print(f"📋 Plans to process: {plan_names}")
        
        removed_count = 0
        
        for plan_name in plan_names:
            print(f"\n--- Processing plan: {plan_name} ---")
            
            if not frappe.db.exists("Plans", plan_name):
                print(f"❌ Plan {plan_name} does not exist")
                continue
                
            plan = frappe.get_doc("Plans", plan_name)
            print(f"📊 Plan loaded: {plan.name}, Milestones: {len(plan.time_and_action_milestones)}")
            
            links_cleared = 0
            # Check what references exist
            for idx, milestone in enumerate(plan.time_and_action_milestones):
                print(f"   Milestone {idx}: {milestone.milestone_name} -> {milestone.reference_document_name}")
                if milestone.reference_document_name == pr_name:
                    print(f"   🎯 FOUND MATCH - clearing this one")
                    milestone.reference_document_name = None
                    milestone.status = 'Pending'
                    milestone.actual_date = None
                    milestone.delay_days = 0
                    links_cleared += 1
            
            if links_cleared > 0:
                # Save the changes
                plan.save(ignore_permissions=True)
                frappe.db.commit()
                print(f"✅ Cleared {links_cleared} PR links from plan {plan_name}")
                removed_count += 1
            else:
                print(f"ℹ️  No PR links found in plan {plan_name}")
        
        return {
            'success': True,
            'message': f'Removed PR links from {removed_count} plan(s)',
            'removed_count': removed_count
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        frappe.log_error(f"Error in remove_pr_links_before_cancel: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }




def subcontracting_order(doc, method=None):
    """
    Subcontracting Order on_submit hook
    Update Time and Action milestones when Subcontracting Order is submitted
    """
    print(f"\n\nSubcontracting Order on_submit: {doc.name}\n\n")
    update_plans_milestones_for_sco(doc)

def update_plans_milestones_for_sco(doc):
    """Update Subcontracting Order milestone for all linked plans"""
    for item in doc.items:
        if item.get('custom_plans'):
            try:
                # Reload the plan to get latest data
                plan = frappe.get_doc("Plans", item.custom_plans)
                print(f"\n\nUpdating Subcontracting Order milestone for plan: {plan.name}")

                # Update the milestone for Subcontracting Order
                plan.update_milestone_status("Subcontracting Order", "Completed", doc.name, item.item_code)
                
            except Exception as e:
                frappe.log_error(f"Error updating plan {item.custom_plans}: {str(e)}")


@frappe.whitelist()
def remove_sco_links_before_cancel(sco_name, plan_names=None):
    """
    Remove Subcontracting Order links from Plans before cancellation (called from JS)
    """
    try:
        print(f"🔗 DEBUG: Removing SCO links for Subcontracting Order: {sco_name}")
        print(f"🔗 DEBUG: plan_names received: {plan_names} (type: {type(plan_names)})")
        
        # Handle the case where plan_names might be a string or list
        if isinstance(plan_names, str):
            try:
                # Try to parse as JSON if it's a string representation of a list
                import json
                plan_names = json.loads(plan_names)
            except:
                # If it's just a single plan name as string, convert to list
                plan_names = [plan_names]
        
        # If plan_names is still not provided or empty, find them from the SCO
        if not plan_names:
            sco = frappe.get_doc("Subcontracting Order", sco_name)
            plan_names = set()
            for item in sco.items:
                if item.get('custom_plans'):
                    plan_names.add(item.custom_plans)
            plan_names = list(plan_names)
        
        print(f"📋 Plans to process: {plan_names}")
        
        removed_count = 0
        
        for plan_name in plan_names:
            print(f"\n--- Processing plan: {plan_name} ---")
            
            if not frappe.db.exists("Plans", plan_name):
                print(f"❌ Plan {plan_name} does not exist")
                continue
                
            plan = frappe.get_doc("Plans", plan_name)
            print(f"📊 Plan loaded: {plan.name}, Milestones: {len(plan.time_and_action_milestones)}")
            
            links_cleared = 0
            # Check what references exist
            for idx, milestone in enumerate(plan.time_and_action_milestones):
                print(f"   Milestone {idx}: {milestone.milestone_name} -> {milestone.reference_document_name}")
                if milestone.reference_document_name == sco_name:
                    print(f"   🎯 FOUND MATCH - clearing this one")
                    milestone.reference_document_name = None
                    milestone.status = 'Pending'
                    milestone.actual_date = None
                    milestone.delay_days = 0
                    links_cleared += 1
            
            if links_cleared > 0:
                # Save the changes
                plan.save(ignore_permissions=True)
                frappe.db.commit()
                print(f"✅ Cleared {links_cleared} SCO links from plan {plan_name}")
                removed_count += 1
            else:
                print(f"ℹ️  No SCO links found in plan {plan_name}")
        
        return {
            'success': True,
            'message': f'Removed SCO links from {removed_count} plan(s)',
            'removed_count': removed_count
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        frappe.log_error(f"Error in remove_sco_links_before_cancel: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


# def stock_entry_on_submit(doc, method=None):
#     """
#     Stock Entry on_submit hook
#     Update Time and Action milestones when Stock Entry with 'Send to Subcontractor' is submitted
#     """
#     try:
#         # Check if this is a 'Send to Subcontractor' stock entry
#         if doc.stock_entry_type == "Send to Subcontractor":
#             print(f"\n\n🔄 Processing Send to Subcontractor Stock Entry: {doc.name}")
#             update_material_transfer_milestones(doc)
            
#     except Exception as e:
#         frappe.log_error(f"Error in stock_entry_on_submit: {str(e)}")
#         frappe.throw(_("Error updating material transfer milestones: {0}").format(str(e)))

# def update_material_transfer_milestones(doc):
#     """Update Material Transfer to Subcontractor milestone for linked plans via Subcontracting Order"""
#     try:
#         updated_plans = []
        
#         # Only process if there's a Subcontracting Order reference
#         if doc.get('subcontracting_order'):
#             sco_name = doc.subcontracting_order
#             print(f"📋 Found Subcontracting Order: {sco_name}")
#             updated_plans = update_milestone_via_sco(sco_name, doc)
#         else:
#             print("ℹ️  No Subcontracting Order found - skipping Material Transfer milestone update")
#             return
        
#         if updated_plans:
#             frappe.msgprint({
#                 'title': _('Success'),
#                 'indicator': 'green', 
#                 'message': _('Updated Material Transfer milestone for {0} plan(s): {1}').format(
#                              len(updated_plans), ', '.join(updated_plans))
#             })
#         else:
#             print("ℹ️  No linked plans found for Material Transfer update")
                
#     except Exception as e:
#         frappe.log_error(f"Error in update_material_transfer_milestones: {str(e)}")
#         raise e

# def update_milestone_via_sco(sco_name, doc):
#     """Update milestone via Subcontracting Order reference - SQL approach"""
#     updated_plans = []
    
#     try:
#         # Get the Subcontracting Order
#         sco = frappe.get_doc("Subcontracting Order", sco_name)
#         print(f"📦 Processing Subcontracting Order: {sco.name}")
        
#         # Find plans linked to this SCO
#         for item in sco.items:
#             if item.get('custom_plans'):
#                 plan_name = item.custom_plans
#                 if frappe.db.exists("Plans", plan_name):
                    
#                     # Direct SQL update
#                     result = frappe.db.sql("""
#                         UPDATE `tabTime and Action Milestones` 
#                         SET status = 'Completed', 
#                             actual_date = %s, 
#                             reference_document_name = %s,
#                             delay_days = CASE 
#                                 WHEN planned_date IS NOT NULL THEN 
#                                     DATEDIFF(%s, planned_date)
#                                 ELSE 0 
#                             END
#                         WHERE parent = %s 
#                         AND milestone_name = 'Material Transfer to Subcontractor'
#                         AND item_code = %s
#                         AND status != 'Completed'
#                     """, (frappe.utils.nowdate(), doc.name, frappe.utils.nowdate(), plan_name, item.item_code))
                    
#                     frappe.db.commit()
                    
#                     if result:
#                         print(f"✅ Updated Material Transfer milestone for plan: {plan_name}")
#                         updated_plans.append(plan_name)
#                     else:
#                         print(f"ℹ️  No matching milestone found in plan: {plan_name}")
                        
#                 else:
#                     print(f"❌ Plan {plan_name} does not exist")
#             else:
#                 print(f"ℹ️  Item {item.item_code} has no custom_plans")
                    
#     except Exception as e:
#         print(f"❌ Error updating via SCO: {str(e)}")
#         frappe.log_error(f"Error in update_milestone_via_sco: {str(e)}")
        
#     return updated_plans

# import frappe
# from frappe.utils import nowdate

def stock_entry_on_submit(doc, method=None):
    """
    Stock Entry on_submit hook
    Update Time and Action milestones when Stock Entry is submitted
    """
    try:
        # Check if this is a 'Material Transfer for Manufacture' stock entry
        if doc.stock_entry_type == "Material Transfer for Manufacture":
            print(f"\n\n🔄 Processing Material Transfer for Manufacture Stock Entry: {doc.name}")
            update_material_transfer_manufacture_milestones(doc)
        elif doc.stock_entry_type == "Manufacture":
            print(f"\n\n🔄 Processing Manufacture Stock Entry: {doc.name}") 
            update_manufacture_milestones(doc)   
        # Keep the existing subcontractor logic
        elif doc.stock_entry_type == "Send to Subcontractor":
            print(f"\n\n🔄 Processing Send to Subcontractor Stock Entry: {doc.name}")
            update_material_transfer_milestones(doc)
            
    except Exception as e:
        frappe.log_error(f"Error in stock_entry_on_submit: {str(e)}")
        frappe.throw(f"Error updating material transfer milestones: {str(e)}")

def update_material_transfer_manufacture_milestones(doc):
    """Update Material Transfer for Manufacture milestone for linked plans via Work Order"""
    try:
        updated_plans = []
        
        # Only process if there's a Work Order reference
        if doc.get('work_order'):
            wo_name = doc.work_order
            print(f"📋 Found Work Order: {wo_name}")
            updated_plans = update_milestone_via_wo(wo_name, doc)
        else:
            print("ℹ️  No Work Order found - skipping Material Transfer for Manufacture milestone update")
            return
        
        if updated_plans:
            frappe.msgprint(f"Updated Material Transfer for Manufacture milestone for {len(updated_plans)} plan(s): {', '.join(updated_plans)}")
        else:
            print("ℹ️  No linked plans found for Material Transfer for Manufacture update")
                
    except Exception as e:
        frappe.log_error(f"Error in update_material_transfer_manufacture_milestones: {str(e)}")
        raise e

def update_manufacture_milestones(doc):
    """Update Manufacture milestone for linked plans via Work Order"""
    try:
        updated_plans = []
        
        # Only process if there's a Work Order reference
        if doc.get('work_order'):
            wo_name = doc.work_order
            print(f"📋 Found Work Order: {wo_name}")
            updated_plans = update_milestone_via_wo_for_manufacture(wo_name, doc)
        else:
            print("ℹ️  No Work Order found - skipping Manufacture milestone update")
            return
        
        if updated_plans:
            frappe.msgprint(f"Updated Manufacture milestone for {len(updated_plans)} plan(s): {', '.join(updated_plans)}")
        else:
            print("ℹ️  No linked plans found for Manufacture update")
                
    except Exception as e:
        frappe.log_error(f"Error in update_manufacture_milestones: {str(e)}")
        raise e        

def update_milestone_via_wo_for_manufacture(wo_name, doc):
    """Update milestone via Work Order reference using document methods"""
    updated_plans = []
    
    try:
        # Get the Work Order
        wo = frappe.get_doc("Work Order", wo_name)
        print(f"🏭 Processing Work Order: {wo.name}")
        
        # Find plans linked to this Work Order
        if wo.get('custom_plans'):
            plan_name = wo.custom_plans
            if frappe.db.exists("Plans", plan_name):
                # Load the plan document
                plan = frappe.get_doc("Plans", plan_name)
                
                # Update both milestones using document method
                plan.update_milestone_status("Production", "Completed", doc.name)
                plan.update_milestone_status("Completed", "Completed", doc.name)
                
                print(f"✅ Updated Production and Completed milestones for plan: {plan_name}")
                updated_plans.append(plan_name)
                
            else:
                print(f"❌ Plan {plan_name} does not exist")
        else:
            print(f"ℹ️  Work Order {wo.name} has no custom_plans")
                    
    except Exception as e:
        print(f"❌ Error updating via Work Order: {str(e)}")
        frappe.log_error(f"Error in update_milestone_via_wo_for_manufacture: {str(e)}")
        
    return updated_plans
        
def update_milestone_via_wo(wo_name, doc):
    """Update milestone via Work Order reference using direct SQL"""
    updated_plans = []
    
    try:
        # Get the Work Order
        wo = frappe.get_doc("Work Order", wo_name)
        print(f"🏭 Processing Work Order: {wo.name}")
        
        # Find plans linked to this Work Order
        if wo.get('custom_plans'):
            plan_name = wo.custom_plans
            if frappe.db.exists("Plans", plan_name):
                # Update using direct SQL
                result = frappe.db.sql("""
                    UPDATE `tabTime and Action Milestones` 
                    SET status = 'Completed', 
                        actual_date = %s, 
                        reference_document_name = %s,
                        delay_days = DATEDIFF(%s, planned_date)
                    WHERE parent = %s 
                    AND milestone_name = 'Material Transfer for Manufacture'
                    AND item_code = %s
                    AND status != 'Completed'
                """, (nowdate(), doc.name, nowdate(), plan_name, wo.production_item))
                
                frappe.db.commit()
                
                if result and result[0][0] > 0:  # Check if rows were affected
                    updated_plans.append(plan_name)
                    print(f"✅ Updated Material Transfer for Manufacture milestone for plan: {plan_name}")
                else:
                    print(f"ℹ️ No update needed for plan: {plan_name}")
            else:
                print(f"❌ Plan {plan_name} does not exist")
        else:
            print(f"ℹ️  Work Order {wo.name} has no custom_plans")
                    
    except Exception as e:
        print(f"❌ Error updating via Work Order: {str(e)}")
        frappe.log_error(f"Error in update_milestone_via_wo: {str(e)}")
        
    return updated_plans

# Keep the existing subcontractor functions
def update_material_transfer_milestones(doc):
    """Update Material Transfer to Subcontractor milestone for linked plans via Subcontracting Order"""
    try:
        updated_plans = []
        
        # Only process if there's a Subcontracting Order reference
        if doc.get('subcontracting_order'):
            sco_name = doc.subcontracting_order
            print(f"📋 Found Subcontracting Order: {sco_name}")
            updated_plans = update_milestone_via_sco(sco_name, doc)
        else:
            print("ℹ️  No Subcontracting Order found - skipping Material Transfer milestone update")
            return
        
        if updated_plans:
            frappe.msgprint(f"Updated Material Transfer milestone for {len(updated_plans)} plan(s): {', '.join(updated_plans)}")
        else:
            print("ℹ️  No linked plans found for Material Transfer update")
                
    except Exception as e:
        frappe.log_error(f"Error in update_material_transfer_milestones: {str(e)}")
        raise e

def update_milestone_via_sco(sco_name, doc):
    """Update milestone via Subcontracting Order reference using direct SQL"""
    updated_plans = []
    
    try:
        # Get the Subcontracting Order
        sco = frappe.get_doc("Subcontracting Order", sco_name)
        print(f"📦 Processing Subcontracting Order: {sco.name}")
        
        # Find plans linked to this SCO
        for sco_item in sco.items:
            if hasattr(sco_item, 'custom_plans') and sco_item.custom_plans:
                plan_name = sco_item.custom_plans
                if frappe.db.exists("Plans", plan_name):
                    # Update using direct SQL
                    result = frappe.db.sql("""
                        UPDATE `tabTime and Action Milestones` 
                        SET status = 'Completed', 
                            actual_date = %s, 
                            reference_document_name = %s,
                            delay_days = DATEDIFF(%s, planned_date)
                        WHERE parent = %s 
                        AND milestone_name = 'Material Transfer to Subcontractor'
                        AND item_code = %s
                        AND status != 'Completed'
                    """, (nowdate(), doc.name, nowdate(), plan_name, sco_item.item_code))
                    
                    frappe.db.commit()
                    
                    if result and result[0][0] > 0:  # Check if rows were affected
                        updated_plans.append(plan_name)
                        print(f"✅ Updated Material Transfer to Subcontractor milestone for plan: {plan_name}")
                    else:
                        print(f"ℹ️ No update needed for plan: {plan_name}")
                else:
                    print(f"❌ Plan {plan_name} does not exist")
            else:
                print(f"ℹ️ SCO Item {sco_item.item_code} has no custom_plans")
                    
    except Exception as e:
        print(f"❌ Error updating via SCO: {str(e)}")
        frappe.log_error(f"Error in update_milestone_via_sco: {str(e)}")
        
    return updated_plans


# @frappe.whitelist()
# def remove_stock_entry_links_before_cancel(stock_entry_name, subcontracting_order=None):
#     """
#     Remove Stock Entry links from Plans before cancellation (called from JS)
#     Only for 'Send to Subcontractor' stock entries
#     """
#     try:
#         print(f"🔗 DEBUG: Removing Stock Entry links for: {stock_entry_name}")
#         print(f"🔗 DEBUG: Subcontracting Order: {subcontracting_order}")
        
#         # Get the Stock Entry document
#         stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
        
#         # Verify this is a 'Send to Subcontractor' stock entry
#         if stock_entry.stock_entry_type != "Send to Subcontractor":
#             return {
#                 'success': False,
#                 'error': 'This is not a Send to Subcontractor stock entry'
#             }
        
#         # Use the provided subcontracting_order or get from stock entry
#         if not subcontracting_order and stock_entry.get('subcontracting_order'):
#             subcontracting_order = stock_entry.subcontracting_order
        
#         if not subcontracting_order:
#             return {
#                 'success': False,
#                 'error': 'No Subcontracting Order found for this Stock Entry'
#             }
        
#         print(f"📋 Processing Subcontracting Order: {subcontracting_order}")
        
#         removed_count = 0
        
#         # Get the Subcontracting Order and find linked plans
#         if frappe.db.exists("Subcontracting Order", subcontracting_order):
#             sco = frappe.get_doc("Subcontracting Order", subcontracting_order)
            
#             for item in sco.items:
#                 if item.get('custom_plans'):
#                     plan_name = item.custom_plans
#                     if frappe.db.exists("Plans", plan_name):
#                         plan = frappe.get_doc("Plans", plan_name)
#                         print(f"📊 Plan loaded: {plan.name}, Milestones: {len(plan.time_and_action_milestones)}")
                        
#                         links_cleared = 0
#                         # Check what references exist for this Stock Entry
#                         for idx, milestone in enumerate(plan.time_and_action_milestones):
#                             print(f"   Milestone {idx}: {milestone.milestone_name} -> {milestone.reference_document_name}")
#                             if (milestone.reference_document_name == stock_entry_name and 
#                                 milestone.milestone_name == "Material Transfer to Subcontractor"):
#                                 print(f"   🎯 FOUND MATCH - clearing Material Transfer milestone")
#                                 milestone.reference_document_name = None
#                                 milestone.status = 'Pending'
#                                 milestone.actual_date = None
#                                 milestone.delay_days = 0
#                                 links_cleared += 1
                        
#                         if links_cleared > 0:
#                             # Save the changes
#                             plan.save(ignore_permissions=True)
#                             frappe.db.commit()
#                             print(f"✅ Cleared {links_cleared} Stock Entry links from plan {plan_name}")
#                             removed_count += 1
#                         else:
#                             print(f"ℹ️  No Stock Entry links found in plan {plan_name}")
#                     else:
#                         print(f"❌ Plan {plan_name} does not exist")
#                 else:
#                     print(f"ℹ️  Item {item.item_code} has no custom_plans")
#         else:
#             print(f"❌ Subcontracting Order {subcontracting_order} does not exist")
        
#         return {
#             'success': True,
#             'message': f'Removed Material Transfer links from {removed_count} plan(s)',
#             'removed_count': removed_count
#         }
        
#     except Exception as e:
#         print(f"❌ ERROR: {str(e)}")
#         frappe.log_error(f"Error in remove_stock_entry_links_before_cancel: {str(e)}")
#         return {
#             'success': False,
#             'error': str(e)
#         }

@frappe.whitelist()
def remove_stock_entry_links_before_cancel(stock_entry_name, work_order=None, subcontracting_order=None):
    """
    Remove Stock Entry links from Plans before cancellation (called from JS)
    Works for 'Material Transfer for Manufacture', 'Manufacture', and 'Send to Subcontractor' stock entries
    """
    try:
        print(f"🔗 DEBUG: Removing Stock Entry links for: {stock_entry_name}")
        print(f"🔗 DEBUG: Work Order: {work_order}")
        print(f"🔗 DEBUG: Subcontracting Order: {subcontracting_order}")
        
        # Get the Stock Entry document
        stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
        
        # Define milestone names based on stock entry type
        milestone_mapping = {
            "Material Transfer for Manufacture": "Material Transfer for Manufacture",
            "Manufacture": "Production", 
            "Send to Subcontractor": "Material Transfer to Subcontractor"
        }
        
        stock_entry_type = stock_entry.stock_entry_type
        milestone_name = milestone_mapping.get(stock_entry_type)
        
        if not milestone_name:
            return {
                'success': False,
                'error': f'Stock Entry type "{stock_entry_type}" not supported for link removal'
            }
        
        print(f"📋 Processing Stock Entry type: {stock_entry_type}, Milestone: {milestone_name}")
        
        removed_count = 0
        
        if stock_entry_type == "Send to Subcontractor":
            # Handle subcontracting stock entries
            if not subcontracting_order and stock_entry.get('subcontracting_order'):
                subcontracting_order = stock_entry.subcontracting_order
            
            if not subcontracting_order:
                return {
                    'success': False,
                    'error': 'No Subcontracting Order found for this Stock Entry'
                }
            
            if frappe.db.exists("Subcontracting Order", subcontracting_order):
                sco = frappe.get_doc("Subcontracting Order", subcontracting_order)
                
                for item in sco.items:
                    if item.get('custom_plans'):
                        plan_name = item.custom_plans
                        removed_count += remove_stock_entry_links_from_plan(plan_name, stock_entry_name, milestone_name)
        
        elif stock_entry_type in ["Material Transfer for Manufacture", "Manufacture"]:
            # Handle manufacturing stock entries
            if not work_order and stock_entry.get('work_order'):
                work_order = stock_entry.work_order
            
            if not work_order:
                return {
                    'success': False,
                    'error': 'No Work Order found for this Stock Entry'
                }
            
            if frappe.db.exists("Work Order", work_order):
                wo = frappe.get_doc("Work Order", work_order)
                
                if wo.get('custom_plans'):
                    plan_name = wo.custom_plans
                    removed_count += remove_stock_entry_links_from_plan(plan_name, stock_entry_name, milestone_name, wo.production_item)
        
        return {
            'success': True,
            'message': f'Removed {milestone_name} links from {removed_count} plan(s)',
            'removed_count': removed_count,
            'milestone_name': milestone_name
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        frappe.log_error(f"Error in remove_stock_entry_links_before_cancel: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def remove_stock_entry_links_from_plan(plan_name, stock_entry_name, milestone_name, item_code=None):
    """Remove stock entry links from a specific plan"""
    try:
        if not frappe.db.exists("Plans", plan_name):
            print(f"❌ Plan {plan_name} does not exist")
            return 0
            
        plan = frappe.get_doc("Plans", plan_name)
        print(f"📊 Plan loaded: {plan.name}, Milestones: {len(plan.time_and_action_milestones)}")
        
        links_cleared = 0
        
        # Check what references exist for this Stock Entry
        for idx, milestone in enumerate(plan.time_and_action_milestones):
            print(f"   Milestone {idx}: {milestone.milestone_name} -> {milestone.reference_document_name}")
            
            # Match by milestone name and reference document
            milestone_matches = (
                milestone.milestone_name == milestone_name and 
                milestone.reference_document_name == stock_entry_name
            )
            
            # If item_code is provided, also match by item_code
            if item_code:
                milestone_matches = milestone_matches and milestone.item_code == item_code
            
            if milestone_matches:
                print(f"   🎯 FOUND MATCH - clearing {milestone_name} milestone")
                milestone.reference_document_name = None
                milestone.status = 'Pending'
                milestone.actual_date = None
                milestone.delay_days = 0
                links_cleared += 1
        
        if links_cleared > 0:
            # Save the changes
            plan.save(ignore_permissions=True)
            frappe.db.commit()
            print(f"✅ Cleared {links_cleared} Stock Entry links from plan {plan_name}")
            return links_cleared
        else:
            print(f"ℹ️  No Stock Entry links found in plan {plan_name}")
            return 0
            
    except Exception as e:
        print(f"❌ Error processing plan {plan_name}: {str(e)}")
        return 0




def subcontracting_receipt_on_submit(doc, method=None):
    """
    Subcontracting Receipt on_submit hook
    Update Time and Action milestones when Subcontracting Receipt is submitted
    """
    try:
        print(f"\n\n🔄 Processing Subcontracting Receipt: {doc.name}")
        update_subcontract_receipt_milestones(doc)
            
    except Exception as e:
        frappe.log_error(f"Error in subcontracting_receipt_on_submit: {str(e)}")
        frappe.throw(_("Error updating subcontract receipt milestones: {0}").format(str(e)))

def update_subcontract_receipt_milestones(doc):
    """Update Subcontract Receipt milestone for linked plans via Subcontracting Order from items"""
    try:
        updated_plans = []
        
        # Process each item in the Subcontracting Receipt
        if hasattr(doc, 'items') and doc.items:
            for item in doc.items:
                # Check if item has subcontracting_order field
                if hasattr(item, 'subcontracting_order') and item.subcontracting_order:
                    sco_name = item.subcontracting_order
                    print(f"📋 Found Subcontracting Order in item: {sco_name}")
                    
                    # Update milestones for this SCO
                    item_updated_plans = update_milestone_via_sco_for_sr(sco_name, doc, item)
                    updated_plans.extend(item_updated_plans)
        
        # Remove duplicates
        updated_plans = list(set(updated_plans))
        
        if updated_plans:
            frappe.msgprint({
                'title': _('Success'),
                'indicator': 'green', 
                'message': _('Updated Subcontract Receipt milestone for {0} plan(s): {1}').format(
                             len(updated_plans), ', '.join(updated_plans))
            })
        else:
            print("ℹ️ No linked plans found for Subcontract Receipt update")
                
    except Exception as e:
        frappe.log_error(f"Error in update_subcontract_receipt_milestones: {str(e)}")
        raise e

def update_milestone_via_sco_for_sr(sco_name, doc, receipt_item):
    """Update milestone via Subcontracting Order reference"""
    updated_plans = []
    
    try:
        # Get the Subcontracting Order
        sco = frappe.get_doc("Subcontracting Order", sco_name)
        print(f"📦 Processing Subcontracting Order: {sco.name}")
        
        # Find plans linked to this SCO
        for sco_item in sco.items:
            if hasattr(sco_item, 'custom_plans') and sco_item.custom_plans:
                plan_name = sco_item.custom_plans
                if frappe.db.exists("Plans", plan_name):
                    # Update using direct SQL (most reliable)
                    result = frappe.db.sql("""
                        UPDATE `tabTime and Action Milestones` 
                        SET status = 'Completed', 
                            actual_date = %s, 
                            reference_document_name = %s
                        WHERE parent = %s 
                        AND milestone_name = 'Subcontract Receipt'
                        AND item_code = %s
                        AND status != 'Completed'
                    """, (frappe.utils.nowdate(), doc.name, plan_name, sco_item.item_code))
                    
                    frappe.db.commit()
                    
                    if result and result[0][0] > 0:  # Check if rows were affected
                        updated_plans.append(plan_name)
                        print(f"✅ Updated Subcontract Receipt milestone for plan: {plan_name}")
                    else:
                        print(f"ℹ️ No update needed for plan: {plan_name}")
                else:
                    print(f"❌ Plan {plan_name} does not exist")
            else:
                print(f"ℹ️ SCO Item {sco_item.item_code} has no custom_plans")
                    
    except Exception as e:
        print(f"❌ Error updating via SCO: {str(e)}")
        frappe.log_error(f"Error in update_milestone_via_sco: {str(e)}")
        
    return updated_plans 


@frappe.whitelist()
def remove_subcontracting_receipt_links_before_cancel(receipt_name, subcontracting_orders=None):
    """
    Remove Subcontracting Receipt links from Plans before cancellation
    Uses Subcontracting Orders from items table
    """
    try:
        removed_count = 0
        
        # Handle the case where subcontracting_orders might be a string or list
        if isinstance(subcontracting_orders, str):
            try:
                import json
                subcontracting_orders = json.loads(subcontracting_orders)
            except:
                subcontracting_orders = [subcontracting_orders]
        
        # Process each Subcontracting Order
        if subcontracting_orders:
            for sco_name in subcontracting_orders:
                # Get the Subcontracting Order
                sco = frappe.get_doc("Subcontracting Order", sco_name)
                print(f"📦 Processing Subcontracting Order for link removal: {sco.name}")
                
                # Reset milestones for all linked plans
                for item in sco.items:
                    if hasattr(item, 'custom_plans') and item.custom_plans:
                        plan_name = item.custom_plans
                        if frappe.db.exists("Plans", plan_name):
                            # Reset using direct SQL
                            frappe.db.sql("""
                                UPDATE `tabTime and Action Milestones` 
                                SET status = 'Pending', 
                                    actual_date = NULL, 
                                    reference_document_name = NULL,
                                    delay_days = 0
                                WHERE parent = %s 
                                AND milestone_name = 'Subcontract Receipt'
                                AND reference_document_name = %s
                                AND item_code = %s
                            """, (plan_name, receipt_name, item.item_code))
                            
                            frappe.db.commit()
                            removed_count += 1
                            print(f"✅ Removed Subcontract Receipt links from plan: {plan_name}")
        
        return {
            'success': True,
            'message': f'Removed Subcontract Receipt links from {removed_count} plan(s)',
            'removed_count': removed_count
        }
        
    except Exception as e:
        print(f"❌ Error in remove_subcontracting_receipt_links_before_cancel: {str(e)}")
        frappe.log_error(f"Error in remove_subcontracting_receipt_links_before_cancel: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def work_order_on_submit(doc, method=None):
    """
    Work Order on_submit hook
    Update Time and Action milestones when Work Order is submitted
    """
    try:
        if doc.get('custom_plans'):
            plan_name = doc.custom_plans  # ← FIXED: should be custom_plans, not custom_source_plan
            if frappe.db.exists("Plans", plan_name):
                # Reload the plan document
                plan = frappe.get_doc("Plans", plan_name)
                print(f"Updating Work Order Creation milestone for plan: {plan.name}")
                
                # Update the milestone using Plans class method
                plan.update_milestone_status("Work Order Creation", "Completed", doc.name, doc.production_item)
                
                frappe.msgprint(f"Updated Work Order Creation milestone for plan: {plan.name}")
            else:
                frappe.msgprint(f"Plan {plan_name} not found")
        else:
            frappe.msgprint("No plan linked to this Work Order")
                            
    except Exception as e:
        frappe.log_error(f"Error in work_order_on_submit: {str(e)}")
        frappe.throw(f"Error updating plan milestones: {str(e)}")  # ← FIXED: Added missing closing parenthesis


@frappe.whitelist()
def remove_wo_links_before_cancel(wo_name, plan_names=None):
    """
    Remove Work Order links from Plans before cancellation (called from JS)
    """
    try:
        print(f"🔗 DEBUG: Removing WO links for Work Order: {wo_name}")
        print(f"🔗 DEBUG: plan_names received: {plan_names} (type: {type(plan_names)})")
        
        # Handle the case where plan_names might be a string or list
        if isinstance(plan_names, str):
            try:
                # Try to parse as JSON if it's a string representation of a list
                import json
                plan_names = json.loads(plan_names)
            except:
                # If it's just a single plan name as string, convert to list
                plan_names = [plan_names]
        
        # If plan_names is still not provided or empty, find them from the WO
        if not plan_names:
            wo = frappe.get_doc("Work Order", wo_name)
            if wo.get('custom_plans'):
                plan_names = [wo.custom_plans]
            else:
                plan_names = []
        
        print(f"📋 Plans to process: {plan_names}")
        
        removed_count = 0
        
        for plan_name in plan_names:
            print(f"\n--- Processing plan: {plan_name} ---")
            
            if not frappe.db.exists("Plans", plan_name):
                print(f"❌ Plan {plan_name} does not exist")
                continue
                
            plan = frappe.get_doc("Plans", plan_name)
            print(f"📊 Plan loaded: {plan.name}, Milestones: {len(plan.time_and_action_milestones)}")
            
            links_cleared = 0
            # Check what references exist
            for idx, milestone in enumerate(plan.time_and_action_milestones):
                print(f"   Milestone {idx}: {milestone.milestone_name} -> {milestone.reference_document_name}")
                if milestone.reference_document_name == wo_name:
                    print(f"   🎯 FOUND MATCH - clearing this one")
                    milestone.reference_document_name = None
                    milestone.status = 'Pending'
                    milestone.actual_date = None
                    milestone.delay_days = 0
                    links_cleared += 1
            
            if links_cleared > 0:
                # Save the changes
                plan.save(ignore_permissions=True)
                frappe.db.commit()
                print(f"✅ Cleared {links_cleared} WO links from plan {plan_name}")
                removed_count += 1
            else:
                print(f"ℹ️  No WO links found in plan {plan_name}")
        
        return {
            'success': True,
            'message': f'Removed WO links from {removed_count} plan(s)',
            'removed_count': removed_count
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        frappe.log_error(f"Error in remove_wo_links_before_cancel: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }



