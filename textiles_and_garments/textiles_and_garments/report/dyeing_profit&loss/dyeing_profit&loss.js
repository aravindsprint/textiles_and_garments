// Copyright (c) 2024, Aravind and contributors
// For license information, please see license.txt



frappe.query_reports["Dyeing Profit&Loss"] = {
	"filters": [
		{
			fieldname: "work_order",
			label: __("Work Order"),
			fieldtype: "Link",
			width: "280",
			options: "Work Order",
			// get_query: () => {
			// 	return {
			// 		filters: {
			// 			has_batch_no: 1,
			// 			disabled: 0,
			// 		},
			// 	};
			// },
		},
		{
			fieldname: "from_date",
			label: __("From This Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -7),
		},
		{
			fieldname: "to_date",
			label: __("To This Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.get_today(),
		},

	]
};
