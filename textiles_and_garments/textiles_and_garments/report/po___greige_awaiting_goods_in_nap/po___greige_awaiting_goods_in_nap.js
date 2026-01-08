// // Copyright (c) 2026, Aravind and contributors
// // For license information, please see license.txt

// frappe.query_reports["PO - Yarn Awaiting goods in NAP"] = {
// 	"filters": [
// 		{
// 			"fieldname": "company",
// 			"label": __("Company"),
// 			"fieldtype": "Link",
// 			"options": "Company",
// 			"default": frappe.defaults.get_user_default("Company"),
// 			"reqd": 0
// 		},
// 		{
// 			"fieldname": "supplier",
// 			"label": __("Supplier"),
// 			"fieldtype": "Link",
// 			"options": "Supplier",
// 			"reqd": 0
// 		},
// 		{
// 			"fieldname": "from_date",
// 			"label": __("From Date"),
// 			"fieldtype": "Date",
// 			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -3),
// 			"reqd": 0
// 		},
// 		{
// 			"fieldname": "to_date",
// 			"label": __("To Date"),
// 			"fieldtype": "Date",
// 			"default": frappe.datetime.get_today(),
// 			"reqd": 0
// 		},
// 		{
// 			"fieldname": "item_code",
// 			"label": __("Item Code"),
// 			"fieldtype": "Link",
// 			"options": "Item",
// 			"reqd": 0
// 		},
// 		{
// 			"fieldname": "material_request",
// 			"label": __("Material Request"),
// 			"fieldtype": "Link",
// 			"options": "Material Request",
// 			"reqd": 0
// 		}
// 	]
// };

// Copyright (c) 2026, Aravind and contributors
// For license information, please see license.txt

// // Copyright (c) 2026, Aravind and contributors
// // For license information, please see license.txt

// frappe.query_reports["PO - Yarn Awaiting goods in NAP"] = {
// 	"filters": [
// 		{
// 			"fieldname": "company",
// 			"label": __("Company"),
// 			"fieldtype": "Link",
// 			"options": "Company",
// 			"default": frappe.defaults.get_user_default("Company"),
// 			"reqd": 0
// 		},
// 		{
// 			"fieldname": "supplier",
// 			"label": __("Supplier"),
// 			"fieldtype": "Link",
// 			"options": "Supplier",
// 			"reqd": 0
// 		},
// 		{
// 			"fieldname": "from_date",
// 			"label": __("From Date"),
// 			"fieldtype": "Date",
// 			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -3),
// 			"reqd": 0
// 		},
// 		{
// 			"fieldname": "to_date",
// 			"label": __("To Date"),
// 			"fieldtype": "Date",
// 			"default": frappe.datetime.get_today(),
// 			"reqd": 0
// 		},
// 		{
// 			"fieldname": "item_code",
// 			"label": __("Item Code"),
// 			"fieldtype": "Link",
// 			"options": "Item",
// 			"reqd": 0
// 		},
// 		{
// 			"fieldname": "material_request",
// 			"label": __("Material Request"),
// 			"fieldtype": "Link",
// 			"options": "Material Request",
// 			"reqd": 0
// 		}
// 	]
// };

// Copyright (c) 2026, Aravind and contributors
// For license information, please see license.txt

frappe.query_reports["PO - Greige Awaiting goods in NAP"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 0
		},
		{
			"fieldname": "supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"reqd": 0
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -3),
			"reqd": 0
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 0
		},
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"reqd": 0
		},
		{
			"fieldname": "material_request",
			"label": __("Material Request"),
			"fieldtype": "Link",
			"options": "Material Request",
			"reqd": 0
		}
	],
	
	"onload": function(report) {
		// Add Summary button
		report.page.add_inner_button(__("Summary"), function() {
			let data = report.data;
			
			if (!data || data.length === 0) {
				frappe.msgprint(__("No data available to summarize"));
				return;
			}
			
			// Filter out total rows (rows without purchase_order or with specific indicators)
			let filtered_data = data.filter(row => {
				// Exclude rows that are totals/subtotals
				// Total rows typically don't have a purchase_order value or have specific markers
				return row.purchase_order && 
				       !row.is_total_row && 
				       row.purchase_order !== "Total" &&
				       row.purchase_order !== "Grand Total";
			});
			
			if (filtered_data.length === 0) {
				frappe.msgprint(__("No valid data rows found"));
				return;
			}
			
			// Calculate summary statistics
			let total_records = filtered_data.length;
			let unique_suppliers = [...new Set(filtered_data.map(row => row.supplier).filter(Boolean))].length;
			let unique_pos = [...new Set(filtered_data.map(row => row.purchase_order).filter(Boolean))].length;
			
			let total_ordered = filtered_data.reduce((sum, row) => sum + (parseFloat(row.qty) || 0), 0);
			let total_received = filtered_data.reduce((sum, row) => sum + (parseFloat(row.received_qty) || 0), 0);
			let total_pending = filtered_data.reduce((sum, row) => sum + (parseFloat(row.pending_qty) || 0), 0);
			
			let avg_per_received = filtered_data.reduce((sum, row) => sum + (parseFloat(row.per_received) || 0), 0) / total_records;
			let avg_aging = filtered_data.reduce((sum, row) => sum + (parseFloat(row.aging_days) || 0), 0) / total_records;
			
			// Show summary dialog
			frappe.msgprint({
				title: __("Greige Awaiting GRN - Summary"),
				message: `
					<div style="font-size: 14px; line-height: 2;">
						<h4 style="margin-bottom: 15px; color: #2563eb;">📊 Report Overview</h4>
						<table style="width: 100%; border-collapse: collapse;">
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Total Line Items:</strong></td>
								<td style="text-align: right; padding: 8px 0;">${total_records}</td>
							</tr>
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Unique Purchase Orders:</strong></td>
								<td style="text-align: right; padding: 8px 0;">${unique_pos}</td>
							</tr>
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Unique Suppliers:</strong></td>
								<td style="text-align: right; padding: 8px 0;">${unique_suppliers}</td>
							</tr>
						</table>
						
						<h4 style="margin: 20px 0 15px 0; color: #16a34a;">📦 Quantity Summary</h4>
						<table style="width: 100%; border-collapse: collapse;">
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Total Ordered Qty:</strong></td>
								<td style="text-align: right; padding: 8px 0;">${total_ordered.toFixed(2)} Kgs</td>
							</tr>
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Total Received Qty:</strong></td>
								<td style="text-align: right; padding: 8px 0; color: #0284c7;">${total_received.toFixed(2)} Kgs</td>
							</tr>
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Total Pending Qty:</strong></td>
								<td style="text-align: right; padding: 8px 0; color: #dc2626; font-weight: 700;">${total_pending.toFixed(2)} Kgs</td>
							</tr>
						</table>
						
						<h4 style="margin: 20px 0 15px 0; color: #ea580c;">📈 Performance Metrics</h4>
						<table style="width: 100%; border-collapse: collapse;">
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Average % Received:</strong></td>
								<td style="text-align: right; padding: 8px 0;">${avg_per_received.toFixed(2)}%</td>
							</tr>
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Average Aging:</strong></td>
								<td style="text-align: right; padding: 8px 0;">${avg_aging.toFixed(1)} Days</td>
							</tr>
						</table>
					</div>
				`,
				indicator: "blue",
				wide: true
			});
		});
	}
};