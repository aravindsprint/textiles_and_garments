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
    conditions = ["p.docstatus = 1"]
    
    if filters.get("plan_name"):
        conditions.append(f"p.name = '{filters['plan_name']}'")
    if filters.get("workflow_type"):
        conditions.append(f"p.purchase_or_manufacture = '{filters['workflow_type']}'")
    if filters.get("status"):
        conditions.append(f"tam.status = '{filters['status']}'")
    if filters.get("item_code"):
        conditions.append(f"tam.item_code = '{filters['item_code']}'")
    
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
        INNER JOIN `tabTime And Action Milestones` tam ON p.name = tam.parent
        WHERE {where_clause}
        ORDER BY p.name, tam.planned_date
    """, as_dict=1)

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