// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

// frappe.query_reports["Fabric With Collar and Cuff Report"] = {
// 	"filters": [

// 	]
// };

// frappe.query_reports["Fabric With Collar and Cuff Report"] = {
//     "tree": True,
//     "parent_field": "parent",
//     "initial_depth": 0,
//     "filters": [
//         {
//             "fieldname": "fabric_type",
//             "label": "Fabric Type", 
//             "fieldtype": "Select",
//             "options": "\nAll\nCotton\nPolyester\nLinen\nSilk",
//             "default": "All",
//             "width": 120
//         },
//         {
//             "fieldname": "item_code",
//             "label": "Item Code",
//             "fieldtype": "Data", 
//             "placeholder": "Search item code...",
//             "width": 120
//         },
//         {
//             "fieldname": "color",
//             "label": "Color",
//             "fieldtype": "Select", 
//             "options": "\nAll\nWhite\nBlack\nBlue\nRed",
//             "default": "All",
//             "width": 120
//         }
//     ]
// }

// This is the key part that registers the report with filters
frappe.query_reports["Fabric With Collar and Cuff Reports"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1,
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
		},
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"get_query": function () {
				return {
					filters: {
						has_batch_no: 1,
					},
				};
			},
		},
		{
			"fieldname": "custom_commercial_name",
			"label": __("Commercial Name"),
			"fieldtype": "Data",
			"width": "100",
		},
		{
			"fieldname": "custom_color",
			"label": __("Color"),
			"fieldtype": "Data",
			"width": "80",
		},
		{
			"fieldname": "custom_item_type",
			"label": __("Item Type"),
			"fieldtype": "Select",
			"options": "\nFabric\nCollar\nCuff",
			"width": "80",
		},
		{
			"fieldname": "warehouse_type",
			"label": __("Warehouse Type"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Warehouse Type",
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"get_query": function () {
				let warehouse_type = frappe.query_report.get_filter_value("warehouse_type");
				let company = frappe.query_report.get_filter_value("company");
				return {
					filters: {
						...(warehouse_type && { warehouse_type }),
						...(company && { company }),
					},
				};
			},
		},
		{
			"fieldname": "batch_no",
			"label": __("Batch No"),
			"fieldtype": "Link",
			"options": "Batch",
			"get_query": function () {
				let item_code = frappe.query_report.get_filter_value("item_code");
				return {
					filters: {
						item: item_code,
					},
				};
			},
		},
		{
			"fieldname": "batch_status",
			"label": __("Batch Status"),
			"fieldtype": "Select",
			"options": "\nQC OK\nGRADE 2",
			"width": "80",
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		if (column.fieldname == "Batch" && data && !!data["Batch"]) {
			value = data["Batch"];
			column.link_onclick =
				"frappe.query_reports['Fabric With Collar and Cuff Reports'].set_batch_route_to_stock_ledger(" +
				JSON.stringify(data) +
				")";
		}

		value = default_formatter(value, row, column, data);
		return value;
	},
	"set_batch_route_to_stock_ledger": function (data) {
		frappe.route_options = {
			batch_no: data["Batch"],
		};

		frappe.set_route("query-report", "Stock Ledger");
	},
};