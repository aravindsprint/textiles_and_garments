import frappe
from frappe.utils import getdate, add_years, today
from frappe import _

def auto_create_earned_leave_allocations():
    """
    Daily scheduled job to create earned leave allocations
    for employees who completed 1 year of service
    """
    employees = frappe.get_all(
        "Employee",
        filters={
            "status": "Active",
            "date_of_joining": ["is", "set"]
        },
        fields=["name", "employee_name", "date_of_joining"]
    )
    
    created_count = 0
    
    for emp in employees:
        joining_date = getdate(emp.date_of_joining)
        allocation_from_date = add_years(joining_date, 1)
        allocation_to_date = add_years(allocation_from_date, 1)
        current_date = getdate(today())
        
        # Check if employee has completed 1 year and allocation period has started
        if current_date >= allocation_from_date:
            # Check if allocation already exists
            existing = frappe.db.exists(
                "Leave Allocation",
                {
                    "employee": emp.name,
                    "leave_type": "Earned Leave",
                    "from_date": allocation_from_date,
                    "to_date": allocation_to_date,
                    "docstatus": ["!=", 2]
                }
            )
            
            if not existing:
                try:
                    leave_allocation = frappe.get_doc({
                        "doctype": "Leave Allocation",
                        "employee": emp.name,
                        "leave_type": "Earned Leave",
                        "from_date": allocation_from_date,
                        "to_date": allocation_to_date,
                        "new_leaves_allocated": 12,
                        "description": f"Auto-generated after 1 year of service (Joined: {emp.date_of_joining})"
                    })
                    
                    leave_allocation.insert(ignore_permissions=True)
                    leave_allocation.submit()
                    created_count += 1
                    
                    frappe.db.commit()
                    
                except Exception as e:
                    frappe.log_error(
                        f"Failed to create EL allocation for {emp.name}: {str(e)}",
                        "Leave Allocation Error"
                    )
    
    if created_count > 0:
        frappe.logger().info(f"Created {created_count} earned leave allocations")
    
    return created_count