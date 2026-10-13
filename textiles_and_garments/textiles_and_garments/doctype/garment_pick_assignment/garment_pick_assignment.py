# Copyright (c) 2026, Pranera Services and Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt


class GarmentPickAssignment(Document):
	"""Garment counterpart of Roll Pick Assignment. Garment items are not
	batch / roll tracked, so a pick is just Item + Warehouse + Stock UOM + Qty
	(see Garment Wise Pick Item) — no batch selection, no roll scanning and
	no roll weight totals."""

	def validate(self):
		self.set_default_item_warehouse()
		self.validate_items()
		self.validate_items_against_sales_order()
		self.set_totals_from_items()
		self.set_warehouse_addresses()

	def set_default_item_warehouse(self):
		"""Rows left without a Warehouse are picked from the header Source Warehouse."""
		for row in self.items or []:
			if not row.warehouse and self.source_warehouse:
				row.warehouse = self.source_warehouse

	def validate_items(self):
		for row in self.items or []:
			if flt(row.qty) <= 0:
				frappe.throw(
					_("Row #{0}: Qty for Item {1} must be greater than zero").format(
						row.idx, frappe.bold(row.item_code)
					),
					title=_("Invalid Qty"),
				)
			if not row.stock_uom and row.item_code:
				row.stock_uom = frappe.get_cached_value("Item", row.item_code, "stock_uom")

	def validate_items_against_sales_order(self):
		"""'To Sales Order' picks: every Items row must be for an item that is
		actually on the linked Sales Order. The form pre-fills one row per SO
		item, but this guards against rows edited by hand or created via API."""
		if self.pick_type != "To Sales Order" or not self.sales_order:
			return

		so_items = set(
			frappe.get_all(
				"Sales Order Item",
				filters={"parent": self.sales_order, "parenttype": "Sales Order"},
				pluck="item_code",
			)
		)
		for row in self.items or []:
			if row.item_code and row.item_code not in so_items:
				frappe.throw(
					_("Row #{0}: Item {1} is not in Sales Order {2}").format(
						row.idx,
						frappe.bold(row.item_code),
						frappe.bold(self.sales_order),
					),
					title=_("Item Not In Sales Order"),
				)

	def set_totals_from_items(self):
		"""Total Qty is always the sum of the Items table. When the table has
		rows, Pick Qty follows it too (same as Roll Pick Assignment deriving
		pick_qty from batch_items); otherwise the entered Pick Qty is kept."""
		self.total_qty = flt(sum(flt(row.qty) for row in self.items or []), 3)
		if self.items:
			self.pick_qty = self.total_qty

	def set_warehouse_addresses(self):
		self.source_warehouse_address = get_warehouse_address(self.source_warehouse)
		self.target_warehouse_address = get_warehouse_address(self.target_warehouse)


def get_warehouse_address(warehouse):
	if not warehouse:
		return None
	return frappe.db.get_value(
		"Dynamic Link",
		{"link_doctype": "Warehouse", "link_name": warehouse, "parenttype": "Address"},
		"parent",
	)


@frappe.whitelist()
def get_work_order_available_item(work_order, source_warehouse):
	"""For 'From Work Order' picks: the Work Order's finished garment item and
	how much of it can be picked from source_warehouse right now — the lower of
	the Work Order's produced qty and the item's actual stock (Bin) in that
	warehouse. Garments have no batch, so Bin is the right source (unlike the
	roll version, which sums the manufactured batches)."""
	if not (work_order and source_warehouse):
		return {}

	wo = frappe.db.get_value(
		"Work Order", work_order, ["production_item", "stock_uom", "produced_qty"], as_dict=True
	)
	if not wo:
		return {}

	actual_qty = flt(
		frappe.db.get_value(
			"Bin", {"item_code": wo.production_item, "warehouse": source_warehouse}, "actual_qty"
		)
	)
	return {
		"item_code": wo.production_item,
		"stock_uom": wo.stock_uom,
		"warehouse": source_warehouse,
		"qty": flt(max(min(flt(wo.produced_qty), actual_qty), 0), 3),
	}


@frappe.whitelist()
def get_warehouses_for_item(doctype, txt, searchfield, start, page_len, filters):
	"""Link-field query for Garment Wise Pick Item.warehouse. Lists only
	warehouses that hold stock of the row's item, with the available qty as the
	dropdown's description line. Garments aren't batch-tracked, so Bin is
	complete and cheap (indexed by item_code + warehouse)."""
	filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})
	item_code = filters.get("item_code")
	if not item_code:
		return []

	return frappe.db.sql(
		"""
		select warehouse, concat('Qty: ', round(actual_qty, 3))
		from `tabBin`
		where item_code = %(item_code)s
			and actual_qty > 0
			and warehouse like %(txt)s
		order by warehouse
		limit %(page_len)s offset %(start)s
		""",
		{
			"item_code": item_code,
			"txt": f"%{txt}%" if txt else "%",
			"start": cint(start),
			"page_len": cint(page_len) or 20,
		},
	)


@frappe.whitelist()
def get_sales_order_items(sales_order):
	"""Distinct stock items on a Sales Order, in SO row order, with the
	still-to-deliver qty in stock UOM. Used by the form to pre-fill Items for
	'To Sales Order' picks. Unlike the roll version there's no batch filter —
	any stock item can be picked."""
	if not sales_order:
		return []
	frappe.has_permission("Sales Order", "read", doc=sales_order, throw=True)

	rows = frappe.db.sql(
		"""
		select
			soi.item_code,
			soi.stock_uom,
			sum(greatest(soi.qty - ifnull(soi.delivered_qty, 0), 0) * ifnull(soi.conversion_factor, 1)) as pending_qty,
			min(soi.warehouse) as warehouse,
			min(soi.idx) as first_idx
		from `tabSales Order Item` soi
		inner join `tabItem` item on item.name = soi.item_code
		where soi.parent = %(sales_order)s
			and soi.parenttype = 'Sales Order'
			and item.is_stock_item = 1
		group by soi.item_code, soi.stock_uom
		order by first_idx
		""",
		{"sales_order": sales_order},
		as_dict=True,
	)
	return [
		{
			"item_code": r.item_code,
			"stock_uom": r.stock_uom,
			"qty": flt(r.pending_qty, 3),
			"warehouse": r.warehouse,
		}
		for r in rows
	]
