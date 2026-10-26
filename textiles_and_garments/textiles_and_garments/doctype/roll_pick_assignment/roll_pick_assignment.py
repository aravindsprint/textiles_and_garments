# Copyright (c) 2026, Pranera Services and Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt

# "To Work Order" picks may go up to this much over the Work Order's required
# qty per item (same ±3% the scan flow uses against Pick Qty).
WORK_ORDER_QTY_TOLERANCE = 0.03


class RollPickAssignment(Document):
	def validate(self):
		self.validate_batch_items_against_sales_order()
		self.validate_batch_items_against_work_order()
		self.set_pick_qty_from_batch_items()
		sync_scanned_roll_warehouses(self)
		self.set_total_weight_from_scanned_rolls()
		self.set_item_wise_weight_from_scanned_rolls()

	def before_update_after_submit(self):
		"""Rolls are scanned AFTER the Assignment is submitted, and saving a
		submitted doc skips validate(). Recompute the weight fields here too."""
		sync_scanned_roll_warehouses(self)
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

	def validate_batch_items_against_work_order(self):
		"""'To Work Order' picks: every Batch Items row must be for an item in
		the Work Order's Required Items, and per item, the qty across all its
		rows here (one item can be split over several batches) PLUS the qty
		already held by other non-cancelled 'To Work Order' assignments for the
		same Work Order must not exceed the required qty by more than
		WORK_ORDER_QTY_TOLERANCE. Under-picking is allowed, so one Work Order
		can still be split across several assignments."""
		if self.pick_type != "To Work Order" or not self.work_order:
			return

		if not self.batch_items:
			frappe.throw(
				_("Batch Items cannot be empty for a 'To Work Order' pick."),
				title=_("Batch Items Missing"),
			)

		required, uoms, _order = get_work_order_required_qty(self.work_order)

		this_qty = {}
		for row in self.batch_items:
			if not row.item:
				continue
			if row.item not in required:
				frappe.throw(
					_("Row #{0}: Item {1} (from Batch {2}) is not in the Required Items of Work Order {3}").format(
						row.idx,
						frappe.bold(row.item),
						frappe.bold(row.batch),
						frappe.bold(self.work_order),
					),
					title=_("Item Not In Work Order"),
				)
			this_qty[row.item] = this_qty.get(row.item, 0) + flt(row.qty)

		other_qty = get_work_order_assigned_qty(self.work_order, exclude=self.name)

		errors = []
		for item, qty in this_qty.items():
			req = required[item]
			others = other_qty.get(item, 0)
			total = qty + others
			allowed = req * (1 + WORK_ORDER_QTY_TOLERANCE)
			if total > allowed + 0.001:
				uom = uoms.get(item) or ""
				errors.append(
					_(
						"Item {0}: Work Order qty {1} {2} (max {3} {2} with {4}% tolerance). "
						"This assignment {5} {2} + other assignments {6} {2} = {7} {2}. Reduce by {8} {2}."
					).format(
						frappe.bold(item),
						flt(req, 3),
						uom,
						flt(allowed, 3),
						flt(WORK_ORDER_QTY_TOLERANCE * 100, 2),
						flt(qty, 3),
						flt(others, 3),
						frappe.bold(flt(total, 3)),
						flt(total - allowed, 3),
					)
				)

		if errors:
			frappe.throw("<br><br>".join(errors), title=_("Batch Qty exceeds Work Order Qty"))

	def set_pick_qty_from_batch_items(self):
		"""For 'From Batch' / 'To Sales Order' / 'To Work Order' picks, pick_qty
		is derived from the batch_items child table rather than entered directly."""
		if self.pick_type in ("From Batch", "To Sales Order", "To Work Order"):
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


# ---------------------------------------------------------------------------
# Scanned Rolls (In Progress) warehouse
#
# DEFAULT  -> each scanned roll takes the warehouse of the Batch Items row with
#             the same batch.
# OVERRIDE -> while the worker has changed the scan screen's Source Warehouse
#             (execution_source_warehouse != source_warehouse), newly scanned
#             rolls take the worker's warehouse and are stamped
#             warehouse_from_worker = 1, after which they are never overwritten.
# ---------------------------------------------------------------------------

def _batch_warehouse_map(doc):
	batch_wh = {}
	for bi in doc.get("batch_items") or []:
		batch = (bi.batch or "").strip()
		# first row wins if the same batch appears twice
		if batch and bi.warehouse and batch not in batch_wh:
			batch_wh[batch] = bi.warehouse
	return batch_wh


def update_source_warehouse_flag(doc):
	"""ON only while the worker has picked something other than the
	assignment's Source Warehouse. Switching back to the default turns it off."""
	doc.source_warehouse_changed = cint(
		bool(doc.execution_source_warehouse)
		and doc.execution_source_warehouse != doc.source_warehouse
	)


def sync_scanned_roll_warehouses(doc):
	"""Set warehouse on Scanned Rolls (In Progress) rows. Returns rows changed.

	Rows scanned before the worker changed the dropdown keep the batch
	warehouse; rows scanned while it was changed keep the worker's choice,
	even if the worker later switches back. Rows whose batch_no has no match
	in Batch Items are left as they are.
	"""
	update_source_warehouse_flag(doc)
	batch_wh = _batch_warehouse_map(doc)
	# Fields only exist after `bench migrate`; until then, skip the override
	# so scanning keeps working on the batch-warehouse default.
	can_override = frappe.get_meta("Roll Pick Assignment Scan").has_field("warehouse_from_worker")

	changed = 0
	for row in doc.get("scanned_rolls") or []:
		if cint(row.get("warehouse_from_worker")):
			continue

		if can_override and row.is_new() and doc.source_warehouse_changed:
			row.warehouse = doc.execution_source_warehouse
			row.warehouse_from_worker = 1
			changed += 1
			continue

		wh = batch_wh.get((row.batch_no or "").strip())
		if wh and row.warehouse != wh:
			row.warehouse = wh
			changed += 1
	return changed


def backfill_scanned_roll_warehouses(name=None):
	"""One-off fix for existing assignments. There's no record of which
	dropdown value was active when old rows were scanned, so they are all
	treated as default (Batch Items warehouse). Stamped rows are skipped.

	bench --site <site> execute \\
	  textiles_and_garments.textiles_and_garments.doctype.roll_pick_assignment.roll_pick_assignment.backfill_scanned_roll_warehouses \\
	  --kwargs "{'name': 'RPA-0810'}"
	"""
	filters = {"docstatus": ["<", 2]}
	if name:
		filters["name"] = name
	else:
		filters["name"] = ["in", frappe.get_all(
			"Roll Pick Assignment Scan",
			filters={"parenttype": "Roll Pick Assignment"},
			pluck="parent",
			distinct=True,
		) or [""]]

	names = frappe.get_all("Roll Pick Assignment", filters=filters, pluck="name")

	total = 0
	for n in names:
		doc = frappe.get_doc("Roll Pick Assignment", n)

		flag = cint(
			bool(doc.execution_source_warehouse)
			and doc.execution_source_warehouse != doc.source_warehouse
		)
		if cint(doc.get("source_warehouse_changed")) != flag:
			doc.db_set("source_warehouse_changed", flag, update_modified=False)

		batch_wh = _batch_warehouse_map(doc)
		for row in doc.scanned_rolls:
			if cint(row.get("warehouse_from_worker")):
				continue
			wh = batch_wh.get((row.batch_no or "").strip())
			if wh and row.warehouse != wh:
				row.db_set("warehouse", wh, update_modified=False)
				total += 1

	frappe.db.commit()
	print(f"Updated {total} scanned roll row(s) across {len(names)} assignment(s)")
	return total


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


# ---------------------------------------------------------------------------
# "To Work Order" picks
# ---------------------------------------------------------------------------

def get_work_order_required_qty(work_order):
	"""Required qty per item from the Work Order's Required Items (summed if
	an item appears on more than one row). Returns (qty_by_item,
	uom_by_item, items_in_row_order)."""
	required, uoms, order = {}, {}, []
	for r in frappe.get_all(
		"Work Order Item",
		filters={"parent": work_order, "parenttype": "Work Order"},
		fields=["item_code", "required_qty", "stock_uom"],
		order_by="idx asc",
	):
		if r.item_code not in required:
			required[r.item_code] = 0.0
			uoms[r.item_code] = r.stock_uom
			order.append(r.item_code)
		required[r.item_code] += flt(r.required_qty)
	return required, uoms, order


def get_work_order_assigned_qty(work_order, exclude=None):
	"""Batch Items qty per item already held by non-cancelled (draft or
	submitted) 'To Work Order' assignments for this Work Order, excluding
	`exclude`. Drafts count too, so two drafts can't both claim the full qty."""
	rows = frappe.db.sql(
		"""
		select bi.item as item, sum(bi.qty) as qty
		from `tabRoll Pick Batch Item` bi
		inner join `tabRoll Pick Assignment` rpa on rpa.name = bi.parent
		where bi.parenttype = 'Roll Pick Assignment'
			and rpa.work_order = %(work_order)s
			and rpa.pick_type = 'To Work Order'
			and rpa.docstatus < 2
			and rpa.name != %(exclude)s
		group by bi.item
		""",
		{"work_order": work_order, "exclude": exclude or ""},
		as_dict=True,
	)
	return {r.item: flt(r.qty) for r in rows}


@frappe.whitelist()
def get_work_order_items(work_order, current=None):
	"""Work Order Required Items with the qty still left to assign (required
	minus what other 'To Work Order' assignments already hold), in WO row
	order. Fully assigned items are skipped. Used by the form to pre-fill
	Batch Items for 'To Work Order' picks."""
	if not work_order:
		return []
	frappe.has_permission("Work Order", "read", doc=work_order, throw=True)

	required, uoms, order = get_work_order_required_qty(work_order)
	assigned = get_work_order_assigned_qty(work_order, exclude=current)

	out = []
	for item_code in order:
		remaining = flt(required[item_code] - assigned.get(item_code, 0), 3)
		if remaining > 0:
			out.append({
				"item_code": item_code,
				"stock_uom": uoms[item_code],
				"qty": remaining,
				"required_qty": flt(required[item_code], 3),
				"already_assigned": flt(assigned.get(item_code, 0), 3),
			})
	return out
