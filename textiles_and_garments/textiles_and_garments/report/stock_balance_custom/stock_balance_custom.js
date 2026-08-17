// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Balance Custom"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			width: "80",
			options: "Company",
			default: frappe.defaults.get_default("company"),
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			width: "80",
			options: "Item Group",
		},
		{
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			width: "80",
			options: "Item",
			get_query: function () {
				let item_group = frappe.query_report.get_filter_value("item_group");

				return {
					query: "erpnext.controllers.queries.item_query",
					filters: {
						...(item_group && { item_group }),
						is_stock_item: 1,
					},
				};
			},
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			width: "80",
			options: "Warehouse",
			get_query: () => {
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
			fieldname: "warehouse_type",
			label: __("Warehouse Type"),
			fieldtype: "Link",
			width: "80",
			options: "Warehouse Type",
		},
		{
			fieldname: "valuation_field_type",
			label: __("Valuation Field Type"),
			fieldtype: "Select",
			width: "80",
			options: "Currency\nFloat",
			default: "Currency",
		},
		{
			fieldname: "include_uom",
			label: __("Include UOM"),
			fieldtype: "Link",
			options: "UOM",
		},
		{
			fieldname: "show_variant_attributes",
			label: __("Show Variant Attributes"),
			fieldtype: "Check",
		},
		{
			fieldname: "show_stock_ageing_data",
			label: __("Show Stock Ageing Data"),
			fieldtype: "Check",
		},
		{
			fieldname: "ignore_closing_balance",
			label: __("Ignore Closing Balance"),
			fieldtype: "Check",
			default: 0,
		},
		{
			fieldname: "include_zero_stock_items",
			label: __("Include Zero Stock Items"),
			fieldtype: "Check",
			default: 0,
		},
		{
			fieldname: "show_dimension_wise_stock",
			label: __("Show Dimension Wise Stock"),
			fieldtype: "Check",
			default: 0,
		},
	],

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "out_qty" && data && data.out_qty > 0) {
			value = "<span style='color:red'>" + value + "</span>";
		} else if (column.fieldname == "in_qty" && data && data.in_qty > 0) {
			value = "<span style='color:green'>" + value + "</span>";
		}

		return value;
	},

	onload: function(report) {
		// Add button to show SO details
		report.page.add_inner_button(__("Show SO Details"), function() {
			var selected_row = report.get_selected_row();
			if (selected_row && selected_row.so_reserved_qty > 0) {
				show_so_details(selected_row);
			} else {
				frappe.msgprint(__("No SO reserved quantity for this item/warehouse"));
			}
		}, __("Actions"));

		// Add custom formatter for SO Res.Qty column to make it clickable
		report.custom_formatter = function(value, row, column, data, default_formatter) {
			value = default_formatter(value, row, column, data);
			
			if (column.fieldname === "so_reserved_qty" && data && data.so_reserved_qty > 0) {
				value = `<a href="#" onclick="show_so_details(${JSON.stringify(data).replace(/"/g, '&quot;')}); return false;" style="color: blue; text-decoration: underline;">${value}</a>`;
			}
			
			return value;
		};
	},
};

// Function to show SO details in a dialog
function show_so_details(row) {
	// Create a dialog to show SO details
	var dialog = new frappe.ui.Dialog({
		title: __('SO Reserved Details - ' + row.item_code + ' / ' + row.warehouse),
		fields: [
			{
				fieldname: "so_details",
				fieldtype: "HTML",
				options: "<div style='height: 300px; overflow: auto;' id='so-details-container'></div>"
			}
		],
		size: 'large'
	});

	// Fetch and display SO details
	frappe.call({
		method: "erpnext.stock.report.stock_balance.stock_balance.get_so_reserved_details",
		args: {
			item_code: row.item_code,
			warehouse: row.warehouse
		},
		callback: function(r) {
			if (r.message) {
				var html = "<table class='table table-bordered' style='width: 100%;'>";
				html += "<thead><tr>";
				html += "<th style='padding: 8px;'>" + __("SO Date") + "</th>";
				html += "<th style='padding: 8px;'>" + __("SO No") + "</th>";
				html += "<th style='padding: 8px;'>" + __("Customer") + "</th>";
				html += "<th style='padding: 8px; text-align: right;'>" + __("Qty") + "</th>";
				html += "<th style='padding: 8px;'>" + __("Warehouse") + "</th>";
				html += "<th style='padding: 8px;'>" + __("Custom SO No") + "</th>";
				html += "</tr></thead><tbody>";
				
				var total_qty = 0;
				r.message.forEach(function(detail) {
					html += "<tr>";
					html += "<td style='padding: 8px;'>" + frappe.datetime.str_to_user(detail.so_date) + "</td>";
					html += "<td style='padding: 8px;'><a href='/app/sales-order/" + detail.sales_order + "' target='_blank'>" + detail.sales_order + "</a></td>";
					html += "<td style='padding: 8px;'>" + (detail.customer || "") + "</td>";
					html += "<td style='padding: 8px; text-align: right;'>" + format_number(detail.reserved_qty, null, 2) + "</td>";
					html += "<td style='padding: 8px;'>" + (detail.warehouse || "") + "</td>";
					html += "<td style='padding: 8px;'>" + (detail.custom_so_no || "") + "</td>";
					html += "</tr>";
					total_qty += detail.reserved_qty;
				});
				
				// Add total row
				html += "<tr style='font-weight: bold; background-color: #f5f5f5;'>";
				html += "<td style='padding: 8px;' colspan='3'>" + __("Total") + "</td>";
				html += "<td style='padding: 8px; text-align: right;'>" + format_number(total_qty, null, 2) + "</td>";
				html += "<td style='padding: 8px;' colspan='2'></td>";
				html += "</tr>";
				
				html += "</tbody></table>";
				$("#so-details-container").html(html);
			} else {
				$("#so-details-container").html(__("No SO reserved details found"));
			}
		}
	});

	dialog.show();
}

erpnext.utils.add_inventory_dimensions("Stock Balance", 8);