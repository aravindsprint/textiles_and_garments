import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Stock Entry fields for the Roll App's "Verify Rolls" put-away flow.

	custom_verified_from_stock_entry — the submitted Material Transfer whose
	    rolls were verified (one put-away per source entry; enforced in
	    api.verify_rolls.validate_verified_transfer).
	custom_verified_rolls — Verified Roll Item rows: roll -> bin.

	Runs post_model_sync, so the Verified Roll Item doctype already exists.
	Idempotent (create_custom_fields updates in place).
	"""
	anchor = (
		"custom_roll_wise_pick_list"
		if frappe.db.exists("Custom Field", "Stock Entry-custom_roll_wise_pick_list")
		else "items"
	)
	create_custom_fields(
		{
			"Stock Entry": [
				{
					"fieldname": "custom_roll_verification_section",
					"fieldtype": "Section Break",
					"label": "Roll Verification",
					"insert_after": anchor,
					"collapsible": 1,
					"depends_on": "eval:doc.custom_verified_from_stock_entry",
				},
				{
					"fieldname": "custom_verified_from_stock_entry",
					"fieldtype": "Link",
					"label": "Verified From Stock Entry",
					"options": "Stock Entry",
					"insert_after": "custom_roll_verification_section",
					"read_only": 1,
					"no_copy": 1,
					"search_index": 1,
				},
				{
					"fieldname": "custom_verified_rolls",
					"fieldtype": "Table",
					"label": "Verified Rolls",
					"options": "Verified Roll Item",
					"insert_after": "custom_verified_from_stock_entry",
					"read_only": 1,
					"no_copy": 1,
				},
			]
		},
		update=True,
	)
