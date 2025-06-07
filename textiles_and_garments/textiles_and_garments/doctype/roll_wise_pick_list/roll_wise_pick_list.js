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
        	console.log("Add Rolls is clicked");
            show_roll_multi_select_dialog(frm);
        });
    }
});

// function show_roll_multi_select_dialog(frm) {
//     const warehouse = frm.doc.warehouse;
//     const parent_warehouse = frm.doc.parent_warehouse;  // Get parent_warehouse from form

//     // if (!warehouse) {
//     //     frappe.msgprint("Please select a Warehouse first.");
//     //     return;
//     // }
//     if (!parent_warehouse && !warehouse) {
//         frappe.msgprint("Please select a Parent Warehouse first.");
//         return;
//     }

//     frappe.call({
//         method: "textiles_and_garments.textiles_and_garments.doctype.roll_wise_pick_list.roll_wise_pick_list.get_filtered_rolls",
//         args: {
//             warehouse: warehouse,
//             parent_warehouse: parent_warehouse   // pass parent_warehouse to backend
//         },
//         callback: function (res) {
//             const all_rolls = res.message || [];
//             const roll_options = all_rolls.map(r => r.name);
//             console.log("all_rolls", all_rolls);
//             console.log("roll_options", roll_options);

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

//                     filters.name = ["in", roll_options];
//                     // filters.parent_warehouse = parent_warehouse;  // add filter here to restrict rolls by parent_warehouse

//                     return { filters };
//                 },

//                 primary_action_label: 'Add to Pick List',

//                 action(selected_names) {
//                     if (!selected_names || selected_names.length === 0) return;

//                     const selected_rolls = all_rolls.filter(r => selected_names.includes(r.name));

//                     // Clear old rows
//                     frm.clear_table('roll_wise_pick_item');
//                     frm.clear_table('batch_wise_pick_item');

//                     // Add to roll_wise_pick_item
//                     selected_rolls.forEach(roll => {
//                         frm.add_child('roll_wise_pick_item', {
//                             item_code: roll.item_code,
//                             batch: roll.batch,
//                             qty: roll.roll_weight,
//                             roll_no: roll.name,
//                             uom: roll.stock_uom,
//                             warehouse: frm.doc.warehouse,
//                             // parent_warehouse: roll.parent_warehouse  // store parent_warehouse if needed
//                         });
//                     });

//                     // Group by item_code + batch and sum qty
//                     const batch_map = {};

//                     selected_rolls.forEach(roll => {
//                         const key = `${roll.item_code}||${roll.batch}`;
//                         if (!batch_map[key]) {
//                             batch_map[key] = {
//                                 item_code: roll.item_code,
//                                 batch: roll.batch,
//                                 qty: 0,
//                                 uom: roll.stock_uom,
//                                 warehouse: frm.doc.warehouse,
//                                 // parent_warehouse: roll.parent_warehouse
//                             };
//                         }
//                         batch_map[key].qty += roll.roll_weight;
//                     });

//                     // Prevent duplicates and add to batch_wise_pick_item
//                     const existing_keys = new Set();
//                     frm.doc.batch_wise_pick_item.forEach(row => {
//                         existing_keys.add(`${row.item_code}||${row.batch}`);
//                     });

//                     Object.entries(batch_map).forEach(([key, batch_entry]) => {
//                         if (!existing_keys.has(key)) {
//                             frm.add_child('batch_wise_pick_item', batch_entry);
//                         }
//                     });

//                     frm.refresh_field('roll_wise_pick_item');
//                     frm.refresh_field('batch_wise_pick_item');

//                     frappe.msgprint(`${selected_rolls.length} roll(s) added to the Pick List.`);
//                     this.dialog.hide();
//                 }
//             });
//         }
//     });
// }



// function show_roll_multi_select_dialog(frm) {
//     const warehouse = frm.doc.warehouse;
//     const batch = frm.doc.batch;
//     if (!warehouse) {
//         frappe.msgprint("Please select a Warehouse first.");
//         return;
//     }

//     frappe.call({
//         method: "textiles_and_garments.textiles_and_garments.doctype.roll_wise_pick_list.roll_wise_pick_list.get_filtered_rolls",
//         args: {
//             warehouse: warehouse,
//             batch: batch
//         },
//         callback: function (res) {
//             const all_rolls = res.message || [];
//             const roll_options = all_rolls.map(r => r.name);

//             console.log("\n\nall_rolls\n\n",all_rolls);
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

//                     // Restrict only to backend-filtered roll list
//                     filters.name = ["in", roll_options];

//                     return { filters };
//                 },

//                 primary_action_label: 'Add to Pick List',

//                 action(selected_names) {
//                     if (!selected_names || selected_names.length === 0) return;

//                     const selected_rolls = all_rolls.filter(r => selected_names.includes(r.name));

//                     // Clear old rows (optional)
//                     // frm.clear_table('roll_wise_pick_item');
//                     // frm.clear_table('batch_wise_pick_item');

//                     // 1. Add individual rolls to roll_wise_pick_item
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

//                     // 2. Group rolls by batch and sum qty
//                     const batch_map = {};

//                     selected_rolls.forEach(roll => {
//                         if (!batch_map[roll.batch]) {
//                             batch_map[roll.batch] = {
//                                 item_code: roll.item_code,
//                                 batch: roll.batch,
//                                 qty: 0,
//                                 uom: roll.stock_uom,
//                                 warehouse: frm.doc.warehouse
//                             };
//                         }

//                         batch_map[roll.batch].qty += roll.roll_weight;
//                     });

//                     Object.values(batch_map).forEach(batch_entry => {
//                         frm.add_child('batch_wise_pick_item', {
//                             item_code: batch_entry.item_code,
//                             batch: batch_entry.batch,
//                             qty: batch_entry.qty,
//                             uom: batch_entry.uom,
//                             warehouse: batch_entry.warehouse
//                         });
//                     });

//                     frm.refresh_field('roll_wise_pick_item');
//                     frm.refresh_field('batch_wise_pick_item');

//                     frappe.msgprint(`${selected_rolls.length} roll(s) added to the Pick List.`);
//                     this.dialog.hide();
//                 }
//             });
//         }
//     });
// }


function show_roll_multi_select_dialog(frm) {
    const warehouse = frm.doc.warehouse;
    const batch = frm.doc.batch;
    if (!warehouse) {
        frappe.msgprint("Please select a Warehouse first.");
        return;
    }

    frappe.call({
        method: "textiles_and_garments.textiles_and_garments.doctype.roll_wise_pick_list.roll_wise_pick_list.get_filtered_rolls",
        args: {
            warehouse: warehouse,
            batch: batch
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

                    // ✅ Collect existing roll_nos to prevent duplicates
                    const existing_roll_nos = frm.doc.roll_wise_pick_item.map(row => row.roll_no);

                    // ✅ Filter out rolls that already exist
                    const new_rolls = selected_rolls.filter(roll => !existing_roll_nos.includes(roll.name));

                    if (new_rolls.length === 0) {
                        frappe.msgprint("Selected rolls are already added.");
                        this.dialog.hide();
                        return;
                    }

                    // ✅ 1. Add only new rolls to roll_wise_pick_item
                    new_rolls.forEach(roll => {
                        frm.add_child('roll_wise_pick_item', {
                            item_code: roll.item_code,
                            batch: roll.batch,
                            qty: roll.roll_weight,
                            roll_no: roll.name,
                            uom: roll.stock_uom,
                            warehouse: frm.doc.warehouse
                        });
                    });

                    // ✅ 2. Group new rolls by batch and sum qty
                    const batch_map = {};

                    new_rolls.forEach(roll => {
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

                    frappe.msgprint(`${new_rolls.length} new roll(s) added to the Pick List.`);
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

//     let page_length = 20;
//     let current_page = 0;
//     let all_rolls = [];

//     const fetch_rolls = (start = 0) => {
//         frappe.call({
//             method: "textiles_and_garments.textiles_and_garments.doctype.roll_wise_pick_list.roll_wise_pick_list.get_filtered_rolls",
//             args: {
//                 warehouse: warehouse
//             },
//             callback: function (res) {
//                 all_rolls = res.message || [];

//                 // Simulate paginated subset
//                 const paginated_rolls = all_rolls.slice(start, start + page_length);
//                 const roll_options = paginated_rolls.map(r => r.name);

//                 let dialog = new frappe.ui.form.MultiSelectDialog({
//                     doctype: "Roll",
//                     target: frm,
//                     setters: {
//                         item_code: null,
//                         batch: null,
//                         roll_weight: null
//                     },
//                     add_filters_group: 1,

//                     get_query() {
//                         const filters = {};
//                         const item_code = dialog.dialog.get_value('item_code');
//                         const batch = dialog.dialog.get_value('batch');
//                         const roll_weight = dialog.dialog.get_value('roll_weight');

//                         if (item_code) filters.item_code = item_code;
//                         if (batch) filters.batch = batch;
//                         if (roll_weight) filters.roll_weight = roll_weight;

//                         // Apply filter to limited set
//                         filters.name = ["in", roll_options];

//                         return { filters };
//                     },

//                     primary_action_label: 'Add to Pick List',

//                     action(selected_names) {
//                         if (!selected_names || selected_names.length === 0) return;

//                         const selected_rolls = all_rolls.filter(r => selected_names.includes(r.name));

//                         // Add to roll_wise_pick_item
//                         selected_rolls.forEach(roll => {
//                             frm.add_child('roll_wise_pick_item', {
//                                 item_code: roll.item_code,
//                                 batch: roll.batch,
//                                 qty: roll.roll_weight,
//                                 roll_no: roll.name,
//                                 uom: roll.stock_uom,
//                                 warehouse: frm.doc.warehouse
//                             });
//                         });

//                         // Group and add to batch_wise_pick_item
//                         const batch_map = {};
//                         selected_rolls.forEach(roll => {
//                             if (!batch_map[roll.batch]) {
//                                 batch_map[roll.batch] = {
//                                     item_code: roll.item_code,
//                                     batch: roll.batch,
//                                     qty: 0,
//                                     uom: roll.stock_uom,
//                                     warehouse: frm.doc.warehouse
//                                 };
//                             }
//                             batch_map[roll.batch].qty += roll.roll_weight;
//                         });

//                         Object.values(batch_map).forEach(batch_entry => {
//                             frm.add_child('batch_wise_pick_item', batch_entry);
//                         });

//                         frm.refresh_field('roll_wise_pick_item');
//                         frm.refresh_field('batch_wise_pick_item');

//                         frappe.msgprint(`${selected_rolls.length} roll(s) added to the Pick List.`);
//                         dialog.dialog.hide();
//                     }
//                 });

//                 // Add Pagination Footer Controls
//                 dialog.dialog.set_primary_action("Next Page", () => {
//                     current_page += 1;
//                     dialog.dialog.hide();
//                     fetch_rolls(current_page * page_length);
//                 });

//                 dialog.dialog.add_custom_button("Previous Page", () => {
//                     if (current_page > 0) {
//                         current_page -= 1;
//                         dialog.dialog.hide();
//                         fetch_rolls(current_page * page_length);
//                     }
//                 }, "left");

//             }
//         });
//     };

//     fetch_rolls(); // Load initial page
// }




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





