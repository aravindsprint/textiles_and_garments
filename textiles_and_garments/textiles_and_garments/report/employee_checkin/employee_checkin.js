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
            
            // Calculate summary statistics
            let total_employees = data.length;
            let on_time = data.filter(row => row.status === 'On Time').length;
            let grace_period = data.filter(row => row.status === 'Grace Period').length;
            let late = data.filter(row => row.status === 'Late').length;
            
            let unique_departments = [...new Set(data.map(row => row.department).filter(Boolean))].length;
            let unique_shifts = [...new Set(data.map(row => row.shift).filter(Boolean))].length;
            
            // Calculate average late time for late employees
            let late_employees = data.filter(row => row.time_difference > 0);
            let avg_late_time = late_employees.length > 0 
                ? late_employees.reduce((sum, row) => sum + (parseFloat(row.time_difference) || 0), 0) / late_employees.length 
                : 0;
            
            // Calculate percentage
            let on_time_percent = ((on_time / total_employees) * 100).toFixed(1);
            let late_percent = ((late / total_employees) * 100).toFixed(1);
            
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
                                <td style="text-align: right; padding: 8px 0; color: #ea580c;">${grace_period}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #e5e7eb;">
                                <td style="padding: 8px 0;"><strong>Late:</strong></td>
                                <td style="text-align: right; padding: 8px 0; color: #dc2626; font-weight: 700;">${late} (${late_percent}%)</td>
                            </tr>
                        </table>
                        
                        <h4 style="margin: 20px 0 15px 0; color: #ea580c;">📈 Performance Metrics</h4>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr style="border-bottom: 1px solid #e5e7eb;">
                                <td style="padding: 8px 0;"><strong>Average Late Time:</strong></td>
                                <td style="text-align: right; padding: 8px 0;">${avg_late_time.toFixed(1)} Minutes</td>
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
        
        // Add color indicators
        report.page.add_inner_button(__("Refresh"), function() {
            report.refresh();
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
        if (column.fieldname === "time_difference" && data.time_difference) {
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
