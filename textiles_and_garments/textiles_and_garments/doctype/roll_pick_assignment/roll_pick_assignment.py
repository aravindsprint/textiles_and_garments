# Copyright (c) 2026, Pranera Services and Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt


class RollPickAssignment(Document):
	def validate(self):
		self.validate_batch_items_against_sales_order()
		self.set_pick_qty_from_batch_items()
		self.set_total_weight_from_scanned_rolls()
		self.set_item_wise_weight_from_scanned_rolls()

	def before_update_after_submit(self):
		"""Rolls are scanned AFTER the Assignment is submitted, and saving a
		submitted doc skips validate(). Recompute the weight fields here too."""
		if not self.scanned_rolls:
			# Rolls are cleared once the final Pick Entry is created - keep the
			# last computed weights instead of wiping them to zero.
			return
		self.set_total_weight_from_scanned_rolls()
		self.set_item_wise_weight_from_scanned_rolls()

	def validate_batch_items_against_sales_order(self):
		"""'To Sales Order' picks: every Batch Items row must be for an item
		that is actually on the linked Sales Order. The form pre-fills one row
		per SO item and filters the Batch dropdown by that item, but Item is
		fetched from the chosen Batch, so this guards against a mismatched
		batch (or rows created via API) slipping through."""
		if self.pick_type != "To Sales Order" or not self.sales_order:
			return

		so_items = set(
			frappe.get_all(
				"Sales Order Item",
				filters={"parent": self.sales_order, "parenttype": "Sales Order"},
				pluck="item_code",
			)
		)
		for row in self.batch_items or []:
			if row.item and row.item not in so_items:
				frappe.throw(
					_("Row #{0}: Item {1} (from Batch {2}) is not in Sales Order {3}").format(
						row.idx,
						frappe.bold(row.item),
						frappe.bold(row.batch),
						frappe.bold(self.sales_order),
					),
					title=_("Item Not In Sales Order"),
				)

	def set_pick_qty_from_batch_items(self):
		"""For 'From Batch' / 'To Sales Order' picks, pick_qty is derived from the
		batch_items child table rather than entered directly."""
		if self.pick_type in ("From Batch", "To Sales Order"):
			self.pick_qty = flt(sum(flt(row.qty) for row in self.batch_items or []))

	def set_total_weight_from_scanned_rolls(self):
		"""Total Weight is always the physical roll weight summed across
		Scanned Rolls (In Progress) — unlike Qty (which is Pcs for
		piece-counted items and Kgs otherwise, so summing it directly would
		mix units), Roll Weight is a constant, UOM-independent measure
		fetched from the Roll doctype at scan time (see
		pranera_knit.api.pick_order.scan_pick_order_roll)."""
		self.total_weight = flt(sum(flt(row.roll_weight) for row in self.scanned_rolls or []), 3)

	def set_item_wise_weight_from_scanned_rolls(self):
		"""Item Wise Weight breaks Total Weight down by Item Code — same
		auto-computed-on-save pattern as Pick Qty (by UOM), just grouped by
		item instead of UOM. Rebuilt from scratch on every save (cheap:
		scanned_rolls is a handful of rows per Assignment, never hundreds),
		so it can never drift out of sync with scanned_rolls."""
		totals_by_item = {}
		order = []
		for row in self.scanned_rolls or []:
			if not row.item_code:
				continue
			if row.item_code not in totals_by_item:
				totals_by_item[row.item_code] = 0.0
				order.append(row.item_code)
			totals_by_item[row.item_code] += flt(row.roll_weight)

		self.set("item_wise_weight", [])
		for item_code in order:
			self.append("item_wise_weight", {
				"item_code": item_code,
				"total_weight": flt(totals_by_item[item_code], 3),
			})


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


@frappe.whitelist()
def get_warehouses_for_batch(doctype, txt, searchfield, start, page_len, filters):
	"""Link-field query for Roll Pick Batch Item.warehouse. Lists only
	warehouses that actually hold stock of the row's batch, with the
	available qty shown as the dropdown's description line — same
	"value + qty" style as the standard Batch No field. Balances are
	computed the same way roll_wise_pick_list.py's get_filtered_rolls()
	does: from Stock Ledger Entry (old-style sle.batch_no) plus Serial
	and Batch Entry (new-style bundles) — Bin doesn't split by batch, so
	neither source alone is complete."""
	filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})
	batch_no = filters.get("batch")
	if not batch_no:
		return []

	return frappe.db.sql(
		"""
		select warehouse, sum(qty) as qty
		from (
			select sle.warehouse as warehouse, sle.actual_qty as qty
			from `tabStock Ledger Entry` sle
			where sle.is_cancelled = 0
				and sle.docstatus = 1
				and sle.batch_no = %(batch_no)s
			union all
			select sbe.warehouse as warehouse, sbe.qty as qty
			from `tabSerial and Batch Entry` sbe
			inner join `tabStock Ledger Entry` sle on sle.serial_and_batch_bundle = sbe.parent
			where sle.is_cancelled = 0
				and sle.docstatus = 1
				and sbe.batch_no = %(batch_no)s
		) combined
		where warehouse like %(txt)s
		group by warehouse
		having sum(qty) > 0
		order by warehouse
		limit %(page_len)s offset %(start)s
		""",
		{
			"batch_no": batch_no,
			"txt": f"%{txt}%" if txt else "%",
			"start": cint(start),
			"page_len": cint(page_len),
		},
	)


@frappe.whitelist()
def get_batches_with_qty(doctype, txt, searchfield, start, page_len, filters):
	"""Link-field query for Roll Pick Batch Item.batch itself. Same
	"value + qty" dropdown style as get_warehouses_for_batch above (and the
	standard Batch No field) — shows each candidate batch's current total
	qty, summed across ALL warehouses (unlike get_warehouses_for_batch,
	which is scoped to one already-chosen batch), as the description line.

	This company has 100k+ Batch records and millions of Stock Ledger
	Entry / Serial and Batch Entry rows, so aggregating qty across the
	whole ledger for every Batch on every keystroke (a straight LEFT JOIN
	+ GROUP BY over all of them) is far too expensive to run inline in an
	autocomplete request — it doesn't error, it just hangs. Instead: find
	a bounded set of candidate batch names matching the search text first
	(cheap — Batch.name/batch_id are indexed), THEN look up qty only for
	those via an indexed `batch_no IN (...)` filter on Stock Ledger Entry /
	Serial and Batch Entry (both have batch_no indexed). Fetches a wider
	candidate window than page_len since some candidates may turn out to
	have 0 qty and get filtered out — so the final result can be shorter
	than page_len even when more matches exist; typing more of the batch
	name narrows it further."""
	filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})
	txt_like = f"%{txt}%" if txt else "%"
	page_len = cint(page_len) or 10

	candidates = frappe.db.sql(
		"""
		select name
		from `tabBatch`
		where disabled = 0
			and (name like %(txt)s or batch_id like %(txt)s)
			{item_condition}
		order by name
		limit %(candidate_limit)s offset %(start)s
		""".format(item_condition="and item = %(item)s" if filters.get("item") else ""),
		{
			"txt": txt_like,
			"item": filters.get("item"),
			"start": cint(start),
			"candidate_limit": page_len * 5,
		},
	)
	candidate_names = [row[0] for row in candidates]
	if not candidate_names:
		return []

	rows = frappe.db.sql(
		"""
		select batch_no, round(sum(qty), 3) as qty
		from (
			select sle.batch_no as batch_no, sle.actual_qty as qty
			from `tabStock Ledger Entry` sle
			where sle.is_cancelled = 0
				and sle.docstatus = 1
				and sle.batch_no in %(candidate_names)s
			union all
			select sbe.batch_no as batch_no, sbe.qty as qty
			from `tabSerial and Batch Entry` sbe
			inner join `tabStock Ledger Entry` sle on sle.serial_and_batch_bundle = sbe.parent
			where sle.is_cancelled = 0
				and sle.docstatus = 1
				and sbe.batch_no in %(candidate_names)s
		) combined
		group by batch_no
		having qty > 0
		order by batch_no
		limit %(page_len)s
		""",
		{
			"candidate_names": candidate_names,
			"page_len": page_len,
		},
	)

	return [(row[0], f"Qty: {row[1]}") for row in rows]


@frappe.whitelist()
def get_sales_order_items(sales_order):
	"""Distinct batch-tracked items on a Sales Order, in SO row order, with
	their total stock qty. Used by the form to pre-fill Batch Items for
	'To Sales Order' picks. Non-batch items are skipped because every
	Roll Pick Batch Item row requires a Batch."""
	if not sales_order:
		return []
	frappe.has_permission("Sales Order", "read", doc=sales_order, throw=True)

	rows = frappe.db.sql(
		"""
		select soi.item_code, soi.stock_uom, sum(soi.stock_qty) as stock_qty, min(soi.idx) as first_idx
		from `tabSales Order Item` soi
		inner join `tabItem` item on item.name = soi.item_code
		where soi.parent = %(sales_order)s
			and soi.parenttype = 'Sales Order'
			and item.has_batch_no = 1
		group by soi.item_code, soi.stock_uom
		order by first_idx
		""",
		{"sales_order": sales_order},
		as_dict=True,
	)
	return [
		{"item_code": r.item_code, "stock_uom": r.stock_uom, "stock_qty": flt(r.stock_qty, 3)}
		for r in rows
	]
