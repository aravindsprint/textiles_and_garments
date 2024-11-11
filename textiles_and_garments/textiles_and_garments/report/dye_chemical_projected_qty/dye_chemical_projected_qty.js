// Copyright (c) 2024, Aravind and contributors
// For license information, please see license.txt
frappe.query_reports["Dye Chemical Projected Qty"] = {
    //"filters": [],
    formatter: function (value, row, column, data, default_formatter) {
    // Default formatting
    value = default_formatter(value, row, column, data);
    
    // Log detailed info about the columns and value
    // console.log("Column:", column.fieldname, "Value:", value);



    // Check if the field being formatted is 'required_qty'
    if (column.fieldname === 'required_qty') {
        // Apply green color if required_qty contains a '-' character
        // console.log( "Value:", value);
        const match = value.match(/-?\d{1,3}(?:,\d{3})*(?:\.\d+)?/);

        // If a match is found, remove the commas and convert to float
        const number = match ? parseFloat(match[0].replace(/,/g, '')) : null;

        console.log(number); // -9985.8
        if (number >= 0) {
            console.log("value",value);
            value = `<b style="color:green">${value}</b>`;
        } else {
            // Apply red color if required_qty does not contain a '-'
            value = `<b style="color:red">${value}</b>`;
        }
    }

    return value;
    }
    
   // "formatter": function(value, row, column, data, default_formatter) {
   //      // Formatter function if needed
   // 	    console.log("value",value);
   //      return default_formatter(value, row, column, data);
   //  },

};







// 	filters: [
// 		{
// 			fieldname: "company",
// 			label: __("Company"),
// 			fieldtype: "Link",
// 			options: "Company",
// 			reqd: 1,
// 			default: frappe.defaults.get_user_default("Company"),
// 		},
// 		{
// 			fieldname: "report_date",
// 			label: __("Posting Date"),
// 			fieldtype: "Date",
// 			default: frappe.datetime.get_today(),
// 		},
// 		{
// 			fieldname: "finance_book",
// 			label: __("Finance Book"),
// 			fieldtype: "Link",
// 			options: "Finance Book",
// 		},
// 		{
// 			fieldname: "cost_center",
// 			label: __("Cost Center"),
// 			fieldtype: "Link",
// 			options: "Cost Center",
// 			get_query: () => {
// 				var company = frappe.query_report.get_filter_value("company");
// 				return {
// 					filters: {
// 						company: company,
// 					},
// 				};
// 			},
// 		},
// 		{
// 			fieldname: "party_account",
// 			label: __("Payable Account"),
// 			fieldtype: "Link",
// 			options: "Account",
// 			get_query: () => {
// 				var company = frappe.query_report.get_filter_value("company");
// 				return {
// 					filters: {
// 						company: company,
// 						account_type: "Payable",
// 						is_group: 0,
// 					},
// 				};
// 			},
// 		},
// 		{
// 			fieldname: "ageing_based_on",
// 			label: __("Ageing Based On"),
// 			fieldtype: "Select",
// 			options: "Posting Date\nDue Date\nSupplier Invoice Date",
// 			default: "Due Date",
// 		},
// 		{
// 			fieldname: "range1",
// 			label: __("Ageing Range 1"),
// 			fieldtype: "Int",
// 			default: "30",
// 			reqd: 1,
// 		},
// 		{
// 			fieldname: "range2",
// 			label: __("Ageing Range 2"),
// 			fieldtype: "Int",
// 			default: "60",
// 			reqd: 1,
// 		},
// 		{
// 			fieldname: "range3",
// 			label: __("Ageing Range 3"),
// 			fieldtype: "Int",
// 			default: "90",
// 			reqd: 1,
// 		},
// 		{
// 			fieldname: "range4",
// 			label: __("Ageing Range 4"),
// 			fieldtype: "Int",
// 			default: "120",
// 			reqd: 1,
// 		},
// 		{
// 			fieldname: "payment_terms_template",
// 			label: __("Payment Terms Template"),
// 			fieldtype: "Link",
// 			options: "Payment Terms Template",
// 		},
// 		{
// 			fieldname: "party_type",
// 			label: __("Party Type"),
// 			fieldtype: "Autocomplete",
// 			options: get_party_type_options(),
// 			on_change: function () {
// 				frappe.query_report.set_filter_value("party", "");
// 				frappe.query_report.toggle_filter_display(
// 					"supplier_group",
// 					frappe.query_report.get_filter_value("party_type") !== "Supplier"
// 				);
// 			},
// 		},
// 		{
// 			fieldname: "party",
// 			label: __("Party"),
// 			fieldtype: "MultiSelectList",
// 			get_data: function (txt) {
// 				if (!frappe.query_report.filters) return;

// 				let party_type = frappe.query_report.get_filter_value("party_type");
// 				if (!party_type) return;

// 				return frappe.db.get_link_options(party_type, txt);
// 			},
// 		},
// 		{
// 			fieldname: "supplier_group",
// 			label: __("Supplier Group"),
// 			fieldtype: "Link",
// 			options: "Supplier Group",
// 			hidden: 1,
// 		},
// 		{
// 			fieldname: "group_by_party",
// 			label: __("Group By Supplier"),
// 			fieldtype: "Check",
// 		},
// 		{
// 			fieldname: "based_on_payment_terms",
// 			label: __("Based On Payment Terms"),
// 			fieldtype: "Check",
// 		},
// 		{
// 			fieldname: "show_remarks",
// 			label: __("Show Remarks"),
// 			fieldtype: "Check",
// 		},
// 		{
// 			fieldname: "show_future_payments",
// 			label: __("Show Future Payments"),
// 			fieldtype: "Check",
// 		},
// 		{
// 			fieldname: "for_revaluation_journals",
// 			label: __("Revaluation Journals"),
// 			fieldtype: "Check",
// 		},
// 		{
// 			fieldname: "ignore_accounts",
// 			label: __("Group by Voucher"),
// 			fieldtype: "Check",
// 		},
// 		{
// 			fieldname: "in_party_currency",
// 			label: __("In Party Currency"),
// 			fieldtype: "Check",
// 		},
// 	],

// 	formatter: function (value, row, column, data, default_formatter) {
// 		value = default_formatter(value, row, column, data);
// 		if (data && data.bold) {
// 			value = value.bold();
// 		}
// 		return value;
// 	},

// 	onload: function (report) {
// 		report.page.add_inner_button(__("Accounts Payable Summary"), function () {
// 			var filters = report.get_values();
// 			frappe.set_route("query-report", "Accounts Payable Summary", { company: filters.company });
// 		});
// 	},
// };


