frappe.listview_settings["Sample Movement Register"] = {
	add_fields: ["status", "expected_return_date", "gate_photo"],
	has_indicator_for_draft: true,
	get_indicator(doc) {
		const colors = {
			Draft: "gray",
			"Pending Approval": "orange",
			Approved: "yellow",
			Out: "blue",
			"Partially Returned": "purple",
			Overdue: "red",
			Escalated: "red",
			Returned: "green",
			"Written Off": "darkgrey",
			Cancelled: "red",
		};
		return [__(doc.status), colors[doc.status] || "gray", "status,=," + doc.status];
	},
};
