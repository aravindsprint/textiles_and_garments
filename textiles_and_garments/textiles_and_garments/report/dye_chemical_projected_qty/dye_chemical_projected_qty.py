# Copyright (c) 2024, Aravind and contributors
# For license information, please see license.txt

import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


# import frappe
# import datetime
# def execute(filters=None):
#     #frappe.msgprint("<pre>{}</pre>".format(filters))
#     columns = [
#         {'fieldname':'name','label':'ID','fieldtype':'Data'},
#         {'fieldname':'first_name','label':'First Name','fieldtype':'Data'},
#         {'fieldname':'last_name','label':'Last Name','fieldtype':'Data'},
#         {'fieldname':'creation','label':'Creation','fieldtype':'Date'}
#     ]
#     data = frappe.db.get_all('User', ['name','first_name','last_name','creation'])
#     frappe.msgprint("<span style='color:Red;'>Once this popup has served it's purpose, then comment out it's invocation, viz. #frappe.msgprint...</span><br><br>" + "<pre>{}</pre>".format(frappe.as_json(data)))
#     datefilter = datetime.datetime.strptime(filters.date_filter,"%Y-%m-%d").date()
#     today = datetime.datetime.now(tz=None).date()
#     data = [dic for dic in data if dic.creation.date() > datefilter]
#     data = sorted(data, key=lambda k: k['first_name'])
#     chart = {
#         'title':"Script Chart Tutorial : Days since the user's database record was created",
#         'data':{
#             'labels':[str(dic.first_name) + " " + str(dic.last_name) for dic in data],
#             'datasets':[{'values':[(today - dic.creation.date()).days for dic in data]}]
#         },
#         'type':'line',
#         'height':300,
#         'colors':['#F16A61'],
#         'lineOptions':{'hideDots':0, 'dotSize':6, 'regionFill':1}
#     }
#     report_summary = [{"label":"Count","value":len(data),'indicator':'Red' if len(data) < 10 else 'Green'}]
#     return columns, data, None, chart, report_summary


# def execute(filters=None):
# 	#frappe.msgprint("<pre>{}</pre>".format(filters))
# 	columns = [
# 		{'fieldname':'name','label':'Name'},
# 		{'fieldname':'full_name','label':'Full Name'},
# 		{'fieldname':'user_type','label':'User Type'},
# 		{'fieldname':'owner','label':'Owner'},
# 		{'fieldname':'subject','label':'Subject'},
# 		{'fieldname':'status','label':'Status'},
# 		{'fieldname':'creation','label':'Creation'}
# 	]
# 	data = []
# 	parent = frappe.db.sql("SELECT t1.name, t1.full_name, t1.user_type, t2.owner FROM `tabUser` AS t1 JOIN `tabUser Type` AS t2 ON t1.user_type = t2.name", as_dict=1)
# 	#frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(parent)))
# 	for dic_p in parent:
# 		dic_p["indent"] = 0
# 		data.append(dic_p)
# 		#frappe.msgprint(dic_p["name"])
# 		child = frappe.db.sql("SELECT subject, status, creation FROM `tabActivity Log` WHERE user = '" + dic_p["name"] + "'", as_dict=1)
# 		#frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(child)))
# 		for dic_c in child:
# 			dic_c["indent"] = 1
# 			data.append(dic_c)
# 	return columns, data


# def execute(filters=None):
#     # Define the columns for the report
#     columns = [
#         {'fieldname': 'finished_goods', 'label': 'Finished Goods', 'fieldtype': 'Data'},
#         {'fieldname': 'requested_qty', 'label': 'Requested Qty', 'fieldtype': 'Float'},
#         {'fieldname': 'material_request', 'label': 'Material Request', 'fieldtype': 'Link', 'options': 'Material Request'},
#         {'fieldname': 'raw_material', 'label': 'Raw Material', 'fieldtype': 'Data'},
#         {'fieldname': 'projected_raw_material_qty', 'label': 'Projected Raw Material Qty', 'fieldtype': 'Float'}
#     ]

#     # Initialize data list
#     data = []

#     # SQL query to fetch Material Request Items and related Dye Recipe Items
#     parent = frappe.db.sql("""
#         SELECT 
#             mr_item.item_code AS finished_goods,
#             mr_item.qty AS requested_qty,
#             mr_item.parent AS material_request
#         FROM 
#             `tabMaterial Request Item` AS mr_item
#         WHERE 
#             mr_item.parenttype = 'Material Request'
#     """, as_dict=1)

#     # Loop through each parent (finished goods)
#     for dic_p in parent:
#         dic_p["indent"] = 0  # Parent row (no indentation)
#         data.append(dic_p)  # Add parent row to data

#         # Query to fetch corresponding raw materials and UOM for each finished good
#         child = frappe.db.sql("""
#             SELECT 
#                 dr_item.item AS raw_material,
#                 dr_item.dosage AS dosage,
#                 dr_item.uom AS uom
#             FROM 
#                 `tabDye Receipe` AS dr
#             JOIN 
#                 `tabDye Receipe Item` AS dr_item ON dr_item.parent = dr.name
#             WHERE 
#                 dr.item = %(finished_goods)s
#                 AND dr_item.item IS NOT NULL
#         """, {'finished_goods': dic_p["finished_goods"], 'requested_qty': dic_p["requested_qty"]}, as_dict=1)

#         # Add each child (raw material) under the parent with the adjusted projected quantity
#         for dic_c in child:
#             if dic_c["uom"] == "Percentage":
#                 dic_c["projected_raw_material_qty"] = (dic_p["requested_qty"] * dic_c["dosage"]) / 100
#             else:
#                 dic_c["projected_raw_material_qty"] = (dic_p["requested_qty"] * dic_c["dosage"]) / 1000

#             dic_c["indent"] = 1  # Child row (indented)
#             data.append(dic_c)

#     return columns, data


# def execute(filters=None):
#     # Define the columns for the report
#     columns = [
#         {'fieldname': 'work_order', 'label': 'Work Order', 'fieldtype': 'Link', 'options': 'Work Order'},
#         {'fieldname': 'finished_goods', 'label': 'Finished Goods', 'fieldtype': 'Data'},
#         {'fieldname': 'requested_qty', 'label': 'Requested Qty', 'fieldtype': 'Float'},
#         {'fieldname': 'raw_material', 'label': 'Raw Material', 'fieldtype': 'Data'},
#         {'fieldname': 'projected_raw_material_qty', 'label': 'Projected Raw Material Qty', 'fieldtype': 'Float'},
#         {'fieldname': 'stock_qty', 'label': 'Stock Qty', 'fieldtype': 'Float'},
#         {'fieldname': 'required_qty', 'label': 'Required Qty', 'fieldtype': 'Float'}  # New column for required quantity
#     ]

#     # Initialize data list
#     data = []

#     # SQL query to fetch Work Order Items and related Dye Recipe Items
#     parent = frappe.db.sql("""
#         SELECT 
#             wo_item.production_item AS finished_goods,
#             wo_item.qty AS requested_qty,
#             wo_item.name AS work_order
#         FROM 
#             `tabWork Order` AS wo_item
#         WHERE 
#             wo_item.status = 'Not Started'
#     """, as_dict=1)

#     # Loop through each parent (finished goods)
#     for dic_p in parent:
#         # Query to fetch corresponding raw materials, UOM, and dosage for each finished good
#         child = frappe.db.sql("""
#             SELECT 
#                 dr_item.item AS raw_material,
#                 dr_item.dosage AS dosage,
#                 dr_item.uom AS uom
#             FROM 
#                 `tabDye Receipe` AS dr
#             JOIN 
#                 `tabDye Receipe Item` AS dr_item ON dr_item.parent = dr.name
#             WHERE 
#                 dr.item = %(finished_goods)s
#                 AND dr_item.item IS NOT NULL
#         """, {'finished_goods': dic_p["finished_goods"], 'requested_qty': dic_p["requested_qty"]}, as_dict=1)

#         # Add each child (raw material) under the parent with the adjusted projected quantity and stock quantity
#         for dic_c in child:
#             # Include parent values in each child row
#             dic_c["finished_goods"] = dic_p["finished_goods"]
#             dic_c["requested_qty"] = dic_p["requested_qty"]
#             dic_c["work_order"] = dic_p["work_order"]

#             # Calculate projected raw material quantity based on UOM
#             if dic_c["uom"] == "Percentage":
#                 dic_c["projected_raw_material_qty"] = (dic_p["requested_qty"] * dic_c["dosage"]) / 100
#             else:
#                 dic_c["projected_raw_material_qty"] = (dic_p["requested_qty"] * dic_c["dosage"]) / 1000

#             # Query to fetch stock quantity for the raw material in the specified warehouse "Stores - PSS"
#             stock_qty = frappe.db.get_value(
#                 'Bin', 
#                 {'item_code': dic_c["raw_material"], 'warehouse': 'Stores - PSS'}, 
#                 'actual_qty'
#             ) or 0
#             dic_c["stock_qty"] = stock_qty

#             # Calculate required quantity as projected_raw_material_qty - stock_qty
#             dic_c["required_qty"] = dic_c["projected_raw_material_qty"] - dic_c["stock_qty"]

#             data.append(dic_c)  # Append child row with parent values to data

#     return columns, data


def execute(filters=None):
    # Define the columns for the report
    columns = [
        {'fieldname': 'work_order', 'label': 'Work Order', 'fieldtype': 'Link', 'options': 'Work Order'},
        {'fieldname': 'finished_goods', 'label': 'Finished Goods', 'fieldtype': 'Data'},
        {'fieldname': 'requested_qty', 'label': 'Requested Qty', 'fieldtype': 'Float'},
        {'fieldname': 'raw_material', 'label': 'Raw Material', 'fieldtype': 'Data'},
        {'fieldname': 'projected_raw_material_qty', 'label': 'Projected Raw Material Qty', 'fieldtype': 'Float'},
        {'fieldname': 'stock_qty', 'label': 'Stock Qty', 'fieldtype': 'Float'},
        {'fieldname': 'required_qty', 'label': 'Required Qty', 'fieldtype': 'Float'}  # New column for required quantity
    ]

    # Initialize data list
    data = []

    # SQL query to fetch Work Order Items and related Dye Recipe Items
    parent = frappe.db.sql("""
        SELECT 
            wo_item.production_item AS finished_goods,
            wo_item.qty AS requested_qty,
            wo_item.name AS work_order
        FROM 
            `tabWork Order` AS wo_item
        WHERE 
            wo_item.status = 'Not Started'
    """, as_dict=1)

    # Loop through each parent (finished goods)
    for dic_p in parent:
        # Add parent row with an indent level of 0
        dic_p["indent"] = 0
        data.append(dic_p)  # Append parent row to data

        # Query to fetch corresponding raw materials, UOM, and dosage for each finished good
        child = frappe.db.sql("""
            SELECT 
                dr_item.item AS raw_material,
                dr_item.dosage AS dosage,
                dr_item.mlr AS mlr,
                dr_item.uom AS uom
            FROM 
                `tabDye Receipe` AS dr
            JOIN 
                `tabDye Receipe Item` AS dr_item ON dr_item.parent = dr.name
            WHERE 
                dr.item = %(finished_goods)s
                AND dr_item.item IS NOT NULL
        """, {'finished_goods': dic_p["finished_goods"], 'requested_qty': dic_p["requested_qty"]}, as_dict=1)

        # Add each child (raw material) under the parent with the adjusted projected quantity and stock quantity
        for dic_c in child:
            # Include parent values in each child row
            dic_c["finished_goods"] = dic_p["finished_goods"]
            dic_c["requested_qty"] = dic_p["requested_qty"]
            dic_c["work_order"] = dic_p["work_order"]

            # Ensure numeric conversion of dosage, mlr, and requested_qty
            dosage = float(dic_c["dosage"] or 0)  # Default to 0 if None
            mlr = float(dic_c["mlr"] or 0)  # Default to 0 if None
            requested_qty = float(dic_p["requested_qty"] or 0)  # Default to 0 if None

            # Calculate projected raw material quantity based on UOM
            if dic_c["uom"] == "Percentage":
                dic_c["projected_raw_material_qty"] = (requested_qty * dosage) / 100
            else:
                dic_c["projected_raw_material_qty"] = (requested_qty * (dosage / 1000) * mlr)

            # Query to fetch stock quantity for the raw material in the specified warehouse "Stores - PSS"
            stock_qty = frappe.db.get_value(
                'Bin', 
                {'item_code': dic_c["raw_material"], 'warehouse': 'Stores - PSS'}, 
                'actual_qty'
            ) or 0
            dic_c["stock_qty"] = stock_qty

            # Calculate required quantity as projected_raw_material_qty - stock_qty
            dic_c["required_qty"] = dic_c["projected_raw_material_qty"] - dic_c["stock_qty"]

            dic_c["indent"] = 1  # Child row (indented)
            data.append(dic_c)  # Append child row with parent values to data

    return columns, data
