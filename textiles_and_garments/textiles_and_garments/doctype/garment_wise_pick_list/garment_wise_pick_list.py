# Copyright (c) 2026, Pranera Services and Solutions Pvt Ltd and contributors
# For license information, please see license.txt

"""Garment Wise Pick List — same as Roll Wise Pick List, but garments have no
batch / roll, so there is one item table (Garment Wise Pick Item: Item Code,
Warehouse, Stock UOM, Qty) and no roll-weight / batch-wise totals."""

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class GarmentWisePickList(Document):
	def validate(self):
		self.total_qty = flt(sum(flt(d.qty) for d in self.garment_wise_pick_item), 3)


@frappe.whitelist()
def get_filtered_items(warehouse):
	"""Garment equivalent of Roll Wise Pick List's get_filtered_rolls: items
	with stock in `warehouse`. Garments aren't batch-tracked, so Bin holds the
	full balance per Item + Warehouse."""
	if not warehouse:
		return []

	return frappe.db.sql(
		"""
		select bin.item_code, item.item_name, item.stock_uom, round(bin.actual_qty, 3) as actual_qty
		from `tabBin` bin
		inner join `tabItem` item on item.name = bin.item_code
		where bin.warehouse = %(warehouse)s
			and bin.actual_qty > 0
			and item.disabled = 0
			and item.has_batch_no = 0
		order by bin.item_code
		""",
		{"warehouse": warehouse},
		as_dict=True,
	)
