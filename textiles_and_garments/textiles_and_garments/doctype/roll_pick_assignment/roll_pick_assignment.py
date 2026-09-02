# Copyright (c) 2026, Pranera Services and Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class RollPickAssignment(Document):
	def validate(self):
		self.set_pick_qty_from_batch_items()

	def set_pick_qty_from_batch_items(self):
		"""For 'From Batch' / 'To Sales Order' picks, pick_qty is derived from the
		batch_items child table rather than entered directly."""
		if self.pick_type in ("From Batch", "To Sales Order"):
			self.pick_qty = flt(sum(flt(row.qty) for row in self.batch_items or []))
