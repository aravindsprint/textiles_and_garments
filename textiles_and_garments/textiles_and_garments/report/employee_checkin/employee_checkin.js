// Copyright (c) 2026, Aravind and contributors
// For license information, please see license.txt

// employee_first_checkin.js

frappe.query_reports["Employee Checkin"] = {
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
        // Add Summary button
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