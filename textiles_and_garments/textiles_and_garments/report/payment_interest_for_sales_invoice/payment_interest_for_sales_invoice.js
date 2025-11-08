// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt


// frappe.query_reports["Payment Interest For Sales Invoice"] = {
//     "filters": [
//         {
//             "fieldname": "sales_invoice",
//             "label": __("Sales Invoice"),
//             "fieldtype": "Link",
//             "options": "Sales Invoice",
//             "width": "280",
//         },
//         {
//             "fieldname": "customer",
//             "label": __("Customer"),
//             "fieldtype": "Link",
//             "options": "Customer",
//             "width": "280",
//         },
//         {
//             "fieldname": "payment_entry",
//             "label": __("Payment Entry"),
//             "fieldtype": "Link",
//             "options": "Payment Entry",
//             "width": "280",
//         },
//         {
//             "fieldname": "from_date",
//             "label": __("From Date"),
//             "fieldtype": "Date",
//             "width": "80",
//             "reqd": 1,
//             "default": frappe.datetime.add_days(frappe.datetime.get_today(), -30),
//         },
//         {
//             "fieldname": "to_date",
//             "label": __("To Date"),
//             "fieldtype": "Date",
//             "width": "80",
//             "reqd": 1,
//             "default": frappe.datetime.get_today(),
//         },
//         {
//             "fieldname": "payment_posting_date",
//             "label": __("Payment Posting Date"),
//             "fieldtype": "Date",
//             "width": "80",
//         }
//     ]
// };


frappe.query_reports["Payment Interest For Sales Invoice"] = {
    "filters": [
        {
            "fieldname": "sales_invoice",
            "label": __("Sales Invoice"),
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": "280",
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": "280",
        },
        {
            "fieldname": "payment_entry",
            "label": __("Payment Entry"),
            "fieldtype": "Link",
            "options": "Payment Entry",
            "width": "280",
        },
        {
            "fieldname": "rate_of_interest",
            "label": __("Rate of Interest (%)"),
            "fieldtype": "Float",
            "width": "80",
            "default": 18.0,
            "precision": 2,
            "min_value": 0,
            "max_value": 100,
            "description": __("Enter annual interest rate (0-100%)")
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "width": "80",
            "reqd": 1,
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -30),
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "width": "80",
            "reqd": 1,
            "default": frappe.datetime.get_today(),
        },
        {
            "fieldname": "payment_posting_date",
            "label": __("Payment Posting Date"),
            "fieldtype": "Date",
            "width": "80",
        }
    ]
};