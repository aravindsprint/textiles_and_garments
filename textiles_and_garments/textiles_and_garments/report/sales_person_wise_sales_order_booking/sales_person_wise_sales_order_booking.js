frappe.query_reports["Sales Person Wise Sales Order Booking"] = {
	"filters": [
		{
			fieldname: "sales_person",
			label: __("Sales Person"),
			fieldtype: "Link",
			width: "280",
			options: "Sales Person",
			get_query: function() {
				return {
					filters: {
						"is_group": 0
					}
				};
			}
		},
		{
			fieldname: "parent_sales_person",
			label: __("Parent Sales Person (Group)"),
			fieldtype: "Link",
			width: "280",
			options: "Sales Person",
			get_query: function() {
				return {
					filters: {
						"is_group": 1
					}
				};
			}
		},
		{
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			width: "280",
			options: "Item",
		},
		{
			fieldname: "commercial_name",
			label: __("Commercial name"),
			fieldtype: "Data",
			width: "280",
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
		{
			fieldname: "custom_item_status",
			label: __("Item Status"),
			fieldtype: "Select",
			options: ["Not Started", "Completed", "Cancelled", "Partially Delivered and Need to Deliver"],
			width: "80",
			
		},
		{
			fieldname: "delivery_status",
			label: __("Delivery Status"),
			fieldtype: "Select",
			options: ["Not Delivered", "Fully Delivered", "Partly Delivered", "Not Applicable"],
			width: "80",
			
		},

	]
};