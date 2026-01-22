// Copyright (c) 2026, Aravind and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Checkins"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 0
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"reqd": 0
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"reqd": 0
		},
		{
			"fieldname": "shift",
			"label": __("Shift"),
			"fieldtype": "Link",
			"options": "Shift Type",
			"reqd": 0
		}
	],
	
	"onload": function(report) {
		// Helper function to generate attendance summary
		function generate_attendance_summary(employee_category, title_suffix) {
			let filters = report.get_values();
			
			let employee_filters = {
				status: "Active",
				company: filters.company || frappe.defaults.get_user_default("Company")
			};
			
			// Add employment type filter
			if (employee_category) {
				employee_filters.employee_category = employee_category;
			}
			
			frappe.call({
				method: "frappe.client.get_list",
				args: {
					doctype: "Employee",
					filters: employee_filters,
					fields: ["name", "employee_name", "department", "employee_category"],
					limit_page_length: 0
				},
				callback: function(r) {
					if (!r.message || r.message.length === 0) {
						frappe.msgprint(__("No active " + (title_suffix || "employees") + " found"));
						return;
					}
					
					let all_employees = r.message;
					let report_data = report.data || [];
					
					// Get checked-in employee IDs from report data
					let checked_in_employees = new Set(
						report_data
							.filter(row => row.employee && !row.is_total_row)
							.map(row => row.employee)
					);
					
					// Group by department
					let dept_summary = {};
					
					all_employees.forEach(emp => {
						let dept = emp.department || "Unknown Department";
						
						if (!dept_summary[dept]) {
							dept_summary[dept] = {
								onroll: 0,
								present: 0
							};
						}
						
						dept_summary[dept].onroll++;
						
						if (checked_in_employees.has(emp.name)) {
							dept_summary[dept].present++;
						}
					});
					
					// Calculate leave & absent and create sorted array
					let summary_array = Object.keys(dept_summary)
						.map(dept => ({
							department: dept,
							onroll: dept_summary[dept].onroll,
							present: dept_summary[dept].present,
							absent: dept_summary[dept].onroll - dept_summary[dept].present
						}))
						.sort((a, b) => a.department.localeCompare(b.department));
					
					// Calculate totals
					let total_onroll = summary_array.reduce((sum, row) => sum + row.onroll, 0);
					let total_present = summary_array.reduce((sum, row) => sum + row.present, 0);
					let total_absent = total_onroll - total_present;
					
					// Build HTML table
					let html = `
						<div style="overflow-x: auto;">
							<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
								<thead>
									<tr style="background-color: #FFFF00;">
										<th style="border: 1px solid #000; padding: 8px; text-align: left; font-weight: bold;">Department</th>
										<th style="border: 1px solid #000; padding: 8px; text-align: center; font-weight: bold;">Onroll<br/>Strength</th>
										<th style="border: 1px solid #000; padding: 8px; text-align: center; font-weight: bold;">Present</th>
										<th style="border: 1px solid #000; padding: 8px; text-align: center; font-weight: bold;">Leave &<br/>Absent</th>
									</tr>
								</thead>
								<tbody>
					`;
					
					summary_array.forEach(row => {
						html += `
							<tr>
								<td style="border: 1px solid #000; padding: 8px;">${row.department}</td>
								<td style="border: 1px solid #000; padding: 8px; text-align: center;">${row.onroll}</td>
								<td style="border: 1px solid #000; padding: 8px; text-align: center;">${row.present}</td>
								<td style="border: 1px solid #000; padding: 8px; text-align: center;">${row.absent}</td>
							</tr>
						`;
					});
					
					html += `
								</tbody>
								<tfoot>
									<tr style="background-color: #D3D3D3; font-weight: bold;">
										<td style="border: 1px solid #000; padding: 8px;">Grand Total</td>
										<td style="border: 1px solid #000; padding: 8px; text-align: center;">${total_onroll}</td>
										<td style="border: 1px solid #000; padding: 8px; text-align: center;">${total_present}</td>
										<td style="border: 1px solid #000; padding: 8px; text-align: center;">${total_absent}</td>
									</tr>
								</tfoot>
							</table>
						</div>
					`;
					
					let dialog = new frappe.ui.Dialog({
						title: __('Attendance Report as on ' + filters.from_date + ' (' + title_suffix + ')'),
						fields: [
							{
								fieldtype: 'HTML',
								fieldname: 'attendance_summary',
								options: html
							}
						],
						size: 'large',
						primary_action_label: __('Export to Excel'),
						primary_action: function() {
							// Prepare data for export with proper structure
							let export_data = [];
							
							// Add data rows
							summary_array.forEach(row => {
								export_data.push([
									row.department,
									row.onroll,
									row.present,
									row.absent
								]);
							});
							
							// Add grand total row
							export_data.push([
								'Grand Total',
								total_onroll,
								total_present,
								total_absent
							]);
							
							// Define columns with headers
							let columns = [
								{fieldname: 'department', label: __('Department')},
								{fieldname: 'onroll_strength', label: __('Onroll Strength')},
								{fieldname: 'present', label: __('Present')},
								{fieldname: 'leave_absent', label: __('Leave & Absent')}
							];
							
							// Export using Frappe's method
							frappe.tools.downloadify(
								export_data,
								columns,
								{
									filename: 'Attendance_Report_' + title_suffix + '_' + filters.from_date
								}
							);
							
							dialog.hide();
						}
					});
					
					dialog.show();
				}
			});
		}
		
		// Add Worker Attendance Summary button
		report.page.add_inner_button(__("Worker Attendance Summary"), function() {
			generate_attendance_summary("Worker", "Worker");
		});
		
		// Add Staff Attendance Summary button
		report.page.add_inner_button(__("Staff Attendance Summary"), function() {
			generate_attendance_summary("Staff", "Staff");
		});
		
		// Add Overall Summary button
		report.page.add_inner_button(__("Summary"), function() {
			let data = report.data;
			
			if (!data || data.length === 0) {
				frappe.msgprint(__("No data available to summarize"));
				return;
			}
			
			// Filter out any total rows if they exist
			let filtered_data = data.filter(row => {
				return row.employee && 
				       !row.is_total_row && 
				       row.employee !== "Total" &&
				       row.employee !== "Grand Total";
			});
			
			if (filtered_data.length === 0) {
				frappe.msgprint(__("No valid data rows found"));
				return;
			}
			
			// Calculate summary statistics
			let total_employees = filtered_data.length;
			let on_time = filtered_data.filter(row => row.status === 'On Time').length;
			let grace_period = filtered_data.filter(row => row.status === 'Grace Period').length;
			let late = filtered_data.filter(row => row.status === 'Late').length;
			
			let unique_departments = [...new Set(filtered_data.map(row => row.department).filter(Boolean))].length;
			let unique_shifts = [...new Set(filtered_data.map(row => row.shift).filter(Boolean))].length;
			
			// Calculate average late time for employees who were late
			let late_employees = filtered_data.filter(row => row.time_difference > 0);
			let avg_late_time = late_employees.length > 0 
				? late_employees.reduce((sum, row) => sum + (parseFloat(row.time_difference) || 0), 0) / late_employees.length 
				: 0;
			
			// Calculate early employees average
			let early_employees = filtered_data.filter(row => row.time_difference < 0);
			let avg_early_time = early_employees.length > 0
				? Math.abs(early_employees.reduce((sum, row) => sum + (parseFloat(row.time_difference) || 0), 0) / early_employees.length)
				: 0;
			
			// Calculate percentage
			let on_time_percent = total_employees > 0 ? ((on_time / total_employees) * 100).toFixed(1) : 0;
			let late_percent = total_employees > 0 ? ((late / total_employees) * 100).toFixed(1) : 0;
			let grace_percent = total_employees > 0 ? ((grace_period / total_employees) * 100).toFixed(1) : 0;
			
			// Show summary dialog
			frappe.msgprint({
				title: __("Employee First Check-in - Summary"),
				message: `
					<div style="font-size: 14px; line-height: 2;">
						<h4 style="margin-bottom: 15px; color: #2563eb;">📊 Attendance Overview</h4>
						<table style="width: 100%; border-collapse: collapse;">
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Total Employees:</strong></td>
								<td style="text-align: right; padding: 8px 0;">${total_employees}</td>
							</tr>
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Unique Departments:</strong></td>
								<td style="text-align: right; padding: 8px 0;">${unique_departments}</td>
							</tr>
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Unique Shifts:</strong></td>
								<td style="text-align: right; padding: 8px 0;">${unique_shifts}</td>
							</tr>
						</table>
						
						<h4 style="margin: 20px 0 15px 0; color: #16a34a;">⏰ Punctuality Summary</h4>
						<table style="width: 100%; border-collapse: collapse;">
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>On Time:</strong></td>
								<td style="text-align: right; padding: 8px 0; color: #16a34a; font-weight: 700;">${on_time} (${on_time_percent}%)</td>
							</tr>
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Grace Period:</strong></td>
								<td style="text-align: right; padding: 8px 0; color: #ea580c;">${grace_period} (${grace_percent}%)</td>
							</tr>
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Late:</strong></td>
								<td style="text-align: right; padding: 8px 0; color: #dc2626; font-weight: 700;">${late} (${late_percent}%)</td>
							</tr>
						</table>
						
						<h4 style="margin: 20px 0 15px 0; color: #ea580c;">📈 Performance Metrics</h4>
						<table style="width: 100%; border-collapse: collapse;">
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Average Early Time:</strong></td>
								<td style="text-align: right; padding: 8px 0; color: #16a34a;">${avg_early_time.toFixed(1)} Minutes</td>
							</tr>
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Average Late Time:</strong></td>
								<td style="text-align: right; padding: 8px 0; color: #dc2626;">${avg_late_time.toFixed(1)} Minutes</td>
							</tr>
							<tr style="border-bottom: 1px solid #e5e7eb;">
								<td style="padding: 8px 0;"><strong>Punctuality Rate:</strong></td>
								<td style="text-align: right; padding: 8px 0; color: ${on_time_percent >= 90 ? '#16a34a' : '#dc2626'}; font-weight: 700;">${on_time_percent}%</td>
							</tr>
						</table>
					</div>
				`,
				indicator: "blue",
				wide: true
			});
		});
	},
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		// Color code the status column
		if (column.fieldname === "status") {
			if (data.status === "On Time") {
				value = `<span style="color: #16a34a; font-weight: 600;">${data.status}</span>`;
			} else if (data.status === "Grace Period") {
				value = `<span style="color: #ea580c; font-weight: 600;">${data.status}</span>`;
			} else if (data.status === "Late") {
				value = `<span style="color: #dc2626; font-weight: 600;">${data.status}</span>`;
			}
		}
		
		// Color code time difference
		if (column.fieldname === "time_difference" && data.time_difference !== null && data.time_difference !== undefined) {
			if (data.time_difference <= 0) {
				value = `<span style="color: #16a34a;">${data.time_difference}</span>`;
			} else if (data.time_difference <= 15) {
				value = `<span style="color: #ea580c;">${data.time_difference}</span>`;
			} else {
				value = `<span style="color: #dc2626; font-weight: 600;">${data.time_difference}</span>`;
			}
		}
		
		return value;
	}
};
