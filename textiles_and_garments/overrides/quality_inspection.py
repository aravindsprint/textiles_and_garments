# textiles_and_garments/overrides/quality_inspection.py
"""
Quality Inspection Submit / Cancel Hooks
-----------------------------------------
Triggered via hooks.py on QI submit and cancel.

On Submit:
  - Reads custom_roll from the QI document.
  - Updates roll_weight (if UOM = Kgs) or total_qty (if UOM = Pcs) on the Roll DocType.
  - Syncs qi_status = QI.status back to the matching child-table row on the Work Order.

On Cancel:
  - Resets qi_status = "Pending" on the matching child-table row.
  - Does NOT revert roll_weight / total_qty (weight data is retained).

Roll DocType fields used:
  - roll.item         (Link → Item)
  - roll.roll_weight  (Float)
  - roll.total_qty    (Float)
  - roll.uom          (Link → UOM)
"""

import frappe


# ==================================================================
# Public hooks (called by ERPNext event system)
# ==================================================================

def update_roll_weight_on_qi_submit(doc, method):
    """
    Triggered on Quality Inspection submit.

    Finds the Roll linked via doc.custom_roll and updates:
      - roll.roll_weight  → when roll.uom == "Kgs"
      - roll.total_qty    → when roll.uom == "Pcs"

    Reads the measured values from:
      - doc.custom_final_weight  (for Kgs)
      - doc.custom_final_qty     (for Pcs)

    Falls back to the existing Roll value if those fields are blank.
    Also syncs QI status back to the Work Order child-table row.
    """
    if not doc.custom_roll:
        frappe.log_error(
            f"QI {doc.name}: custom_roll is not set. Skipping roll weight update.",
            "WO Roll QI — Missing Roll"
        )
        return

    roll = frappe.get_doc("Roll", doc.custom_roll)

    # Roll DocType actual fieldnames: stock_uom (not uom), item_code (not item)
    if roll.stock_uom == "Kgs":
        new_weight = doc.get("custom_final_weight") or roll.roll_weight
        roll.roll_weight = new_weight
        frappe.logger().info(
            f"QI {doc.name}: Updating Roll {roll.name} roll_weight → {new_weight} Kgs"
        )
    elif roll.stock_uom == "Pcs":
        new_qty = doc.get("custom_final_qty") or roll.total_qty
        roll.total_qty = new_qty
        frappe.logger().info(
            f"QI {doc.name}: Updating Roll {roll.name} total_qty → {new_qty} Pcs"
        )
    else:
        frappe.log_error(
            f"QI {doc.name}: Unrecognised stock_uom '{roll.stock_uom}' on Roll {roll.name}. "
            "Expected 'Kgs' or 'Pcs'. No update performed.",
            "WO Roll QI — Unknown UOM"
        )
        return

    roll.flags.ignore_permissions = True
    roll.save()
    frappe.db.commit()

    # Sync QI status back to Work Order child table
    _sync_qi_status_to_work_order(
        roll_name=doc.custom_roll,
        qi_name=doc.name,
        status=doc.status          # "Accepted" or "Rejected"
    )

    # Sync item field on the child-table row (in case it was missing)
    _sync_item_to_work_order(
        roll_name=doc.custom_roll,
        qi_name=doc.name,
        item=roll.item_code       # Roll.item_code → child table.item
    )


def revert_roll_weight_on_qi_cancel(doc, method):
    """
    Triggered on Quality Inspection cancel.

    Resets qi_status to "Pending" on the Work Order child-table row.
    Roll weight / qty are intentionally NOT reverted.
    """
    if not doc.custom_roll:
        return

    _sync_qi_status_to_work_order(
        roll_name=doc.custom_roll,
        qi_name=doc.name,
        status="Pending"
    )


# ==================================================================
# Private helpers
# ==================================================================

def _sync_qi_status_to_work_order(roll_name, qi_name, status):
    """
    Locates the Work Order Roll QI Entry child-table row(s) that match
    both roll and quality_inspection, then sets qi_status.

    Uses frappe.db.set_value for a lightweight single-field update
    (avoids loading the full child document).
    """
    wo_rows = frappe.get_all(
        "Work Order Roll QI Entry",
        filters={
            "roll": roll_name,
            "quality_inspection": qi_name
        },
        fields=["name", "parent"]
    )

    if not wo_rows:
        frappe.log_error(
            f"No Work Order Roll QI Entry found for Roll={roll_name}, QI={qi_name}. "
            "qi_status not synced.",
            "WO Roll QI — Row Not Found"
        )
        return

    for row in wo_rows:
        frappe.db.set_value(
            "Work Order Roll QI Entry",
            row["name"],
            "qi_status",
            status
        )
        frappe.logger().info(
            f"Synced qi_status='{status}' on WO {row['parent']} "
            f"child row {row['name']} (Roll={roll_name}, QI={qi_name})"
        )

    frappe.db.commit()


def _sync_item_to_work_order(roll_name, qi_name, item):
    """
    Backfills the 'item' field (Link → Item) on the child-table row
    if it is blank. Uses the item fetched from the Roll DocType.
    """
    if not item:
        return

    wo_rows = frappe.get_all(
        "Work Order Roll QI Entry",
        filters={
            "roll": roll_name,
            "quality_inspection": qi_name,
            "item": ["in", ["", None]]   # only update if blank
        },
        fields=["name"]
    )

    for row in wo_rows:
        frappe.db.set_value(
            "Work Order Roll QI Entry",
            row["name"],
            "item",
            item
        )

    if wo_rows:
        frappe.db.commit()