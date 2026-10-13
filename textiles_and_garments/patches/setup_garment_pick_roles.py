"""Create the roles used by Garment Pick Assignment.

* Garment Sales  - creates / submits / cancels Garment Pick Assignments
* Garment Picker - reads the assignments they are asked to pick

Idempotent - safe to re-run.
"""

import frappe

ROLES = ("Garment Sales", "Garment Picker")


def execute():
	for role in ROLES:
		if frappe.db.exists("Role", role):
			continue
		frappe.get_doc(
			{
				"doctype": "Role",
				"role_name": role,
				"desk_access": 1,
			}
		).insert(ignore_permissions=True)

	frappe.clear_cache()
