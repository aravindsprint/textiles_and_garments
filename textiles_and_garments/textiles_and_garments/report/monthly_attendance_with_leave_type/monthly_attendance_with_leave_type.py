# Copyright (c) 2026, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, cstr, getdate, get_first_day, get_last_day
from calendar import monthrange
from datetime import timedelta


def execute(filters=None):
    if not filters:
        filters = {}
    validate_filters(filters)
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data, filters)
    return columns, data, None, chart


def validate_filters(filters):
    if not filters.get("month") or not filters.get("year"):
        frappe.throw(_("Month and Year are mandatory"))


def get_columns(filters):
    columns = [
        {
            "label":     _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options":   "Employee",
            "width":     110
        },
        {
            "label":     _("Employee Name"),
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width":     150
        },
        {
            "label":     _("Department"),
            "fieldname": "department",
            "fieldtype": "Link",
            "options":   "Department",
            "width":     120
        },
        {
            "label":     _("Shift"),
            "fieldname": "shift",
            "fieldtype": "Data",
            "width":     80
        },
    ]

    month    = cint(filters.get("month"))
    year     = cint(filters.get("year"))
    num_days = monthrange(year, month)[1]

    for day in range(1, num_days + 1):
        columns.append({
            "label":     cstr(day),
            "fieldname": "day_" + cstr(day),
            "fieldtype": "Data",
            "width":     45,
        })

    columns += [
        {"label": _("Total Present"), "fieldname": "total_present", "fieldtype": "Float", "width": 100},
        {"label": _("Total Leave"),   "fieldname": "total_leave",   "fieldtype": "Float", "width": 90},
        {"label": _("Total Absent"),  "fieldname": "total_absent",  "fieldtype": "Float", "width": 90},
        {"label": _("Total WFH"),     "fieldname": "total_wfh",     "fieldtype": "Float", "width": 90},
    ]

    return columns


def get_data(filters):
    month     = cint(filters.get("month"))
    year      = cint(filters.get("year"))
    from_date = get_first_day(str(year) + "-" + str(month).zfill(2) + "-01")
    to_date   = get_last_day(str(year) + "-" + str(month).zfill(2) + "-01")

    att_conditions = build_conditions(filters, table="att")
    leave_map      = build_leave_map(from_date, to_date, filters)

    attendance_list = frappe.db.sql("""
        SELECT
            att.employee,
            att.employee_name,
            att.department,
            att.shift,
            att.attendance_date,
            att.status
        FROM `tabAttendance` att
        WHERE
            att.docstatus = 1
            AND att.attendance_date BETWEEN %(from_date)s AND %(to_date)s
            {conditions}
        ORDER BY att.employee, att.attendance_date
    """.format(conditions=att_conditions), {
        "from_date":  from_date,
        "to_date":    to_date,
        "employee":   filters.get("employee") or "",
        "department": filters.get("department") or "",
        "company":    filters.get("company") or "",
    }, as_dict=True)

    emp_data = {}

    for att in attendance_list:
        emp = att.employee

        if emp not in emp_data:
            emp_data[emp] = {
                "employee":      emp,
                "employee_name": att.employee_name,
                "department":    att.department,
                "shift":         att.shift or "",
                "total_present": 0.0,
                "total_leave":   0.0,
                "total_absent":  0.0,
                "total_wfh":     0.0,
            }

        day    = getdate(att.attendance_date).day
        key    = "day_" + cstr(day)
        status = att.status

        if status == "Present":
            emp_data[emp][key] = "P"
            emp_data[emp]["total_present"] += 1

        elif status == "Absent":
            emp_data[emp][key] = "A"
            emp_data[emp]["total_absent"] += 1

        elif status == "Half Day":
            emp_data[emp][key] = "HD/P"
            emp_data[emp]["total_present"] += 0.5

        elif status == "Work From Home":
            emp_data[emp][key] = "WFH"
            emp_data[emp]["total_wfh"]     += 1
            emp_data[emp]["total_present"] += 1

        elif status == "On Leave":
            abbr = get_leave_abbr_for_day(emp, att.attendance_date, leave_map)
            emp_data[emp][key] = abbr
            emp_data[emp]["total_leave"] += 1

    return list(emp_data.values())


def build_leave_map(from_date, to_date, filters):
    extra = ""
    if filters.get("employee"):
        extra += " AND la.employee = %(employee)s"
    if filters.get("company"):
        extra += " AND la.company = %(company)s"

    leave_apps = frappe.db.sql("""
        SELECT
            la.employee,
            la.from_date,
            la.to_date,
            la.leave_type
        FROM `tabLeave Application` la
        WHERE
            la.docstatus = 1
            AND la.status = 'Approved'
            AND (
                la.from_date BETWEEN %(from_date)s AND %(to_date)s
                OR la.to_date   BETWEEN %(from_date)s AND %(to_date)s
                OR (la.from_date <= %(from_date)s AND la.to_date >= %(to_date)s)
            )
            {extra}
    """.format(extra=extra), {
        "from_date": from_date,
        "to_date":   to_date,
        "employee":  filters.get("employee") or "",
        "company":   filters.get("company") or "",
    }, as_dict=True)

    leave_map = {}

    for la in leave_apps:
        emp  = la.employee
        abbr = get_abbr(la.leave_type)

        if emp not in leave_map:
            leave_map[emp] = {}

        current = getdate(la.from_date)
        end     = getdate(la.to_date)

        while current <= end:
            leave_map[emp][cstr(current)] = abbr
            current += timedelta(days=1)

    return leave_map


def get_leave_abbr_for_day(employee, date, leave_map):
    date_str = cstr(getdate(date))
    return leave_map.get(employee, {}).get(date_str, "L")


def get_abbr(leave_type):
    abbr_map = {
        "Casual Leave":      "CL",
        "Earned Leave":      "EL",
        "Sick Leave":        "SL",
        "Privilege Leave":   "PL",
        "Annual Leave":      "AL",
        "Maternity Leave":   "ML",
        "Paternity Leave":   "PatL",
        "Compensatory Off":  "CO",
        "Leave Without Pay": "LWP",
        "Bereavement Leave": "BL",
    }
    if leave_type in abbr_map:
        return abbr_map[leave_type]
    # Auto-generate abbreviation from leave type name
    return "".join(w[0].upper() for w in leave_type.split()) or "L"


def build_conditions(filters, table=""):
    """
    ✅ FIX: Added 'All Departments' guard so passing that
    default value doesn't create a bad SQL condition.
    """
    prefix = table + "." if table else ""
    conds  = ""

    if filters.get("employee"):
        conds += " AND " + prefix + "employee = %(employee)s"

    # ✅ KEY FIX: skip if value is blank OR the UI default "All Departments"
    if filters.get("department") and filters.get("department") != "All Departments":
        conds += " AND " + prefix + "department = %(department)s"

    if filters.get("company"):
        conds += " AND " + prefix + "company = %(company)s"

    return conds


def get_chart(data, filters):
    month    = cint(filters.get("month"))
    year     = cint(filters.get("year"))
    num_days = monthrange(year, month)[1]

    daily_present = [0] * num_days
    daily_absent  = [0] * num_days
    daily_leave   = [0] * num_days

    for row in data:
        for day in range(1, num_days + 1):
            val = row.get("day_" + cstr(day), "")
            if val in ("P", "WFH", "HD/P"):
                daily_present[day - 1] += 1
            elif val == "A":
                daily_absent[day - 1] += 1
            elif val and val not in ("P", "A", "HD/P", "WFH"):
                daily_leave[day - 1] += 1

    labels = [cstr(d) for d in range(1, num_days + 1)]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": "Present", "values": daily_present, "chartType": "line"},
                {"name": "Absent",  "values": daily_absent,  "chartType": "line"},
                {"name": "Leave",   "values": daily_leave,   "chartType": "line"},
            ]
        },
        "type":   "line",
        "colors": ["#28a745", "#dc3545", "#007bff"],
    }