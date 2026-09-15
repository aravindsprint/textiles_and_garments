# textiles_and_garments/setup/install.py
"""
Post-install setup script for textiles_and_garments app.

Run via:  bench --site erp.pranera.in run-script
Or automatically called during: bench --site erp.pranera.in install-app textiles_and_garments

What this does:
  1. Adds the custom_roll_qi_entries Table field to Work Order (upgrade-safe via Custom Field).
  2. Adds custom_final_weight and custom_final_qty fields to Quality Inspection.
  3. Adds custom_roll Link field to Quality Inspection (the hook trigger).
"""

import frappe


def after_install():
    """Called by Frappe after the app is installed."""
    _add_work_order_fields()
    _add_quality_inspection_fields()
    frappe.db.commit()
    frappe.msgprint("textiles_and_garments: Custom fields created successfully.")


# ------------------------------------------------------------------
# Work Order — add the Roll QI Entries child table
# ------------------------------------------------------------------
def _add_work_order_fields():
    if frappe.db.exists("Custom Field", "Work Order-custom_roll_qi_entries"):
        print("  [SKIP] Work Order.custom_roll_qi_entries already exists.")
        return

    frappe.get_doc({
        "doctype": "Custom Field",
        "dt": "Work Order",
        "label": "Roll QI Entries",
        "fieldname": "custom_roll_qi_entries",
        "fieldtype": "Table",
        "options": "Work Order Roll QI Entry",
        "insert_after": "expected_delivery_date",
        "module": "Manufacturing"
    }).insert(ignore_permissions=True)
    print("  [OK] Added Work Order.custom_roll_qi_entries")


# ------------------------------------------------------------------
# Quality Inspection — add custom_roll, custom_final_weight, custom_final_qty
# ------------------------------------------------------------------
def _add_quality_inspection_fields():
    fields_to_add = [
        {
            "label": "Roll",
            "fieldname": "custom_roll",
            "fieldtype": "Link",
            "options": "Roll",
            "insert_after": "item_code",
            "description": "The Roll being inspected. Used by the QI submit hook to write back weight/qty."
        },
        {
            "label": "Final Weight (Kgs)",
            "fieldname": "custom_final_weight",
            "fieldtype": "Float",
            "insert_after": "custom_roll",
            "description": "Inspector-measured final weight. Written to Roll.roll_weight on QI submit (UOM=Kgs)."
        },
        {
            "label": "Final Qty (Pcs)",
            "fieldname": "custom_final_qty",
            "fieldtype": "Float",
            "insert_after": "custom_final_weight",
            "description": "Inspector-measured final qty. Written to Roll.total_qty on QI submit (UOM=Pcs)."
        }
    ]

    for fdef in fields_to_add:
        cf_name = f"Quality Inspection-{fdef['fieldname']}"
        if frappe.db.exists("Custom Field", cf_name):
            print(f"  [SKIP] Quality Inspection.{fdef['fieldname']} already exists.")
            continue

        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Quality Inspection",
            "module": "Manufacturing",
            **fdef
        }).insert(ignore_permissions=True)
        print(f"  [OK] Added Quality Inspection.{fdef['fieldname']}")