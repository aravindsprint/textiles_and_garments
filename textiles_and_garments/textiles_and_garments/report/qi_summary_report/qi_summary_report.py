from collections import defaultdict
import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today

def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    columns = get_columns(filters)
    return columns, data


def get_columns(filters):
    columns = []

    columns.extend(
        [
            {
                "label": _("Date"),
                "fieldname": "posting_date",
                "fieldtype": "Date",
                "width": 150,
            },
            {
                "label": _("QI Report Details"),
                "fieldname": "qi_report_details",
                "fieldtype": "Link",
                "options": "QI Report Details",
                "width": 150,
            },
            {
                "label": _("Item Code"),
                "fieldname": "item_code",
                "fieldtype": "Link",
                "options": "Item",
                "width": 200,
            },
            {
                "label": _("Batch No"),
                "fieldname": "batch_no",
                "fieldtype": "Link",
                "options": "Batch",
                "width": 200,
            },
            {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 90,
            },
            {
                "label": _("UOM"),
                "fieldname": "stock_uom",
                "fieldtype": "Data",
                "width": 50
            },
            {
                "label": _("Roll No"),
                "fieldname": "roll_no",
                "fieldtype": "Data",
                "width": 50
            },
            {
                "label": _("Vertical Line"),
                "fieldname": "vertical_line",
                "fieldtype": "Data",
                "width": 50
            },
            {
                "label": _("Rope Mark"),
                "fieldname": "rope_mark",
                "fieldtype": "Data",
                "width": 50
            },
            # {
            #     "label": _("Crow Feet"),
            #     "fieldname": "crow_feet",
            #     "fieldtype": "Data",
            #     "width": 50
            # },
            {
                "label": _("Crow Feet"),
                "fieldname": "crow_feet1",
                "fieldtype": "Data",
                "width": 50
            },
            # {
            #     "label": _("Patta Problem"),
            #     "fieldname": "patta_problem",
            #     "fieldtype": "Data",
            #     "width": 50
            # },
            {
                "label": _("Patta Problem"),
                "fieldname": "patta_problem1",
                "fieldtype": "Data",
                "width": 50
            },
            {
                "label": _("Status"),
                "fieldname": "status",
                "fieldtype": "Data",
                "width": 50,
            }
        ]
    )

    return columns


def get_data(filters):
    data = []
    sales_data = get_sales_data_from_stock_entry(filters)
    data.extend(sales_data)
    return data


def get_sales_data_from_stock_entry(filters):
    # Base query to fetch data from Sales Invoice and Sales Invoice Item
    query = """
        SELECT 
            qi_report_details_item.item_code AS item_code,
            si.weight AS work_order,
            si.vertical_line AS vertical_line,
            si.rope_mark AS rope_mark,
            si.crow_feet AS crow_feet,
            roll_details.roll_no AS roll_no,
            roll_details.crow_feet AS crow_feet1,
            si.patta_problem AS patta_problem,
            roll_details.patta_problem AS patta_problem1,
            si.parent AS qi_report_details,
            qi_report_details_item.batch_no AS batch_no,
            roll_details.roll_weight AS qty,
            qi_report_details_item.stock_uom AS stock_uom,
            qi_report_details_item.date AS posting_date,
            qi_report_details_item.docstatus AS status
        FROM 
            `tabQI Report Details` AS qi_report_details_item
        LEFT JOIN 
            `tabQI Summary` AS si
        ON 
            qi_report_details_item.name = si.parent
        LEFT JOIN 
            `tabRoll Details` AS roll_details
        ON 
            qi_report_details_item.name = roll_details.parent      
        WHERE 
            qi_report_details_item.docstatus = 1
    """

    

    
    # Dynamically append additional filter conditions
    conditions = []
    
    if filters.get("item_code"):
        conditions.append("sales_invoice_item.item_code = %(item_code)s")
    
    if filters.get("batch_no"):
        conditions.append("sales_invoice_item.batch_no = %(batch_no)s")
    
    if filters.get("work_order"):
        conditions.append("si.custom_work_order = %(work_order)s")
    
    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
    
    if filters.get("status"):
        conditions.append("si.status = %(status)s")
    
    # If conditions were added, append them to the query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Define filter values to pass as parameters
    filter_values = {
        "item_code_pattern": '%/%',  # Passing the pattern as a parameter
        "item_code": filters.get("item_code"),
        "batch_no": filters.get("batch_no"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "status": filters.get("status")
    }
    
    # Execute the query with filters
    return frappe.db.sql(query, filter_values, as_dict=1)