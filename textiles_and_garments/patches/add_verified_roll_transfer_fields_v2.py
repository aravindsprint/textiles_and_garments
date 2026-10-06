import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Stock Entry fields for the Roll App's "Verify Rolls" put-away flow.

	Adds ONLY column-less fields to Stock Entry:
	  custom_roll_verification_section  Section Break
	  custom_verified_rolls             Table -> Verified Roll Item
	The source Material Transfer is stored per row in
	Verified Roll Item.source_stock_entry instead of a Stock Entry column,
	because `tabStock Entry` is at MariaDB's 65,535-byte row-size limit
	(error 1118) and can't take another varchar.

	Replaces add_verified_roll_transfer_fields (v1), which tried to add a
	Link column custom_verified_from_stock_entry and failed with 1118 on
	production. That failure can leave the Custom Field record behind
	without its column; any later schema sync of Stock Entry would then
	retry the same failing ALTER, so it's removed FIRST — before
	create_custom_fields triggers a sync. Where v1 did succeed (a dev site
	with a narrower Stock Entry), the column is dropped too.
	"""
	_remove_v1_link_field()
	create_custom_fields(
		{
			"Stock Entry": [
				{
					"fieldname": "custom_roll_verification_section",
					"fieldtype": "Section Break",
					"label": "Roll Verification",
					"insert_after": _anchor(),
					"collapsible": 1,
					"depends_on": "eval:(doc.custom_verified_rolls || []).length",
				},
				{
					"fieldname": "custom_verified_rolls",
					"fieldtype": "Table",
					"label": "Verified Rolls",
					"options": "Verified Roll Item",
					"insert_after": "custom_roll_verification_section",
					"read_only": 1,
					"no_copy": 1,
				},
			]
		},
		update=True,
	)


def _anchor():
	return (
		"custom_roll_wise_pick_list"
		if frappe.db.exists("Custom Field", "Stock Entry-custom_roll_wise_pick_list")
		else "items"
	)


def _remove_v1_link_field():
	name = "Stock Entry-custom_verified_from_stock_entry"
	if frappe.db.exists("Custom Field", name):
		# Raw delete: deleting through the document API can trigger a schema
		# sync of Stock Entry, which is the very thing that fails.
		frappe.db.delete("Custom Field", {"name": name})
		frappe.db.delete("Property Setter", {"doc_type": "Stock Entry", "field_name": "custom_verified_from_stock_entry"})

	if frappe.db.has_column("Stock Entry", "custom_verified_from_stock_entry"):
		frappe.db.sql_ddl("ALTER TABLE `tabStock Entry` DROP COLUMN `custom_verified_from_stock_entry`")

	frappe.clear_cache(doctype="Stock Entry")
