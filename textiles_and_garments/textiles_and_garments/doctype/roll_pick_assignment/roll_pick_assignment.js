// Copyright (c) 2026, Pranera Services and Solutions Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Roll Pick Assignment", {
	pick_type(frm) {
		update_pick_qty_from_batch_items(frm);
		populate_batch_items_from_sales_order(frm);
	},
	refresh(frm) {
		update_pick_qty_from_batch_items(frm);
		set_batch_item_warehouse_query(frm);
		set_batch_item_batch_query(frm);
	},
	work_order(frm) {
		update_pick_qty_from_manufactured_batch(frm);
	},
	source_warehouse(frm) {
		update_pick_qty_from_manufactured_batch(frm);
	},
	sales_order(frm) {
		populate_batch_items_from_sales_order(frm);
	},
});

frappe.ui.form.on("Roll Pick Batch Item", {
	qty(frm) {
		update_pick_qty_from_batch_items(frm);
	},
	batch_items_add(frm) {
		update_pick_qty_from_batch_items(frm);
	},
	batch_items_remove(frm) {
		update_pick_qty_from_batch_items(frm);
	},
	batch(frm, cdt, cdn) {
		// Item is auto-filled via fetch_from (batch.item) — nothing to do
		// here for that. Warehouse, though, depends on which batch is
		// selected (its available-qty options come from get_warehouses_for_batch
		// below), so a warehouse chosen for the previous batch may not even
		// hold this one — don't leave a stale value sitting there.
		frappe.model.set_value(cdt, cdn, "warehouse", "");
	},
});

function populate_batch_items_from_sales_order(frm) {
	// "To Sales Order" picks: once a Sales Order is chosen, add one Batch
	// Items row per item on that order (skipping any item already
	// represented in the table, so this never clobbers batches the
	// supervisor already picked) with just the item code filled in — the
	// supervisor still picks the actual batch/warehouse/qty per row. Only
	// sets item, same as this request asked; doesn't touch qty or try to
	// guess a batch.
	if (frm.doc.pick_type !== "To Sales Order" || !frm.doc.sales_order) {
		return;
	}

	frappe.db.get_doc("Sales Order", frm.doc.sales_order).then((so) => {
		// Bail if the user switched pick_type/sales_order again while this
		// was in flight.
		if (frm.doc.pick_type !== "To Sales Order" || frm.doc.sales_order !== so.name) {
			return;
		}

		const existing_items = new Set(
			(frm.doc.batch_items || []).map((r) => r.item).filter(Boolean)
		);

		(so.items || []).forEach((so_item) => {
			if (!so_item.item_code || existing_items.has(so_item.item_code)) {
				return;
			}
			const row = frm.add_child("batch_items");
			row.item = so_item.item_code;
			existing_items.add(so_item.item_code);
		});

		frm.refresh_field("batch_items");
	});
}

function set_batch_item_warehouse_query(frm) {
	// Shows, for each candidate warehouse, how much of THIS row's batch is
	// actually sitting there right now — the same "value + qty" dropdown
	// style as the standard Batch No field.
	frm.set_query("warehouse", "batch_items", function (doc, cdt, cdn) {
		const row = locals[cdt][cdn];
		return {
			query:
				"textiles_and_garments.textiles_and_garments.doctype.roll_pick_assignment.roll_pick_assignment.get_warehouses_for_batch",
			filters: { batch: row.batch },
		};
	});
}

function set_batch_item_batch_query(frm) {
	// Shows each candidate batch's total qty (summed across all
	// warehouses) in its own dropdown — same "value + qty" style as the
	// warehouse field above.
	frm.set_query("batch", "batch_items", function () {
		return {
			query:
				"textiles_and_garments.textiles_and_garments.doctype.roll_pick_assignment.roll_pick_assignment.get_batches_with_qty",
		};
	});
}

function update_pick_qty_from_batch_items(frm) {
	// Only auto-total when the child table is actually in play for this pick_type
	if (!["From Batch", "To Sales Order"].includes(frm.doc.pick_type)) {
		return;
	}

	let total = 0;
	(frm.doc.batch_items || []).forEach((row) => {
		total += flt(row.qty);
	});

	frm.set_value("pick_qty", total);
}

function update_pick_qty_from_manufactured_batch(frm) {
	// For "From Work Order" picks, pick_qty is auto-set to whatever stock is
	// actually still available (in source_warehouse) from the batch(es) this
	// Work Order manufactured, so the worker isn't asked to pick more than exists.
	if (frm.doc.pick_type !== "From Work Order") {
		return;
	}
	if (!frm.doc.work_order || !frm.doc.source_warehouse) {
		return;
	}

	frappe.call({
		method:
			"textiles_and_garments.textiles_and_garments.doctype.roll_pick_assignment.roll_pick_assignment.get_manufactured_batch_available_qty",
		args: {
			work_order: frm.doc.work_order,
			source_warehouse: frm.doc.source_warehouse,
		},
		callback: function (r) {
			if (r.message !== undefined) {
				frm.set_value("pick_qty", r.message);
			}
		},
	});
}
