# Copyright (c) 2026, Aravind and contributors
# For license information, please see license.txt

# employee_first_checkin.py

import frappe
from frappe import _
from frappe.utils import getdate, today, get_datetime

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
            "width": 200
        },
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "width": 180
        },
        {
            "fieldname": "designation",
            "label": _("Designation"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "checkin_time",
            "label": _("Check-in Time"),
            "fieldtype": "Datetime",
            "width": 160
        },
        {
            "fieldname": "shift",
            "label": _("Shift"),
            "fieldtype": "Link",
            "options": "Shift Type",
            "width": 180
        },
        {
            "fieldname": "shift_start",
            "label": _("Shift Start Time"),
            "fieldtype": "Datetime",
            "width": 160
        },
        {
            "fieldname": "shift_end",
            "label": _("Shift End Time"),
            "fieldtype": "Datetime",
            "width": 160
        },
        {
            "fieldname": "time_difference",
            "label": _("Early/Late (Minutes)"),
            "fieldtype": "Int",
            "width": 130
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
            ec.department,
            ec.designation,
            ec.checkin_time,
            ec.shift,
            ec.shift_start,
            ec.shift_end,
            ec.time_difference,
            ec.status
        FROM (
            SELECT 
                checkin.employee as employee,
                checkin.employee_name as employee_name,
                emp.department as department,
                emp.designation as designation,
                MIN(checkin.time) as checkin_time,
                checkin.shift as shift,
                checkin.shift_start as shift_start,
                checkin.shift_end as shift_end,
                TIMESTAMPDIFF(MINUTE, checkin.shift_start, MIN(checkin.time)) as time_difference,
                CASE 
                    WHEN TIMESTAMPDIFF(MINUTE, checkin.shift_start, MIN(checkin.time)) <= 0 THEN 'On Time'
                    WHEN TIMESTAMPDIFF(MINUTE, checkin.shift_start, MIN(checkin.time)) <= 15 THEN 'Grace Period'
                    ELSE 'Late'
                END as status,
                DATE(checkin.time) as checkin_date
            FROM 
                `tabEmployee Checkin` checkin
            LEFT JOIN 
                `tabEmployee` emp ON emp.name = checkin.employee
            WHERE 
                1=1
                {conditions}
            GROUP BY 
                checkin.employee, DATE(checkin.time), checkin.shift, checkin.shift_start, 
                checkin.shift_end, emp.department, emp.designation, checkin.employee_name
        ) ec
        ORDER BY 
            ec.checkin_date DESC, ec.checkin_time ASC
    """, filters, as_dict=1)
    
    return data

def get_conditions(filters):
    """Build additional filter conditions"""
    conditions = ""
    
    if filters.get("from_date"):
        conditions += " AND DATE(checkin.time) >= %(from_date)s"
    else:
        # Default to today if no date filter
        conditions += f" AND DATE(checkin.time) = '{today()}'"
    
    if filters.get("to_date"):
        conditions += " AND DATE(checkin.time) <= %(to_date)s"
    
    if filters.get("employee"):
        conditions += " AND checkin.employee = %(employee)s"
    
    if filters.get("department"):
        conditions += " AND emp.department = %(department)s"
    
    if filters.get("shift"):
        conditions += " AND checkin.shift = %(shift)s"
    
    if filters.get("company"):
        conditions += " AND emp.company = %(company)s"
    
    return conditions