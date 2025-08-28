# import frappe
# from frappe import _

# def on_submit_create_reservation(doc, method):
#     doctype_map = {
#         "Purchase Receipt": "Purchase Receipt",
#         "Stock Entry": "Stock Entry",
#         "Subcontracting Receipt": "Subcontracting Receipt"
#     }

#     for item in doc.items:
#         if item.get("custom_plans"):
#             create_production_stock_reservation_from_plan(
#                 plan_name=item.custom_plans,
#                 item_code=item.item_code,
#                 actual_qty=item.qty,
#                 reference_doctype=doctype_map.get(doc.doctype),
#                 reference_docname=doc.name,
#                 warehouse=item.warehouse,  # fallback for both Stock Entry and Purchase Receipt
#                 batch_no=item.batch_no
#             )

# def create_production_stock_reservation_from_plan(plan_name, item_code, actual_qty, reference_doctype, reference_docname, warehouse, batch_no):
#     plan_doc = frappe.get_doc("Plans", plan_name)
#     print("\n\nCreating production stock reservation for item:", item_code)

#     for row in plan_doc.get("reserved_wip_plans") or []:
#         if row.reserve_qty > 0:
#             if not frappe.db.exists("Production Stock Reservation", {
#                 "plan": plan_name,
#                 "item_code": item_code,
#                 "reference_doctype": reference_doctype,
#                 "reference_name": reference_docname
#             }):
#                 reservation = frappe.new_doc("Production Stock Reservation")
#                 reservation.plan = plan_name
#                 reservation.plans_no = row.plan  # or plan_doc.name if needed
#                 reservation.plan_against = "Stock"
#                 reservation.item_code = item_code
#                 reservation.stock_uom = frappe.db.get_value("Item", item_code, "stock_uom")
#                 reservation.qty = row.reserve_qty
#                 reservation.reference_doctype = reference_doctype
#                 reservation.reference_name = reference_docname
#                 reservation.reserve_type = "WIP"
#                 reservation.reservation_based_on = "Serial and Batch"
#                 reservation.posting_date = frappe.utils.today()

#                 # Add child row to sb_entries
#                 reservation.append("sb_entries", {
#                     "batch_no": batch_no,
#                     "qty": row.reserve_qty,
#                     "warehouse": warehouse,
#                     # "voucher_qty": row.reserve_qty,
#                     # "voucher_type": reference_doctype,
#                     # "is_outward": 0
#                 })

#                 reservation.insert()
#                 reservation.submit()


# import frappe
# from frappe import _

# def on_submit_create_reservation(doc, method):
#     doctype_map = {
#         "Purchase Receipt": "Purchase Receipt",
#         "Stock Entry": "Stock Entry",
#         "Subcontracting Receipt": "Subcontracting Receipt"
#     }

#     for item in doc.items:
#         if item.get("custom_plans"):
#             create_production_stock_reservation_from_plan(
#                 plan_name=item.custom_plans,
#                 item_code=item.item_code,
#                 actual_qty=item.qty,
#                 reference_doctype=doctype_map.get(doc.doctype),
#                 reference_docname=doc.name,
#                 warehouse=item.warehouse or item.t_warehouse,
#                 batch_no=item.batch_no,
#                 parent_doc=doc  # pass full parent doc
#             )

# def create_production_stock_reservation_from_plan(plan_name, item_code, actual_qty, reference_doctype, reference_docname, warehouse, batch_no, parent_doc):
#     plan_doc = frappe.get_doc("Plans", plan_name)
#     print("\n\nCreating production stock reservation for item:", item_code)

#     for row in plan_doc.get("reserved_wip_plans") or []:
#         if row.reserve_qty > 0:
#             if not frappe.db.exists("Production Stock Reservation", {
#                 "plan": plan_name,
#                 "item_code": item_code,
#                 "reference_doctype": reference_doctype,
#                 "reference_name": reference_docname
#             }):
#                 reservation = frappe.new_doc("Production Stock Reservation")
#                 reservation.plan = plan_name
#                 reservation.plans_no = row.plan  # or plan_doc.name
#                 reservation.plan_against = "Stock"
#                 reservation.item_code = item_code
#                 reservation.stock_uom = frappe.db.get_value("Item", item_code, "stock_uom")
#                 reservation.qty = row.reserve_qty
#                 reservation.reference_doctype = reference_doctype
#                 reservation.reference_name = reference_docname
#                 reservation.reserve_type = "WIP"
#                 reservation.reservation_based_on = "Serial and Batch"
#                 reservation.posting_date = frappe.utils.today()

#                 reservation.append("sb_entries", {
#                     "batch_no": batch_no,
#                     "qty": row.reserve_qty,
#                     "warehouse": warehouse,
#                 })

#                 reservation.insert()

#                 # ✅ Only submit under allowed conditions
#                 should_submit = (
#                     reference_doctype == "Purchase Receipt"
#                     or reference_doctype == "Subcontracting Receipt"
#                     or (reference_doctype == "Stock Entry" and parent_doc.get("stock_entry_type") == "Send to Subcontractor")
#                 )

#                 if should_submit:
#                     reservation.submit()


# import frappe
# from frappe import _

# def on_submit_create_reservation(doc, method):
#     doctype_map = {
#         "Purchase Receipt": "Purchase Receipt",
#         "Stock Entry": "Stock Entry",
#         "Subcontracting Receipt": "Subcontracting Receipt"
#     }

#     for item in doc.items:
#         if item.get("custom_plans"):
#             # Determine correct warehouse based on doctype
#             if doc.doctype == "Purchase Receipt" or doc.doctype == "Subcontracting Receipt":
#                 warehouse = item.warehouse
#             elif doc.doctype == "Stock Entry":
#                 # Assuming 'Send to Subcontractor' means we care about source warehouse
#                 warehouse = item.s_warehouse or item.t_warehouse
#             else:
#                 warehouse = None

#             create_production_stock_reservation_from_plan(
#                 plan_name=item.custom_plans,
#                 item_code=item.item_code,
#                 actual_qty=item.qty,
#                 reference_doctype=doctype_map.get(doc.doctype),
#                 reference_docname=doc.name,
#                 warehouse=warehouse,
#                 batch_no=item.batch_no,
#                 parent_doc=doc
#             )

# def create_production_stock_reservation_from_plan(plan_name, item_code, actual_qty, reference_doctype, reference_docname, warehouse, batch_no, parent_doc):
#     plan_doc = frappe.get_doc("Plans", plan_name)
#     print("\n\nCreating production stock reservation for item:", item_code)

#     for row in plan_doc.get("reserved_wip_plans") or []:
#         if row.reserve_qty > 0:
#             if not frappe.db.exists("Production Stock Reservation", {
#                 "plan": plan_name,
#                 "item_code": item_code,
#                 "reference_doctype": reference_doctype,
#                 "reference_name": reference_docname
#             }):
#                 reservation = frappe.new_doc("Production Stock Reservation")
#                 reservation.plan = plan_name
#                 reservation.plans_no = row.plan  # or plan_doc.name
#                 reservation.plan_against = "Stock"
#                 reservation.item_code = item_code
#                 reservation.stock_uom = frappe.db.get_value("Item", item_code, "stock_uom")
#                 reservation.qty = row.reserve_qty
#                 reservation.reference_doctype = reference_doctype
#                 reservation.reference_name = reference_docname
#                 reservation.reserve_type = "WIP"
#                 reservation.reservation_based_on = "Serial and Batch"
#                 reservation.posting_date = frappe.utils.today()

#                 reservation.append("sb_entries", {
#                     "batch_no": batch_no,
#                     "qty": row.reserve_qty,
#                     "warehouse": warehouse,
#                 })

#                 reservation.insert()

#                 # ✅ Submit only under correct conditions
#                 should_submit = (
#                     reference_doctype == "Purchase Receipt"
#                     or reference_doctype == "Subcontracting Receipt"
#                     or (reference_doctype == "Stock Entry" and parent_doc.get("stock_entry_type") == "Send to Subcontractor")
#                 )

#                 if should_submit:
#                     reservation.submit()

# import frappe
# from frappe import _

# def on_submit_create_reservation(doc, method):
#     doctype_map = {
#         "Purchase Receipt": "Purchase Receipt",
#         "Stock Entry": "Stock Entry",
#         "Subcontracting Receipt": "Subcontracting Receipt"
#     }

#     for item in doc.items:
#         if item.get("custom_plans"):
#             # Determine correct warehouse based on doctype
#             if doc.doctype in ["Purchase Receipt", "Subcontracting Receipt"]:
#                 warehouse = item.warehouse
#             elif doc.doctype == "Stock Entry":
#                 # For 'Manufacture', use 's_warehouse' or fallback to 't_warehouse'
#                 warehouse = item.s_warehouse or item.t_warehouse
#             else:
#                 warehouse = None

#             create_production_stock_reservation_from_plan(
#                 plan_name=item.custom_plans,
#                 item_code=item.item_code,
#                 actual_qty=item.qty,
#                 reference_doctype=doctype_map.get(doc.doctype),
#                 reference_docname=doc.name,
#                 warehouse=warehouse,
#                 batch_no=item.batch_no,
#                 parent_doc=doc
#             )

# def create_production_stock_reservation_from_plan(plan_name, item_code, actual_qty, reference_doctype, reference_docname, warehouse, batch_no, parent_doc):
#     plan_doc = frappe.get_doc("Plans", plan_name)
#     print("\n\nCreating production stock reservation for item:\n\n", item_code)

#     for row in plan_doc.get("reserved_wip_plans") or []:
#         if row.reserve_qty > 0:
#             if not frappe.db.exists("Production Stock Reservation", {
#                 "plan": plan_name,
#                 "item_code": item_code,
#                 "reference_doctype": reference_doctype,
#                 "reference_name": reference_docname
#             }):
#                 reservation = frappe.new_doc("Production Stock Reservation")
#                 reservation.plan = plan_name
#                 reservation.plans_no = row.plan  # or plan_doc.name
#                 reservation.plan_against = "Stock"
#                 reservation.item_code = item_code
#                 reservation.stock_uom = frappe.db.get_value("Item", item_code, "stock_uom")
#                 reservation.qty = row.reserve_qty
#                 reservation.reference_doctype = reference_doctype
#                 reservation.reference_name = reference_docname
#                 reservation.reserve_type = "WIP"
#                 reservation.reservation_based_on = "Serial and Batch"
#                 reservation.posting_date = frappe.utils.today()

#                 reservation.append("sb_entries", {
#                     "batch_no": batch_no,
#                     "qty": row.reserve_qty,
#                     "warehouse": warehouse,
#                 })

#                 # ✅ Submit only under specified conditions
#                 should_submit = (
#                     reference_doctype == "Purchase Receipt"
#                     or reference_doctype == "Subcontracting Receipt"
#                     or (reference_doctype == "Stock Entry" and parent_doc.get("stock_entry_type") == "Manufacture")
#                 )

#                 if should_submit:
#                     reservation.insert()
#                     reservation.submit()

#########################################################################



import frappe
from frappe import _
from frappe.model.document import Document
from collections import defaultdict
from frappe.utils import cint, flt


# def on_submit_create_reservation(doc, method):
#     doctype_map = {
#         "Purchase Receipt": "Purchase Receipt",
#         "Stock Entry": "Stock Entry",
#         "Subcontracting Receipt": "Subcontracting Receipt"
#     }

#     for item in doc.items:
#         if item.get("custom_plans"):
#             # Determine correct warehouse based on doctype
#             if doc.doctype in ["Purchase Receipt", "Subcontracting Receipt"]:
#                 warehouse = item.warehouse
#             elif doc.doctype == "Stock Entry":
#                 # For 'Manufacture', use 's_warehouse' or fallback to 't_warehouse'
#                 warehouse = item.s_warehouse or item.t_warehouse
#             else:
#                 warehouse = None

#             create_production_stock_reservation_from_plan(
#                 plan_name=item.custom_plans,
#                 item_code=item.item_code,
#                 actual_qty=item.qty,
#                 reference_doctype=doctype_map.get(doc.doctype),
#                 reference_docname=doc.name,
#                 warehouse=warehouse,
#                 batch_no=item.batch_no,
#                 parent_doc=doc
#             )

# def create_production_stock_reservation_from_plan(plan_name, item_code, actual_qty, reference_doctype, reference_docname, warehouse, batch_no, parent_doc):
#     plan_doc = frappe.get_doc("Plans", plan_name)
#     print("\n\nCreating production stock reservation for plan:\n\n", plan_doc)
    
#     print("\n\nCreating production stock reservation for item:\n\n", item_code)

#     for row in plan_doc.get("reserved_wip_plans") or []:
#         print("\n\nrow\n\n",row)
#         if row.reserve_qty > 0:
#             if not frappe.db.exists("Production Stock Reservation", {
#                 "plan": plan_name,
#                 "item_code": item_code,
#                 "reference_doctype": reference_doctype,
#                 "reference_name": reference_docname
#             }):
#                 reservation = frappe.new_doc("Production Stock Reservation")
#                 reservation.plan = plan_name
#                 reservation.plans_no = row.plan
#                 reservation.plan_against = "Stock"
#                 reservation.item_code = item_code
#                 reservation.stock_uom = frappe.db.get_value("Item", item_code, "stock_uom")
#                 reservation.qty = row.reserve_qty
#                 reservation.reference_doctype = reference_doctype
#                 reservation.reference_name = reference_docname
#                 reservation.reserve_type = "WIP"
#                 reservation.reservation_based_on = "Serial and Batch"
#                 reservation.posting_date = frappe.utils.today()

#                 reservation.append("sb_entries", {
#                     "batch_no": batch_no,
#                     "qty": row.reserve_qty,
#                     "warehouse": warehouse,
#                 })

#                 should_submit = (
#                     reference_doctype == "Purchase Receipt"
#                     or reference_doctype == "Subcontracting Receipt"
#                     or (reference_doctype == "Stock Entry" and parent_doc.get("stock_entry_type") == "Manufacture")
#                 )

#                 if should_submit:
#                     reservation.insert()
#                     reservation.submit()


def on_submit_create_reservation(doc, method):
    print("\n\non_submit_create_reservation in plan_stock_reservation\n\n")
    doctype_map = {
        "Purchase Receipt": "Purchase Receipt",
        "Stock Entry": "Stock Entry",
        "Subcontracting Receipt": "Subcontracting Receipt"
    }

    for item in doc.items:
        if item.get("custom_plans"):
            # Determine correct warehouse based on doctype
            if doc.doctype in ["Purchase Receipt", "Subcontracting Receipt"]:
                warehouse = item.warehouse
            elif doc.doctype == "Stock Entry":
                warehouse = item.s_warehouse or item.t_warehouse
            else:
                warehouse = None

            create_production_stock_reservation_from_plan(
                plan_name=item.custom_plans,
                item_code=item.item_code,
                actual_qty=item.qty,
                reference_doctype=doctype_map.get(doc.doctype),
                reference_docname=doc.name,
                warehouse=warehouse,
                batch_no=item.batch_no,
                parent_doc=doc,
                create_for_all=item.get("custom_create_psr_for_all_reserved_wip_plans"),
                specific_reserved_plan=item.get("custom_create_psr_for_reserved_wip_plan")
            )



from frappe.utils import cint, flt

def create_production_stock_reservation_from_plan(
    plan_name, item_code, actual_qty, reference_doctype, reference_docname,
    warehouse, batch_no, parent_doc, create_for_all=None, specific_reserved_plan=None
):
    plan_doc = frappe.get_doc("Plans", plan_name)
    
    # Convert actual_qty to float for calculations
    actual_qty = flt(actual_qty)
    
    # Debug prints (consider using frappe.logger() in production)
    print("\n\nCreating production stock reservation for plan:", plan_name)
    print("For item:", item_code)
    print("Actual quantity:", actual_qty)

    # Initialize variables with proper float conversion
    reserved_received_qty = flt(plan_doc.get("reserved_received_qty", 0))
    unreserved_received_qty = flt(plan_doc.get("unreserved_received_qty", 0))
    reserved_qty = flt(plan_doc.get("reserved_qty", 0))
    plan_qty = flt(plan_doc.get("plan_qty", 0))

    # Update received quantities based on reservation type
    if create_for_all is None and specific_reserved_plan is None:
        print("Updating unreserved received quantity")
        plan_doc.received_qty = actual_qty
        plan_doc.unreserved_received_qty = flt(plan_doc.get("unreserved_received_qty", 0)) + actual_qty
        plan_doc.unreserved_qty = plan_qty - plan_doc.unreserved_received_qty - plan_doc.reserved_qty
    else:
        print("Updating reserved received quantity")
        plan_doc.received_qty = actual_qty
        plan_doc.reserved_received_qty = flt(plan_doc.get("reserved_received_qty", 0)) + actual_qty
        plan_doc.unreserved_qty = plan_qty - plan_doc.unreserved_received_qty - plan_doc.reserved_qty

    # Save and commit changes
    plan_doc.save()
    frappe.db.commit()

    reserved_wip_plans = plan_doc.get("reserved_wip_plans") or []

    # ✅ Validation 1: If create_for_all is 1, sum all reserve_qty and compare
    if cint(create_for_all):
        total_reserved_qty = sum(flt(row.reserve_qty) for row in reserved_wip_plans if row.reserve_qty > 0)
        if flt(total_reserved_qty) > flt(actual_qty):
            frappe.throw(
                f"Total reserved qty ({total_reserved_qty}) for all plans exceeds received qty ({actual_qty}) for item '{item_code}'"
            )

    for row in reserved_wip_plans:
        if row.reserve_qty > 0:
            print("\n\ncreate_for_all\n", create_for_all)
            print("\n\nspecific_reserved_plan\n", specific_reserved_plan)
            print("\n\nCreating production stock reservation for item_code:\n\n", item_code)
            print("\n\nCreating production stock reservation for row.plan:\n\n", row.plan)

            print("\n\nCreating production stock reservation for reference_doctype:\n\n", reference_doctype)
            print("\n\nCreating production stock reservation for reference_docname:\n\n", reference_docname)

            # ✅ Validation 2: Skip rows not matching the specific plan if create_for_all is 0
            if not cint(create_for_all):
                if not specific_reserved_plan or row.plan != specific_reserved_plan:
                    continue

                # Validate individual reserve_qty against actual_qty
                if flt(row.reserve_qty) > flt(actual_qty):
                    print("reserve_qty")
                    frappe.throw(
                        f"Reserved qty ({row.reserve_qty}) for plan '{row.plan}' exceeds received qty ({actual_qty}) for item '{item_code}'"
                    )

            
            # psr_exist = frappe.db.exists("Production Stock Reservation", {
            #     "item_code": item_code,
            #     # "reference_doctype": reference_doctype,
            #     # "reference_name": reference_docname,
            #     "plans_no": row.plan,
            #     "docstatus": 1
            # })
            # print("\n\npsr_exist\n\n",psr_exist)
            # ✅ Check for existing reservation
            if not frappe.db.exists("Production Stock Reservation", {
                # "item_code": item_code,
                # "reference_doctype": reference_doctype,
                # "reference_name": reference_docname,
                "plans_no": row.plan,
                "docstatus": 1
            }):
                reservation = frappe.new_doc("Production Stock Reservation")
                reservation.plan = plan_name
                reservation.plans_no = row.plan
                reservation.plan_against = "Stock"
                reservation.item_code = item_code
                reservation.stock_uom = frappe.db.get_value("Item", item_code, "stock_uom")
                reservation.qty = row.reserve_qty
                reservation.reference_doctype = reference_doctype
                reservation.reference_name = reference_docname
                reservation.reserve_type = "WIP"
                reservation.reservation_based_on = "Serial and Batch"
                reservation.posting_date = frappe.utils.today()

                reservation.append("sb_entries", {
                    "batch_no": batch_no,
                    "qty": row.reserve_qty,
                    "warehouse": warehouse,
                })

                should_submit = (
                    reference_doctype == "Purchase Receipt"
                    or reference_doctype == "Subcontracting Receipt"
                    or (reference_doctype == "Stock Entry" and parent_doc.get("stock_entry_type") == "Manufacture")
                )

                if should_submit:
                    reservation.insert()
                    reservation.submit()




def on_cancel_cancel_reservation(doc, method):
    if doc.doctype == "Stock Entry" and doc.get("stock_entry_type") != "Manufacture":
        return

    for item in doc.items:
        if item.get("custom_plans"):
            plan_doc = frappe.get_doc("Plans", item.custom_plans)
            # Convert actual_qty to float for calculations
            actual_qty = flt(plan_doc.get("actual_qty", 0))
            
            # Debug prints (consider using frappe.logger() in production)
            print("\n\nCreating production stock reservation for plan:", plan_name)
            print("For item:", item_code)
            print("Actual quantity:", actual_qty)

            # Initialize variables with proper float conversion
            reserved_received_qty = flt(plan_doc.get("reserved_received_qty", 0))
            unreserved_received_qty = flt(plan_doc.get("unreserved_received_qty", 0))
            reserved_qty = flt(plan_doc.get("reserved_qty", 0))
            plan_qty = flt(plan_doc.get("plan_qty", 0))

            # Update received quantities based on reservation type
            if create_for_all is None and specific_reserved_plan is None:
                print("Updating unreserved received quantity")
                plan_doc.received_qty = actual_qty
                plan_doc.unreserved_received_qty = flt(plan_doc.get("unreserved_received_qty", 0)) - actual_qty
                plan_doc.unreserved_qty = plan_qty - plan_doc.unreserved_received_qty - plan_doc.reserved_qty
            else:
                print("Updating reserved received quantity")
                plan_doc.received_qty = actual_qty
                plan_doc.reserved_received_qty = flt(plan_doc.get("reserved_received_qty", 0)) - actual_qty
                plan_doc.unreserved_qty = plan_qty - plan_doc.unreserved_received_qty - plan_doc.reserved_qty

            # Save and commit changes
            plan_doc.save()
            frappe.db.commit()
            
            for row in plan_doc.get("reserved_wip_plans") or []:
                # print("\n\nreserved_wip_plans\n\n", reserved_wip_plans)
                filters = {
                    # "plan": item.custom_plans,
                    "plans_no": row.plan,
                    # "reference_doctype": doc.doctype,
                    # "reference_name": doc.name
                }
                reservation_name = frappe.db.get_value("Production Stock Reservation", filters, "name")
                if reservation_name:
                    try:
                        reservation_doc = frappe.get_doc("Production Stock Reservation", reservation_name)
                        if reservation_doc.docstatus == 1:
                            reservation_doc.cancel()
                    except Exception:
                        frappe.log_error(frappe.get_traceback(), f"Failed to cancel Production Stock Reservation: {reservation_name}")


# def on_stock_entry_cancel_reservation(doc, method):
#     if doc.doctype == "Stock Entry" and doc.get("stock_entry_type") != "Manufacture":
#         return

#     for item in doc.items:
#         if item.get("custom_plans"):
#             plan_doc = frappe.get_doc("Plans", item.custom_plans)
#             for row in plan_doc.get("reserved_wip_plans") or []:
#                 # print("\n\nreserved_wip_plans\n\n", reserved_wip_plans)
#                 filters = {
#                     # "plan": item.custom_plans,
#                     "plans_no": row.plan,
#                     # "reference_doctype": doc.doctype,
#                     # "reference_name": doc.name
#                 }
#                 reservation_name = frappe.db.get_value("Production Stock Reservation", filters, "name")
#                 if reservation_name:
#                     try:
#                         reservation_doc = frappe.get_doc("Production Stock Reservation", reservation_name)
#                         if reservation_doc.docstatus == 1:
#                             reservation_doc.cancel()
#                     except Exception:
#                         frappe.log_error(frappe.get_traceback(), f"Failed to cancel Production Stock Reservation: {reservation_name}")



# def update_psr_on_return_submit(doc, method):
#     """Handle PSR updates when return stock entry is submitted"""
#     if doc.stock_entry_type != "Material Transfer":
#         return

#     print(f"\n\n[SUBMIT RETURN] Updating PSR from Return Stock Entry: {doc.name}")

#     for row in doc.items:
#         if not row.custom_plans or not row.batch_no:
#             continue

#         update_psr_return_quantities(row, operation="add")

# def reset_psr_on_return_cancel(doc, method):
#     """Handle PSR updates when return stock entry is cancelled"""
#     if doc.stock_entry_type != "Material Transfer":
#         return

#     print(f"\n\n[CANCEL RETURN] Resetting PSR from Return Stock Entry in PSR: {doc.name}")

#     for row in doc.items:
#         print("\nrow.custom_plans\n",row.custom_plans)
#         print("\nrow.batch_no\n",row.batch_no)
#         if not row.custom_plans:
#             continue

#         update_psr_return_quantities(row, operation="subtract")

# def update_psr_return_quantities(row, operation):
#     # console.log("\n\nupdate_psr_return_quantities\n\n")
#     print("\n\nupdate_psr_return_quantities\n\n")
#     """Common function to update PSR quantities for both submit and cancel"""
#     reservations = frappe.get_all(
#         "Production Stock Reservation",
#         filters={"plans_no": row.custom_plans},
#         fields=["name"]
#     )

#     for res in reservations:
#         psr_doc = frappe.get_doc("Production Stock Reservation", res.name)
#         updated = False

#         for entry in psr_doc.get("sb_entries", []):
#             # if entry.batch_no != row.batch_no:
#             #     continue

#             if row.t_warehouse and entry.warehouse == row.t_warehouse:
#                 # console.log("operation",operation);
#                 if operation == "add":
#                     entry.returned_qty = (entry.returned_qty or 0) + (row.qty or 0)
#                 else:  # subtract
#                     entry.returned_qty = max((entry.returned_qty or 0) - (row.qty or 0), 0)
#                 updated = True

#             if updated:
#                 entry.actual_delivered_qty = (entry.delivered_qty or 0) - (entry.returned_qty or 0)
#                 entry.need_to_deliver_qty = (entry.qty or 0) - (entry.actual_delivered_qty or 0)

#         if updated:
#             psr_doc.save(ignore_permissions=True)

def update_psr_on_return_submit(doc, method):
    """Handle PSR updates when return stock entry is submitted"""
    if doc.stock_entry_type not in ["Material Transfer", "Material Transfer for Manufacture", "Send to Subcontractor"]:
        return

    print(f"\n\n[SUBMIT] Updating PSR from Stock Entry: {doc.name} ({doc.stock_entry_type})")

    for row in doc.items:
        if not row.custom_plans or not row.batch_no:
            continue

        if doc.stock_entry_type == "Material Transfer":
            update_psr_return_quantities(row, operation="add")
        elif doc.stock_entry_type == "Material Transfer for Manufacture" or doc.stock_entry_type == "Send to Subcontractor":
            update_psr_transfer_quantities(row, operation="add")

def reset_psr_on_return_cancel(doc, method):
    """Handle PSR updates when return stock entry is cancelled"""
    if doc.stock_entry_type not in ["Material Transfer", "Material Transfer for Manufacture", "Send to Subcontractor"]:
        return

    print(f"\n\n[CANCEL] Resetting PSR from Stock Entry: {doc.name} ({doc.stock_entry_type})")

    for row in doc.items:
        if not row.custom_plans:
            continue

        if doc.stock_entry_type == "Material Transfer":
            update_psr_return_quantities(row, operation="subtract")
        elif doc.stock_entry_type == "Material Transfer for Manufacture" or doc.stock_entry_type == "Send to Subcontractor":
            update_psr_transfer_quantities(row, operation="subtract")

def update_psr_return_quantities(row, operation):
    """Update returned quantities in PSR"""
    print("\nUpdating PSR return quantities")
    reservations = frappe.get_all(
        "Production Stock Reservation",
        filters={"plans_no": row.custom_plans},
        fields=["name"]
    )

    for res in reservations:
        psr_doc = frappe.get_doc("Production Stock Reservation", res.name)
        updated = False

        for entry in psr_doc.get("sb_entries", []):
            if row.t_warehouse and entry.warehouse == row.t_warehouse:
                if operation == "add":
                    entry.returned_qty = (entry.returned_qty or 0) + (row.qty or 0)
                else:  # subtract
                    entry.returned_qty = max((entry.returned_qty or 0) - (row.qty or 0), 0)
                updated = True

            if updated:
                entry.actual_delivered_qty = (entry.delivered_qty or 0) - (entry.returned_qty or 0)
                entry.need_to_deliver_qty = (entry.qty or 0) - (entry.actual_delivered_qty or 0)

        if updated:
            psr_doc.save(ignore_permissions=True)

def update_psr_transfer_quantities(row, operation):
    """Update transfer quantities in PSR for Material Transfer for Manufacture"""
    print("\nUpdating PSR transfer quantities")
    reservations = frappe.get_all(
        "Production Stock Reservation",
        filters={"plans_no": row.custom_plans},
        fields=["name"]
    )

    for res in reservations:
        psr_doc = frappe.get_doc("Production Stock Reservation", res.name)
        updated = False

        for entry in psr_doc.get("sb_entries", []):
            if row.s_warehouse and entry.warehouse == row.s_warehouse:
                if operation == "add":
                    entry.delivered_qty = (entry.delivered_qty or 0) + (row.qty or 0)
                else:  # subtract
                    entry.delivered_qty = max((entry.delivered_qty or 0) - (row.qty or 0), 0)
                updated = True

            if updated:
                entry.actual_delivered_qty = (entry.delivered_qty or 0) - (entry.returned_qty or 0)
                entry.need_to_deliver_qty = (entry.qty or 0) - (entry.actual_delivered_qty or 0)

        if updated:
            psr_doc.save(ignore_permissions=True)


def on_stock_entry_cancel_reservation(doc, method):
    """Cancel PSR when manufacturing stock entry is cancelled"""
    if doc.doctype != "Stock Entry" or doc.stock_entry_type != "Manufacture":
        return

    for item in doc.items:
        if not item.get("custom_plans"):
            continue

        plan_doc = frappe.get_doc("Plans", item.custom_plans)

        # Convert actual_qty to float for calculations
        actual_qty = flt(plan_doc.get("actual_qty", 0))
        
        # Debug prints (consider using frappe.logger() in production)
        print("\n\nCreating production stock reservation for plan:", plan_name)
        print("For item:", item_code)
        print("Actual quantity:", actual_qty)

        # Initialize variables with proper float conversion
        reserved_received_qty = flt(plan_doc.get("reserved_received_qty", 0))
        unreserved_received_qty = flt(plan_doc.get("unreserved_received_qty", 0))
        reserved_qty = flt(plan_doc.get("reserved_qty", 0))
        plan_qty = flt(plan_doc.get("plan_qty", 0))

        # Update received quantities based on reservation type
        if create_for_all is None and specific_reserved_plan is None:
            print("Updating unreserved received quantity")
            plan_doc.received_qty = actual_qty
            plan_doc.unreserved_received_qty = flt(plan_doc.get("unreserved_received_qty", 0)) - actual_qty
            plan_doc.unreserved_qty = plan_qty - plan_doc.unreserved_received_qty - plan_doc.reserved_qty
        else:
            print("Updating reserved received quantity")
            plan_doc.received_qty = actual_qty
            plan_doc.reserved_received_qty = flt(plan_doc.get("reserved_received_qty", 0)) - actual_qty
            plan_doc.unreserved_qty = plan_qty - plan_doc.unreserved_received_qty - plan_doc.reserved_qty

        # Save and commit changes
        plan_doc.save()
        frappe.db.commit()

        for row in plan_doc.get("reserved_wip_plans") or []:
            filters = {
                "plans_no": row.plan,
            }
            reservation_name = frappe.db.get_value("Production Stock Reservation", filters, "name")
            
            if reservation_name:
                try:
                    reservation_doc = frappe.get_doc("Production Stock Reservation", reservation_name)
                    if reservation_doc.docstatus == 1:
                        reservation_doc.cancel()
                except Exception:
                    frappe.log_error(frappe.get_traceback(), 
                        f"Failed to cancel Production Stock Reservation: {reservation_name}")




def validate_purchase_order_qty(doc, method):
    for item in doc.items:
        if not item.custom_plans:
            continue

        # Get the plan_qty from the linked Plans document
        plan_qty = frappe.db.get_value("Plans", item.custom_plans, "plan_qty") or 0

        # Get total qty and total short_close_po_qty from existing submitted POs (excluding current doc)
        existing_data = frappe.db.sql("""
            SELECT 
                COALESCE(SUM(poi.qty), 0) AS total_qty,
                COALESCE(SUM(poi.custom_short_close_po_qty), 0) AS total_short_close
            FROM 
                `tabPurchase Order Item` poi
            INNER JOIN 
                `tabPurchase Order` po ON poi.parent = po.name
            WHERE 
                poi.custom_plans = %s
                AND po.docstatus = 1
                AND po.name != %s
        """, (item.custom_plans, doc.name))[0]

        existing_qty = existing_data[0]
        short_close_qty = existing_data[1]

        # Compute actual committed qty = existing_qty - short_closed
        committed_qty = existing_qty - short_close_qty

        # Add current row's new qty (excluding its short close)
        current_committed_qty = (item.qty or 0) - (item.custom_short_close_po_qty or 0)
        total_committed_qty = committed_qty + current_committed_qty

        if total_committed_qty > plan_qty:
            frappe.throw(_(
                "Total committed quantity for Plan {0} exceeds allowed plan_qty.\n"
                "Plan Qty: {1}, Already Committed: {2}, This PO: {3}, Total: {4}".format(
                    item.custom_plans,
                    plan_qty,
                    committed_qty,
                    current_committed_qty,
                    total_committed_qty
                )
            ))

from collections import defaultdict
import frappe

def on_update_after_submit_po(doc, method):
    print("\n\n[on_update_after_submit_po triggered]\n")

    for item in doc.items:
        if not item.custom_plans or item.custom_short_close_plan_qty is None:
            continue

        # Optional: Fetch plan_qty
        plan_qty = frappe.db.get_value("Plans", item.custom_plans, "plan_qty") or 0

        # Get total qty and short close qty from submitted Purchase Orders
        existing_data = frappe.db.sql("""
            SELECT 
                COALESCE(SUM(poi.qty), 0) AS total_qty,
                COALESCE(SUM(poi.custom_short_close_plan_qty), 0) AS total_short_close
            FROM 
                `tabPurchase Order Item` poi
            INNER JOIN 
                `tabPurchase Order` po ON poi.parent = po.name
            WHERE 
                poi.custom_plans = %s
                AND po.docstatus = 1
        """, (item.custom_plans,))[0]

        existing_short_close_po_data = frappe.db.sql("""
            SELECT 
                COALESCE(SUM(poi.custom_short_close_po_qty), 0) AS total_short_close_po
            FROM 
                `tabPurchase Order Item` poi
            INNER JOIN 
                `tabPurchase Order` po ON poi.parent = po.name
            WHERE 
                poi.custom_plans = %s
                AND po.docstatus = 1
        """, (item.custom_plans,))[0]


        total_po_qty_after_short_close = existing_data[0] - existing_short_close_po_data[0] - existing_data[1]

        total_short_close_qty = existing_data[1]

        print(f"\n📘 existing_data: {existing_data}")
        print(f"\n📘 Plan: {item.custom_plans}")
        print(f"➤ PO Qty: {total_po_qty_after_short_close}, Short Close Qty: {total_short_close_qty}")

        # ✅ Update the short_close_plan_qty in Plans doc
        frappe.db.set_value("Plans", item.custom_plans, "short_close_plan_qty", total_short_close_qty)
        # ✅ Update the rm_reserved_qty in Plans doc
        # frappe.db.set_value("Plans", item.custom_plans, "rm_reserved_qty", total_po_qty_after_short_close)

        # 🔄 Adjust plan_qty in plan_item_planned_wise inside Plan Items
        plan_items = frappe.get_all(
            "Plan Items",
            filters={"plan": item.custom_plans},
            fields=["name"]
        )

        for plan_item in plan_items:
            plan_item_doc = frappe.get_doc("Plan Items", plan_item.name)

            for row in plan_item_doc.get("plan_item_planned_wise", []):
                if row.plan == item.custom_plans:
                    original_qty = row.plan_qty or 0
                    # new_qty = max(original_qty - total_short_close_qty, 0)
                    new_qty = total_po_qty_after_short_close
                    print(f"🔧 Updating row {row.name} in plan_item_planned_wise: {original_qty} → {new_qty}")
                    row.plan_qty = new_qty

            # 💾 Save Plan Item doc after updating both tables
            plan_item_doc.save(ignore_permissions=True)

            # ✅ Update summary table inside Plan Items doc
            update_plan_items_summary_po(plan_item_doc.name)


def update_plan_items_summary_po(docname):
    print("\n\n📄 Updating Plan Items Summary PO for:", docname)

    # Load the linked Plan Items document
    plan_item_doc = frappe.get_doc("Plan Items", docname)

    # Step 1: Aggregate total plan_qty per item_code from plan_item_planned_wise
    item_code_totals = defaultdict(float)
    for row in plan_item_doc.plan_item_planned_wise:
        if row.item_code:
            item_code_totals[row.item_code] += row.plan_qty
            print(f"➕ Adding {row.plan_qty} to {row.item_code} → Total: {item_code_totals[row.item_code]}")
    print("\n📊 item_code_totals:\n", item_code_totals)

    # Step 2: Update matching rows in plan_items_summary
    for summary_row in plan_item_doc.plan_items_summary:
        item_code = summary_row.item_code
        if item_code in item_code_totals:
            planned_qty = item_code_totals[item_code]
            original_qty = summary_row.qty or 0

            summary_row.planned_qty = planned_qty
            summary_row.need_to_plan_qty = original_qty - planned_qty

            print(f"✅ Updated {item_code} → Planned: {planned_qty}, Need to Plan: {summary_row.need_to_plan_qty}")

    # Save changes
    plan_item_doc.save(ignore_permissions=True)
    frappe.db.commit()
    print(f"🎉 Plan Items Summary updated successfully for: {docname}")
    return True


def validate_work_order_qty(doc, method):
    if not doc.custom_plans:
        return

    # Get the plan_qty from the linked Plans document
    plan_qty = frappe.db.get_value("Plans", doc.custom_plans, "plan_qty") or 0

    # Get total qty and total short_close_po_qty from existing submitted WOs (excluding current doc)
    existing_data = frappe.db.sql("""
        SELECT 
            COALESCE(SUM(wo.qty), 0) AS total_qty,
            COALESCE(SUM(wo.custom_short_close_wo_qty), 0) AS total_short_close
        FROM 
            `tabWork Order` wo
        WHERE 
            wo.custom_plans = %s
            AND wo.docstatus = 1
            AND wo.name != %s
    """, (doc.custom_plans, doc.name))[0]
    print("\n\nexisting_data\n\n",existing_data)


    existing_qty = existing_data[0]
    short_close_qty = existing_data[1]

    # Compute actual committed qty = existing_qty - short_closed
    committed_qty = existing_qty - short_close_qty

    # Add current row's new qty (excluding its short close)
    current_committed_qty = (doc.qty or 0) - (doc.custom_short_close_wo_qty or 0)
    total_committed_qty = committed_qty + current_committed_qty

    if total_committed_qty > plan_qty:
        frappe.throw(_(
            "Total committed quantity for Plan {0} exceeds allowed plan_qty.\n"
            "Plan Qty: {1}, Already Committed: {2}, This WO: {3}, Total: {4}".format(
                doc.custom_plans,
                plan_qty,
                committed_qty,
                current_committed_qty,
                total_committed_qty
            )
        ))


def on_cancel_wo(doc, method):
    print("\n\non_cancel_wo triggered]\n")
    if doc.custom_short_close_wo_qty >= 0:
        cancel_plans_for_wo_short_close_qty(doc.custom_plans, doc.custom_short_close_wo_qty)

def cancel_plans_for_wo_short_close_qty(docname, qty):
    print("cancel_plans_for_wo_short_close_qty")

    try:
        # Load the Plans document by name
        plan_doc = frappe.get_doc("Plans", docname)

        # Update the short_close_wo_qty field
        plan_doc.short_close_wo_qty = 0
        print("\n\nplan_doc.short_close_wo_qty\n\n",plan_doc.short_close_wo_qty)

        # Save the updated document
        plan_doc.save(ignore_permissions=True)

        # Optional: Submit or update status if needed
        # plan_doc.submit() or plan_doc.db_set(...) if needed

        print(f"Updated short_close_wo_qty to {qty} for Plan: {docname}")
        return {"status": "success", "message": f"Plan {docname} updated."}
    
    except frappe.DoesNotExistError:
        frappe.throw(f"Plan {docname} does not exist.")
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "update_plans_for_wo_short_close_qty")
        return {"status": "error", "message": str(e)}

# uncomment this below code while deploy in pranera instance
def on_submit_wo(doc, method):
    print("\n\non_submit_wo triggered]\n")

    if doc.custom_short_close_wo_qty >= 0:
        update_plans_for_wo_short_close_qty(doc.custom_plans, doc.custom_short_close_wo_qty)

    if not doc.custom_plans or doc.custom_short_close_plan_qty is None:
        return

    # Optional: Fetch plan_qty
    plan_qty = frappe.db.get_value("Plans", doc.custom_plans, "plan_qty") or 0

    # Get total qty and short close qty from submitted Work Orders
    existing_data = frappe.db.sql("""
        SELECT 
            COALESCE(SUM(wo.qty), 0) AS total_qty,
            COALESCE(SUM(wo.custom_short_close_plan_qty), 0) AS total_short_close
        FROM 
            `tabWork Order` wo
        WHERE 
            wo.custom_plans = %s
            AND wo.docstatus = 1
    """, (doc.custom_plans,))[0]

    total_wo_qty = existing_data[0]
    total_short_close_qty = existing_data[1]

    print(f"\n📘 Plan: {doc.custom_plans}")
    print(f"➤ WO Qty: {total_wo_qty}, Short Close Qty: {total_short_close_qty}")

    # ✅ Update the short_close_plan_qty in Plans doc
    frappe.db.set_value("Plans", doc.custom_plans, "short_close_plan_qty", total_short_close_qty)

    # 🔄 Adjust plan_qty in plan_item_planned_wise inside Plan Items
    plan_items = frappe.get_all(
        "Plan Items",
        filters={"plan": doc.custom_plans},
        fields=["name"]
    )

    for plan_item in plan_items:
        plan_item_doc = frappe.get_doc("Plan Items", plan_item.name)

        for row in plan_item_doc.get("plan_item_planned_wise", []):
            if row.plan == doc.custom_plans:
                original_qty = row.plan_qty or 0
                new_qty = max(original_qty - total_short_close_qty, 0)
                print(f"🔧 Updating row {row.name} in plan_item_planned_wise: {original_qty} → {new_qty}")
                row.plan_qty = new_qty

        # 💾 Save Plan Item doc after updating both tables
        plan_item_doc.save(ignore_permissions=True)

        # ✅ Update summary table inside Plan Items doc
        update_plan_items_summary_wo(plan_item_doc.name)



def on_update_after_submit_wo(doc, method):
    print("\n\non_update_after_submit_wo triggered]\n")

    if doc.custom_short_close_wo_qty >= 0:
        update_plans_for_wo_short_close_qty(doc.custom_plans, doc.custom_short_close_wo_qty)

    
    if not doc.custom_plans and doc.custom_short_close_plan_qty is None:
        return

    # if doc.custom_short_close_plan_qty > 0:
    # Optional: Fetch plan_qty
    plan_qty = frappe.db.get_value("Plans", doc.custom_plans, "plan_qty") or 0

    # Get total qty and short close qty from submitted Work Orders
    existing_data = frappe.db.sql("""
        SELECT 
            COALESCE(SUM(wo.qty), 0) AS total_qty,
            COALESCE(SUM(wo.custom_short_close_plan_qty), 0) AS total_short_close
        FROM 
            `tabWork Order` wo
        WHERE 
            wo.custom_plans = %s
            AND wo.docstatus = 1
    """, (doc.custom_plans,))[0]

    existing_short_close_wo_data = frappe.db.sql("""
        SELECT 
            COALESCE(SUM(wo.custom_short_close_wo_qty), 0) AS total_short_close_wo
        FROM 
            `tabWork Order` wo
        WHERE 
            wo.custom_plans = %s
            AND wo.docstatus = 1
    """, (doc.custom_plans,))[0]

    total_wo_qty_after_short_close = existing_data[0] - existing_data[1]
    total_short_close_qty = existing_data[1]

    print(f"\n📘 Plan: {doc.custom_plans}")
    print(f"➤ WO Qty: {total_wo_qty_after_short_close}, Short Close Qty: {total_short_close_qty}")

    # ✅ Update the short_close_plan_qty in Plans doc
    frappe.db.set_value("Plans", doc.custom_plans, "short_close_plan_qty", total_short_close_qty)

    # frappe.db.set_value("Plans", doc.custom_plans, "short_close_plan_qty", total_short_close_qty)


    # frappe.db.set_value("Plans", doc.custom_plans, "rm_reserved_qty", total_wo_qty_after_short_close)

    # 🔄 Adjust plan_qty in plan_item_planned_wise inside Plan Items
    plan_items = frappe.get_all(
        "Plan Items",
        filters={"plan": doc.custom_plans},
        fields=["name"]
    )

    for plan_item in plan_items:
        plan_item_doc = frappe.get_doc("Plan Items", plan_item.name)

        for row in plan_item_doc.get("plan_item_planned_wise", []):
            if row.plan == doc.custom_plans:
                original_qty = row.plan_qty or 0
                # new_qty = max(original_qty - total_short_close_qty, 0)
                new_qty = total_wo_qty_after_short_close
                print(f"🔧 Updating row {row.name} in plan_item_planned_wise: {original_qty} → {new_qty}")
                row.plan_qty = new_qty

        # 💾 Save Plan Item doc after updating both tables
        plan_item_doc.save(ignore_permissions=True)

        # ✅ Update summary table inside Plan Items doc
        update_plan_items_summary_wo(plan_item_doc.name)
# uncomment this above code while deploy in pranera instance



def update_plans_for_wo_short_close_qty(docname, qty):
    print("update_plans_for_wo_short_close_qty")

    try:
        # Load the Plans document by name
        plan_doc = frappe.get_doc("Plans", docname)

        # Update the short_close_wo_qty field
        plan_doc.short_close_wo_qty = qty
        print("\n\nplan_doc.short_close_wo_qty\n\n",plan_doc.short_close_wo_qty)

        # Save the updated document
        plan_doc.save(ignore_permissions=True)

        # Optional: Submit or update status if needed
        # plan_doc.submit() or plan_doc.db_set(...) if needed

        print(f"Updated short_close_wo_qty to {qty} for Plan: {docname}")
        return {"status": "success", "message": f"Plan {docname} updated."}
    
    except frappe.DoesNotExistError:
        frappe.throw(f"Plan {docname} does not exist.")
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "update_plans_for_wo_short_close_qty")
        return {"status": "error", "message": str(e)}



def update_plan_items_summary_wo(docname):
    print("\n\n📄 Updating Plan Items Summary WO for:", docname)

    # Load the linked Plan Items document
    plan_item_doc = frappe.get_doc("Plan Items", docname)

    # Step 1: Aggregate total plan_qty per item_code from plan_item_planned_wise
    item_code_totals = defaultdict(float)
    for row in plan_item_doc.plan_item_planned_wise:
        print("\n\nrow plan_item_planned_wise\n\n",row)
        print("\n\nrow plan_item_planned_wise item_code\n\n",row.item_code)
        print("\n\nrow plan_item_planned_wise plan_qty\n\n",row.plan_qty)
        if row.item_code:
            item_code_totals[row.item_code] += row.plan_qty
            print(f"➕ Adding {row.plan_qty} to {row.item_code} → Total: {item_code_totals[row.item_code]}")
    print("\n📊 item_code_totals:\n", item_code_totals)

    # Step 2: Update matching rows in plan_items_summary
    for summary_row in plan_item_doc.plan_items_summary:
        item_code = summary_row.item_code
        if item_code in item_code_totals:
            planned_qty = item_code_totals[item_code]
            original_qty = summary_row.qty or 0

            summary_row.planned_qty = planned_qty
            summary_row.need_to_plan_qty = original_qty - planned_qty

            print(f"✅ Updated {item_code} → Planned: {planned_qty}, Need to Plan: {summary_row.need_to_plan_qty}")

    # Save changes
    plan_item_doc.save(ignore_permissions=True)
    frappe.db.commit()
    print(f"🎉 Plan Items Summary updated successfully for: {docname}")
    return True



 
