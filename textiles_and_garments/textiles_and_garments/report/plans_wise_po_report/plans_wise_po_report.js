// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt



frappe.query_reports["Plans Wise PO Report"] = {
    "filters": [
        {
            "fieldname": "plan_items",
            "label": __("Plan Items"),
            "fieldtype": "Link",
            "options": "Plan Items",
            "width": "380"
        },
        {
            "fieldname": "plans",
            "label": __("Plans"),
            "fieldtype": "Link",
            "options": "Plans",
            "width": "380"
        },
        {
            "fieldname": "item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "width": "280"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "width": "80",
            "reqd": 1,
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -7)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "width": "80",
            "reqd": 1,
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "commercial_name",
            "label": __("Commercial Name"),
            "fieldtype": "Data",
            "width": "200"
        },
        {
            "fieldname": "color",
            "label": __("Color"),
            "fieldtype": "Data",
            "width": "200"
        }
    ]
};







