// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

frappe.query_reports["Work Order in Pipeline - Draft"] = {
    "filters": [
        {
            "fieldname": "work_order",
            "label": __("Work Order"),
            "fieldtype": "Link",
            "options": "Work Order",
            "width": "200"
        },
        {
            "fieldname": "production_item",
            "label": __("Production Item"),
            "fieldtype": "Link",
            "options": "Item",
            "width": "200",
            "get_query": function() {
                return {
                    "filters": {
                        "item_code": ["like", "GKF%"]
                    }
                };
            }
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "width": "200",
            "default": frappe.defaults.get_user_default("Company")
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
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -30)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "width": "100",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "fg_warehouse",
            "label": __("Target Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": "200"
        },
        {
            "fieldname": "wip_warehouse",
            "label": __("WIP Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": "200"
        }
    ]
};
