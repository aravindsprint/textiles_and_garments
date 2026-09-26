import frappe
from frappe.utils import flt


def execute():
	"""1. Batch Wise Pick Item.weight on submitted Roll Wise Pick Lists was saved
	   as Qty (Pcs count) instead of the sum of Roll Weight - recompute it.
	2. Roll Pick Assignments whose Scanned Rolls were already cleared lost their
	   Total Weight / Item Wise Weight - rebuild them from their Pick Lists."""

	# ---- 1. Batch Wise Pick Item.weight = sum(Roll Wise Pick Item.roll_weight) ----
	frappe.db.sql(
		"""
		update `tabBatch Wise Pick Item` b
		join (
			select parent, item_code, warehouse, batch, sum(roll_weight) as w
			from `tabRoll Wise Pick Item`
			where parenttype = 'Roll Wise Pick List'
			group by parent, item_code, warehouse, batch
		) r
			on r.parent = b.parent
			and r.item_code <=> b.item_code
			and r.warehouse <=> b.warehouse
			and r.batch <=> b.batch
		set b.weight = round(r.w, 3)
		where b.parenttype = 'Roll Wise Pick List'
		"""
	)

	# ---- 2. Rebuild RPA weights from linked, submitted Pick Lists ----
	rows = frappe.db.sql(
		"""
		select pl.roll_pick_assignment as rpa, ri.item_code, sum(ri.roll_weight) as w
		from `tabRoll Wise Pick List` pl
		join `tabRoll Wise Pick Item` ri
			on ri.parent = pl.name and ri.parenttype = 'Roll Wise Pick List'
		where pl.docstatus = 1
			and ifnull(pl.roll_pick_assignment, '') != ''
			and not exists (
				select 1 from `tabRoll Pick Assignment Scan` s
				where s.parent = pl.roll_pick_assignment
					and s.parenttype = 'Roll Pick Assignment'
			)
		group by pl.roll_pick_assignment, ri.item_code
		order by pl.roll_pick_assignment, min(ri.idx)
		""",
		as_dict=True,
	)

	by_rpa = {}
	for r in rows:
		by_rpa.setdefault(r.rpa, []).append(r)

	for rpa, items in by_rpa.items():
		docstatus = frappe.db.get_value("Roll Pick Assignment", rpa, "docstatus")
		if docstatus is None:
			continue

		frappe.db.delete(
			"Roll Pick Item Weight",
			{"parent": rpa, "parenttype": "Roll Pick Assignment", "parentfield": "item_wise_weight"},
		)
		for idx, r in enumerate(items, 1):
			frappe.get_doc({
				"doctype": "Roll Pick Item Weight",
				"parent": rpa,
				"parenttype": "Roll Pick Assignment",
				"parentfield": "item_wise_weight",
				"idx": idx,
				"docstatus": docstatus,
				"item_code": r.item_code,
				"total_weight": flt(r.w, 3),
			}).db_insert()

		frappe.db.set_value(
			"Roll Pick Assignment", rpa, "total_weight",
			flt(sum(flt(r.w) for r in items), 3), update_modified=False,
		)

	frappe.db.commit()
