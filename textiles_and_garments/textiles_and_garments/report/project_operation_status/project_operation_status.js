// Copyright (c) 2026, Arkotrix and contributors
// For license information, please see license.txt

const POS_OPERATIONS = [
	"Material Request",
	"Purchase Order",
	"Purchase Receipt",
	"Subcontracting Order",
	"SCO Raw Material Supply",
	"Subcontracting Receipt",
	"Work Order",
	"Job Card",
	"Stock Entry",
];

frappe.query_reports["Project Operation Status"] = {
	filters: [
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
			reqd: 1,
		},
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: "Item\nOperation",
			default: "Item",
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "operation",
			label: __("Operations"),
			fieldtype: "MultiSelectList",
			get_data: (txt) =>
				POS_OPERATIONS.filter((op) => !txt || op.toLowerCase().includes(txt.toLowerCase())).map(
					(op) => ({ value: op, description: "" })
				),
		},
		{
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
		},
		{
			fieldname: "pending_only",
			label: __("Pending Only"),
			fieldtype: "Check",
		},
		{
			fieldname: "include_draft",
			label: __("Include Draft"),
			fieldtype: "Check",
		},
	],

	tree: true,
	name_field: "row_key",
	parent_field: "parent_key",
	initial_depth: 1,

	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (!data) return value;

		if (data.is_group) {
			value = `<b>${value}</b>`;
		}

		if (column.fieldname === "pending_qty" && flt(data.pending_qty) > 0) {
			value = `<span style="color: var(--red-500)">${value}</span>`;
		}

		if (column.fieldname === "completion_pct" && data.completion_pct != null) {
			const pct = flt(data.completion_pct);
			const color = pct >= 100 ? "--green-500" : pct > 0 ? "--orange-500" : "--red-500";
			value = `<span style="color: var(${color})">${value}</span>`;
		}

		return value;
	},
};
