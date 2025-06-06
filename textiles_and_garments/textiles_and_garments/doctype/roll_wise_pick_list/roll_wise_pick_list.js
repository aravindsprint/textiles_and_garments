// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Roll Wise Pick List", {
// 	refresh(frm) {

// 	},
// });

// frappe.ui.form.on('Roll Wise Pick List', {
//     refresh(frm) {
//         frm.add_custom_button('Add Rolls', () => {
//             show_roll_multi_select_dialog(frm);
//         });
//     }
// });

// function show_roll_multi_select_dialog(frm) {
//     new frappe.ui.form.MultiSelectDialog({
//         doctype: "Roll",
//         target: frm,
//         setters: {
//             item_code: null,
//             batch: null,
//             roll_weight: null
//         },
//         add_filters_group: 1,
//         primary_action_label: 'Add to Pick List',
//         action(selected_names) {
//             if (!selected_names || selected_names.length === 0) return;

//             frappe.call({
//                 method: "frappe.client.get_list",
//                 args: {
//                     doctype: "Roll",
//                     filters: {
//                         name: ["in", selected_names]
//                     },
//                     fields: ["name", "item_code", "batch", "roll_weight", "stock_uom"]
//                 },
//                 callback: function (r) {
//                     const rolls = r.message || [];

//                     rolls.forEach(roll => {
//                         frm.add_child('roll_wise_pick_item', {
//                             item_code: roll.item_code,
//                             batch: roll.batch,
//                             qty: roll.roll_weight,
//                             roll: roll.name,
//                             uom: roll.stock_uom
//                         });
//                     });

//                     frm.refresh_field('roll_wise_pick_item');
//                     frappe.msgprint(`${rolls.length} roll(s) added to the Pick List.`);
//                 }
//             });
//         }
//     });
// }


frappe.ui.form.on('Roll Wise Pick List', {
    refresh(frm) {
        frm.add_custom_button('Add Rolls', () => {
            show_roll_multi_select_dialog(frm);
        });
    }
});


function show_roll_multi_select_dialog(frm) {
    const warehouse = frm.doc.warehouse;
    if (!warehouse) {
        frappe.msgprint("Please select a Warehouse first.");
        return;
    }

    frappe.call({
        method: "textiles_and_garments.textiles_and_garments.doctype.roll_wise_pick_list.roll_wise_pick_list.get_filtered_rolls",
        args: {
            warehouse: warehouse
        },
        callback: function (res) {
            const all_rolls = res.message || [];
            const roll_options = all_rolls.map(r => r.name);

            new frappe.ui.form.MultiSelectDialog({
                doctype: "Roll",
                target: frm,
                setters: {
                    item_code: null,
                    batch: null,
                    roll_weight: null
                },
                add_filters_group: 1,

                get_query() {
                    const filters = {};
                    const item_code = this.dialog.get_value('item_code');
                    const batch = this.dialog.get_value('batch');
                    const roll_weight = this.dialog.get_value('roll_weight');

                    if (item_code) filters.item_code = item_code;
                    if (batch) filters.batch = batch;
                    if (roll_weight) filters.roll_weight = roll_weight;

                    // Restrict only to backend-filtered roll list
                    filters.name = ["in", roll_options];

                    return { filters };
                },

                primary_action_label: 'Add to Pick List',

                action(selected_names) {
                    if (!selected_names || selected_names.length === 0) return;

                    const selected_rolls = all_rolls.filter(r => selected_names.includes(r.name));

                    // Clear old rows (optional)
                    // frm.clear_table('roll_wise_pick_item');
                    // frm.clear_table('batch_wise_pick_item');

                    // 1. Add individual rolls to roll_wise_pick_item
                    selected_rolls.forEach(roll => {
                        frm.add_child('roll_wise_pick_item', {
                            item_code: roll.item_code,
                            batch: roll.batch,
                            qty: roll.roll_weight,
                            roll_no: roll.name,
                            uom: roll.stock_uom,
                            warehouse: frm.doc.warehouse
                        });
                    });

                    // 2. Group rolls by batch and sum qty
                    const batch_map = {};

                    selected_rolls.forEach(roll => {
                        if (!batch_map[roll.batch]) {
                            batch_map[roll.batch] = {
                                item_code: roll.item_code,
                                batch: roll.batch,
                                qty: 0,
                                uom: roll.stock_uom,
                                warehouse: frm.doc.warehouse
                            };
                        }

                        batch_map[roll.batch].qty += roll.roll_weight;
                    });

                    Object.values(batch_map).forEach(batch_entry => {
                        frm.add_child('batch_wise_pick_item', {
                            item_code: batch_entry.item_code,
                            batch: batch_entry.batch,
                            qty: batch_entry.qty,
                            uom: batch_entry.uom,
                            warehouse: batch_entry.warehouse
                        });
                    });

                    frm.refresh_field('roll_wise_pick_item');
                    frm.refresh_field('batch_wise_pick_item');

                    frappe.msgprint(`${selected_rolls.length} roll(s) added to the Pick List.`);
                    this.dialog.hide();
                }
            });
        }
    });
}



// function show_roll_multi_select_dialog(frm) {
//     const warehouse = frm.doc.warehouse;
//     if (!warehouse) {
//         frappe.msgprint("Please select a Warehouse first.");
//         return;
//     }

//     frappe.call({
//         method: "textiles_and_garments.textiles_and_garments.doctype.roll_wise_pick_list.roll_wise_pick_list.get_filtered_rolls", // Update this
//         args: {
//             warehouse: warehouse
//         },
//         callback: function (res) {
//             const all_rolls = res.message || [];
//             console.log("\n\nall_rolls\n\n",all_rolls);

//             const roll_options = all_rolls.map(r => r.name);
//             console.log("\n\nroll_options\n\n",roll_options);

//             new frappe.ui.form.MultiSelectDialog({
//                 doctype: "Roll",
//                 target: frm,
//                 setters: {
//                     item_code: null,
//                     batch: null,
//                     roll_weight: null
//                 },
//                 add_filters_group: 1,

//                 get_query() {
//                     const filters = {};

//                     const item_code = this.dialog.get_value('item_code');
//                     const batch = this.dialog.get_value('batch');
//                     const roll_weight = this.dialog.get_value('roll_weight');

//                     if (item_code) filters.item_code = item_code;
//                     if (batch) filters.batch = batch;
//                     if (roll_weight) filters.roll_weight = roll_weight;
//                     // if (warehouse) filters.warehouse = warehouse;

//                     // Add filter to restrict to backend roll list
//                     filters.name = ["in", roll_options];

//                     return { filters };
//                 },

//                 primary_action_label: 'Add to Pick List',

//                 action(selected_names) {
//                     if (!selected_names || selected_names.length === 0) return;

//                     const selected_rolls = all_rolls.filter(r => selected_names.includes(r.name));

//                     selected_rolls.forEach(roll => {
//                         frm.add_child('roll_wise_pick_item', {
//                             item_code: roll.item_code,
//                             batch: roll.batch,
//                             qty: roll.roll_weight,
//                             roll_no: roll.name,
//                             uom: roll.stock_uom,
//                             warehouse: frm.doc.warehouse
//                         });
//                     });

//                     frm.refresh_field('roll_wise_pick_item');
//                     frappe.msgprint(`${selected_rolls.length} roll(s) added to the Pick List.`);
//                     this.dialog.hide();
//                 }
//             });
//         }
//     });
// }


// function show_roll_multi_select_dialog(frm) {
//     const warehouse = frm.doc.warehouse;
//     if (!warehouse) {
//         frappe.msgprint("Please select a Warehouse first.");
//         return;
//     }

//     frappe.call({
//         method: "textiles_and_garments.textiles_and_garments.doctype.roll_wise_pick_list.roll_wise_pick_list.get_filtered_rolls",
//         args: { warehouse },
//         callback: function (res) {
//             const all_rolls = res.message || [];
//             const roll_options = all_rolls.map(r => r.name);

//             const dialog = new frappe.ui.form.MultiSelectDialog({
//                 doctype: "Roll",
//                 target: frm,
//                 setters: {
//                     item_code: null,
//                     batch: null,
//                     roll_weight: null
//                 },
//                 add_filters_group: 1,

//                 get_query() {
//                     const filters = {};
//                     const item_code = this.dialog.get_value('item_code');
//                     const batch = this.dialog.get_value('batch');
//                     const roll_weight = this.dialog.get_value('roll_weight');

//                     if (item_code) filters.item_code = item_code;
//                     if (batch) filters.batch = batch;
//                     if (roll_weight) filters.roll_weight = roll_weight;

//                     filters.name = ["in", roll_options];
//                     return { filters };
//                 },

//                 // data_fields: [
//                 //     { label: 'Roll No', fieldname: 'name', fieldtype: 'Data', in_list_view: 1 },
//                 //     { label: 'Item Code', fieldname: 'item_code', fieldtype: 'Data', in_list_view: 1 },
//                 //     { label: 'Batch', fieldname: 'batch', fieldtype: 'Link', options: 'Batch', in_list_view: 1 },
//                 //     { label: 'Roll Weight', fieldname: 'roll_weight', fieldtype: 'Float', in_list_view: 1 }
//                 // ],

//                 primary_action_label: 'Add to Pick List',

//                 action(selected_names) {
//                     if (!selected_names?.length) return;

//                     const selected_rolls = all_rolls.filter(r => selected_names.includes(r.name));

//                     selected_rolls.forEach(roll => {
//                         frm.add_child('roll_wise_pick_item', {
//                             item_code: roll.item_code,
//                             batch: roll.batch,
//                             qty: roll.roll_weight,
//                             roll_no: roll.name,
//                             uom: roll.stock_uom
//                         });
//                     });

//                     frm.refresh_field('roll_wise_pick_item');
//                     frappe.msgprint(`${selected_rolls.length} roll(s) added to the Pick List.`);
//                     dialog.dialog.hide();
//                 }
//             });

//             // Wait until datatable is rendered, then apply column style
//             setTimeout(() => {
//                 const style = document.createElement("style");
//                 style.innerHTML = `
//                     .frappe-control[data-fieldname="roll_weight"] .dt-cell__content,
//                     .data-row .dt-cell:nth-child(4) { text-align: right !important; }
//                 `;
//                 document.head.appendChild(style);
//             }, 500); // allow DataTable to render
//         }
//     });
// }





