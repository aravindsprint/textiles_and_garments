import frappe
from frappe.utils import getdate, add_years, today
from frappe import _


def auto_create_earned_leave_allocations():
    """
    Daily scheduled job to create earned leave allocations
    for employees on their yearly anniversary date.
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
    current_date = getdate(today())

    for emp in employees:
        joining_date = getdate(emp.date_of_joining)

        # ✅ Employee must have completed at least 1 year of service
        one_year_completion = add_years(joining_date, 1)
        if current_date < one_year_completion:
            continue

        # ✅ Build this year's anniversary date (same day & month, current year)
        try:
            allocation_from_date = joining_date.replace(year=current_date.year)
        except ValueError:
            # Edge case: Feb 29 joining date on non-leap year → use Feb 28
            allocation_from_date = joining_date.replace(year=current_date.year, day=28)

        # ✅ allocation_to = same day & month, next year
        try:
            allocation_to_date = joining_date.replace(year=current_date.year + 1)
        except ValueError:
            allocation_to_date = joining_date.replace(year=current_date.year + 1, day=28)

        # ✅ Only create on or after this year's anniversary date
        if current_date < allocation_from_date:
            continue

        # ✅ FIX 1: Check for ANY allocation whose from_date falls in this period
        existing_by_from = frappe.db.exists(
            "Leave Allocation",
            {
                "employee": emp.name,
                "leave_type": "Earned Leave",
                "from_date": ["between", [allocation_from_date, allocation_to_date]],
                "docstatus": ["!=", 2]
            }
        )

        # ✅ FIX 2: Also check if any allocation's to_date overlaps this period
        existing_by_to = frappe.db.exists(
            "Leave Allocation",
            {
                "employee": emp.name,
                "leave_type": "Earned Leave",
                "to_date": ["between", [allocation_from_date, allocation_to_date]],
                "docstatus": ["!=", 2]
            }
        )

        if existing_by_from or existing_by_to:
            frappe.logger().info(
                f"Skipping {emp.name} ({emp.employee_name}): "
                f"Allocation already exists for period "
                f"{allocation_from_date} to {allocation_to_date}"
            )
            continue

        try:
            leave_allocation = frappe.get_doc({
                "doctype": "Leave Allocation",
                "employee": emp.name,
                "leave_type": "Earned Leave",
                "from_date": allocation_from_date,
                "to_date": allocation_to_date,
                "new_leaves_allocated": 12,
                # ✅ FIX 3: Explicitly disable carry-forward to prevent
                # ERPNext from modifying previous allocation documents
                "carry_forward": 0,
                "description": (
                    f"Auto-generated annual allocation "
                    f"(Joined: {emp.date_of_joining}, "
                    f"Period: {allocation_from_date} to {allocation_to_date})"
                )
            })

            # ✅ FIX 4: Set flag on doc instead of passing inside insert()
            leave_allocation.flags.ignore_permissions = True
            leave_allocation.insert()

            # ✅ FIX 5: Commit after insert, before submit — isolates failures
            frappe.db.commit()

            leave_allocation.submit()
            frappe.db.commit()

            created_count += 1
            frappe.logger().info(
                f"Created EL allocation for {emp.name} ({emp.employee_name}): "
                f"{allocation_from_date} to {allocation_to_date}"
            )

        except Exception as e:
            frappe.db.rollback()
            frappe.log_error(
                message=frappe.get_traceback(),
                title=f"EL Allocation Failed: {emp.name} - {str(e)}"
            )

    if created_count > 0:
        frappe.logger().info(
            f"[auto_create_earned_leave_allocations] "
            f"Successfully created {created_count} earned leave allocation(s)."
        )
    else:
        frappe.logger().info(
            "[auto_create_earned_leave_allocations] "
            "No new allocations created. All employees are up to date."
        )

    return created_count