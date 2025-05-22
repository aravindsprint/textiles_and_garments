# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


# import frappe
# from frappe import _
# from frappe.query_builder.functions import Sum


# def execute(filters=None):
# 	if not filters:
# 		filters = {}
# 	columns = get_columns(filters)
# 	stock = get_total_stock(filters)

# 	return columns, stock


# def get_columns(filters):
# 	columns = [
# 		_("Item") + ":Link/Item:150",
# 		_("Description") + "::300",
# 		_("Current Qty") + ":Float:100",
# 	]

# 	if filters.get("group_by") == "Warehouse":
# 		columns.insert(0, _("Warehouse") + ":Link/Warehouse:150")
# 	else:
# 		columns.insert(0, _("Company") + ":Link/Company:250")

# 	return columns


# def get_total_stock(filters):
# 	bin = frappe.qb.DocType("Bin")
# 	item = frappe.qb.DocType("Item")
# 	wh = frappe.qb.DocType("Warehouse")

# 	query = (
# 		frappe.qb.from_(bin)
# 		.inner_join(item)
# 		.on(bin.item_code == item.item_code)
# 		.inner_join(wh)
# 		.on(wh.name == bin.warehouse)
# 		.where(bin.actual_qty != 0)
# 	)

# 	if filters.get("group_by") == "Warehouse":
# 		if filters.get("company"):
# 			query = query.where(wh.company == filters.get("company"))

# 		query = query.select(bin.warehouse).groupby(bin.warehouse)
# 	else:
# 		query = query.select(wh.company).groupby(wh.company)

# 	query = query.select(item.item_code, item.description, Sum(bin.actual_qty).as_("actual_qty")).groupby(
# 		item.item_code
# 	)

# 	return query.run()

# import frappe
# from frappe import _
# from frappe.query_builder.functions import Sum


# def execute(filters=None):
# 	if not filters:
# 		filters = {}
# 	columns = get_columns(filters)
# 	stock = get_total_stock(filters)

# 	return columns, stock


# def get_columns(filters):
# 	columns = [
# 		_("Item") + ":Link/Item:150",
# 		_("Description") + "::300",
# 		_("Current Qty") + ":Float:100",
# 		_("WIP Qty") + ":Float:100",  # New column
# 	]

# 	if filters.get("group_by") == "Warehouse":
# 		columns.insert(0, _("Warehouse") + ":Link/Warehouse:150")
# 	else:
# 		columns.insert(0, _("Company") + ":Link/Company:250")

# 	return columns


# def get_total_stock(filters):
# 	bin = frappe.qb.DocType("Bin")
# 	item = frappe.qb.DocType("Item")
# 	wh = frappe.qb.DocType("Warehouse")

# 	query = (
# 		frappe.qb.from_(bin)
# 		.inner_join(item)
# 		.on(bin.item_code == item.item_code)
# 		.inner_join(wh)
# 		.on(wh.name == bin.warehouse)
# 		.where(bin.actual_qty != 0)
# 	)

# 	if filters.get("group_by") == "Warehouse":
# 		if filters.get("company"):
# 			query = query.where(wh.company == filters.get("company"))
# 		query = query.select(bin.warehouse).groupby(bin.warehouse)
# 	else:
# 		query = query.select(wh.company).groupby(wh.company)

# 	query = query.select(
# 		item.item_code,
# 		item.description,
# 		Sum(bin.actual_qty).as_("actual_qty")
# 	).groupby(item.item_code)

# 	result = query.run()

# 	# Add default WIP Qty = 0 to each row
# 	stock_with_wip = [row + (0,) for row in result]  # appends 0 as the WIP Qty

# 	return stock_with_wip

import frappe
from frappe import _
from frappe.query_builder.functions import Sum


def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns(filters)
    actual_stock = get_total_stock(filters)
    wip_qty_map = get_wip_qty_map()

    # Merge WIP qty into actual stock data
    stock_with_wip = []
    for row in actual_stock:
        # Adjust index based on group_by
        item_code = row[1] if filters.get("group_by") == "Warehouse" else row[1]
        wip_qty = wip_qty_map.get(item_code, 0)
        stock_with_wip.append(row + (wip_qty,))

    return columns, stock_with_wip


def get_columns(filters):
    columns = [
        _("Item") + ":Link/Item:150",
        _("Commercial Name") + "::200",
        _("Color") + "::100",
        _("Width") + "::70",
        _("Description") + "::300",
        _("Current Qty") + ":Float:100",
        _("WIP Qty") + ":Float:100",  # New column
    ]

    if filters.get("group_by") == "Warehouse":
        columns.insert(0, _("Warehouse") + ":Link/Warehouse:150")
    elif filters.get("group_by") == "Parent Warehouse":
        columns.insert(0, _("Parent Warehouse") + ":Link/Warehouse:150")    
    else:
        columns.insert(0, _("Company") + ":Link/Company:250")

    return columns




def get_total_stock(filters):
    bin = frappe.qb.DocType("Bin")
    item = frappe.qb.DocType("Item")
    wh = frappe.qb.DocType("Warehouse")

    # Base query
    query = (
        frappe.qb.from_(bin)
        .inner_join(item)
        .on(bin.item_code == item.item_code)
        .inner_join(wh)
        .on(wh.name == bin.warehouse)
        .where(bin.actual_qty != 0)
        .where(wh.is_group == 0)
    )

    # Warehouse filtering condition
    allowed_warehouses = [
        ("like", "JV/%"),
        ("=", "LAYA SAMPLE ROOM - PSS"),
        ("=", "Laya Stock in JV - PSS"),
        ("like", "PT/%"),
    ]

    # allowed_warehouses = [
    #     ("like", "DYE/%"),
    #     ("=", "Stores - PSS")
    # ]

    # Build OR condition for warehouse filters
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

    # Build OR condition for warehouse filters
    parent_warehouse_conditions = None
    for operator, pattern in allowed_parent_warehouses:
        condition = wh.parent_warehouse.like(pattern) if operator == "like" else wh.parent_warehouse == pattern
        parent_warehouse_conditions = condition if parent_warehouse_conditions is None else parent_warehouse_conditions | condition

    query = query.where(parent_warehouse_conditions)

    # Grouping by Warehouse or Company
    if filters.get("group_by") == "Warehouse":
        if filters.get("company"):
            query = query.where(wh.company == filters.get("company"))
        query = query.select(bin.warehouse).groupby(bin.warehouse)
    elif filters.get("group_by") == "Parent Warehouse":
        if filters.get("company"):
            query = query.where(wh.company == filters.get("company"))
        query = query.select(wh.parent_warehouse).groupby(wh.parent_warehouse)	
    else:
        query = query.select(wh.company).groupby(wh.company)

    # Final select
    query = query.select(
        item.item_code,
        item.commercial_name,
        item.color,
        item.width,
        item.description,
        Sum(bin.actual_qty).as_("actual_qty")
    ).groupby(item.item_code)

    return query.run()



def get_wip_qty_map():
    """Returns a dictionary { item_code: total_wip_qty } from Material Request Items where parent status is 'Pending'."""
    wip_qty_map = {}

    results = frappe.db.sql("""
        SELECT 
            mri.item_code,
            SUM(mri.qty) AS wip_qty
        FROM 
            `tabMaterial Request Item` mri
        INNER JOIN 
            `tabMaterial Request` mr ON mr.name = mri.parent
        WHERE 
            mr.status = 'Pending'
            AND mri.qty > 0
        GROUP BY 
            mri.item_code
    """, as_dict=1)

    for row in results:
        wip_qty_map[row.item_code] = row.wip_qty or 0

    return wip_qty_map


