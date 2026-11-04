# Copyright (c) 2026, Arkotrix and contributors
# For license information, please see license.txt
#
# Project Operation Status
# ------------------------
# Every document line linked to a Project:
#   Material Request -> Purchase Order -> Purchase Receipt
#   Subcontracting Order (FG) -> SCO Raw Material Supply -> Subcontracting Receipt
#   Work Order -> Job Card -> Stock Entry
# shown as Ordered / Completed / Pending qty.
#
# Group By = Item (default):      Item  > Operation > Document line
# Group By = Operation:           Operation > Document line
#
# Project matching uses the ITEM-level project first and falls back to the
# header-level project only when the item project is blank (header project is
# often empty on PO / SCO at Pranera).

import json

import frappe
from frappe import _
from frappe.utils import flt

OPERATIONS = [
	"Material Request",
	"Purchase Order",
	"Purchase Receipt",
	"Subcontracting Order",
	"SCO Raw Material Supply",
	"Subcontracting Receipt",
	"Work Order",
	"Job Card",
	"Stock Entry",
]

# Operations that only record completed movement (no "ordered" side)
RECEIPT_TYPE = {"Purchase Receipt", "Subcontracting Receipt", "Stock Entry"}

QTY_KEYS = ("ordered_qty", "completed_qty", "pending_qty", "rejected_qty", "returned_qty", "other_qty")


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.project:
		frappe.throw(_("Please select a Project"))

	selected = filters.get("operation") or []
	if isinstance(selected, str):
		selected = json.loads(selected) if selected.startswith("[") else [selected]
	selected = selected or OPERATIONS

	fetchers = {
		"Material Request": get_material_requests,
		"Purchase Order": get_purchase_orders,
		"Purchase Receipt": get_purchase_receipts,
		"Subcontracting Order": get_subcontracting_orders,
		"SCO Raw Material Supply": get_sco_supplied_items,
		"Subcontracting Receipt": get_subcontracting_receipts,
		"Work Order": get_work_orders,
		"Job Card": get_job_cards,
		"Stock Entry": get_stock_entries,
	}

	rows_by_op, summary = {}, []
	for op in OPERATIONS:
		if op not in selected:
			continue
		if filters.pending_only and op in RECEIPT_TYPE:
			continue

		rows = fetchers[op](filters)
		if filters.pending_only:
			rows = [r for r in rows if flt(r.pending_qty) > 0]
		if not rows:
			continue

		for r in rows:
			r.completion_pct = pct(r.completed_qty, r.ordered_qty)
		rows_by_op[op] = rows
		summary.append(make_group(op, rows))

	if (filters.group_by or "Item") == "Operation":
		data = build_operation_tree(rows_by_op)
	else:
		data = build_item_tree(rows_by_op)

	return get_columns(), data, None, get_chart(summary), get_report_summary(summary)


# --------------------------------------------------------------------------- #
# Tree builders
# --------------------------------------------------------------------------- #
def build_item_tree(rows_by_op):
	"""Item > Operation > Document line"""
	# Stock Entries are split by type (Material Transfer / Manufacture / ...) so
	# transfer + consumption of the same qty is not summed into one figure.
	items = {}
	for op in OPERATIONS:
		for r in rows_by_op.get(op, []):
			label = f"{op} ({r.sub_type})" if op == "Stock Entry" and r.sub_type else op
			items.setdefault(r.item_code or "", {}).setdefault(label, []).append(r)

	data = []
	for item_code in sorted(items):
		ops = items[item_code]
		first = list(ops.values())[0][0]
		item_key = f"ITEM::{item_code}"
		pending_ops = [op for op, rows in ops.items() if sum(flt(r.pending_qty) for r in rows) > 0]

		data.append(
			frappe._dict(
				particulars=item_code or _("(No Item)"),
				item_code=item_code,
				item_name=first.item_name,
				row_key=item_key,
				parent_key=None,
				indent=0,
				is_group=1,
				status=_("Pending: {0}").format(", ".join(pending_ops)) if pending_ops else _("Completed"),
			)
		)

		for label, rows in ops.items():
			op = rows[0].operation
			op_key = f"{item_key}::{label}"
			group = make_group(op, rows)
			group.update(
				particulars=label,
				item_code=item_code,
				item_name=first.item_name,
				uom=rows[0].uom,
				row_key=op_key,
				parent_key=item_key,
				indent=1,
			)
			data.append(group)

			for r in rows:
				data.append(as_line(r, op_key, 2))

	return data


def build_operation_tree(rows_by_op):
	"""Operation > Document line"""
	data = []
	for op in OPERATIONS:
		rows = rows_by_op.get(op)
		if not rows:
			continue
		group = make_group(op, rows)
		group.update(particulars=op, row_key=op, parent_key=None, indent=0)
		data.append(group)
		for r in rows:
			data.append(as_line(r, op, 1))
	return data


def as_line(r, parent_key, indent):
	r = frappe._dict(r)
	r.particulars = r.document
	r.parent_key = parent_key
	r.indent = indent
	r.row_key = f"{parent_key}::{r.document}::{r.get('row_name') or r.item_code}"
	return r


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def pct(done, total):
	return round(flt(done) * 100.0 / flt(total), 2) if flt(total) else None


def make_group(op, rows):
	totals = {k: sum(flt(r.get(k)) for r in rows) for k in QTY_KEYS}
	if op in RECEIPT_TYPE:
		totals["ordered_qty"] = None
		totals["pending_qty"] = None

	docs = {r.document for r in rows}
	open_docs = {r.document for r in rows if flt(r.pending_qty) > 0}
	return frappe._dict(
		operation=op,
		is_group=1,
		document=_("{0} doc(s)").format(len(docs)),
		completion_pct=pct(totals["completed_qty"], totals["ordered_qty"]),
		open_docs=len(open_docs),
		status=(_("{0} open").format(len(open_docs)) if open_docs else _("Completed"))
		if op not in RECEIPT_TYPE
		else None,
		**totals,
	)


def conditions(filters, parent, date_field, item_field, always_include_draft=False):
	cond = []
	if filters.include_draft or always_include_draft:
		cond.append(f"{parent}.docstatus < 2")
	else:
		cond.append(f"{parent}.docstatus = 1")
	if filters.company:
		cond.append(f"{parent}.company = %(company)s")
	if filters.from_date:
		cond.append(f"{date_field} >= %(from_date)s")
	if filters.to_date:
		cond.append(f"{date_field} <= %(to_date)s")
	if filters.item_code and item_field:
		cond.append(f"{item_field} = %(item_code)s")
	return " AND " + " AND ".join(cond)


def project_match(item_alias, item_dt, parent_alias, parent_dt):
	"""Item-level project first, header-level project as fallback.

	Only uses columns that exist on this site: the header `project` field is a
	custom field on some benches (e.g. Material Request) and absent on others.
	"""
	has_item = bool(item_dt) and frappe.db.has_column(item_dt, "project")
	has_parent = bool(parent_dt) and frappe.db.has_column(parent_dt, "project")

	if has_item and has_parent:
		return (
			f"({item_alias}.project = %(project)s"
			f" OR (IFNULL({item_alias}.project, '') = '' AND {parent_alias}.project = %(project)s))"
		)
	if has_item:
		return f"{item_alias}.project = %(project)s"
	if has_parent:
		return f"{parent_alias}.project = %(project)s"
	return "1 = 0"


def run(sql, filters):
	return frappe.db.sql(sql, filters, as_dict=True)


# --------------------------------------------------------------------------- #
# Fetchers — every query returns the same column set
# --------------------------------------------------------------------------- #
def get_material_requests(filters):
	cond = conditions(filters, "mr", "mr.transaction_date", "mri.item_code")
	return run(
		f"""
		SELECT 'Material Request' AS operation, 'Material Request' AS doctype,
			mr.name AS document, mri.name AS row_name, mr.transaction_date AS posting_date,
			mr.material_request_type AS sub_type, NULL AS party, NULL AS against,
			mri.item_code, mri.item_name, mri.warehouse, mri.stock_uom AS uom,
			mri.stock_qty AS ordered_qty,
			mri.ordered_qty AS completed_qty,
			GREATEST(mri.stock_qty - mri.ordered_qty, 0) AS pending_qty,
			0 AS rejected_qty, 0 AS returned_qty,
			mri.received_qty AS other_qty,
			mr.status
		FROM `tabMaterial Request Item` mri
		INNER JOIN `tabMaterial Request` mr ON mr.name = mri.parent
		WHERE {project_match("mri", "Material Request Item", "mr", "Material Request")}
			{cond}
		ORDER BY mr.transaction_date, mr.name, mri.idx
		""",
		filters,
	)


def get_purchase_orders(filters):
	# Subcontracted POs are covered by the Subcontracting Order section
	cond = conditions(filters, "po", "po.transaction_date", "poi.item_code")
	return run(
		f"""
		SELECT 'Purchase Order' AS operation, 'Purchase Order' AS doctype,
			po.name AS document, poi.name AS row_name, po.transaction_date AS posting_date,
			'Purchase' AS sub_type, po.supplier AS party, poi.material_request AS against,
			poi.item_code, poi.item_name, poi.warehouse, poi.stock_uom AS uom,
			poi.stock_qty AS ordered_qty,
			poi.received_qty AS completed_qty,
			GREATEST(poi.stock_qty - poi.received_qty, 0) AS pending_qty,
			0 AS rejected_qty, poi.returned_qty,
			0 AS other_qty,
			po.status
		FROM `tabPurchase Order Item` poi
		INNER JOIN `tabPurchase Order` po ON po.name = poi.parent
		WHERE IFNULL(po.is_subcontracted, 0) = 0
			AND {project_match("poi", "Purchase Order Item", "po", "Purchase Order")}
			{cond}
		ORDER BY po.transaction_date, po.name, poi.idx
		""",
		filters,
	)


def get_purchase_receipts(filters):
	cond = conditions(filters, "pr", "pr.posting_date", "pri.item_code")
	return run(
		f"""
		SELECT 'Purchase Receipt' AS operation, 'Purchase Receipt' AS doctype,
			pr.name AS document, pri.name AS row_name, pr.posting_date,
			IF(pr.is_return = 1, 'Return', 'Receipt') AS sub_type,
			pr.supplier AS party, pri.purchase_order AS against,
			pri.item_code, pri.item_name, pri.warehouse, pri.stock_uom AS uom,
			NULL AS ordered_qty,
			pri.stock_qty AS completed_qty,
			NULL AS pending_qty,
			pri.rejected_qty * IFNULL(pri.conversion_factor, 1) AS rejected_qty,
			pri.returned_qty,
			pri.received_stock_qty AS other_qty,
			pr.status
		FROM `tabPurchase Receipt Item` pri
		INNER JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
		WHERE {project_match("pri", "Purchase Receipt Item", "pr", "Purchase Receipt")}
			{cond}
		ORDER BY pr.posting_date, pr.name, pri.idx
		""",
		filters,
	)


def get_subcontracting_orders(filters):
	cond = conditions(filters, "sco", "sco.transaction_date", "scoi.item_code")
	return run(
		f"""
		SELECT 'Subcontracting Order' AS operation, 'Subcontracting Order' AS doctype,
			sco.name AS document, scoi.name AS row_name, sco.transaction_date AS posting_date,
			'Finished Goods' AS sub_type, sco.supplier AS party, sco.purchase_order AS against,
			scoi.item_code, scoi.item_name, scoi.warehouse, scoi.stock_uom AS uom,
			scoi.qty AS ordered_qty,
			scoi.received_qty AS completed_qty,
			GREATEST(scoi.qty - scoi.received_qty, 0) AS pending_qty,
			0 AS rejected_qty, scoi.returned_qty,
			0 AS other_qty,
			sco.status
		FROM `tabSubcontracting Order Item` scoi
		INNER JOIN `tabSubcontracting Order` sco ON sco.name = scoi.parent
		WHERE {project_match("scoi", "Subcontracting Order Item", "sco", "Subcontracting Order")}
			{cond}
		ORDER BY sco.transaction_date, sco.name, scoi.idx
		""",
		filters,
	)


def get_sco_supplied_items(filters):
	# Raw material sent to the subcontractor; project comes from the FG row it belongs to
	cond = conditions(filters, "sco", "sco.transaction_date", "si.rm_item_code")
	return run(
		f"""
		SELECT 'SCO Raw Material Supply' AS operation, 'Subcontracting Order' AS doctype,
			sco.name AS document, si.name AS row_name, sco.transaction_date AS posting_date,
			CONCAT('RM for ', si.main_item_code) AS sub_type, sco.supplier AS party,
			sco.purchase_order AS against,
			si.rm_item_code AS item_code, rm.item_name, NULL AS warehouse, si.stock_uom AS uom,
			si.required_qty AS ordered_qty,
			si.supplied_qty AS completed_qty,
			GREATEST(si.required_qty - si.supplied_qty, 0) AS pending_qty,
			0 AS rejected_qty, si.returned_qty,
			si.consumed_qty AS other_qty,
			sco.status
		FROM `tabSubcontracting Order Supplied Item` si
		INNER JOIN `tabSubcontracting Order` sco ON sco.name = si.parent
		LEFT JOIN `tabSubcontracting Order Item` scoi ON scoi.name = si.reference_name
		LEFT JOIN `tabItem` rm ON rm.name = si.rm_item_code
		WHERE {project_match("scoi", "Subcontracting Order Item", "sco", "Subcontracting Order")}
			{cond}
		ORDER BY sco.transaction_date, sco.name, si.idx
		""",
		filters,
	)


def get_subcontracting_receipts(filters):
	cond = conditions(filters, "scr", "scr.posting_date", "scri.item_code")
	return run(
		f"""
		SELECT 'Subcontracting Receipt' AS operation, 'Subcontracting Receipt' AS doctype,
			scr.name AS document, scri.name AS row_name, scr.posting_date,
			IF(scr.is_return = 1, 'Return', 'Receipt') AS sub_type,
			scr.supplier AS party, scri.subcontracting_order AS against,
			scri.item_code, scri.item_name, scri.warehouse, scri.stock_uom AS uom,
			NULL AS ordered_qty,
			scri.qty AS completed_qty,
			NULL AS pending_qty,
			scri.rejected_qty, scri.returned_qty,
			scri.received_qty AS other_qty,
			scr.status
		FROM `tabSubcontracting Receipt Item` scri
		INNER JOIN `tabSubcontracting Receipt` scr ON scr.name = scri.parent
		WHERE {project_match("scri", "Subcontracting Receipt Item", "scr", "Subcontracting Receipt")}
			{cond}
		ORDER BY scr.posting_date, scr.name, scri.idx
		""",
		filters,
	)


def get_work_orders(filters):
	cond = conditions(filters, "wo", "DATE(wo.planned_start_date)", "wo.production_item")
	return run(
		f"""
		SELECT 'Work Order' AS operation, 'Work Order' AS doctype,
			wo.name AS document, wo.name AS row_name, DATE(wo.planned_start_date) AS posting_date,
			NULL AS sub_type, NULL AS party, wo.sales_order AS against,
			wo.production_item AS item_code, wo.item_name, wo.fg_warehouse AS warehouse,
			wo.stock_uom AS uom,
			wo.qty AS ordered_qty,
			wo.produced_qty AS completed_qty,
			GREATEST(wo.qty - wo.produced_qty - IFNULL(wo.process_loss_qty, 0), 0) AS pending_qty,
			IFNULL(wo.process_loss_qty, 0) AS rejected_qty, 0 AS returned_qty,
			wo.material_transferred_for_manufacturing AS other_qty,
			wo.status
		FROM `tabWork Order` wo
		WHERE {project_match(None, None, "wo", "Work Order")}
			{cond}
		ORDER BY wo.planned_start_date, wo.name
		""",
		filters,
	)


def get_job_cards(filters):
	# Job Cards stay in draft until completed, so drafts are always included
	cond = conditions(filters, "jc", "jc.posting_date", "jc.production_item", always_include_draft=True)
	return run(
		f"""
		SELECT 'Job Card' AS operation, 'Job Card' AS doctype,
			jc.name AS document, jc.name AS row_name, jc.posting_date,
			CONCAT_WS(' @ ', jc.operation, jc.workstation) AS sub_type,
			NULL AS party, jc.work_order AS against,
			jc.production_item AS item_code, jc.item_name, NULL AS warehouse,
			wo.stock_uom AS uom,
			jc.for_quantity AS ordered_qty,
			jc.total_completed_qty AS completed_qty,
			GREATEST(jc.for_quantity - jc.total_completed_qty - IFNULL(jc.process_loss_qty, 0), 0)
				AS pending_qty,
			IFNULL(jc.process_loss_qty, 0) AS rejected_qty, 0 AS returned_qty,
			0 AS other_qty,
			jc.status
		FROM `tabJob Card` jc
		LEFT JOIN `tabWork Order` wo ON wo.name = jc.work_order
		WHERE {project_match("jc", "Job Card", "wo", "Work Order")}
			{cond}
		ORDER BY jc.posting_date, jc.name
		""",
		filters,
	)


def get_stock_entries(filters):
	cond = conditions(filters, "se", "se.posting_date", "sed.item_code")
	return run(
		f"""
		SELECT 'Stock Entry' AS operation, 'Stock Entry' AS doctype,
			se.name AS document, CONCAT(se.name, '-', sed.item_code) AS row_name, se.posting_date,
			IF(se.is_return = 1, CONCAT(se.stock_entry_type, ' (Return)'), se.stock_entry_type)
				AS sub_type,
			NULL AS party,
			COALESCE(NULLIF(se.work_order, ''), NULLIF(se.subcontracting_order, ''),
				NULLIF(se.purchase_order, '')) AS against,
			sed.item_code, MAX(sed.item_name) AS item_name,
			MAX(COALESCE(sed.t_warehouse, sed.s_warehouse)) AS warehouse,
			MAX(sed.stock_uom) AS uom,
			NULL AS ordered_qty,
			SUM(sed.transfer_qty) AS completed_qty,
			NULL AS pending_qty,
			0 AS rejected_qty, 0 AS returned_qty, 0 AS other_qty,
			IF(se.docstatus = 1, 'Submitted', 'Draft') AS status
		FROM `tabStock Entry Detail` sed
		INNER JOIN `tabStock Entry` se ON se.name = sed.parent
		WHERE {project_match("sed", "Stock Entry Detail", "se", "Stock Entry")}
			{cond}
		GROUP BY se.name, sed.item_code
		ORDER BY se.posting_date, se.name
		""",
		filters,
	)


# --------------------------------------------------------------------------- #
# Columns / chart / summary
# --------------------------------------------------------------------------- #
def get_columns():
	return [
		{"label": _("Item / Operation / Document"), "fieldname": "particulars", "fieldtype": "Data", "width": 260},
		{"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
		{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
		{"label": _("Operation"), "fieldname": "operation", "fieldtype": "Data", "width": 160},
		{"label": _("Doc Type"), "fieldname": "doctype", "fieldtype": "Data", "hidden": 1},
		{"label": _("Document"), "fieldname": "document", "fieldtype": "Dynamic Link", "options": "doctype", "width": 160},
		{"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 95},
		{"label": _("UOM"), "fieldname": "uom", "fieldtype": "Link", "options": "UOM", "width": 60},
		{"label": _("Ordered Qty"), "fieldname": "ordered_qty", "fieldtype": "Float", "width": 110},
		{"label": _("Completed Qty"), "fieldname": "completed_qty", "fieldtype": "Float", "width": 115},
		{"label": _("Pending Qty"), "fieldname": "pending_qty", "fieldtype": "Float", "width": 110},
		{"label": _("Completion %"), "fieldname": "completion_pct", "fieldtype": "Percent", "width": 100},
		{"label": _("Rejected / Process Loss"), "fieldname": "rejected_qty", "fieldtype": "Float", "width": 120},
		{"label": _("Returned Qty"), "fieldname": "returned_qty", "fieldtype": "Float", "width": 105},
		{"label": _("Received / Consumed / Transferred"), "fieldname": "other_qty", "fieldtype": "Float", "width": 130},
		{"label": _("Type / Operation"), "fieldname": "sub_type", "fieldtype": "Data", "width": 150},
		{"label": _("Supplier"), "fieldname": "party", "fieldtype": "Link", "options": "Supplier", "width": 140},
		{"label": _("Against"), "fieldname": "against", "fieldtype": "Data", "width": 150},
		{"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 140},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 160},
	]


def get_chart(summary):
	rows = [s for s in summary if s.operation not in RECEIPT_TYPE]
	if not rows:
		return None
	return {
		"data": {
			"labels": [s.operation for s in rows],
			"datasets": [
				{"name": _("Ordered"), "values": [flt(s.ordered_qty) for s in rows]},
				{"name": _("Completed"), "values": [flt(s.completed_qty) for s in rows]},
				{"name": _("Pending"), "values": [flt(s.pending_qty) for s in rows]},
			],
		},
		"type": "bar",
		"colors": ["#5e64ff", "#28a745", "#ff5858"],
	}


def get_report_summary(summary):
	out = []
	for s in summary:
		if s.operation in RECEIPT_TYPE:
			continue
		out.append(
			{
				"value": s.open_docs,
				"label": _("{0} - Open").format(s.operation),
				"datatype": "Int",
				"indicator": "Red" if s.open_docs else "Green",
			}
		)
	return out
