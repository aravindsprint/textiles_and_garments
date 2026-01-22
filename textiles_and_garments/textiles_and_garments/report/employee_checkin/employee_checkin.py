# Copyright (c) 2026, Aravind and contributors
# For license information, please see license.txt

# employee_first_checkin.py

import frappe
from frappe import _
from frappe.utils import getdate, today

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "employee",
            "label": _("Employee ID"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": 120
        },
        {
            "fieldname": "employee_name",
            "label": _("Employee Name"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "width": 150
        },
        {
            "fieldname": "designation",
            "label": _("Designation"),
            "fieldtype": "Data",
            "width": 130
        },
        {
            "fieldname": "checkin_time",
            "label": _("Check-in Time"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "shift",
            "label": _("Shift"),
            "fieldtype": "Link",
            "options": "Shift Type",
            "width": 150
        },
        {
            "fieldname": "shift_start",
            "label": _("Shift Start Time"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "shift_end",
            "label": _("Shift End Time"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "time_difference",
            "label": _("Early/Late (Minutes)"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        }
    ]

def get_data(filters):
    """
    Fetch first check-in for each employee on a daily basis
    """
    conditions = get_conditions(filters)
    
    # Get first check-in per employee per day
    data = frappe.db.sql(f"""
        SELECT 
            ec.employee,
            ec.employee_name,
            emp.department,
            emp.designation,
            ec.time as checkin_time,
            ec.shift,
            ec.shift_start,
            ec.shift_end,
            TIMESTAMPDIFF(MINUTE, ec.shift_start, ec.time) as time_difference,
            CASE 
                WHEN TIMESTAMPDIFF(MINUTE, ec.shift_start, ec.time) <= 0 THEN 'On Time'
                WHEN TIMESTAMPDIFF(MINUTE, ec.shift_start, ec.time) <= 15 THEN 'Grace Period'
                ELSE 'Late'
            END as status
        FROM (
            SELECT 
                employee,
                employee_name,
                shift,
                MIN(time) as time,
                DATE(time) as checkin_date,
                shift_start,
                shift_end
            FROM 
                `tabEmployee Checkin`
            WHERE 
                1=1
                {conditions}
            GROUP BY 
                employee, DATE(time)
        ) ec
        LEFT JOIN 
            `tabEmployee` emp ON emp.name = ec.employee
        ORDER BY 
            ec.checkin_date DESC, ec.time ASC
    """, filters, as_dict=1)
    
    return data

def get_conditions(filters):
    """Build additional filter conditions"""
    conditions = ""
    
    if filters.get("from_date"):
        conditions += " AND DATE(time) >= %(from_date)s"
    else:
        # Default to today if no date filter
        conditions += f" AND DATE(time) = '{today()}'"
    
    if filters.get("to_date"):
        conditions += " AND DATE(time) <= %(to_date)s"
    
    if filters.get("employee"):
        conditions += " AND employee = %(employee)s"
    
    if filters.get("department"):
        conditions += " AND employee IN (SELECT name FROM `tabEmployee` WHERE department = %(department)s)"
    
    if filters.get("shift"):
        conditions += " AND shift = %(shift)s"
    
    if filters.get("company"):
        conditions += " AND employee IN (SELECT name FROM `tabEmployee` WHERE company = %(company)s)"
    
    return conditions

    
