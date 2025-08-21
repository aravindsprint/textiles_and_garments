import frappe
from frappe import _

# def validate_stock_entry(doc, method):
#     print("\n\nvalidate_stock_entry\n\n")
#     if doc.stock_entry_type not in ["Send to Subcontractor", "Material Transfer for Manufacture"]:
#         return

#     print("\n\nvalidate_stock_entry\n\n", doc)

#     # Step 1: Collect all unique plans from stock entry items
#     plan_item_map = {}
#     for item in doc.items:
#         if not item.custom_plans:
#             continue
#         key = (item.custom_plans, item.batch_no, item.s_warehouse)
#         plan_item_map[key] = plan_item_map.get(key, 0) + item.qty

#     print("\n\nplan_item_map (current doc items)\n\n", plan_item_map)

#     for (plan_no, batch_no, warehouse), total_qty in plan_item_map.items():
#         # Step 2: Fetch reservations for this plan
#         reservations = frappe.get_all(
#             "Production Stock Reservation",
#             filters={"plans_no": plan_no},
#             fields=["name"]
#         )

#         reservation_map = {}
#         for res in reservations:
#             child_rows = frappe.get_all(
#                 "Serial and Batch Entry Plans",
#                 filters={"parent": res.name},
#                 fields=["batch_no", "warehouse", "qty"]
#             )
#             for row in child_rows:
#                 key = (row.batch_no, row.warehouse)
#                 reservation_map[key] = reservation_map.get(key, 0) + row.qty

#         print(f"\n\nreservation_map for plan {plan_no}\n\n", reservation_map)

#         # Step 3: Get previously used qty (from other submitted Stock Entries with the same plan)
#         previous_entries = frappe.get_all(
#             "Stock Entry",
#             filters={
#                 "docstatus": 1,
#                 "name": ["!=", doc.name]
#             },
#             fields=["name"]
#         )

#         used_qty = 0
#         for entry in previous_entries:
#             entry_doc = frappe.get_doc("Stock Entry", entry.name)
#             for entry_item in entry_doc.items:
#                 if entry_item.custom_plans == plan_no and \
#                    entry_item.batch_no == batch_no and \
#                    entry_item.s_warehouse == warehouse:
#                     used_qty += entry_item.qty

#         # Add current qty
#         used_qty += total_qty

#         reserved_qty = reservation_map.get((batch_no, warehouse))
#         if reserved_qty is None:
#             frappe.throw(_(
#                 f"Batch No <b>{batch_no}</b> from Warehouse <b>{warehouse}</b> is not reserved for Plan <b>{plan_no}</b>."
#             ))

#         allowed_qty = reserved_qty * 1.02
#         if used_qty > allowed_qty:
#             frappe.throw(_(
#                 f"Total used Qty <b>{used_qty}</b> for Batch No <b>{batch_no}</b> in Warehouse <b>{warehouse}</b> exceeds allowed limit <b>{allowed_qty:.2f}</b> (2% tolerance included) for Plan <b>{plan_no}</b>."
#             ))

# def validate_stock_entry(doc, method):
#     if doc.stock_entry_type not in ["Send to Subcontractor", "Material Transfer for Manufacture"]:
#         return

#     for row in doc.get("items", []):
#         if not row.custom_plans or not row.batch_no:
#             continue

#         try:
#             psr_doc = frappe.get_doc("Production Stock Reservation", row.custom_plans)
#         except frappe.DoesNotExistError:
#             frappe.msgprint(f"Production Stock Reservation {row.custom_plans} not found.")
#             continue

#         updated = False
#         for entry in psr_doc.get("serial_and_batch_entry_plans", []):
#             if entry.batch_no != row.batch_no:
#                 continue

#             # Delivered Qty (source warehouse)
#             if row.s_warehouse and entry.warehouse == row.s_warehouse:
#                 entry.delivered_qty = (entry.delivered_qty or 0) + (row.qty or 0)
#                 updated = True

#             # Returned Qty (target warehouse)
#             if row.t_warehouse and entry.warehouse == row.t_warehouse:
#                 entry.returned_qty = (entry.returned_qty or 0) + (row.qty or 0)
#                 updated = True

#         if updated:
#             psr_doc.save(ignore_permissions=True)



import frappe
from frappe import _

# def validate_stock_entry(doc, method):
#     if doc.stock_entry_type not in ["Send to Subcontractor", "Material Transfer for Manufacture"]:
#         return

#     print(f"\n\n✅ validate_stock_entry triggered for: {doc.name}\n")

#     # Step 1: Collect all unique (plan, batch, s_warehouse) combinations
#     plan_item_map = {}
#     for item in doc.items:
#         if not item.custom_plans or not item.batch_no:
#             continue
#         key = (item.custom_plans, item.batch_no, item.s_warehouse)
#         plan_item_map[key] = plan_item_map.get(key, 0) + (item.qty or 0)

#     print("\n\n🧾 plan_item_map (current Stock Entry items):\n", plan_item_map)

#     for (plan_no, batch_no, warehouse), total_qty in plan_item_map.items():
#         # Step 2: Fetch reservations for this plan
#         reservations = frappe.get_all(
#             "Production Stock Reservation",
#             filters={"plans_no": plan_no},
#             fields=["name"]
#         )

#         reservation_map = {}
#         for res in reservations:
#             child_rows = frappe.get_all(
#                 "Serial and Batch Entry Plans",
#                 filters={"parent": res.name},
#                 fields=["batch_no", "warehouse", "qty"]
#             )
#             for row in child_rows:
#                 key = (row.batch_no, row.warehouse)
#                 reservation_map[key] = reservation_map.get(key, 0) + (row.qty or 0)

#         print(f"\n📦 reservation_map for Plan {plan_no}:\n", reservation_map)

#         # Step 3: Calculate used qty from submitted Stock Entries
#         used_qty = 0
#         previous_entries = frappe.get_all(
#             "Stock Entry",
#             filters={"docstatus": 1, "name": ["!=", doc.name]},
#             fields=["name"]
#         )

#         for entry in previous_entries:
#             entry_doc = frappe.get_doc("Stock Entry", entry.name)
#             for entry_item in entry_doc.items:
#                 if (
#                     entry_item.custom_plans == plan_no
#                     and entry_item.batch_no == batch_no
#                     and entry_item.s_warehouse == warehouse
#                 ):
#                     used_qty += (entry_item.qty or 0)

#         used_qty += total_qty  # include current document
#         print("\n📊 used_qty (including current doc):", used_qty)

#         reserved_qty = reservation_map.get((batch_no, warehouse))
#         if reserved_qty is None:
#             frappe.throw(_(
#                 f"Batch No <b>{batch_no}</b> from Warehouse <b>{warehouse}</b> is not reserved for Plan <b>{plan_no}</b>."
#             ))

#         allowed_qty = reserved_qty * 1.02  # 2% tolerance
#         if used_qty > allowed_qty:
#             frappe.throw(_(
#                 f"Total used Qty <b>{used_qty}</b> for Batch No <b>{batch_no}</b> from Warehouse <b>{warehouse}</b> exceeds allowed limit <b>{allowed_qty:.2f}</b> (2% tolerance included) for Plan <b>{plan_no}</b>."
#             ))

#     # Step 4: Update Production Stock Reservation's delivered_qty/returned_qty
#     for row in doc.items:
#         if not row.custom_plans or not row.batch_no:
#             continue

#         reservations = frappe.get_all(
#             "Production Stock Reservation",
#             filters={"plans_no": row.custom_plans},
#             fields=["name"]
#         )
#         print("\n\nreservations\n\n",reservations)

#         for res in reservations:
#             psr_doc = frappe.get_doc("Production Stock Reservation", res.name)
#             child_table = psr_doc.get("sb_entries") or []
#             print("\n\nchild_table\n\n",child_table)
#             updated = False

#             for entry in child_table:
#                 if entry.batch_no != row.batch_no:
#                     continue

#                 # Delivered Qty (source warehouse)
#                 if row.s_warehouse and entry.warehouse == row.s_warehouse:
#                     entry.delivered_qty = (entry.delivered_qty or 0) + (row.qty or 0)
#                     entry.actual_delivered_qty = entry.delivered_qty - entry.returned_qty
#                     entry.need_to_deliver_qty = entry.qty - entry.actual_delivered_qty
#                     updated = True

#                 # Returned Qty (target warehouse)
#                 if row.t_warehouse and entry.warehouse == row.t_warehouse:
#                     entry.returned_qty = (entry.returned_qty or 0) + (row.qty or 0)
#                     entry.actual_delivered_qty = entry.delivered_qty - entry.returned_qty
#                     entry.need_to_deliver_qty = entry.qty - entry.actual_delivered_qty
#                     updated = True

#             if updated:
#                 psr_doc.save(ignore_permissions=True)

import frappe
from frappe import _

def validate_stock_entry_before_submit(doc, method):
    if doc.stock_entry_type not in ["Send to Subcontractor", "Material Transfer for Manufacture"]:
        return

    print(f"\n\n✅ [VALIDATE] Stock Entry: {doc.name}")

    plan_item_map = {}
    for item in doc.items:
        if not item.custom_plans or not item.batch_no:
            continue
        key = (item.custom_plans, item.batch_no, item.s_warehouse)
        plan_item_map[key] = plan_item_map.get(key, 0) + (item.qty or 0)

    for (plan_no, batch_no, warehouse), current_qty in plan_item_map.items():
        reservations = frappe.get_all(
            "Production Stock Reservation",
            filters={"plans_no": plan_no},
            fields=["name"]
        )

        if not reservations:
            # print("reservations")
            frappe.throw(_(
                f"No Production Stock Reservation found for Plan <b>{plan_no}</b>."
            ))

        used_qty = 0
        total_reserved_qty = 0
        match_found = False  # Track if any row matches batch+warehouse

        for res in reservations:
            psr_doc = frappe.get_doc("Production Stock Reservation", res.name)
            for entry in psr_doc.get("sb_entries", []):
                if entry.batch_no == batch_no and entry.warehouse == warehouse:
                    match_found = True
                    used_qty += entry.actual_delivered_qty or 0
                    total_reserved_qty += entry.qty or 0

        if not match_found:
            print("match_found")
            frappe.throw(_(
                f"Batch No <b>{batch_no}</b> from Warehouse <b>{warehouse}</b> is not reserved in any matching row of "
                f"Production Stock Reservation for Plan <b>{plan_no}</b>."
            ))

        total_used_qty = used_qty + current_qty
        total_allowed_qty = total_reserved_qty * 1.02  # 2% tolerance

        print(f"\nPlan: {plan_no} | Batch: {batch_no} | Warehouse: {warehouse}")
        print(f"Used Qty: {used_qty}")
        print(f"Current Qty: {current_qty}")
        print(f"Total Used Qty: {total_used_qty}")
        print(f"Reserved Qty: {total_reserved_qty}")
        print(f"Allowed Qty (2%): {total_allowed_qty}")

        if total_used_qty > total_allowed_qty:
            print("total_used_qty")
            frappe.throw(_(
                f"Total used Qty <b>{total_used_qty}</b> for Batch No <b>{batch_no}</b> from Warehouse <b>{warehouse}</b> "
                f"exceeds allowed limit <b>{total_allowed_qty:.2f}</b> (2% tolerance) for Plan <b>{plan_no}</b>."
                f" Kindly transfer below <b>{total_allowed_qty - used_qty:.2f}</b> only."
            ))


def update_psr_on_submit(doc, method):
    if doc.stock_entry_type not in ["Send to Subcontractor", "Material Transfer for Manufacture"]:
        return

    print(f"\n\n[SUBMIT] Updating PSR from Stock Entry: {doc.name}")

    for row in doc.items:
        if not row.custom_plans or not row.batch_no:
            continue

        reservations = frappe.get_all(
            "Production Stock Reservation",
            filters={"plans_no": row.custom_plans},
            fields=["name"]
        )

        for res in reservations:
            psr_doc = frappe.get_doc("Production Stock Reservation", res.name)
            updated = False

            for entry in psr_doc.get("sb_entries", []):
                if entry.batch_no != row.batch_no:
                    continue

                if row.s_warehouse and entry.warehouse == row.s_warehouse:
                    entry.delivered_qty = (entry.delivered_qty or 0) + (row.qty or 0)
                    updated = True

                if row.t_warehouse and entry.warehouse == row.t_warehouse:
                    entry.returned_qty = (entry.returned_qty or 0) + (row.qty or 0)
                    updated = True

                if updated:
                    entry.actual_delivered_qty = (entry.delivered_qty or 0) - (entry.returned_qty or 0)
                    entry.need_to_deliver_qty = (entry.qty or 0) - (entry.actual_delivered_qty or 0)

            if updated:
                psr_doc.save(ignore_permissions=True)


def validate_return_stock_entry(doc, method):
    if doc.stock_entry_type != "Material Transfer":
        return

    print(f"\n\n✅ [VALIDATE RETURN] Stock Entry: {doc.name}")

    plan_item_map = {}
    for item in doc.items:
        if not item.custom_plans or not item.batch_no:
            continue
        key = (item.custom_plans, item.batch_no, item.t_warehouse)
        plan_item_map[key] = plan_item_map.get(key, 0) + (item.qty or 0)

    for (plan_no, batch_no, warehouse), current_qty in plan_item_map.items():
        reservations = frappe.get_all(
            "Production Stock Reservation",
            filters={"plans_no": plan_no},
            fields=["name"]
        )

        if not reservations:
            # print("reservations")
            frappe.throw(_(
                f"No Production Stock Reservation found for Plan <b>{plan_no}</b>."
            ))

        used_returned_qty = 0
        total_reserved_qty = 0
        match_found = False

        for res in reservations:
            psr_doc = frappe.get_doc("Production Stock Reservation", res.name)
            for entry in psr_doc.get("sb_entries", []):
                if entry.batch_no == batch_no and entry.warehouse == warehouse:
                    match_found = True
                    used_returned_qty += entry.returned_qty or 0
                    total_reserved_qty += entry.qty or 0

        if not match_found:
            frappe.throw(_(
                f"Return Batch No <b>{batch_no}</b> from Warehouse <b>{warehouse}</b> is not reserved in any matching row of "
                f"Production Stock Reservation for Plan <b>{plan_no}</b>."
            ))

        total_returned_qty = used_returned_qty + current_qty
        total_allowed_qty = total_reserved_qty * 1.02  # 2% tolerance

        print(f"\nPlan: {plan_no} | Batch: {batch_no} | Warehouse: {warehouse}")
        print(f"Already Returned Qty: {used_returned_qty}")
        print(f"Current Return Qty: {current_qty}")
        print(f"Total Returned Qty: {total_returned_qty}")
        print(f"Reserved Qty: {total_reserved_qty}")
        print(f"Allowed Qty (2%): {total_allowed_qty}")

        if total_returned_qty > total_allowed_qty:
            frappe.throw(_(
                f"Total Returned Qty <b>{total_returned_qty}</b> for Batch No <b>{batch_no}</b> from Warehouse <b>{warehouse}</b> "
                f"exceeds allowed limit <b>{total_allowed_qty:.2f}</b> (2% tolerance) for Plan <b>{plan_no}</b>."
            ))

def update_psr_on_return_submit(doc, method):
    if doc.stock_entry_type != "Material Transfer":
        return

    print(f"\n\n[SUBMIT RETURN] Updating PSR from Return Stock Entry: {doc.name}")

    for row in doc.items:
        if not row.custom_plans or not row.batch_no:
            continue

        reservations = frappe.get_all(
            "Production Stock Reservation",
            filters={"plans_no": row.custom_plans},
            fields=["name"]
        )

        for res in reservations:
            psr_doc = frappe.get_doc("Production Stock Reservation", res.name)
            updated = False

            for entry in psr_doc.get("sb_entries", []):
                if entry.batch_no != row.batch_no:
                    continue

                # Match return by checking target warehouse
                if row.t_warehouse and entry.warehouse == row.t_warehouse:
                    entry.returned_qty = (entry.returned_qty or 0) + (row.qty or 0)
                    updated = True

                if updated:
                    entry.actual_delivered_qty = (entry.delivered_qty or 0) - (entry.returned_qty or 0)
                    entry.need_to_deliver_qty = (entry.qty or 0) - (entry.actual_delivered_qty or 0)

            if updated:
                psr_doc.save(ignore_permissions=True)

# def reset_psr_on_return_cancel(doc, method):
#     if doc.stock_entry_type != "Material Transfer":
#         return

#     print(f"\n\n[CANCEL RETURN] Resetting PSR from Return Stock Entry: {doc.name}")

#     for row in doc.items:
#         if not row.custom_plans or not row.batch_no:
#             continue

#         reservations = frappe.get_all(
#             "Production Stock Reservation",
#             filters={"plans_no": row.custom_plans},
#             fields=["name"]
#         )

#         for res in reservations:
#             psr_doc = frappe.get_doc("Production Stock Reservation", res.name)
#             updated = False

#             for entry in psr_doc.get("sb_entries", []):
#                 if entry.batch_no != row.batch_no:
#                     continue

#                 # Match return by checking target warehouse
#                 if row.t_warehouse and entry.warehouse == row.t_warehouse:
#                     entry.returned_qty = max((entry.returned_qty or 0) - (row.qty or 0), 0)
#                     updated = True

#                 if updated:
#                     entry.actual_delivered_qty = (entry.delivered_qty or 0) - (entry.returned_qty or 0)
#                     entry.need_to_deliver_qty = (entry.qty or 0) - (entry.actual_delivered_qty or 0)

#             if updated:
#                 psr_doc.save(ignore_permissions=True)

def validate_stock_entry1(doc, method):
    if doc.stock_entry_type not in ["Material Transfer"]:
        return

    print(f"\n\n✅ validate_stock_entry triggered for Material Transfer: {doc.name}\n")

    # Step 1: Collect all unique (plan, batch, s_warehouse) combinations
    plan_item_map = {}
    for item in doc.items:
        if not item.custom_plans or not item.batch_no:
            continue
        key = (item.custom_plans, item.batch_no, item.t_warehouse)
        plan_item_map[key] = plan_item_map.get(key, 0) + (item.qty or 0)

    print("\n\n🧾 plan_item_map (current Stock Entry items):\n", plan_item_map)

    for (plan_no, batch_no, warehouse), total_qty in plan_item_map.items():
        # Step 2: Fetch reservations for this plan
        reservations = frappe.get_all(
            "Production Stock Reservation",
            filters={"plans_no": plan_no},
            fields=["name"]
        )

        reservation_map = {}
        for res in reservations:
            child_rows = frappe.get_all(
                "Serial and Batch Entry Plans",
                filters={"parent": res.name},
                fields=["batch_no", "warehouse", "qty"]
            )
            for row in child_rows:
                key = (row.batch_no, row.warehouse)
                reservation_map[key] = reservation_map.get(key, 0) + (row.qty or 0)

        print(f"\n📦 reservation_map for Plan {plan_no}:\n", reservation_map)

        # Step 3: Calculate used qty from submitted Stock Entries
        used_qty = 0
        previous_entries = frappe.get_all(
            "Stock Entry",
            filters={"docstatus": 1, "name": ["!=", doc.name]},
            fields=["name"]
        )

        for entry in previous_entries:
            entry_doc = frappe.get_doc("Stock Entry", entry.name)
            for entry_item in entry_doc.items:
                if (
                    entry_item.custom_plans == plan_no
                    and entry_item.batch_no == batch_no
                    and entry_item.t_warehouse == warehouse
                ):
                    used_qty += (entry_item.qty or 0)

        used_qty += total_qty  # include current document
        print("\n📊 used_qty (including current doc):", used_qty)

        reserved_qty = reservation_map.get((batch_no, warehouse))
        if reserved_qty is None:
            frappe.throw(_(
                f"Batch No <b>{batch_no}</b> from Warehouse <b>{warehouse}</b> is not reserved for Plan <b>{plan_no}</b>."
            ))

        allowed_qty = reserved_qty * 1.02  # 2% tolerance
        if used_qty > allowed_qty:
            frappe.throw(_(
                f"Total used Qty <b>{used_qty}</b> for Batch No <b>{batch_no}</b> from Warehouse <b>{warehouse}</b> exceeds allowed limit <b>{allowed_qty:.2f}</b> (2% tolerance included) for Plan <b>{plan_no}</b>."
            ))

    # Step 4: Update Production Stock Reservation's delivered_qty/returned_qty
    for row in doc.items:
        if not row.custom_plans or not row.batch_no:
            continue

        reservations = frappe.get_all(
            "Production Stock Reservation",
            filters={"plans_no": row.custom_plans},
            fields=["name"]
        )
        print("\n\nreservations\n\n",reservations)

        for res in reservations:
            psr_doc = frappe.get_doc("Production Stock Reservation", res.name)
            child_table = psr_doc.get("sb_entries") or []
            print("\n\nchild_table\n\n",child_table)
            updated = False

            for entry in child_table:
                if entry.batch_no != row.batch_no:
                    continue

                # Delivered Qty (source warehouse)
                if row.s_warehouse and entry.warehouse == row.s_warehouse:
                    entry.delivered_qty = (entry.delivered_qty or 0) + (row.qty or 0)
                    entry.actual_delivered_qty = entry.delivered_qty - entry.returned_qty
                    entry.need_to_deliver_qty = entry.qty - entry.actual_delivered_qty
                    updated = True

                # Returned Qty (target warehouse)
                if row.t_warehouse and entry.warehouse == row.t_warehouse:
                    entry.returned_qty = (entry.returned_qty or 0) + (row.qty or 0)
                    entry.actual_delivered_qty = entry.delivered_qty - entry.returned_qty
                    entry.need_to_deliver_qty = entry.qty - entry.actual_delivered_qty
                    updated = True

            if updated:
                psr_doc.save(ignore_permissions=True)                


