# Copyright (c) 2026, Aravind and contributors
# For license information, please see license.txt

# employee_first_checkin.py

import frappe
from frappe import _
from frappe.utils import today, get_datetime, add_to_date

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
            "width": 150
        },
        {
            "fieldname": "shift",
            "label": _("Shift"),
            "fieldtype": "Link",
            "options": "Shift Type",
            "width": 120
        },
        {
            "fieldname": "checkin_time",
            "label": _("Check-in Time"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "shift_start",
            "label": _("Shift Start"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "shift_end",
            "label": _("Shift End"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "time_difference",
            "label": _("Early/Late (Min)"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "company",
            "label": _("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "width": 150
        }
    ]

def get_data(filters):
    """
    Fetch first check-in for each employee on a daily basis with shift information
    """
    conditions = get_conditions(filters)
    
    # Get first checkin data with employee details
    data = frappe.db.sql(f"""
        SELECT 
            ec.employee as employee,
            ec.employee_name as employee_name,
            emp.department as department,
            emp.designation as designation,
            emp.default_shift as shift,
            MIN(ec.time) as checkin_time,
            DATE(MIN(ec.time)) as checkin_date,
            emp.company as company
        FROM 
            `tabEmployee Checkin` ec
        INNER JOIN 
            `tabEmployee` emp ON emp.name = ec.employee
        WHERE 
            1=1
            {conditions}
        GROUP BY 
            ec.employee, 
            DATE(ec.time)
        ORDER BY 
            DATE(MIN(ec.time)) DESC,
            MIN(ec.time) ASC
    """, filters, as_dict=1)
    
    # Process each record to add shift times and calculate status
    result = []
    for row in data:
        shift_start = None
        shift_end = None
        time_difference = None
        status = "No Shift"
        
        # Get shift type details if shift exists
        if row.get('shift'):
            shift_type = frappe.db.get_value('Shift Type', row['shift'], 
                ['start_time', 'end_time'], as_dict=1)
            
            if shift_type and shift_type.start_time:
                # Combine date with shift times
                checkin_date = row['checkin_date']
                shift_start = get_datetime(f"{checkin_date} {shift_type.start_time}")
                
                if shift_type.end_time:
                    # Check if end time is next day
                    shift_end = get_datetime(f"{checkin_date} {shift_type.end_time}")
                    if shift_end < shift_start:
                        shift_end = add_to_date(shift_end, days=1)
                
                # Calculate time difference in minutes
                checkin_datetime = get_datetime(row['checkin_time'])
                time_difference = int((checkin_datetime - shift_start).total_seconds() / 60)
                
                # Determine status
                if time_difference <= 0:
                    status = "On Time"
                elif time_difference <= 15:
                    status = "Grace Period"
                else:
                    status = "Late"
        
        result.append({
            'employee': row['employee'],
            'employee_name': row['employee_name'],
            'department': row['department'],
            'designation': row['designation'],
            'shift': row['shift'],
            'checkin_time': row['checkin_time'],
            'shift_start': shift_start,
            'shift_end': shift_end,
            'time_difference': time_difference,
            'status': status,
            'company': row['company']
        })
    
    return result

def get_conditions(filters):
    """Build additional filter conditions"""
    conditions = ""
    
    if filters.get("from_date"):
        conditions += " AND DATE(ec.time) >= %(from_date)s"
    else:
        # Default to today if no date filter
        conditions += f" AND DATE(ec.time) = '{today()}'"
    
    if filters.get("to_date"):
        conditions += " AND DATE(ec.time) <= %(to_date)s"
    
    if filters.get("employee"):
        conditions += " AND ec.employee = %(employee)s"
    
    if filters.get("department"):
        conditions += " AND emp.department = %(department)s"
    
    if filters.get("shift"):
        conditions += " AND emp.default_shift = %(shift)s"
    
    if filters.get("company"):
        conditions += " AND emp.company = %(company)s"
    
    return conditions