// Copyright (c) 2026, Pranera Services and Solutions Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Roll Pick Assignment", {
	pick_type(frm) {
		update_pick_qty_from_batch_items(frm);
	},
	refresh(frm) {
		update_pick_qty_from_batch_items(frm);
		set_batch_item_warehouse_query(frm);
	},
	work_order(frm) {
		update_pick_qty_from_manufactured_batch(frm);
	},
	source_warehouse(frm) {
		update_pick_qty_from_manufactured_batch(frm);
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
