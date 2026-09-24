# Copyright (c) 2026, Pranera Services and Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt


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
	Balances are computed the same way: Stock Ledger Entry (old-style
	batch_no) plus Serial and Batch Entry (new-style bundles)."""
	filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})
	txt_like = f"%{txt}%" if txt else "%"

	rows = frappe.db.sql(
		"""
		select b.name, round(coalesce(sum(qty_source.qty), 0), 3) as qty
		from `tabBatch` b
		left join (
			select sle.batch_no as batch_no, sle.actual_qty as qty
			from `tabStock Ledger Entry` sle
			where sle.is_cancelled = 0
				and sle.docstatus = 1
			union all
			select sbe.batch_no as batch_no, sbe.qty as qty
			from `tabSerial and Batch Entry` sbe
			inner join `tabStock Ledger Entry` sle on sle.serial_and_batch_bundle = sbe.parent
			where sle.is_cancelled = 0
				and sle.docstatus = 1
		) qty_source on qty_source.batch_no = b.name
		where b.disabled = 0
			and (b.name like %(txt)s or b.batch_id like %(txt)s)
		group by b.name
		having qty > 0
		order by b.name
		limit %(page_len)s offset %(start)s
		""",
		{
			"txt": txt_like,
			"start": cint(start),
			"page_len": cint(page_len),
		},
	)

	return [(row[0], f"Qty: {row[1]}") for row in rows]
