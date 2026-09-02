// Copyright (c) 2026, Pranera Services and Solutions Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Roll Pick Assignment", {
	pick_type(frm) {
		update_pick_qty_from_batch_items(frm);
	},
	refresh(frm) {
		update_pick_qty_from_batch_items(frm);
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
});

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
