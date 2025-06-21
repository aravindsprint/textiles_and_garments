# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
# from frappe import _
# from frappe.query_builder.functions import Sum

# def execute(filters=None):
#     if not filters:
#         filters = {}
#     columns = get_columns(filters)
#     actual_stock = get_total_stock(filters)
#     indent_qty_map = get_indent_qty_map()
#     grn_qty_map = get_grn_qty_map()
#     wo_qty_map = get_wo_qty_map()

#     stock_with_wip = []
#     for row in actual_stock:
#         if filters.get("group_by") == "Warehouse":
#             warehouse = row[0]
#             item_code = row[1]
#         elif filters.get("group_by") == "Company":
#             warehouse = None
#             item_code = row[1]
#         else:  # For "Parent Warehouse" or no group_by
#             warehouse = None
#             item_code = row[0]

#         reorder_qty = row[-2]
#         reorder_level = row[-1]
#         row_without_reorder = row[:-2]
#         actual_qty = row_without_reorder[-1]

#         # Fallback logic for WIP matching
#         if filters.get("group_by") == "Warehouse":
#             indent_qty = indent_qty_map.get((item_code, warehouse), 0)
#             received_qty = grn_qty_map.get((item_code, warehouse), 0)
#             print("\n\nreceived_qty\n\n",received_qty)
#             wo_produced_qty = wo_qty_map.get((item_code, warehouse), 0)
#             print("\n\nwo_produced_qty\n\n",wo_produced_qty)
#         else:
#             indent_qty = indent_qty_map.get(item_code, 0)
#             received_qty = grn_qty_map.get(item_code, 0)
#             print("\n\nreceived_qty\n\n",received_qty)
#             wo_produced_qty = wo_qty_map.get(item_code, 0)
#             print("\n\nwo_produced_qty\n\n",wo_produced_qty)

#         total_qty = actual_qty + indent_qty
#         wip_qty = indent_qty - received_qty - wo_produced_qty

#         # Remove current actual_qty before reordering and re-append below
#         row_core = row_without_reorder[:-1]  # remove actual_qty

#         stock_with_wip.append(
#             row_core + (actual_qty, indent_qty, total_qty, wip_qty, reorder_level, reorder_qty)
#         )

#     return columns, stock_with_wip


# def get_columns(filters):
#     columns = [
#         _("Item") + ":Link/Item:150",
#         _("Commercial Name") + "::200",
#         _("Color") + "::100",
#         _("Width") + "::70",
#         _("Description") + "::300",
#         _("Current Qty") + ":Float:100",
#         _("Indent Qty") + ":Float:100",
#         _("Total Qty") + ":Float:100",
#         _("WIP Qty") + ":Float:100",
#         _("Reorder Level") + ":Float:120",
#         _("Reorder Qty") + ":Float:120",
#     ]

#     if filters.get("group_by") == "Warehouse":
#         columns.insert(0, _("Warehouse") + ":Link/Warehouse:150")
#     elif filters.get("group_by") == "Company":
#         columns.insert(0, _("Company") + ":Link/Company:150")

#     return columns


# def get_total_stock(filters):
#     bin = frappe.qb.DocType("Bin")
#     item = frappe.qb.DocType("Item")
#     wh = frappe.qb.DocType("Warehouse")
#     rol = frappe.qb.DocType("Item Reorder")

#     query = (
#         frappe.qb.from_(bin)
#         .inner_join(item).on(bin.item_code == item.item_code)
#         .inner_join(wh).on(wh.name == bin.warehouse)
#         .left_join(rol).on((rol.parent == item.item_code) & (rol.warehouse == bin.warehouse))
#         .where(bin.actual_qty != 0)
#         .where(wh.is_group == 0)
#     )

#     # allowed_warehouses = [
#     #     ("like", "JV/%"),
#     #     ("=", "LAYA SAMPLE ROOM - PSS"),
#     #     ("=", "Laya Stock in JV - PSS"),
#     #     ("like", "PT/%"),
#     # ]

#     allowed_warehouses = [
#         ("like", "JV/RFD02 - PSS%")
#     ]

#     # allowed_warehouses = [
#     #     ("like", "DYE/%"),
#     #     ("like", "F%"),
#     #     ("=", "Stores - PSS")
#     # ]

#     warehouse_conditions = None
#     for operator, pattern in allowed_warehouses:
#         condition = wh.name.like(pattern) if operator == "like" else wh.name == pattern
#         warehouse_conditions = condition if warehouse_conditions is None else warehouse_conditions | condition
#     query = query.where(warehouse_conditions)

#     # allowed_parent_warehouses = [
#     #     ("like", "JV%"),
#     #     ("like", "PT/%"),
#     #     ("=", "LAYA - PSS"),
#     # ]

#     allowed_parent_warehouses = [
#         ("like", "JV%")
#     ]
#     # allowed_parent_warehouses = [("like", "ALL%")]

#     parent_warehouse_conditions = None
#     for operator, pattern in allowed_parent_warehouses:
#         condition = wh.parent_warehouse.like(pattern) if operator == "like" else wh.parent_warehouse == pattern
#         parent_warehouse_conditions = condition if parent_warehouse_conditions is None else parent_warehouse_conditions | condition
#     query = query.where(parent_warehouse_conditions)

#     if filters.get("group_by") == "Warehouse":
#         if filters.get("company"):
#             query = query.where(wh.company == filters.get("company"))
#         query = query.select(bin.warehouse).groupby(bin.warehouse)
#     elif filters.get("group_by") == "Parent Warehouse":
#         if filters.get("company"):
#             query = query.where(wh.company == filters.get("company"))
#     else:
#         query = query.select(wh.company).groupby(wh.company)

#     query = query.select(
#         item.item_code,
#         item.commercial_name,
#         item.color,
#         item.width,
#         item.description,
#         Sum(bin.actual_qty).as_("actual_qty"),
#         Sum(rol.warehouse_reorder_qty).as_("reorder_qty"),
#         Sum(rol.warehouse_reorder_level).as_("reorder_level")
#     ).groupby(item.item_code)

#     return query.run()


# def get_indent_qty_map():
#     """Returns a dictionary {(item_code, warehouse) or item_code: total_wip_qty}"""
#     indent_qty_map = {}

#     results = frappe.db.sql("""
#         SELECT 
#             mri.item_code,
#             mri.warehouse,
#             SUM(mri.qty) AS indent_qty
#         FROM 
#             `tabMaterial Request Item` mri
#         INNER JOIN 
#             `tabMaterial Request` mr ON mr.name = mri.parent
#         WHERE 
#             mr.indent_status = 'Open'
#             AND mri.qty > 0
#         GROUP BY 
#             mri.item_code, mri.warehouse
#     """, as_dict=1)

#     for row in results:
#         # Store both full key (item_code, warehouse) and fallback (item_code)
#         indent_qty_map[(row.item_code, row.warehouse)] = row.indent_qty or 0
#         indent_qty_map[row.item_code] = indent_qty_map.get(row.item_code, 0) + (row.indent_qty or 0)

#     return indent_qty_map


# def get_grn_qty_map():
#     """Returns a dictionary {(item_code, warehouse) or item_code: total_wip_qty}"""
#     grn_qty_map = {}

#     results = frappe.db.sql("""
#         SELECT 
#             poi.item_code,
#             poi.warehouse,
#             SUM(poi.received_qty) AS received_qty
#         FROM 
#             `tabPurchase Order Item` poi
#         INNER JOIN 
#             `tabMaterial Request` mr ON mr.name = poi.material_request
#         WHERE 
#             mr.indent_status = 'Open'
#             AND poi.qty > 0
#         GROUP BY 
#             poi.item_code, poi.warehouse
#     """, as_dict=1)

#     print("\n\nget_grn_qty_map results\n\n",get_grn_qty_map)

#     for row in results:
#         # Store both full key (item_code, warehouse) and fallback (item_code)
#         grn_qty_map[(row.item_code, row.warehouse)] = row.received_qty or 0
#         grn_qty_map[row.item_code] = grn_qty_map.get(row.item_code, 0) + (row.received_qty or 0)
#         print("\n\ngrn_qty_map\n\n",grn_qty_map)

#     return grn_qty_map

# def get_wo_qty_map():
#     """Returns a dictionary {(item_code, warehouse) or item_code: total_wip_qty}"""
#     wo_qty_map = {}

#     results = frappe.db.sql("""
#         SELECT 
#             wo.production_item AS item_code,
#             wo.fg_warehouse AS warehouse,
#             SUM(wo.produced_qty) AS produced_qty
#         FROM 
#             `tabWork Order` wo
#         INNER JOIN 
#             `tabMaterial Request` mr ON mr.name = wo.material_request
#         WHERE 
#             mr.indent_status = 'Open'
#             AND wo.qty > 0
#         GROUP BY 
#             wo.production_item, wo.fg_warehouse
#     """, as_dict=1)

#     print("\n\nget_wo_qty_map results\n\n",get_wo_qty_map)

#     for row in results:
#         # Store both full key (item_code, warehouse) and fallback (item_code)
#         wo_qty_map[(row.item_code, row.warehouse)] = row.produced_qty or 0
#         wo_qty_map[row.item_code] = wo_qty_map.get(row.item_code, 0) + (row.produced_qty or 0)
#         print("\n\ngrn_qty_map\n\n",wo_qty_map)

#     return wo_qty_map    




import frappe
from frappe import _
from frappe.query_builder.functions import Sum

def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns(filters)
    actual_stock = get_total_stock(filters)
    indent_qty_map = get_indent_qty_map()
    grn_qty_map = get_grn_qty_map()
    wo_qty_map = get_wo_qty_map()

    stock_with_wip = []
    for row in actual_stock:
        if filters.get("group_by") == "Warehouse":
            warehouse = row[0]
            item_code = row[1]
        elif filters.get("group_by") == "Company":
            warehouse = None
            item_code = row[1]
        else:
            warehouse = None
            item_code = row[0]

        reorder_qty = row[-2] or 0
        reorder_level = row[-1] or 0
        row_without_reorder = row[:-2]
        actual_qty = row_without_reorder[-1]

        if filters.get("group_by") == "Warehouse":
            indent_qty = indent_qty_map.get((item_code, warehouse), 0)
            received_qty = grn_qty_map.get((item_code, warehouse), 0)
            wo_produced_qty = wo_qty_map.get((item_code, warehouse), 0)
        else:
            indent_qty = indent_qty_map.get(item_code, 0)
            received_qty = grn_qty_map.get(item_code, 0)
            wo_produced_qty = wo_qty_map.get(item_code, 0)

        total_qty = actual_qty + indent_qty
        wip_qty = indent_qty - received_qty - wo_produced_qty
        to_be_plan_qty = reorder_qty if actual_qty < reorder_level else 0

        row_core = row_without_reorder[:-1]  # remove actual_qty

        stock_with_wip.append(
            row_core + (actual_qty, indent_qty, total_qty, wip_qty, reorder_level, reorder_qty, to_be_plan_qty)
        )

    return columns, stock_with_wip


def get_columns(filters):
    columns = [
        _("Item") + ":Link/Item:150",
        _("Commercial Name") + "::200",
        _("Color") + "::100",
        _("Width") + "::70",
        _("Description") + "::300",
        _("Current Qty") + ":Float:100",
        _("Indent Qty") + ":Float:100",
        _("Total Qty") + ":Float:100",
        _("WIP Qty") + ":Float:100",
        _("Reorder Level") + ":Float:120",
        _("Reorder Qty") + ":Float:120",
        _("To Be Plan Qty") + ":Float:120",
    ]

    if filters.get("group_by") == "Warehouse":
        columns.insert(0, _("Warehouse") + ":Link/Warehouse:150")
    elif filters.get("group_by") == "Company":
        columns.insert(0, _("Company") + ":Link/Company:150")

    return columns


def get_total_stock(filters):
    bin = frappe.qb.DocType("Bin")
    item = frappe.qb.DocType("Item")
    wh = frappe.qb.DocType("Warehouse")
    rol = frappe.qb.DocType("Item Reorder")

    query = (
        frappe.qb.from_(bin)
        .inner_join(item).on(bin.item_code == item.item_code)
        .inner_join(wh).on(wh.name == bin.warehouse)
        .left_join(rol).on((rol.parent == item.item_code) & (rol.warehouse == bin.warehouse))
        .where(bin.actual_qty != 0)
        .where(wh.is_group == 0)
    )

    allowed_warehouses = [
        ("like", "JV/%"),
        ("=", "LAYA SAMPLE ROOM - PSS"),
        ("=", "Laya Stock in JV - PSS"),
        ("like", "PT/%"),
    ]

    # allowed_warehouses = [
    #     ("like", "JV/RFD02 - PSS%")
    # ]

    # allowed_warehouses = [
    #     ("like", "DYE/%"),
    #     ("like", "F%"),
    #     ("=", "Stores - PSS")
    # ]

    warehouse_conditions = None
    for operator, pattern in allowed_warehouses:
        condition = wh.name.like(pattern) if operator == "like" else wh.name == pattern
        warehouse_conditions = condition if warehouse_conditions is None else warehouse_conditions | condition
    query = query.where(warehouse_conditions)

    
    allowed_parent_warehouses = [
        ("like", "JV%"),
        ("like", "PT/%"),
        ("=", "LAYA - PSS"),
    ]

    # allowed_parent_warehouses = [
    #     ("like", "JV%")
    # ]

    # allowed_parent_warehouses = [("like", "ALL%")]

    parent_warehouse_conditions = None
    for operator, pattern in allowed_parent_warehouses:
        condition = wh.parent_warehouse.like(pattern) if operator == "like" else wh.parent_warehouse == pattern
        parent_warehouse_conditions = condition if parent_warehouse_conditions is None else parent_warehouse_conditions | condition
    query = query.where(parent_warehouse_conditions)

    if filters.get("group_by") == "Warehouse":
        if filters.get("company"):
            query = query.where(wh.company == filters.get("company"))
        query = query.select(bin.warehouse).groupby(bin.warehouse)
    elif filters.get("group_by") == "Parent Warehouse":
        if filters.get("company"):
            query = query.where(wh.company == filters.get("company"))
    else:
        query = query.select(wh.company).groupby(wh.company)

    query = query.select(
        item.item_code,
        item.commercial_name,
        item.color,
        item.width,
        item.description,
        Sum(bin.actual_qty).as_("actual_qty"),
        Sum(rol.warehouse_reorder_qty).as_("reorder_qty"),
        Sum(rol.warehouse_reorder_level).as_("reorder_level")
    ).groupby(item.item_code)

    return query.run()


def get_indent_qty_map():
    indent_qty_map = {}

    results = frappe.db.sql("""
        SELECT 
            mri.item_code,
            mri.warehouse,
            SUM(mri.qty) AS indent_qty
        FROM 
            `tabMaterial Request Item` mri
        INNER JOIN 
            `tabMaterial Request` mr ON mr.name = mri.parent
        WHERE 
            mr.indent_status = 'Open'
            AND mri.qty > 0
        GROUP BY 
            mri.item_code, mri.warehouse
    """, as_dict=1)

    for row in results:
        indent_qty_map[(row.item_code, row.warehouse)] = row.indent_qty or 0
        indent_qty_map[row.item_code] = indent_qty_map.get(row.item_code, 0) + (row.indent_qty or 0)

    return indent_qty_map


def get_grn_qty_map():
    grn_qty_map = {}

    results = frappe.db.sql("""
        SELECT 
            poi.item_code,
            poi.warehouse,
            SUM(poi.received_qty) AS received_qty
        FROM 
            `tabPurchase Order Item` poi
        INNER JOIN 
            `tabMaterial Request` mr ON mr.name = poi.material_request
        WHERE 
            mr.indent_status = 'Open'
            AND poi.qty > 0
        GROUP BY 
            poi.item_code, poi.warehouse
    """, as_dict=1)

    for row in results:
        grn_qty_map[(row.item_code, row.warehouse)] = row.received_qty or 0
        grn_qty_map[row.item_code] = grn_qty_map.get(row.item_code, 0) + (row.received_qty or 0)

    return grn_qty_map


def get_wo_qty_map():
    wo_qty_map = {}

    results = frappe.db.sql("""
        SELECT 
            wo.production_item AS item_code,
            wo.fg_warehouse AS warehouse,
            SUM(wo.produced_qty) AS produced_qty
        FROM 
            `tabWork Order` wo
        INNER JOIN 
            `tabMaterial Request` mr ON mr.name = wo.material_request
        WHERE 
            mr.indent_status = 'Open'
            AND wo.qty > 0
        GROUP BY 
            wo.production_item, wo.fg_warehouse
    """, as_dict=1)

    for row in results:
        wo_qty_map[(row.item_code, row.warehouse)] = row.produced_qty or 0
        wo_qty_map[row.item_code] = wo_qty_map.get(row.item_code, 0) + (row.produced_qty or 0)

    return wo_qty_map


