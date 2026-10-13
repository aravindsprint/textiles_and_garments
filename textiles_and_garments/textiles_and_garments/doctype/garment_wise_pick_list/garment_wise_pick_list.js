// Copyright (c) 2026, Pranera Services and Solutions Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Garment Wise Pick List", {
	refresh(frm) {
		frm.add_custom_button("Add Items", () => {
			show_item_multi_select_dialog(frm);
		});
	},
});

frappe.ui.form.on("Garment Wise Pick Item", {
	qty(frm) {
		update_total_qty(frm);
	},
	garment_wise_pick_item_remove(frm) {
		update_total_qty(frm);
	},
});

function update_total_qty(frm) {
	let total = 0;
	(frm.doc.garment_wise_pick_item || []).forEach((row) => (total += flt(row.qty)));
	frm.set_value("total_qty", total);
}

// Same flow as "Add Rolls" on Roll Wise Pick List, but per Item instead of per
// Roll: list items with stock in the Warehouse, add the selected ones with
// their full available qty (edit Qty in the table to pick less).
function show_item_multi_select_dialog(frm) {
	const warehouse = frm.doc.warehouse;
	if (!warehouse) {
		frappe.msgprint("Please select a Warehouse first.");
		return;
	}

	frappe.call({
		method: "textiles_and_garments.textiles_and_garments.doctype.garment_wise_pick_list.garment_wise_pick_list.get_filtered_items",
		args: { warehouse: warehouse },
		callback: function (res) {
			const all_items = res.message || [];
			const item_options = all_items.map((r) => r.item_code);

			if (!item_options.length) {
				frappe.msgprint(`No garment stock found in ${warehouse}.`);
				return;
			}

			new frappe.ui.form.MultiSelectDialog({
				doctype: "Item",
				target: frm,
				setters: {
					item_group: null,
				},
				add_filters_group: 1,

				get_query() {
					const filters = {};
					const item_group = this.dialog.get_value("item_group");
					if (item_group) filters.item_group = item_group;

					// Restrict only to backend-filtered item list
					filters.name = ["in", item_options];

					return { filters };
				},

				primary_action_label: "Add to Pick List",

				action(selected_names) {
					if (!selected_names || selected_names.length === 0) return;

					const selected_items = all_items.filter((r) => selected_names.includes(r.item_code));

					// Prevent duplicates (same Item + Warehouse already in the list)
					const existing = (frm.doc.garment_wise_pick_item || []).map(
						(row) => `${row.item_code}||${row.warehouse}`
					);
					const new_items = selected_items.filter(
						(item) => !existing.includes(`${item.item_code}||${warehouse}`)
					);

					if (new_items.length === 0) {
						frappe.msgprint("Selected items are already added.");
						this.dialog.hide();
						return;
					}

					new_items.forEach((item) => {
						frm.add_child("garment_wise_pick_item", {
							item_code: item.item_code,
							warehouse: warehouse,
							stock_uom: item.stock_uom,
							qty: item.actual_qty,
						});
					});

					frm.refresh_field("garment_wise_pick_item");
					update_total_qty(frm);

					frappe.msgprint(`${new_items.length} new item(s) added to the Pick List.`);
					this.dialog.hide();
				},
			});
		},
	});
}
