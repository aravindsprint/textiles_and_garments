// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt







frappe.query_reports["Plans Wise WO Report"] = {
    "filters": [
        {
            "fieldname": "plan_items",
            "label": __("Plan Items"),
            "fieldtype": "Link",
            "options": "Plan Items",
            "width": "200"
        },
        {
            "fieldname": "plans",
            "label": __("Plans"),
            "fieldtype": "Link",
            "options": "Plans",
            "width": "200"
        },
        {
            "fieldname": "item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "width": "200"
        },
        {
            "fieldname": "work_order",
            "label": __("Work Order"),
            "fieldtype": "Link",
            "options": "Work Order",
            "width": "200"
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "width": "200"
        },
        {
            "fieldname": "status",
            "label": __("WO Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nSubmitted\nNot Started\nIn Process\nCompleted\nStopped\nClosed\nCancelled",
            "width": "200"
        },
        {
            "fieldname": "bom_no",
            "label": __("BOM No"),
            "fieldtype": "Link",
            "options": "BOM",
            "width": "200"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "width": "100",
            "reqd": 1,
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -30)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "width": "100",
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
        },
        {
            "fieldname": "docstatus",
            "label": __("Document Status"),
            "fieldtype": "Select",
            "options": "\n0-Draft\n1-Submitted\n2-Cancelled",
            "default": "1",
            "width": "200"
        }
    ]
};




