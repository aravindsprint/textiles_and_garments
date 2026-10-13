// Copyright (c) 2026, Pranera Services and Solutions Pvt Ltd and contributors
// For license information, please see license.txt

const GPA_METHOD =
	"textiles_and_garments.textiles_and_garments.doctype.garment_pick_assignment.garment_pick_assignment";

frappe.ui.form.on("Garment Pick Assignment", {
	setup(frm) {
		set_item_warehouse_query(frm);
	},
	refresh(frm) {
		toggle_pick_qty_read_only(frm);
		add_get_items_from_sales_order_button(frm);

		// Drafts that already have a Sales Order but no Items rows (e.g. created
		// from the app): pre-fill once on open.
		if (
			frm.doc.docstatus === 0 &&
			frm.doc.pick_type === "To Sales Order" &&
			frm.doc.sales_order &&
			!(frm.doc.items || []).length
		) {
			populate_items_from_sales_order(frm);
		}
	},
	pick_type(frm) {
		populate_items_from_sales_order(frm);
		populate_item_from_work_order(frm);
	},
	work_order(frm) {
		populate_item_from_work_order(frm);
	},
	source_warehouse(frm) {
		populate_item_from_work_order(frm);
	},
	sales_order(frm) {
		populate_items_from_sales_order(frm, { replace: true });
	},
});

frappe.ui.form.on("Garment Wise Pick Item", {
	qty(frm) {
		update_totals_from_items(frm);
	},
	items_add(frm, cdt, cdn) {
		// Default the row's warehouse to the header Source Warehouse.
		if (frm.doc.source_warehouse) {
			frappe.model.set_value(cdt, cdn, "warehouse", frm.doc.source_warehouse);
		}
		update_totals_from_items(frm);
	},
	items_remove(frm) {
		update_totals_from_items(frm);
	},
});

function set_item_warehouse_query(frm) {
	// Shows only warehouses holding stock of THIS row's item, with qty as the
	// description line. Falls back to all warehouses until an item is chosen.
	frm.set_query("warehouse", "items", function (doc, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.item_code) {
			return { filters: { is_group: 0 } };
		}
		return {
			query: `${GPA_METHOD}.get_warehouses_for_item`,
			filters: { item_code: row.item_code },
		};
	});
}

function add_get_items_from_sales_order_button(frm) {
	if (frm.doc.docstatus !== 0 || frm.doc.pick_type !== "To Sales Order" || !frm.doc.sales_order) {
		return;
	}
	frm.add_custom_button(__("Get Items from Sales Order"), () => {
		populate_items_from_sales_order(frm, { replace: true });
	});
}

function populate_items_from_sales_order(frm, opts = {}) {
	// "To Sales Order" picks: one Items row per stock item on the Sales Order,
	// pre-filled with pending qty in stock UOM. Garments have no batch, so the
	// rows are ready to go — the supervisor only adjusts Warehouse / Qty.
	if (frm.doc.pick_type !== "To Sales Order" || !frm.doc.sales_order) {
		return;
	}
	const sales_order = frm.doc.sales_order;

	frappe.call({
		method: `${GPA_METHOD}.get_sales_order_items`,
		args: { sales_order },
		freeze: true,
		freeze_message: __("Fetching Sales Order items..."),
		callback(r) {
			if (frm.doc.pick_type !== "To Sales Order" || frm.doc.sales_order !== sales_order) {
				return;
			}
			const so_items = r.message || [];

			if (opts.replace) {
				frm.clear_table("items");
			}

			const existing = new Set((frm.doc.items || []).map((row) => row.item_code).filter(Boolean));
			let added = 0;
			so_items.forEach((so_item) => {
				if (existing.has(so_item.item_code)) {
					return;
				}
				const row = frm.add_child("items");
				row.item_code = so_item.item_code;
				row.stock_uom = so_item.stock_uom;
				row.warehouse = frm.doc.source_warehouse || so_item.warehouse;
				row.qty = so_item.qty;
				existing.add(so_item.item_code);
				added++;
			});

			frm.refresh_field("items");
			update_totals_from_items(frm);

			if (!so_items.length) {
				frappe.show_alert({
					message: __("No stock items found in {0}", [sales_order]),
					indicator: "orange",
				});
			} else if (added) {
				frappe.show_alert({
					message: __("Added {0} item row(s) from {1}", [added, sales_order]),
					indicator: "green",
				});
			}
		},
	});
}

function populate_item_from_work_order(frm) {
	// "From Work Order" picks: set a single Items row for the Work Order's
	// finished garment, with qty capped at what's actually in Source Warehouse.
	if (frm.doc.docstatus !== 0 || frm.doc.pick_type !== "From Work Order") {
		return;
	}
	if (!frm.doc.work_order || !frm.doc.source_warehouse) {
		return;
	}

	frappe.call({
		method: `${GPA_METHOD}.get_work_order_available_item`,
		args: {
			work_order: frm.doc.work_order,
			source_warehouse: frm.doc.source_warehouse,
		},
		callback(r) {
			const d = r.message;
			if (!d || !d.item_code) {
				return;
			}
			frm.clear_table("items");
			const row = frm.add_child("items");
			row.item_code = d.item_code;
			row.stock_uom = d.stock_uom;
			row.warehouse = d.warehouse;
			row.qty = d.qty;
			frm.refresh_field("items");
			update_totals_from_items(frm);

			if (!flt(d.qty)) {
				frappe.show_alert({
					message: __("No stock of {0} in {1}", [d.item_code, d.warehouse]),
					indicator: "orange",
				});
			}
		},
	});
}

function update_totals_from_items(frm) {
	const items = frm.doc.items || [];
	let total = 0;
	items.forEach((row) => {
		total += flt(row.qty);
	});
	frm.set_value("total_qty", total);
	if (items.length) {
		frm.set_value("pick_qty", total);
	}
	toggle_pick_qty_read_only(frm);
}

function toggle_pick_qty_read_only(frm) {
	// Pick Qty is derived from Items whenever the table has rows.
	frm.set_df_property("pick_qty", "read_only", (frm.doc.items || []).length ? 1 : 0);
}
