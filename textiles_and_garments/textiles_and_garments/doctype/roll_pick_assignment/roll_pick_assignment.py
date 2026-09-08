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


@frappe.whitelist()
def get_manufactured_batch_available_qty(work_order, source_warehouse):
	"""Total qty still available in source_warehouse across the batch(es) created as
	the finished-item output of this Work Order's Manufacture Stock Entries.
	Used to auto-set Pick Qty for 'From Work Order' picks."""
	if not (work_order and source_warehouse):
		return 0

	batch_rows = frappe.db.sql(
		"""
		select distinct sed.batch_no
		from `tabStock Entry Detail` sed
		inner join `tabStock Entry` se on se.name = sed.parent
		where se.work_order = %s
			and se.purpose = 'Manufacture'
			and se.docstatus = 1
			and sed.is_finished_item = 1
			and ifnull(sed.batch_no, '') != ''
		""",
		work_order,
		as_dict=True,
	)

	if not batch_rows:
		return 0

	get_batch_qty = frappe.get_attr("erpnext.stock.doctype.batch.batch.get_batch_qty")
	total = sum(flt(get_batch_qty(batch_no=row.batch_no, warehouse=source_warehouse)) for row in batch_rows)
	return flt(total, 3)
