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
		add_get_items_from_sales_order_button(frm);

		// Existing drafts (e.g. created from the knit app, or saved before this
		// feature) that already have a Sales Order but no Batch Items rows:
		// pre-fill once on open so the supervisor only has to pick batches.
		if (
			frm.doc.docstatus === 0 &&
			frm.doc.pick_type === "To Sales Order" &&
			frm.doc.sales_order &&
			!(frm.doc.batch_items || []).length
		) {
			populate_batch_items_from_sales_order(frm);
		}
	},
	work_order(frm) {
		update_pick_qty_from_manufactured_batch(frm);
	},
	source_warehouse(frm) {
		update_pick_qty_from_manufactured_batch(frm);
	},
	sales_order(frm) {
		populate_batch_items_from_sales_order(frm, { replace_unpicked: true });
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
		// Item is auto-filled via fetch_from (batch.item). Warehouse depends on
		// which batch is selected, so clear any stale value from the previous batch.
		frappe.model.set_value(cdt, cdn, "warehouse", "");
	},
});

function add_get_items_from_sales_order_button(frm) {
	if (frm.doc.docstatus !== 0 || frm.doc.pick_type !== "To Sales Order" || !frm.doc.sales_order) {
		return;
	}
	frm.add_custom_button(__("Get Items from Sales Order"), () => {
		populate_batch_items_from_sales_order(frm, { replace_unpicked: true });
	});
}

function populate_batch_items_from_sales_order(frm, opts = {}) {
	// "To Sales Order" picks: add one Batch Items row per (batch-tracked) item
	// on the linked Sales Order with only Item filled in. The supervisor then
	// picks Batch (dropdown filtered to that item), Warehouse and Qty per row.
	// Rows that already have a Batch are never touched.
	if (frm.doc.pick_type !== "To Sales Order" || !frm.doc.sales_order) {
		return;
	}
	const sales_order = frm.doc.sales_order;

	frappe.call({
		method:
			"textiles_and_garments.textiles_and_garments.doctype.roll_pick_assignment.roll_pick_assignment.get_sales_order_items",
		args: { sales_order },
		freeze: true,
		freeze_message: __("Fetching Sales Order items..."),
		callback(r) {
			// Bail if pick_type / sales_order changed while this was in flight.
			if (frm.doc.pick_type !== "To Sales Order" || frm.doc.sales_order !== sales_order) {
				return;
			}
			const so_items = r.message || [];

			if (opts.replace_unpicked) {
				// Drop placeholder rows (no batch chosen yet) — e.g. left over from
				// a previously selected Sales Order.
				frm.doc.batch_items = (frm.doc.batch_items || []).filter((row) => row.batch);
				frm.doc.batch_items.forEach((row, i) => (row.idx = i + 1));
			}

			const existing_items = new Set((frm.doc.batch_items || []).map((r) => r.item).filter(Boolean));
			let added = 0;
			so_items.forEach((so_item) => {
				if (existing_items.has(so_item.item_code)) {
					return;
				}
				const row = frm.add_child("batch_items");
				row.item = so_item.item_code;
				existing_items.add(so_item.item_code);
				added++;
			});

			frm.refresh_field("batch_items");
			update_pick_qty_from_batch_items(frm);

			if (!so_items.length) {
				frappe.show_alert({
					message: __("No batch-tracked items found in {0}", [sales_order]),
					indicator: "orange",
				});
			} else if (added) {
				frappe.show_alert({
					message: __("Added {0} item row(s) from {1}. Select Batch, Warehouse and Qty for each.", [
						added,
						sales_order,
					]),
					indicator: "green",
				});
			}
		},
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
	// For "To Sales Order" picks the row's Item comes from the Sales Order, so
	// only that item's batches are offered.
	frm.set_query("batch", "batch_items", function (doc, cdt, cdn) {
		const row = locals[cdt][cdn];
		const filters = {};
		if (doc.pick_type === "To Sales Order" && row.item) {
			filters.item = row.item;
		}
		return {
			query:
				"textiles_and_garments.textiles_and_garments.doctype.roll_pick_assignment.roll_pick_assignment.get_batches_with_qty",
			filters,
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
