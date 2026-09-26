import frappe


def execute():
	"""One-time backfill: Total Weight / Item Wise Weight were only computed in
	validate(), which never runs for scans on a submitted Roll Pick Assignment."""
	names = frappe.get_all(
		"Roll Pick Assignment Scan",
		filters={"parenttype": "Roll Pick Assignment"},
		pluck="parent",
		distinct=True,
	)

	for name in names:
		doc = frappe.get_doc("Roll Pick Assignment", name)
		doc.set_total_weight_from_scanned_rolls()
		doc.set_item_wise_weight_from_scanned_rolls()

		frappe.db.delete(
			"Roll Pick Item Weight",
			{"parent": name, "parenttype": "Roll Pick Assignment", "parentfield": "item_wise_weight"},
		)
		for row in doc.item_wise_weight:
			row.db_insert()

		frappe.db.set_value(
			"Roll Pick Assignment", name, "total_weight", doc.total_weight, update_modified=False
		)

	frappe.db.commit()
