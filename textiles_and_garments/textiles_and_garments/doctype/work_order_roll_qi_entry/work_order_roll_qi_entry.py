# textiles_and_garments/doctype/work_order_roll_qi_entry/work_order_roll_qi_entry.py
"""
Controller for Work Order Roll QI Entry (child table DocType).

Validation rules:
  - A Roll must not appear more than once in the same Work Order's entries.
  - If a Quality Inspection is linked, its custom_roll must match this row's roll.

Note: 'item' field is Link → Item (not item_code / Data).
"""

import frappe
from frappe.model.document import Document


class WorkOrderRollQIEntry(Document):

    def validate(self):
        self._validate_no_duplicate_roll()
        self._validate_qi_roll_match()
        self._autofetch_item_from_roll()

    # ----------------------------------------------------------
    # Auto-fetch item from Roll if not already set
    # ----------------------------------------------------------
    def _autofetch_item_from_roll(self):
        if not self.roll:
            return
        if self.item:
            return  # already set

        # Roll.item_code → child table.item
        item = frappe.db.get_value("Roll", self.roll, "item_code")
        if item:
            self.item = item

    # ----------------------------------------------------------
    # Ensure the same Roll is not added twice in the parent WO
    # ----------------------------------------------------------
    def _validate_no_duplicate_roll(self):
        if not self.roll or not self.parent:
            return

        parent_doc = frappe.get_doc(self.parenttype, self.parent)
        roll_count = sum(
            1 for row in parent_doc.custom_roll_qi_entries
            if row.roll == self.roll and row.name != self.name
        )
        if roll_count > 0:
            frappe.throw(
                f"Roll <b>{self.roll}</b> is already listed in this Work Order's "
                "Roll QI Entries. Each Roll must appear only once."
            )

    # ----------------------------------------------------------
    # Warn if the linked QI belongs to a different Roll
    # ----------------------------------------------------------
    def _validate_qi_roll_match(self):
        if not self.quality_inspection or not self.roll:
            return

        qi_roll = frappe.db.get_value(
            "Quality Inspection", self.quality_inspection, "custom_roll"
        )
        if qi_roll and qi_roll != self.roll:
            frappe.throw(
                f"Quality Inspection <b>{self.quality_inspection}</b> is linked to "
                f"Roll <b>{qi_roll}</b>, but this row is for Roll <b>{self.roll}</b>. "
                "Please verify and correct the linkage."
            )