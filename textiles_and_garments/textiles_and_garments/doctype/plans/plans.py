# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today
import json
from collections import defaultdict
from frappe import _
from frappe.utils import nowdate, add_days, getdate





class Plans(Document):
    def before_save(self):
        """Automatically generate Time and Action milestones"""
        if self.is_new() or not self.get('time_and_action_milestones'):
            self.generate_time_and_action_milestones()
        self.update_overall_status()

    def generate_time_and_action_milestones(self):
        """Generate milestones based on purchase_or_manufacture"""
        base_date = self.posting_date or nowdate()
        self.time_and_action_milestones = []
        
        if self.purchase_or_manufacture == "Purchase":
            self.generate_purchase_milestones(base_date)
        elif self.purchase_or_manufacture == "Manufacture":
            self.generate_manufacture_milestones(base_date)
        elif self.purchase_or_manufacture == "Subcontract":
            self.generate_subcontract_milestones(base_date)

    def generate_purchase_milestones(self, base_date):
        milestones = [
            {"name": "PO Creation", "days": 0, "ref_type": "Purchase Order", "parallel": True},
            {"name": "Purchase Receipt", "days": 7, "ref_type": "Purchase Receipt", "parallel": False},
            {"name": "Completed", "days": 10, "ref_type": None, "parallel": False}
        ]
        
        for milestone in milestones:
            self.append("time_and_action_milestones", {
                "item_code": self.item_code,
                "milestone_name": milestone["name"],
                "planned_date": add_days(base_date, milestone["days"]),
                "status": "Pending",
                "reference_document_type": milestone["ref_type"],
                "qty": self.plan_qty,
                "is_parallel": milestone["parallel"]
            })

    def generate_manufacture_milestones(self, base_date):
        milestones = [
            {"name": "Work Order Creation", "days": 0, "ref_type": "Work Order", "parallel": True},
            {"name": "Material Transfer for Manufacture", "days": 2, "ref_type": "Stock Entry", "parallel": False},
            {"name": "Production", "days": 5, "ref_type": "Stock Entry", "parallel": False},
            {"name": "Completed", "days": 8, "ref_type": None, "parallel": False}
        ]
        
        for milestone in milestones:
            self.append("time_and_action_milestones", {
                "item_code": self.item_code,
                "milestone_name": milestone["name"],
                "planned_date": add_days(base_date, milestone["days"]),
                "status": "Pending",
                "reference_document_type": milestone["ref_type"],
                "qty": self.plan_qty,
                "is_parallel": milestone["parallel"]
            })

    def generate_subcontract_milestones(self, base_date):
        milestones = [
            {"name": "PO Creation", "days": 0, "ref_type": "Purchase Order", "parallel": True},
            {"name": "Subcontracting Order", "days": 2, "ref_type": "Subcontracting Order", "parallel": False},
            {"name": "Material Transfer to Subcontractor", "days": 3, "ref_type": "Stock Entry", "parallel": False},
            {"name": "Subcontract Receipt", "days": 12, "ref_type": "Subcontracting Receipt", "parallel": False},
            {"name": "Purchase Receipt", "days": 14, "ref_type": "Purchase Receipt", "parallel": False},
            {"name": "Completed", "days": 15, "ref_type": None, "parallel": False}
        ]
        
        for milestone in milestones:
            self.append("time_and_action_milestones", {
                "item_code": self.item_code,
                "milestone_name": milestone["name"],
                "planned_date": add_days(base_date, milestone["days"]),
                "status": "Pending",
                "reference_document_type": milestone["ref_type"],
                "qty": self.plan_qty,
                "is_parallel": milestone["parallel"]
            })

    def update_overall_status(self):
        """Update overall status based on milestones"""
        if not self.get('time_and_action_milestones'):
            self.completed_milestones = 0
            self.total_milestones = 0
            self.progress_percentage = 0
            # Only update overall_status if document is draft
            if self.docstatus == 0:
                self.overall_status = "Planning"
            return
            
        total = len(self.time_and_action_milestones)
        completed = len([m for m in self.time_and_action_milestones if m.status == "Completed"])
        
        self.completed_milestones = completed
        self.total_milestones = total
        self.progress_percentage = (completed / total * 100) if total > 0 else 0
        
        # Only update overall_status if document is draft
        if self.docstatus == 1:
            # Check for delays
            today = nowdate()
            delayed_milestones = 0
            
            for m in self.time_and_action_milestones:
                try:
                    if (m.status == "Pending" and m.planned_date):
                        planned_date = getdate(m.planned_date)
                        if planned_date < today:
                            delayed_milestones += 1
                except Exception as e:
                    print(f"Error processing milestone date: {m.planned_date}, Error: {e}")
                    continue
            
            if completed == total:
                self.overall_status = "Completed"
                self.overall_actual_date = nowdate()
            elif delayed_milestones > 0:
                self.overall_status = "Delayed"
            elif completed > 0:
                self.overall_status = "In Progress" 
            else:
                self.overall_status = "Planning"
            
            print(f"Updated overall status: {self.overall_status}, Progress: {self.progress_percentage}%")

    def update_milestone_status(self, milestone_name, status, reference_doc_name=None, item_code=None):
        """Update milestone status and calculate delays"""
        for milestone in self.time_and_action_milestones:
            if (milestone.milestone_name == milestone_name and 
                (not item_code or milestone.item_code == item_code) and
                milestone.status != "Completed"):
                
                milestone.status = status
                milestone.actual_date = nowdate()
                
                if reference_doc_name:
                    milestone.reference_document_name = reference_doc_name
                
                # Calculate delay
                if milestone.planned_date and milestone.actual_date:
                    planned_date = getdate(milestone.planned_date)
                    actual_date = getdate(milestone.actual_date)
                    milestone.delay_days = frappe.utils.date_diff(actual_date, planned_date)
                
                break
        
        # Check if all other milestones are completed, then mark "Completed" milestone as done
        self.check_and_complete_final_milestone()
        
        # Update overall status after milestone update
        self.update_overall_status()
        self.save(ignore_permissions=True)

    def check_and_complete_final_milestone(self):
        """Automatically mark the 'Completed' milestone when all other milestones are done"""
        if not self.get('time_and_action_milestones'):
            return
        
        # Get all milestones except the "Completed" one
        non_completed_milestones = [
            m for m in self.time_and_action_milestones 
            if m.milestone_name != "Completed" and m.status != "Completed"
        ]
        
        # If all non-completed milestones are done, mark the "Completed" milestone
        if len(non_completed_milestones) == 0:
            for milestone in self.time_and_action_milestones:
                if milestone.milestone_name == "Completed" and milestone.status != "Completed":
                    milestone.status = "Completed"
                    milestone.actual_date = nowdate()
                    print(f"Automatically completed final milestone for plan: {self.name}")
                    break

    # def on_submit(self):
    #     """Trigger document creation when Plan is submitted"""
    #     if self.purchase_or_manufacture == "Purchase":
    #         self.create_purchase_order()
    #     elif self.purchase_or_manufacture == "Manufacture":
    #         self.create_work_order()
    #     elif self.purchase_or_manufacture == "Subcontract":
    #         self.create_purchase_order()
    #     self.update_production_wip_plans()     

    # def create_purchase_order(self):
    #     """Create Purchase Order from Plans"""
    #     print("\n\ncreate_purchase_order\n\n")
    #     po = frappe.new_doc("Purchase Order")
    #     po.schedule_date = self.posting_date
    #     po.custom_source_plan = self.name
        
    #     # Add item to PO
    #     po.append("items", {
    #         "item_code": self.item_code,
    #         "qty": self.plan_qty,
    #         "rate": 0,  # You might want to fetch from Item Price
    #         "schedule_date": self.posting_date
    #     })
        
    #     po.insert()
    #     po.submit()
        
    #     # Update milestone
    #     self.update_milestone_status("PO Creation", "Completed", po.name, self.item_code)
        
    #     # If subcontract, create subcontracting order
    #     if self.purchase_or_manufacture == "Subcontract":
    #         frappe.enqueue(self.create_subcontracting_order, queue='short', po_name=po.name)

    # def create_work_order(self):
    #     """Create Work Order from Plans"""
    #     wo = frappe.new_doc("Work Order")
    #     wo.production_item = self.item_code
    #     wo.qty = self.plan_qty
    #     wo.planned_start_date = self.posting_date
    #     wo.bom_no = self.bom
    #     wo.custom_source_plan = self.name
        
    #     wo.insert()
    #     wo.submit()
        
    #     self.update_milestone_status("Work Order Creation", "Completed", wo.name, self.item_code)

    # def create_subcontracting_order(self, po_name):
    #     """Create Subcontracting Order from Purchase Order"""
    #     # Wait a bit for PO to be fully committed
    #     import time
    #     time.sleep(2)
        
    #     po = frappe.get_doc("Purchase Order", po_name)
        
    #     # Create Subcontracting Order
    #     sco = frappe.new_doc("Subcontracting Order")
    #     sco.purchase_order = po_name
    #     sco.supplier = po.supplier
    #     sco.custom_source_plan = self.name
        
    #     # Copy items from PO
    #     for item in po.items:
    #         sco.append("items", {
    #             "item_code": item.item_code,
    #             "qty": item.qty,
    #             "rate": item.rate
    #         })
        
    #     sco.insert()
    #     sco.submit()
        
    #     self.update_milestone_status("Subcontracting Order", "Completed", sco.name, self.item_code)

    # def update_milestone_status(self, milestone_name, status, reference_doc_name=None, item_code=None):
    #     """Update milestone status and calculate delays"""
    #     for milestone in self.time_and_action_milestones:
    #         if (milestone.milestone_name == milestone_name and 
    #             (not item_code or milestone.item_code == item_code) and
    #             milestone.status != "Completed"):
                
    #             milestone.status = status
    #             milestone.actual_date = nowdate()
                
    #             if reference_doc_name:
    #                 milestone.reference_document_name = reference_doc_name
                
    #             # Calculate delay
    #             if milestone.planned_date and milestone.actual_date:
    #                 milestone.delay_days = frappe.utils.date_diff(milestone.actual_date, milestone.planned_date)
                
    #             break
        
    #     self.save()

    def before_cancel(self):
        print("\n\nbefore cancel\n\n")
        # frappe.msgprint("✅ after_cancel hook triggered")
        # unlink_plan_item_planned_wise_referencess1(self.name)
        unlink_and_update_plan_item_summary(self.name)

    def validate(self):
        self.validate_plan_qty()
        self.set_reserved_and_unreserved_qty_based_wip()

    # def on_submit(self):
    #     self.update_production_wip_plans()    
         

    
    def update_production_wip_plans(self):
        # Iterate over the child table rows
        for row in self.plans_wip_item:
            target_child_plan = row.get("plan")  # This is the "Plans" document to update
            reserve_plan_name = row.get("parent")  # The 'plan' value inside the child table
            reserve_qty = flt(row.get("to_reserve_qty"))

            if not target_child_plan or not reserve_plan_name:
                continue

            try:
                # Fetch the target Plans document
                plan_doc = frappe.get_doc("Plans", target_child_plan)

                # Check if the child row already exists
                existing_rows = [child for child in plan_doc.get("reserved_wip_plans") if child.plan == reserve_plan_name]

                if reserve_qty == 0:
                    # Delete the row if reserve_qty is 0
                    plan_doc.reserved_wip_plans = [
                        child for child in plan_doc.reserved_wip_plans if child.plan != reserve_plan_name
                    ]
                else:
                    if existing_rows:
                        # Update existing row
                        existing_rows[0].reserve_qty = reserve_qty
                    else:
                        # Insert new row
                        plan_doc.append("reserved_wip_plans", {
                            "plan": reserve_plan_name,
                            "reserve_qty": reserve_qty
                        })

                # Recalculate total reserved_qty from child table
                total_reserved_qty = sum(flt(c.reserve_qty) for c in plan_doc.get("reserved_wip_plans"))
                plan_doc.reserved_qty = total_reserved_qty
                plan_doc.unreserved_qty = flt(plan_doc.plan_qty) - flt(plan_doc.unreserved_received_qty) - total_reserved_qty

                # Save the updated Plans doc
                plan_doc.save(ignore_permissions=True)

            except frappe.DoesNotExistError:
                frappe.log_error(f"Plans document '{target_child_plan}' not found.")
                continue

        frappe.db.commit()
    
    def set_reserved_and_unreserved_qty_based_wip(self):
        print("\n\nset_reserved_and_unreserved_qty_based_wip\n\n")

        # Check if Reserved WIP Plans table is empty
        if not self.get("reserved_wip_plans"):
            self.reserved_qty = 0
            self.unreserved_qty = self.plan_qty or 0
            return

        # Optional: Handle the case where the table has rows (if needed)
        total_reserved = sum([row.reserved_qty or 0 for row in self.reserved_wip_plans])
        self.reserved_qty = total_reserved
        self.unreserved_qty = (self.plan_qty or 0) - total_reserved


    def validate_plan_qty(self):
        if not self.plan_items or not self.item_code:
            return  # Skip if key fields are missing

        # Get allowed qty for item_code from Plan Items Detail table
        total_allowed_qty = frappe.db.sql("""
            SELECT SUM(qty)
            FROM `tabPlan Items Detail`
            WHERE parent = %s AND item_code = %s
        """, (self.plan_items, self.item_code))[0][0] or 0
        print("\n\ntotal_allowed_qty\n\n",total_allowed_qty)

        # Get sum of plan_qty from all submitted Plans with same plan_items and item_code (excluding current doc)
        existing_total_plan_qty = frappe.db.sql("""
            SELECT SUM(plan_qty)
            FROM `tabPlans`
            WHERE plan_items = %s AND item_code = %s AND docstatus = 1 AND name != %s
        """, (self.plan_items, self.item_code, self.name))[0][0] or 0
        print("\n\nexisting_total_plan_qty\n\n",existing_total_plan_qty)
        print("\n\nself.plan_qty\n\n",self.plan_qty)

        existing_shortclose_plan_qty = frappe.db.sql("""
            SELECT SUM(short_close_plan_qty)
            FROM `tabPlans`
            WHERE plan_items = %s AND item_code = %s AND docstatus = 1 AND name != %s
        """, (self.plan_items, self.item_code, self.name))[0][0] or 0
        print("\n\nexisting_shortclose_plan_qty\n\n",existing_shortclose_plan_qty)
        print("\n\nself.plan_qty\n\n",self.plan_qty)

        # Calculate combined plan_qty (existing + current)
        combined_plan_qty = existing_total_plan_qty - existing_shortclose_plan_qty + (self.plan_qty or 0)

        if combined_plan_qty > total_allowed_qty:
            frappe.throw(_(
                "Total Planned Qty ({0}) exceeds allowed Qty ({1}) in Plan Items Detail for Item Code: {2}.".format(
                    combined_plan_qty, total_allowed_qty, self.item_code
                )
            ))    




def unlink_and_update_plan_item_summary(docname):
    print("\n\nunlink_and_update_plan_item_summary\n\n")

    # Load the Plans document
    plans_doc = frappe.get_doc("Plans", docname)
    plan = plans_doc.name

    # Ensure plan_items field is linked
    if not plans_doc.plan_items:
        frappe.throw("No Plan Items document is linked in this Plans document.")

    # Load the linked Plan Items document
    plan_item_doc = frappe.get_doc("Plan Items", plans_doc.plan_items)

    # Step 1: Remove rows in plan_item_planned_wise that match the plan
    original_count = len(plan_item_doc.plan_item_planned_wise)
    print("\n\noriginal_count\n\n", original_count)

    plan_item_doc.set(
        "plan_item_planned_wise",
        [row for row in plan_item_doc.plan_item_planned_wise if row.plan != plan]
    )

    removed_count = original_count - len(plan_item_doc.plan_item_planned_wise)
    print("\n\nremoved_count\n\n", removed_count)

    # Step 2: Recalculate summary
    summary = defaultdict(float)
    for row in plan_item_doc.plan_item_planned_wise:
        summary[row.item_code] += row.plan_qty

    # Step 3: Clear old summary
    plan_item_doc.set("plan_items_summary", [])

    # Step 4: Rebuild summary rows using plan_items_detail
    item_totals = defaultdict(float)
    for row in plan_item_doc.get("plan_items_detail", []):
        if row.item_code:
            item_totals[row.item_code] += row.qty or 0

    for item_code, original_qty in item_totals.items():
        planned_qty = summary.get(item_code, 0)
        need_to_plan_qty = original_qty - planned_qty

        item_details = frappe.db.get_value(
            "Item",
            item_code,
            ["custom_commercial_name", "stock_uom"],
            as_dict=True
        ) or {}

        plan_item_doc.append("plan_items_summary", {
            "item_code": item_code,
            "commercial_name": item_details.get("custom_commercial_name"),
            "uom": item_details.get("stock_uom"),
            "qty": original_qty,
            "planned_qty": planned_qty,
            "need_to_plan_qty": need_to_plan_qty
        })

    # Step 5: Save only if rows were removed
    if removed_count > 0:
        plan_item_doc.save(ignore_permissions=True)
        frappe.db.commit()

    return f"{removed_count} row(s) removed from plan_item_planned_wise and summary table updated."





@frappe.whitelist()
def update_production_wip_plans(plans_wip_item):
    if isinstance(plans_wip_item, str):
        plans_wip_item = json.loads(plans_wip_item)

    for row in plans_wip_item:
        target_child_plan = row.get("plan")  # This is the "Plans" document to update
        reserve_plan_name = row.get("parent")  # The 'plan' value inside the child table
        reserve_qty = flt(row.get("to_reserve_qty"))

        if not target_child_plan or not reserve_plan_name:
            continue

        try:
            # Fetch the target Plans document
            plan_doc = frappe.get_doc("Plans", target_child_plan)

            # Check if the child row already exists
            existing_rows = [child for child in plan_doc.get("reserved_wip_plans") if child.plan == reserve_plan_name]

            if reserve_qty == 0:
                # Delete the row if reserve_qty is 0
                plan_doc.reserved_wip_plans = [
                    child for child in plan_doc.reserved_wip_plans if child.plan != reserve_plan_name
                ]
            else:
                if existing_rows:
                    # Update existing row
                    existing_rows[0].reserve_qty = reserve_qty
                else:
                    # Insert new row
                    plan_doc.append("reserved_wip_plans", {
                        "plan": reserve_plan_name,
                        "reserve_qty": reserve_qty
                    })

            # Recalculate total reserved_qty from child table
            total_reserved_qty = sum(flt(c.reserve_qty) for c in plan_doc.get("reserved_wip_plans"))
            plan_doc.reserved_qty = total_reserved_qty
            # plan_doc.unreserved_qty = flt(plan_doc.plan_qty) - total_reserved_qty
            plan_doc.unreserved_qty = flt(plan_doc.plan_qty) - flt(plan_doc.unreserved_received_qty) - total_reserved_qty

            # Save the updated Plans doc
            plan_doc.save(ignore_permissions=True)

        except frappe.DoesNotExistError:
            frappe.log_error(f"Plans document '{target_child_plan}' not found.")
            continue

    frappe.db.commit()
    return "Reserved WIP Plans updated successfully."



@frappe.whitelist()
def mark_plan_completed(plan_name):
    """Manually mark a plan as completed"""
    plan = frappe.get_doc("Plans", plan_name)
    
    for milestone in plan.time_and_action_milestones:
        if milestone.milestone_name == "Completed" and milestone.status != "Completed":
            milestone.status = "Completed"
            milestone.actual_date = nowdate()
            break
    
    plan.update_overall_status()
    plan.save(ignore_permissions=True)
    frappe.msgprint(f"Plan {plan_name} marked as completed")




@frappe.whitelist()
def cancel_production_stock_reservation(docname):
    print("\n\ncancel_production_stock_reservation\n\n")

    # Find all submitted Production Stock Reservations linked to this plan
    reservations = frappe.get_all(
        "Production Stock Reservation",
        filters={
            "plans_no": docname,
            "docstatus": 1  # Only submitted docs
        },
        pluck="name"
    )

    if not reservations:
        return "No Production Stock Reservations found to cancel."

    for name in reservations:
        try:
            psr = frappe.get_doc("Production Stock Reservation", name)
            psr.cancel()
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"Failed to cancel PSR: {name}")
            frappe.throw(_("Error cancelling PSR {0}: {1}").format(name, str(e)))

    return "Cancelled"


@frappe.whitelist()
def unlink_plan_item_planned_wise_referencess(docname):
    print("\n\nunlink_plan_item_planned_wise_referencess\n\n")

    # Load the Plans document
    plans_doc = frappe.get_doc("Plans", docname)
    plan = plans_doc.name

    # Ensure plan_items field is linked
    if not plans_doc.plan_items:
        frappe.throw("No Plan Items document is linked in this Plans document.")

    # Load the linked Plan Items document
    plan_item_doc = frappe.get_doc("Plan Items", plans_doc.plan_items)

    # Step 1: Remove rows matching the plan from plan_item_planned_wise
    original_count = len(plan_item_doc.plan_item_planned_wise)
    print("\n\noriginal_count\n\n", original_count)

    plan_item_doc.set(
        "plan_item_planned_wise",
        [row for row in plan_item_doc.plan_item_planned_wise if row.plan != plan]
    )

    removed_count = original_count - len(plan_item_doc.plan_item_planned_wise)
    print("\n\nremoved_count\n\n", removed_count)

    # Step 2: Recalculate planned_qty summary from remaining plan_item_planned_wise entries
    summary = defaultdict(float)
    for row in plan_item_doc.plan_item_planned_wise:
        summary[row.item_code] += row.plan_qty

    # Clear old summary
    plan_item_doc.set("plan_items_summary", [])

    # Create a temporary list to hold the newly built summary rows
    temp_new_summary_rows = []

    # Rebuild plan_items_summary using plan_items_detail as the base for original_qty
    # Iterate through all items in plan_items_detail to ensure all relevant items are considered
    # and their original_qty is correctly captured.
    item_details_from_detail_table = defaultdict(float)
    for detail_row in plan_item_doc.get("plan_items_detail", []):
        if detail_row.item_code:
            item_details_from_detail_table[detail_row.item_code] += detail_row.qty or 0

    for item_code, original_qty in item_details_from_detail_table.items():
        planned_qty = summary.get(item_code, 0) # Get planned_qty from the aggregated summary
        need_to_plan_qty = original_qty - planned_qty

        # Fetch additional item details from the Item doctype
        item_details = frappe.db.get_value(
            "Item",
            item_code,
            ["custom_commercial_name", "stock_uom"],
            as_dict=True
        ) or {}

        # Append to the temporary list
        temp_new_summary_rows.append({
            "item_code": item_code,
            "commercial_name": item_details.get("custom_commercial_name"),
            "uom": item_details.get("stock_uom"),
            "qty": original_qty, # This is the total original qty from plan_items_detail
            "planned_qty": planned_qty,
            "need_to_plan_qty": need_to_plan_qty
        })

    # --- Step 3: Rearrange plan_items_summary based on plan_items_detail order ---
    # Get the desired order of item_codes from plan_item_doc.plan_items_detail
    ordered_item_codes = [detail_row.item_code for detail_row in plan_item_doc.plan_items_detail]

    # Create a dictionary for quick lookup of the newly built summary rows by item_code
    new_summary_map = {row["item_code"]: row for row in temp_new_summary_rows}

    # Construct the final, ordered list for plan_items_summary
    final_ordered_summary = []
    for item_code in ordered_item_codes:
        if item_code in new_summary_map:
            final_ordered_summary.append(new_summary_map[item_code])
        # If an item_code from detail is not found in the new summary (e.g., if it was
        # never planned and had 0 quantity after unlinking), you might choose to
        # add it here with 0 planned_qty if it's desired to always show all detail items.
        # For now, it will only include items that were processed in temp_new_summary_rows.

    # Assign the newly ordered list back to the child table
    plan_item_doc.plan_items_summary = final_ordered_summary

    # --- Final Save ---
    # Save the document regardless, as the summary table has been rebuilt.
    # The 'removed_count' check is no longer strictly necessary for saving,
    # as the summary is always updated.
    plan_item_doc.save(ignore_permissions=True)
    frappe.db.commit()

    return f"{removed_count} row(s) removed from plan_item_planned_wise and summary table updated."




def on_cancel(self):
    frappe.msgprint("✅ on_cancel fallback triggered")

@frappe.whitelist()
def unlink_plan_item_planned_wise_referencesss(docname):
    print("\n\n--- unlink_plan_item_planned_wise_referencesss ---\n\n")

    # Load the Plans document
    plans_doc = frappe.get_doc("Plans", docname)
    plan = plans_doc.name

    if not plans_doc.plan_items:
        frappe.throw("No Plan Items document linked in Plans.")

    print(f"\n\nLinked Plan Items Doc: \n\n{plans_doc.plan_items}\n\n")

    # Load the linked Plan Items document
    plan_item_doc = frappe.get_doc("Plan Items", plans_doc.plan_items)

    if not hasattr(plan_item_doc, "plan_item_planned_wise"):
        frappe.throw("Child table 'plan_item_planned_wise' not found in Plan Items.")

    updated_count = 0

    for row in plan_item_doc.plan_item_planned_wise:
        if row.plan == plan:
            print(f"Setting plan_qty = 0 for row with plan = {row.plan}")
            row.plan_qty = 0
            updated_count += 1

    if updated_count > 0:
        plan_item_doc.save(ignore_permissions=True)
        frappe.db.commit()
        return f"Updated {updated_count} row(s) in Plan Item Planned Wise (plan_qty set to 0)."
    else:
        return "No matching rows found to update."

@frappe.whitelist()
def cancel_plan_dependencies(docname):
    print("\n\ncancel_plan_dependencies\n\n")

    messages = []

    # Step 1: Cancel Production Stock Reservations
    reservations = frappe.get_all(
        "Production Stock Reservation",
        filters={
            "plans_no": docname,
            "docstatus": 1
        },
        pluck="name"
    )

    if reservations:
        for name in reservations:
            try:
                psr = frappe.get_doc("Production Stock Reservation", name)
                psr.cancel()
                frappe.db.commit()
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Failed to cancel PSR: {name}")
                frappe.throw(_("Error cancelling PSR {0}: {1}").format(name, str(e)))

        messages.append(f"Cancelled {len(reservations)} Production Stock Reservation(s).")
    else:
        messages.append("No Production Stock Reservations found to cancel.")

    # Step 2: Remove Plan Item Planned Wise entries
    plans_doc = frappe.get_doc("Plans", docname)
    plan_no = plans_doc.name

    if not plans_doc.plan_items:
        frappe.throw("No Plan Items document linked in Plans.")

    plan_item_doc = frappe.get_doc("Plan Items", plans_doc.plan_items)

    before_count = len(plan_item_doc.plan_item_planned_wise)

    print("\n\n\nbefore_count\n\n\n",before_count)
    plan_item_doc.set(
        "plan_item_planned_wise",
        [row for row in plan_item_doc.plan_item_planned_wise if row.plan_no != plan_no]
    )
    after_count = len(plan_item_doc.plan_item_planned_wise)
    print("\n\n\nafter_count\n\n\n",after_count)

    if before_count != after_count:
        plan_item_doc.save(ignore_permissions=True)
        frappe.db.commit()
        messages.append(f"Removed {before_count - after_count} row(s) from Plan Item Planned Wise.")
    else:
        messages.append("No matching plan item planned wise entries found to remove.")

    return "\n".join(messages)







@frappe.whitelist()
def update_plan_items_planned_wise(docname):
    # Load the Plans document
    plans_doc = frappe.get_doc("Plans", docname)

    if not plans_doc.plan_items:
        frappe.throw("No linked Plan Items found in the Plans document.")

    # Load the linked Plan Items document
    plan_item_doc = frappe.get_doc("Plan Items", plans_doc.plan_items)

    # Extract values from the Plans doc
    plan_item_code = plans_doc.item_code
    plan_qty = plans_doc.plan_qty
    plan = plans_doc.name

    # Append to plan_item_planned_wise if not already present
    exists = any(child.plan == plan for child in plan_item_doc.plan_item_planned_wise)
    print("\n\nexists\n\n",exists)

    print("\n\nexists\n\n",exists)
    if not exists:
        print("\n\nexists\n\n",exists)
        plan_item_doc.append("plan_item_planned_wise", {
            "item_code": plan_item_code,
            "plan": plan,
            "plan_qty": plan_qty,
            "plan_against": plans_doc.plan_against,
            "purchase_or_manufacture": plans_doc.purchase_or_manufacture,
        })
        plan_item_doc.save(ignore_permissions=True)

    # Step 2: Aggregate planned qty by item_code from plan_item_planned_wise
    summary_data = defaultdict(float)
    for row in plan_item_doc.plan_item_planned_wise:
        summary_data[row.item_code] += row.plan_qty
        print("\n\nsummary_data\n\n",summary_data)

    # Step 3: Update existing plan_items_summary rows
    for summary_row in plan_item_doc.plan_items_summary:
        print("\n\nsummary_row\n\n",summary_row)
        item_code = summary_row.item_code
        if item_code in summary_data:
            print("\n\nitem_code\n\n",item_code )
            print("\n\nsummary_row\n\n",summary_row.qty )
            print("\n\nsummary_data\n\n",summary_data )
            # Corrected line: Use item_code as the key for summary_data
            planned_qty = summary_data[item_code]
            print("\n\nplanned_qty\n\n",planned_qty )
            original_qty = summary_row.qty or 0
            print("\n\noriginal_qty\n\n",original_qty )
            summary_row.planned_qty = planned_qty
            summary_row.need_to_plan_qty = original_qty - planned_qty
            print("\n\nsummary_row\n\n",summary_row)

    plan_item_doc.save(ignore_permissions=True)
    frappe.db.commit()
    return True






@frappe.whitelist()
def create_production_stock_reservation(docname, plans_stock_item):
    print("\n\ncreate_production_stock_reservation\n\n")

    if isinstance(plans_stock_item, str):
        plans_stock_item = json.loads(plans_stock_item)

    for row in plans_stock_item:
        reserved_qty = flt(row.get("reserve_qty"))
        if reserved_qty <= 0:
            continue  # Skip rows with no reservation

        item_code = row.get("item")
        batch_no = row.get("batch")
        warehouse = row.get("warehouse")
        uom = row.get("uom")

        # Check if reservation already exists for this item + batch + warehouse + plan
        exists = frappe.db.exists(
            "Production Stock Reservation",
            {
                "item_code": item_code,
                "plans_no": docname,
                "reservation_based_on": "Serial and Batch"
            }
        )

        if exists:
            existing_psr = frappe.get_doc("Production Stock Reservation", exists)
            for entry in existing_psr.sb_entries:
                if entry.batch_no == batch_no and entry.warehouse == warehouse:
                    print(f"Skipping duplicate reservation for {item_code}, {batch_no}, {warehouse}")
                    break
            else:
                # No matching entry in child table — append new child row
                existing_psr.append("sb_entries", {
                    "batch_no": batch_no,
                    "warehouse": warehouse,
                    "qty": reserved_qty,
                    "voucher_qty": reserved_qty,
                    "stock_uom": uom,
                    "delivered_qty": 0,
                    "incoming_rate": 0,
                    "outgoing_rate": 0,
                    "is_outward": 0,
                    "stock_value_difference": 0,
                })
                existing_psr.save(ignore_permissions=True)
                if existing_psr.docstatus == 0:
                    existing_psr.submit()
                frappe.db.commit()
        else:
            # No PSR exists yet for this item/plan — create a new one
            psr = frappe.new_doc("Production Stock Reservation")
            psr.item_code = item_code
            psr.plans_no = docname
            psr.reserved_qty = reserved_qty
            psr.stock_uom = uom
            psr.company = frappe.db.get_value("Global Defaults", None, "default_company")
            psr.reservation_based_on = "Serial and Batch"

            psr.append("sb_entries", {
                "batch_no": batch_no,
                "warehouse": warehouse,
                "qty": reserved_qty,
                "voucher_qty": reserved_qty,
                "stock_uom": uom,
                "delivered_qty": 0,
                "incoming_rate": 0,
                "outgoing_rate": 0,
                "is_outward": 0,
                "stock_value_difference": 0,
            })

            psr.insert(ignore_permissions=True)
            psr.submit()
            frappe.db.commit()

    return "Created and Submitted"




@frappe.whitelist()
def get_wip_details(docname, item_code, bom):
    if not bom:
        return []

    # Get item codes from BOM
    bom_doc = frappe.get_doc("BOM", bom)
    item_codes = [item.item_code for item in bom_doc.items]

    if not item_codes:
        return []

    # Collect all matching Plans records for the BOM items
    all_plans = []
    for code in item_codes:
        plans = frappe.get_all(
            "Plans",
            filters={"item_code": code, "docstatus": 1},
            fields=["name", "item_code", "plan_qty", "plan_items", "reserved_qty", "unreserved_qty", "unreserved_received_qty", "reserved_received_qty"]
        )

        # Filter out the current document and plans with zero quantity
        filtered = [plan for plan in plans if plan["name"] != docname and plan["plan_qty"] > 0]
        
        # Calculate to_reserve_qty for each plan
        for plan in filtered:
            unreserved_received_qty = flt(plan.get("unreserved_received_qty", 0))
            reserved_qty = flt(plan.get("reserved_qty", 0))
            plan_qty = flt(plan.get("plan_qty", 0))

            plan["to_reserve_qty"] = plan_qty - unreserved_received_qty - reserved_qty

            print("\n\nunreserved_received_qty\n\n",unreserved_received_qty)
            print("\n\nreserved_qty\n\n",reserved_qty)
            print("\n\nplan_qty\n\n",plan_qty)
            print("\n\nplan[to_reserve_qty]\n\n",plan["to_reserve_qty"])
            
            # # Simplified logic for calculating to_reserve_qty
            # if received_qty == 0 and reserved_qty == 0:
            #     plan["to_reserve_qty"] = plan_qty
            # else:
            #     plan["to_reserve_qty"] = plan_qty - max(received_qty, reserved_qty)
            
            # # Ensure to_reserve_qty is not negative
            # plan["to_reserve_qty"] = max(0, plan["to_reserve_qty"])
            
            # Debug prints (consider removing in production)
            # print("\n\nplan[name]\n\n",plan["name"])
            # # print("\n\nplan[unreserved_received_qty]\n\n",plan["unreserved_received_qty"])
            # print("\n\nplan[reserved_qty]\n\n",plan["reserved_qty"])
            # print("\n\nplan[to_reserve_qty]\n\n",plan["to_reserve_qty"])
        
        all_plans.extend(filtered)

    # Sort by "name" in descending order
    all_plans.sort(key=lambda x: x["name"], reverse=True)

    return all_plans

def get_received_quantity_for_plan(plan_name, item_code):
    # print("\n\nplan_name\n\n",plan_name)
    """Get total received quantity from purchase and subcontracting receipts for a plan"""
    # Get from Purchase Receipts
    pr_qty = frappe.db.sql("""
        SELECT SUM(pri.qty) as qty
        FROM `tabPurchase Receipt Item` pri
        JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
        WHERE pri.custom_plans = %s
        AND pri.item_code = %s
        AND pr.docstatus = 1
    """, (plan_name, item_code), as_dict=True)[0].qty or 0

    # Get from Subcontracting Receipts
    scr_qty = frappe.db.sql("""
        SELECT SUM(sri.received_qty) as qty
        FROM `tabSubcontracting Receipt Item` sri
        JOIN `tabSubcontracting Receipt` sr ON sr.name = sri.parent
        WHERE sri.custom_plans = %s
        AND sri.item_code = %s
        AND sr.docstatus = 1
    """, (plan_name, item_code), as_dict=True)[0].qty or 0


    wo_qty = frappe.db.sql("""
        SELECT SUM(wo.produced_qty) as qty
        FROM `tabWork Order` wo
        WHERE wo.custom_plans = %s
        AND wo.production_item = %s
        AND wo.docstatus = 1
    """, (plan_name, item_code), as_dict=True)[0].qty or 0

    return pr_qty + scr_qty + wo_qty





@frappe.whitelist()
def remove_zero_reserve_rows(docname, plans_stock_item):
    
    if isinstance(plans_stock_item, str):
        plans_stock_item = json.loads(plans_stock_item)

    # Filter out rows with reserve_qty == 0
    filtered_items = [
        row for row in plans_stock_item
        if flt(row.get("reserve_qty", 0)) > 0
    ]

    return filtered_items

@frappe.whitelist()
def remove_zero_reserve_rows_in_wip(docname, plans_wip_item):
    
    if isinstance(plans_wip_item, str):
        plans_wip_item = json.loads(plans_wip_item)

    # Filter out rows with reserve_qty == 0
    filtered_items = [
        row for row in plans_wip_item
        if flt(row.get("to_reserve_qty", 0)) > 0
    ]

    return filtered_items    



@frappe.whitelist()
def get_bom_details_from_plan_items(docname, bom, plan_items_detail, search_batch=None):
    if not bom:
        return []

    
    print("\n\ndocname,\n\n",docname)
    print("\n\nbom,\n\n",bom)
    print("\n\nplan_items_detail,\n\n",plan_items_detail)
    # print("\n\ndocname,\n\n",docname)
    bom_doc = frappe.get_doc("BOM", bom)
    item_codes = [item.item_code for item in bom_doc.items]

    if not item_codes:
        return []

    filters = frappe._dict({
        "item_codes": item_codes,
        "include_expired_batches": False,
        "to_date": today()
    })

    batchwise_data = get_batchwise_data_from_stock_ledger(filters)
    batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)
    data = parse_batchwise_data(batchwise_data)

    # Filter data based on search_batch if provided
    # if search_batch:
    #     search_batches = [b.strip() for b in search_batch.split(',')]
    #     print("\n\nsearch_batches\n\n",search_batches)
    #     data = [row for row in data if row.get("batch_no") in search_batches]
    if search_batch:
        search_patterns = [b.strip().replace('%', '') for b in search_batch.split(',')]
        print("\n\nsearch_patterns\n\n", search_patterns)
        
        data = [
            row for row in data 
            if any(
                pattern in (row.get("batch_no") or "")
                for pattern in search_patterns
            )
        ]

    # Fetch previous reservations from Plans Stock Item
    reserved_map = get_reserved_quantities(docname)

    for row in data:
        key = (row.get("warehouse"), row.get("batch_no"))
        print("\n\nkey\n\n",key)
        print("\n\nreserved_map.get(key, 0)\n\n",reserved_map.get(key, 0))
        previous_reserved_qty = reserved_map.get(key, 0)
        row["previous_reserved_qty"] = previous_reserved_qty
        row["avail_qty"] = flt(row.get("balance_qty")) - flt(previous_reserved_qty)

    return data
    



@frappe.whitelist()
def get_bom_details(docname, bom, search_batch, indent):
    if not bom:
        return []

    bom_doc = frappe.get_doc("BOM", bom)
    item_codes = [item.item_code for item in bom_doc.items]

    if not item_codes:
        return []

    filters = frappe._dict({
        "item_codes": item_codes,
        "include_expired_batches": False,
        "to_date": today()
    })

    batchwise_data = get_batchwise_data_from_stock_ledger(filters)
    batchwise_data = get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters)
    data = parse_batchwise_data(batchwise_data)

    # Filter data based on search_batch if provided
    # if search_batch:
    #     search_batches = [b.strip() for b in search_batch.split(',')]
    #     print("\n\nsearch_batches\n\n",search_batches)
    #     data = [row for row in data if row.get("batch_no") in search_batches]
    if search_batch:
        search_patterns = [b.strip().replace('%', '') for b in search_batch.split(',')]
        print("\n\nsearch_patterns\n\n", search_patterns)
        
        data = [
            row for row in data 
            if any(
                pattern in (row.get("batch_no") or "")
                for pattern in search_patterns
            )
        ]

    # Fetch previous reservations from Plans Stock Item
    reserved_map = get_reserved_quantities(docname)

    for row in data:
        key = (row.get("warehouse"), row.get("batch_no"))
        print("\n\nkey\n\n",key)
        print("\n\nreserved_map.get(key, 0)\n\n",reserved_map.get(key, 0))
        previous_reserved_qty = reserved_map.get(key, 0)
        row["previous_reserved_qty"] = previous_reserved_qty
        row["avail_qty"] = flt(row.get("balance_qty")) - flt(previous_reserved_qty)

    return data



def get_reserved_quantities(exclude_docname):
    """
    Returns a dictionary with key (warehouse, batch) and value as 
    (sum of all reserve_qty) - (sum of all actual_delivered_qty)
    from all 'Plans Stock Item' entries excluding the current docname.
    """
    reserved_map = {}

    # First get all reserve quantities grouped by warehouse and batch
    # reserve_results = frappe.db.get_all(
    #     "Plans Stock Item",
    #     fields=["warehouse", "batch", "sum(reserve_qty) as total_reserve"],
    #     filters={"parent": ["!=", exclude_docname], "docstatus": ["=", 1]},
    #     group_by="warehouse, batch"
    # )

    reserve_results = frappe.db.get_all(
        "Serial and Batch Entry Plans",
        fields=["warehouse", "batch_no", "sum(qty) as total_reserve"],
        filters={"parenttype": "Production Stock Reservation", "docstatus": ["=", 1]},
        group_by="warehouse, batch_no"
    )

    print("\n\nreserve_results\n\n", reserve_results)

    # Create a dictionary of all actual delivered quantities by warehouse and batch
    actual_delivered_map = {}
    actual_delivered_results = frappe.db.get_all(
        "Serial and Batch Entry Plans",
        fields=["warehouse", "batch_no", "sum(actual_delivered_qty) as total_delivered"],
        filters={"parenttype": "Production Stock Reservation"},
        group_by="warehouse, batch_no"
    )

    print("\n\nactual_delivered_results\n\n", actual_delivered_results)

    for entry in actual_delivered_results:
        key = (entry.warehouse, entry.batch_no)
        actual_delivered_map[key] = flt(entry.total_delivered or 0)

    # Create a dictionary of all short close quantities by warehouse and batch
    short_close_map = {}
    short_close_results = frappe.db.get_all(
        "Serial and Batch Entry Plans",
        fields=["warehouse", "batch_no", "sum(short_close_qty) as total_short_close"],
        filters={"parenttype": "Production Stock Reservation", "docstatus": 1},
        group_by="warehouse, batch_no"
    )
    print("\n\nshort_close_results\n\n",short_close_results)

    for entry in short_close_results:
        key = (entry.warehouse, entry.batch_no)
        short_close_map[key] = flt(entry.total_short_close or 0)

    # Calculate final reserved quantities
    for row in reserve_results:
        key = (row.warehouse, row.batch_no)
        print("\n\nkey\n\n",key)
        total_reserve = flt(row.total_reserve or 0)
        print("\n\ntotal_reserve\n\n",total_reserve)
        total_delivered = actual_delivered_map.get(key, 0)
        print("\n\ntotal_delivered\n\n",total_delivered)
        total_short_close = short_close_map.get(key, 0)
        print("\n\ntotal_short_close\n\n",total_short_close)
        
        adjusted_reserve = total_reserve - total_delivered - total_short_close
        
        if adjusted_reserve > 0:
            reserved_map[key] = adjusted_reserve

    return reserved_map


def parse_batchwise_data(batchwise_data):
    data = []
    for key in batchwise_data:
        d = batchwise_data[key]
        if flt(d.balance_qty) == 0:
            continue
        data.append(d)
    return data


def get_batchwise_data_from_stock_ledger(filters):
    batchwise_data = frappe._dict()
    table = frappe.qb.DocType("Stock Ledger Entry")
    batch = frappe.qb.DocType("Batch")
    item = frappe.qb.DocType("Item")

    query = (
        frappe.qb.from_(table)
        .inner_join(batch).on(table.batch_no == batch.name)
        .inner_join(item).on(table.item_code == item.name)
        .select(
            table.item_code,
            table.warehouse,
            table.batch_no,
            item.stock_uom,
            Sum(table.actual_qty).as_("balance_qty"),
        )
        .where(table.is_cancelled == 0)
        .groupby(table.item_code, table.warehouse, table.batch_no, item.stock_uom)
    )

    if filters.get("item_codes"):
        query = query.where(table.item_code.isin(filters.item_codes))

    for d in query.run(as_dict=True):
        key = (d.item_code, d.warehouse, d.batch_no)
        batchwise_data.setdefault(key, d)

    return batchwise_data


def get_batchwise_data_from_serial_batch_bundle(batchwise_data, filters):
    table = frappe.qb.DocType("Stock Ledger Entry")
    ch_table = frappe.qb.DocType("Serial and Batch Entry")
    batch = frappe.qb.DocType("Batch")
    item = frappe.qb.DocType("Item")

    query = (
        frappe.qb.from_(table)
        .inner_join(ch_table).on(table.serial_and_batch_bundle == ch_table.parent)
        .inner_join(batch).on(ch_table.batch_no == batch.name)
        .inner_join(item).on(table.item_code == item.name)
        .select(
            table.item_code,
            ch_table.warehouse,
            ch_table.batch_no,
            item.stock_uom,
            Sum(ch_table.qty).as_("balance_qty"),
        )
        .where((table.is_cancelled == 0) & (table.docstatus == 1))
        .groupby(table.item_code, ch_table.warehouse, ch_table.batch_no, item.stock_uom)
    )

    if filters.get("item_codes"):
        query = query.where(table.item_code.isin(filters.item_codes))

    for d in query.run(as_dict=True):
        key = (d.item_code, d.warehouse, d.batch_no)
        if key in batchwise_data:
            batchwise_data[key].balance_qty += flt(d.balance_qty)
        else:
            batchwise_data.setdefault(key, d)

    return batchwise_data




@frappe.whitelist()
def get_selected_plans(custom_plan_items):
    # Ensure input is a list
    if isinstance(custom_plan_items, str):
        custom_plan_items = custom_plan_items.strip()
        if not custom_plan_items:
            return []
        try:
            custom_plan_items = json.loads(custom_plan_items)
        except json.JSONDecodeError:
            frappe.throw("Invalid format for custom_plan_items. Must be a list of Plan Item names.")

    if not isinstance(custom_plan_items, list) or not custom_plan_items:
        return []

    # Fetch Plans where plan_items field contains any of the given Plan Items
    plans = frappe.get_all(
        "Plans",
        filters={
            "plan_items": ["in", custom_plan_items],
            "docstatus": 1
        },
        fields=["*"]
    )
    return plans






