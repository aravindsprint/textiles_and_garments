frappe.query_reports["Samples Currently Out"] = {
	filters: [
		{ fieldname: "department", label: __("Department"), fieldtype: "Link", options: "Department" },
		{ fieldname: "carried_by", label: __("Employee"), fieldtype: "Link", options: "Employee" },
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ["", "Approved", "Out", "Partially Returned", "Overdue", "Escalated"],
		},
		{ fieldname: "party_type", label: __("Party Type"), fieldtype: "Select", options: ["", "Customer", "Supplier", "Other"] },
		{ fieldname: "only_overdue", label: __("Only Overdue"), fieldtype: "Check" },
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "days_overdue" && data && data.days_overdue > 0) {
			value = `<span style="color:var(--red-600);font-weight:600">${value}</span>`;
		}
		return value;
	},
};
