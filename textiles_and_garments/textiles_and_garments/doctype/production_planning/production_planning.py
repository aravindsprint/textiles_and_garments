# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from collections import defaultdict



class ProductionPlanning(Document):
    pass

# @frappe.whitelist()
# def get_need_to_allocate_qty(docname):
#     if not docname:
#         return 0  # Return 0 if no docname is provided

#     indent_item_allocation_doc = frappe.get_doc("Indent Item Allocation", docname)
#     production_planning_doc = frappe.get_doc("Production Planning", indent_item_allocation_doc.indent_no)

#     from_item_code = indent_item_allocation_doc.from_item_code
#     print("\n\nfrom_item_code\n",from_item_code)
#     need_to_allocate_qty = 0
#     total_allocated_qty = 0
#     found = False  # Flag to check if an item is found

#     production_planning_items_list = frappe.get_all(
#         "Production Planning Items",
#         filters={
#             "parent": ["=", production_planning_doc],
#             "raw_material_item": ["=", from_item_code]
#         },
#         fields=["*"]
#     )
#     print("\n\n\nproduction_planning_items_list\n\n\n",production_planning_items_list)


#     # Loop through all child table rows
#     for item in production_planning_doc.production_planning_items:
#         print("\n\nProduction     Planning Item Row:", item.as_dict())  # Debugging
#         print("\n\nitem.   raw_material_item\n",item.raw_material_item)

#         if item.raw_material_item == from_item_code:
#             total_allocated_qty += item.rm_allocated_qty
#             need_to_allocate_qty = production_planning_doc.indent_qty - total_allocated_qty
#             found = True  # Mark as found
#             break  # Exit loop as we found the item

#     # If no matching item was found, assign `indent_qty`
#     if not found:
#         need_to_allocate_qty = production_planning_doc.indent_qty

#     return need_to_allocate_qty


@frappe.whitelist()
def get_need_to_allocate_qty(docname):
    if not docname:
        return 0  # Return 0 if no docname is provided

    indent_item_allocation_doc = frappe.get_doc("Indent Item Allocation", docname)
    production_planning_doc = frappe.get_doc("Production Planning", indent_item_allocation_doc.indent_no)

    from_item_code = indent_item_allocation_doc.from_item_code
    indent_item = indent_item_allocation_doc.allocate_indent_item
    print("\n\nfrom_item_code\n", from_item_code)

    total_allocated_qty = 0
    found = False  # Flag to check if an item is found

    # Fetch the production planning items list
    production_planning_items_list = frappe.get_all(
        "Production Planning Items",
        filters={
            "parent": production_planning_doc.name,
            "raw_material_item": from_item_code
        },
        fields=["*"],
        order_by="creation ASC"  # Ensure chronological order
    )

    print("\n\n\nproduction_planning_items_list\n\n\n", production_planning_items_list)

    # Get the last row if the list is not empty
    last_row = production_planning_items_list[-1] if production_planning_items_list else None

    if last_row:
        print("\n\nLast Row:\n", last_row)

        total_allocated_qty = sum(item["rm_allocated_qty"] for item in production_planning_items_list)
        need_to_allocate_qty = production_planning_doc.indent_qty - total_allocated_qty
        print("\n\nneed_to_allocate_qty\n\n", need_to_allocate_qty)

        need_to_allocate_qty = last_row.to_allocate_qty
        found = True
        return need_to_allocate_qty

    # If no matching item was found, assign `indent_qty`
    if not found and indent_item == "Yes":
        need_to_allocate_qty = production_planning_doc.indent_qty
        return need_to_allocate_qty
    else:
        print("\n\nfound\n\n",found)
        production_planning_items_list_for_finished_material_item = frappe.get_all(
            "Production Planning Items",
            filters={
                "parent": production_planning_doc.name,
                "finished_material_item": from_item_code
            },
            fields=["*"],
            order_by="creation ASC"  # Ensure chronological order
        )

        total_rm_allocated_qty = sum(item["rm_allocated_qty"] for item in production_planning_items_list_for_finished_material_item)

        print("\n\nTotal RM Allocated Qty:", total_rm_allocated_qty)
        need_to_allocate_qty = total_rm_allocated_qty
        return need_to_allocate_qty

    if not production_planning_items_list:
        print("not production_planning_items_list")
        production_planning_items_list_for_finished_material_item = frappe.get_all(
            "Production Planning Items",
            filters={
                "parent": production_planning_doc.name,
                "finished_material_item": from_item_code
            },
            fields=["*"],
            order_by="creation ASC"  # Ensure chronological order
        )

        total_rm_allocated_qty = sum(item["rm_allocated_qty"] for item in production_planning_items_list_for_finished_material_item)

        print("\n\nTotal RM Allocated Qty:", total_rm_allocated_qty)
        need_to_allocate_qty = total_rm_allocated_qty
        return need_to_allocate_qty

           
            

    # return need_to_allocate_qty









@frappe.whitelist()
def set_production_plan(docname):
    """Updates the production planning items based on Indent Item Allocation."""
    if not docname:
        return "Invalid document name"

    indent_item_allocation_doc = frappe.get_doc("Indent Item Allocation", docname)
    production_planning_doc = frappe.get_doc("Production Planning", indent_item_allocation_doc.indent_no)

    

    from_item_code = indent_item_allocation_doc.from_item_code
    print("\n\nfrom_item_code\n\n",from_item_code)

    to_item_code_from_doc_save = indent_item_allocation_doc.to_item_code
    print("\n\nto_item_code_from_doc_save\n\n",to_item_code_from_doc_save)

    rm_allocated_qty_from_doc_save = indent_item_allocation_doc.rm_allocated_qty

    print("\n\nrm_allocated_qty_from_doc_save\n\n",rm_allocated_qty_from_doc_save)

    # Calculate total rm_allocated_qty for matching raw_material_item
    total_allocated_qty = sum(
        item.rm_allocated_qty for item in production_planning_doc.production_planning_items
        if item.raw_material_item == from_item_code
    )

    if indent_item_allocation_doc.allocate_indent_item == "No":
        print("indent_item_allocation_doc.allocate_indent_item as No")
        total_allocated_qty = sum(
            item.rm_allocated_qty for item in production_planning_doc.production_planning_items
            if item.finished_material_item == from_item_code
        )
        print("\n\ntotal_allocated_qty\n\n",total_allocated_qty)
        already_allocated_qty = sum(
            item.rm_allocated_qty for item in production_planning_doc.production_planning_items
            if item.raw_material_item == from_item_code
        )
        print("\n\nalready_allocated_qty\n\n",already_allocated_qty)
        to_allocate_qty = total_allocated_qty - already_allocated_qty - rm_allocated_qty_from_doc_save
        # Append new row to production_planning_items table
        production_planning_doc.append("production_planning_items", {
            "raw_material_item": from_item_code,
            "finished_material_item": indent_item_allocation_doc.to_item_code,
            "rm_allocated_qty": indent_item_allocation_doc.rm_allocated_qty,
            "to_allocate_qty": to_allocate_qty,
            "operation": indent_item_allocation_doc.operation,
            "indent_item_allocation": indent_item_allocation_doc.name
        })

        # Save and commit changes
        production_planning_doc.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.msgprint(f"Updated Production Plan for {docname}.")

        return "Production Plan Updated Successfully"

    if indent_item_allocation_doc.allocate_indent_item == "Yes":
        print("indent_item_allocation_doc.allocate_indent_item as Yes")
        # If no matching rows found, use default calculation
        if total_allocated_qty == 0:
            to_allocate_qty = indent_item_allocation_doc.indent_qty - rm_allocated_qty_from_doc_save
        else:
            to_allocate_qty = indent_item_allocation_doc.indent_qty - total_allocated_qty - rm_allocated_qty_from_doc_save

        # Append new row to production_planning_items table
        production_planning_doc.append("production_planning_items", {
            "raw_material_item": from_item_code,
            "finished_material_item": indent_item_allocation_doc.to_item_code,
            "rm_allocated_qty": indent_item_allocation_doc.rm_allocated_qty,
            "to_allocate_qty": to_allocate_qty,
            "operation": indent_item_allocation_doc.operation,
            "indent_item_allocation": indent_item_allocation_doc.name
        })

        # Save and commit changes
        production_planning_doc.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.msgprint(f"Updated Production Plan for {docname}.")

        return "Production Plan Updated Successfully"



# @frappe.whitelist()
# def set_production_plan_item_summary(docname):
#     print("\n\n\nset_production_plan_item_summary\n\n\n", docname)

#     if not docname:
#         return "Invalid document name"

#     production_planning_doc = frappe.get_doc("Production Planning", docname)
#     production_planning_items_list_for_finished_material_item = frappe.get_all(
#             "Production Planning Items",
#             filters={
#                 "parent": docname,
#             },
#             fields=["*"],
#             order_by="creation ASC"  # Ensure chronological order
#         )

#     print("\n\nproduction_planning_items_list_for_finished_material_item\n\n", production_planning_items_list_for_finished_material_item)
#     # Summing up rm_allocated_qty by finished_material_item
#     summary = defaultdict(float)
#     for item in production_planning_items_list_for_finished_material_item:
#         summary[item["finished_material_item"]] += item["rm_allocated_qty"]

#     # Sorting order for finished_material_item
#     def sorting_key(item):
#         if item.startswith("GKF"):
#             return (1, item)
#         elif item.startswith("HKF"):
#             return (2, item)
#         elif item.startswith("PFKF"):
#             return (3, item)
#         elif item.startswith("DKF"):
#             return (4, item)
#         elif item.startswith("WKF"):
#             return (5, item)        
#         elif item.startswith("SKF"):
#             return (6, item)
#         elif item.startswith("PKF"):
#             return (7, item)    
#         return (8, item)  # Default for any other prefixes

#     # Convert summary to a sorted list of dicts
#     sorted_summary_list = sorted(
#         [{"finished_material_item": k, "rm_allocated_qty": v} for k, v in summary.items()],
#         key=lambda x: sorting_key(x["finished_material_item"])
#     )    

#     # Convert summary to list of dicts
#     # summary_list = [{"finished_material_item": k, "total_rm_allocated_qty": v} for k, v in summary.items()]

#     print("\n\nProduction Plan Item Summary\n\n", sorted_summary_list)

#     # return summary_list
#     # Clear existing summary items before inserting new ones
#     production_planning_doc.set("production_planning_items_summary", [])

#     # Insert summarized data into the child table "Production Planning Items Summary"
#     for summary_item in sorted_summary_list:
#         production_planning_doc.append("production_planning_items_summary", summary_item)

#     # Save the updated document
#     production_planning_doc.save()
#     frappe.db.commit()

#     print("\n\nProduction Plan Item Summary inserted successfully\n\n")

#     return "Production Planning Items Summary updated successfully!" 


from collections import defaultdict
import frappe

# @frappe.whitelist()
# def set_production_plan_item_summary(docname):
#     print("\n\n\nset_production_plan_item_summary\n\n\n", docname)

#     if not docname:
#         return "Invalid document name"

#     production_planning_doc = frappe.get_doc("Production Planning", docname)
#     production_planning_items_list_for_finished_material_item = frappe.get_all(
#         "Production Planning Items",
#         filters={"parent": docname},
#         fields=["finished_material_item", "rm_allocated_qty", "to_allocate_qty"],
#         order_by="creation ASC"  # Ensure chronological order
#     )

#     production_planning_items_list_for_raw_material_item = frappe.get_all(
#         "Production Planning Items",
#         filters={"parent": docname},
#         fields=["raw_material_item", "rm_allocated_qty", "to_allocate_qty"],
#         order_by="creation ASC"  # Ensure chronological order
#     )

#     print("\n\nproduction_planning_items_list_for_finished_material_item\n\n", 
#           production_planning_items_list_for_finished_material_item)

#     print("\n\nproduction_planning_items_list_for_raw_material_item\n\n", 
#           production_planning_items_list_for_raw_material_item)

#     # Summing up rm_allocated_qty by finished_material_item and tracking the last row's to_allocate_qty
#     summary = defaultdict(lambda: {"rm_allocated_qty": 0, "to_allocate": 0})

#     for item in production_planning_items_list_for_finished_material_item:
#         finished_material_item = item["finished_material_item"]
#         summary[finished_material_item]["rm_allocated_qty"] += item["rm_allocated_qty"]
#         summary[finished_material_item]["to_allocate"] = item["to_allocate_qty"]  # Always updates to last row value

#     # Sorting order for finished_material_item
#     def sorting_key(item):
#         if item.startswith("GKF"):
#             return (1, item)
#         elif item.startswith("HKF"):
#             return (2, item)
#         elif item.startswith("PFKF"):
#             return (3, item)
#         elif item.startswith("DKF"):
#             return (4, item)
#         elif item.startswith("WKF"):
#             return (5, item)
#         elif item.startswith("SKF"):
#             return (6, item)
#         elif item.startswith("PKF"):
#             return (7, item)
#         return (8, item)  # Default for any other prefixes

#     # Convert summary to a sorted list of dicts
#     sorted_summary_list = sorted(
#         [
#             {
#                 "finished_material_item": k,
#                 "rm_allocated_qty": v["rm_allocated_qty"],
#                 "to_allocate_qty": v["to_allocate"]
#             } 
#             for k, v in summary.items()
#         ],
#         key=lambda x: sorting_key(x["finished_material_item"])
#     )

#     print("\n\nProduction Plan Item Summary\n\n", sorted_summary_list)

#     # Clear existing summary items before inserting new ones
#     production_planning_doc.set("production_planning_items_summary", [])

#     # Insert summarized data into the child table "Production Planning Items Summary"
#     for summary_item in sorted_summary_list:
#         production_planning_doc.append("production_planning_items_summary", summary_item)

#     # Save the updated document
#     production_planning_doc.save()
#     frappe.db.commit()

#     print("\n\nProduction Plan Item Summary inserted successfully\n\n")

#     return "Production Planning Items Summary updated successfully!"


from collections import defaultdict
import frappe

# @frappe.whitelist()
# def set_production_plan_item_summary(docname):
#     print("\n\n\nset_production_plan_item_summary\n\n\n", docname)

#     if not docname:
#         return "Invalid document name"

#     production_planning_doc = frappe.get_doc("Production Planning", docname)

#     # Fetch items related to finished_material_item
#     production_planning_items_list_for_finished_material_item = frappe.get_all(
#         "Production Planning Items",
#         filters={"parent": docname},
#         fields=["finished_material_item", "rm_allocated_qty", "to_allocate_qty"],
#         order_by="creation ASC"
#     )

#     # Fetch items related to raw_material_item
#     production_planning_items_list_for_raw_material_item = frappe.get_all(
#         "Production Planning Items",
#         filters={"parent": docname},
#         fields=["raw_material_item", "rm_allocated_qty", "to_allocate_qty"],
#         order_by="creation ASC"
#     )

#     print("\n\nproduction_planning_items_list_for_finished_material_item\n\n", 
#           production_planning_items_list_for_finished_material_item)

#     print("\n\nproduction_planning_items_list_for_raw_material_item\n\n", 
#           production_planning_items_list_for_raw_material_item)

#     # Summing up rm_allocated_qty by finished_material_item and tracking the last row's to_allocate_qty
#     summary = defaultdict(lambda: {"rm_allocated_qty": 0, "to_allocate": 0, "to_allocate_qty": 0})

#     for item in production_planning_items_list_for_finished_material_item:
#         finished_material_item = item["finished_material_item"]
#         summary[finished_material_item]["rm_allocated_qty"] += item["rm_allocated_qty"]
#         summary[finished_material_item]["to_allocate"] = item["to_allocate_qty"]  # Always updates to last row value

#     # Tracking the last row's to_allocate_qty for each raw_material_item
#     last_to_allocate_qty = {}

#     for item in production_planning_items_list_for_raw_material_item:
#         raw_material_item = item["raw_material_item"]
#         last_to_allocate_qty[raw_material_item] = item["to_allocate_qty"]  # Always stores the last row value

#     # Assigning last row's to_allocate_qty for each finished_material_item
#     for finished_material_item in summary.keys():
#         summary[finished_material_item]["to_allocate_qty"] = last_to_allocate_qty.get(finished_material_item, 0)

#     # Sorting order for finished_material_item
#     def sorting_key(item):
#         if item.startswith("GKF"):
#             return (1, item)
#         elif item.startswith("HKF"):
#             return (2, item)
#         elif item.startswith("PFKF"):
#             return (3, item)
#         elif item.startswith("DKF"):
#             return (4, item)
#         elif item.startswith("WKF"):
#             return (5, item)
#         elif item.startswith("SKF"):
#             return (6, item)
#         elif item.startswith("PKF"):
#             return (7, item)
#         return (8, item)  # Default for any other prefixes

#     # Convert summary to a sorted list of dicts
#     sorted_summary_list = sorted(
#         [
#             {
#                 "finished_material_item": k,
#                 "rm_allocated_qty": v["rm_allocated_qty"],
#                 "to_allocate_qty": v["to_allocate"],  # From finished_material_item's last row
#                 "to_allocate_qty": v["to_allocate_qty"]  # From raw_material_item's last row
#             } 
#             for k, v in summary.items()
#         ],
#         key=lambda x: sorting_key(x["finished_material_item"])
#     )

#     print("\n\nProduction Plan Item Summary\n\n", sorted_summary_list)

#     # Clear existing summary items before inserting new ones
#     production_planning_doc.set("production_planning_items_summary", [])

#     # Insert summarized data into the child table "Production Planning Items Summary"
#     for summary_item in sorted_summary_list:
#         production_planning_doc.append("production_planning_items_summary", summary_item)

#     # Save the updated document
#     production_planning_doc.save()
#     frappe.db.commit()

#     print("\n\nProduction Plan Item Summary inserted successfully\n\n")

#     return "Production Planning Items Summary updated successfully!"

@frappe.whitelist()
def set_production_plan_item_summary(docname):
    print("\n\n\nset_production_plan_item_summary\n\n\n", docname)

    if not docname:
        return "Invalid document name"

    production_planning_doc = frappe.get_doc("Production Planning", docname)

    # Fetch items related to finished_material_item
    production_planning_items_list_for_finished_material_item = frappe.get_all(
        "Production Planning Items",
        filters={"parent": docname},
        fields=["finished_material_item", "rm_allocated_qty", "to_allocate_qty"],
        order_by="creation ASC"
    )

    # Fetch items related to raw_material_item
    production_planning_items_list_for_raw_material_item = frappe.get_all(
        "Production Planning Items",
        filters={"parent": docname},
        fields=["raw_material_item", "rm_allocated_qty", "to_allocate_qty"],
        order_by="creation ASC"
    )

    print("\n\nproduction_planning_items_list_for_finished_material_item\n\n", 
          production_planning_items_list_for_finished_material_item)

    print("\n\nproduction_planning_items_list_for_raw_material_item\n\n", 
          production_planning_items_list_for_raw_material_item)

    # Summing up rm_allocated_qty by finished_material_item and tracking the last row's to_allocate_qty
    summary = defaultdict(lambda: {"rm_allocated_qty": 0, "to_allocate": 0, "to_allocate_qty": 0})

    for item in production_planning_items_list_for_finished_material_item:
        finished_material_item = item["finished_material_item"]
        summary[finished_material_item]["rm_allocated_qty"] += item["rm_allocated_qty"]
        summary[finished_material_item]["to_allocate"] = item["to_allocate_qty"]  # Always updates to last row value

    # Tracking the last row's to_allocate_qty for each raw_material_item
    last_to_allocate_qty = {}

    for item in production_planning_items_list_for_raw_material_item:
        raw_material_item = item["raw_material_item"]
        last_to_allocate_qty[raw_material_item] = item["to_allocate_qty"]  # Always stores the last row value

    # Assigning last row's to_allocate_qty for each finished_material_item
    for finished_material_item, values in summary.items():
        if finished_material_item in last_to_allocate_qty:
            summary[finished_material_item]["to_allocate_qty"] = last_to_allocate_qty[finished_material_item]
        else:
            summary[finished_material_item]["to_allocate_qty"] = values["rm_allocated_qty"]  # Use rm_allocated_qty if no match

    # Sorting order for finished_material_item
    def sorting_key(item):
        if item.startswith("GKF"):
            return (1, item)
        elif item.startswith("HKF"):
            return (2, item)
        elif item.startswith("PFKF"):
            return (3, item)
        elif item.startswith("DKF"):
            return (4, item)
        elif item.startswith("WKF"):
            return (5, item)
        elif item.startswith("SKF"):
            return (6, item)
        elif item.startswith("PKF"):
            return (7, item)
        return (8, item)  # Default for any other prefixes

    # Convert summary to a sorted list of dicts
    sorted_summary_list = sorted(
        [
            {
                "finished_material_item": k,
                "rm_allocated_qty": v["rm_allocated_qty"],
                "to_allocate_qty": v["to_allocate"],  # From finished_material_item's last row
                "to_allocate_qty": v["to_allocate_qty"]  # From raw_material_item's last row OR rm_allocated_qty if no match
            } 
            for k, v in summary.items()
        ],
        key=lambda x: sorting_key(x["finished_material_item"])
    )

    print("\n\nProduction Plan Item Summary\n\n", sorted_summary_list)

    # Clear existing summary items before inserting new ones
    production_planning_doc.set("production_planning_items_summary", [])

    # Insert summarized data into the child table "Production Planning Items Summary"
    for summary_item in sorted_summary_list:
        production_planning_doc.append("production_planning_items_summary", summary_item)

    # Save the updated document
    production_planning_doc.save()
    frappe.db.commit()

    print("\n\nProduction Plan Item Summary inserted successfully\n\n")

    return "Production Planning Items Summary updated successfully!"



@frappe.whitelist()
def set_production_plan_process_summary(docname):
    print("\n\n\nset_production_plan_process_summary\n\n\n", docname)

    if not docname:
        return "Invalid document name"

    # Fetch the Production Planning document
    production_planning_doc = frappe.get_doc("Production Planning", docname)

    # Fetch the items from "Production Planning Items"
    production_planning_items_summary_list = frappe.get_all(
        "Production Planning Items Summary",
        filters={"parent": docname},
        fields=["operation", "rm_allocated_qty", "to_allocate_qty"],
        order_by="creation ASC"
    )

    # Corrected defaultdict to store dictionaries instead of floats
    summary = defaultdict(lambda: {"completed_qty": 0, "balance_qty": 0})

    for item in production_planning_items_summary_list:
        operation = item["operation"] or "Not Specified"  # Handle None values
        summary[operation]["completed_qty"] += item["rm_allocated_qty"]  # ✅ Specify key
        summary[operation]["balance_qty"] += item["rm_allocated_qty"] - item["to_allocate_qty"]  # ✅ Specify key

    # Convert summary to a list of dicts with balance_qty adjusted if greater than 0
    summary_list = [
        {
            "operation": op,
            "completed_qty": data["completed_qty"],
            "balance_qty": data["completed_qty"] - data["balance_qty"]
            if data["balance_qty"] > 0 else data["balance_qty"]
        }
        for op, data in summary.items()
    ]

    print("\n\nsummary_list (before sorting)\n\n", summary_list)   

    # Fetch production workflow with priority
    production_planning_process_workflow_list = frappe.get_all(
        "Production Planning Process Workflow",
        filters={"parent": docname},
        fields=["operation", "priority"],
        order_by="priority ASC"
    )
    
    print("\n\nProduction Planning Process Workflow\n\n", production_planning_process_workflow_list)

    # Create a priority mapping
    priority_mapping = {item["operation"]: item["priority"] for item in production_planning_process_workflow_list}

    # Sort summary_list based on priority, defaulting to high value (e.g., 999) for missing operations
    summary_list.sort(key=lambda x: priority_mapping.get(x["operation"], 999))

    print("\n\nsummary_list (after sorting)\n\n", summary_list)

    # Clear existing summary items before inserting new ones
    production_planning_doc.set("production_planning_process_summary", [])

    # Insert summarized data into the child table
    for summary_item in summary_list:
        production_planning_doc.append("production_planning_process_summary", summary_item)

    # Save the updated document
    production_planning_doc.save()
    frappe.db.commit()

    print("\n\nProduction Plan Process Summary inserted successfully\n\n")

    return "Production Planning Process Summary updated successfully!" 





# @frappe.whitelist()
# def set_production_plan_process_summary_old(docname):
#     print("\n\n\nset_production_plan_process_summary\n\n\n", docname)

#     if not docname:
#         return "Invalid document name"

#     # Fetch the Production Planning document
#     production_planning_doc = frappe.get_doc("Production Planning", docname)

#     # Fetch the items from "Production Planning Items"
#     production_planning_items_list = frappe.get_all(
#         "Production Planning Items",
#         filters={"parent": docname},
#         fields=["operation", "rm_allocated_qty"],
#         order_by="creation ASC"
#     )

#     # Corrected defaultdict to store dictionaries instead of floats
#     summary = defaultdict(lambda: {"completed_qty": 0, "total_rm_allocated_qty": 0})

#     for item in production_planning_items_list:
#         operation = item["operation"] or "Not Specified"  # Handle None values
#         summary[operation]["completed_qty"] += item["rm_allocated_qty"]  # ✅ Specify key
#         summary[operation]["total_rm_allocated_qty"] += item["rm_allocated_qty"]  # ✅ Specify key

#     # Convert summary to a list of dicts with balance_qty for each operation
#     summary_list = [
#         {
#             "operation": op,
#             "completed_qty": data["completed_qty"],
#             "balance_qty": (production_planning_doc.indent_qty or 0) - data["total_rm_allocated_qty"]
#         }
#         for op, data in summary.items()
#     ]

#     print("\n\nsummary_list (before sorting)\n\n", summary_list)

#     # Fetch production workflow with priority
#     production_planning_process_workflow_list = frappe.get_all(
#         "Production Planning Process Workflow",
#         filters={"parent": docname},
#         fields=["operation", "priority"],
#         order_by="priority ASC"
#     )
    
#     print("\n\nProduction Planning Process Workflow\n\n", production_planning_process_workflow_list)

#     # Create a priority mapping
#     priority_mapping = {item["operation"]: item["priority"] for item in production_planning_process_workflow_list}

#     # Sort summary_list based on priority, defaulting to high value (e.g., 999) for missing operations
#     summary_list.sort(key=lambda x: priority_mapping.get(x["operation"], 999))

#     print("\n\nsummary_list (after sorting)\n\n", summary_list)

#     # Clear existing summary items before inserting new ones
#     production_planning_doc.set("production_planning_process_summary", [])

#     # Insert summarized data into the child table
#     for summary_item in summary_list:
#         production_planning_doc.append("production_planning_process_summary", summary_item)

#     # Save the updated document
#     production_planning_doc.save()
#     frappe.db.commit()

#     print("\n\nProduction Plan Process Summary inserted successfully\n\n")

#     return "Production Planning Process Summary updated successfully!"





