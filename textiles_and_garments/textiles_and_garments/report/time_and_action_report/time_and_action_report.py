# time_and_action_report.py
import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart

def get_columns():
    return [
        {"label": "Plan ID", "fieldname": "plan_name", "fieldtype": "Link", "options": "Plans", "width": 120},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 120},
        {"label": "Workflow", "fieldname": "workflow_type", "fieldtype": "Data", "width": 100},
        {"label": "Milestone", "fieldname": "milestone_name", "fieldtype": "Data", "width": 180},
        {"label": "Planned Date", "fieldname": "planned_date", "fieldtype": "Date", "width": 100},
        {"label": "Actual Date", "fieldname": "actual_date", "fieldtype": "Date", "width": 100},
        {"label": "Delay (Days)", "fieldname": "delay_days", "fieldtype": "Int", "width": 90},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Reference Doc", "fieldname": "reference_document_name", "fieldtype": "Dynamic Link", "width": 120},
        {"label": "Progress %", "fieldname": "progress_percentage", "fieldtype": "Percent", "width": 80},
    ]

def get_data(filters):
    filters = filters or {}
    conditions = ["p.docstatus = 1"]
    values = {}

    # Map each filter to its column; user input is only ever passed as a bound value
    for key, column in (
        ("plan_name", "p.name"),
        ("workflow_type", "p.purchase_or_manufacture"),
        ("status", "tam.status"),
        ("item_code", "tam.item_code"),
    ):
        if filters.get(key):
            conditions.append(f"{column} = %({key})s")
            values[key] = filters.get(key)

    where_clause = " AND ".join(conditions)

    return frappe.db.sql(f"""
        SELECT 
            p.name as plan_name,
            tam.item_code,
            p.purchase_or_manufacture as workflow_type,
            tam.milestone_name,
            tam.planned_date,
            tam.actual_date,
            tam.delay_days,
            tam.status,
            tam.reference_document_name,
            p.progress_percentage
        FROM `tabPlans` p
        INNER JOIN `tabTime and Action Milestones` tam ON p.name = tam.parent
        WHERE {where_clause}
        ORDER BY p.name, tam.planned_date
    """, values, as_dict=1)

def get_chart(data):
    if not data:
        return None
        
    status_count = {}
    for row in data:
        status_count[row.status] = status_count.get(row.status, 0) + 1
    
    chart = {
        "data": {
            "labels": list(status_count.keys()),
            "datasets": [{"values": list(status_count.values())}]
        },
        "type": "pie",
        "title": "Milestone Status Distribution"
    }
    
    return chart