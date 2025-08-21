// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

frappe.ui.form.on("Plan Items", {
	refresh(frm) {
	},
});


// Trigger this once on form load to make sure summary starts clean
frappe.ui.form.on('Plan Items', {
    onload(frm) {
        // Optional: you can refresh summary here initially if needed
    }
});

// --- Event handlers for Plan Items Detail ---
frappe.ui.form.on('Plan Items Detail', {
    item_code(frm, cdt, cdn) {
        const row = locals[cdt][cdn];

        // Check if item_code already exists (excluding current row)
        let duplicate = frm.doc.plan_items_detail.some(r => 
            r.item_code === row.item_code && r.name !== row.name
        );

        if (duplicate) {
            frappe.msgprint({
                title: __("Duplicate Item"),
                message: __("Item Code {0} is already added in Plan Items Detail.", [row.item_code]),
                indicator: 'red'
            });

            // Clear the duplicate value
            frappe.model.set_value(cdt, cdn, 'item_code', '');
            return;
        }

        sync_summary_row(frm, row.item_code);
    },

    qty(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        sync_summary_row(frm, row.item_code);
    }
});




// --- Core function to sync the summary table ---
// function sync_summary_row(frm, item_code) {
//     if (!item_code) return;

//     let total_qty = 0;

//     // Sum qty for all detail rows with the same item_code
//     frm.doc.plan_items_detail.forEach(row => {
//         if (row.item_code === item_code) {
//             total_qty += flt(row.qty);
//         }
//     });

//     // Find the matching summary row
//     let summary_row = frm.doc.plan_items_summary.find(r => r.item_code === item_code);

//     if (summary_row) {
//         if (total_qty === 0) {
//             // Remove the row if qty is 0
//             frm.doc.plan_items_summary = frm.doc.plan_items_summary.filter(r => r.item_code !== item_code);
//         } else {
//             summary_row.qty = total_qty;
//             summary_row.need_to_plan_qty = flt(total_qty) - flt(summary_row.planned_qty || 0);
//         }
//     } else if (total_qty > 0) {
//         // Add a new row
//         let new_row = frm.add_child('plan_items_summary', {
//             item_code: item_code,
//             qty: total_qty,
//             planned_qty: 0,
//             need_to_plan_qty: total_qty
//         });
//     }

//     frm.refresh_field('plan_items_summary');
// }
// This script is typically placed in ERPNext's Custom Scripts for a DocType.

function sync_summary_row(frm, item_code) {
    if (!item_code) return;

    let total_qty = 0;

    // Sum qty for all detail rows with the same item_code
    frm.doc.plan_items_detail.forEach(row => {
        if (row.item_code === item_code) {
            total_qty += flt(row.qty);
        }
    });

    // Find the matching summary row
    let summary_row = frm.doc.plan_items_summary.find(r => r.item_code === item_code);

    if (summary_row) {
        if (total_qty === 0) {
            // Remove the row if qty is 0
            frm.doc.plan_items_summary = frm.doc.plan_items_summary.filter(r => r.item_code !== item_code);
        } else {
            summary_row.qty = total_qty;
            summary_row.need_to_plan_qty = flt(total_qty) - flt(summary_row.planned_qty || 0);
        }
    } else if (total_qty > 0) {
        // Add a new row
        let new_row = frm.add_child('plan_items_summary', {
            item_code: item_code,
            qty: total_qty,
            planned_qty: 0,
            need_to_plan_qty: total_qty
        });
        // Note: frm.add_child automatically appends. We will reorder below.
    }

    // --- NEW LOGIC: Reorder plan_items_summary based on plan_items_detail order ---

    // 1. Get the desired order of item_codes from plan_items_detail
    const ordered_item_codes = frm.doc.plan_items_detail.map(detail_row => detail_row.item_code);

    // 2. Create a map for quick lookup of current summary rows
    const current_summary_map = {};
    frm.doc.plan_items_summary.forEach(summary_row => {
        current_summary_map[summary_row.item_code] = summary_row;
    });

    // 3. Build a new, ordered array for plan_items_summary
    const new_ordered_summary = [];
    ordered_item_codes.forEach(item_code_from_detail => {
        if (current_summary_map[item_code_from_detail]) {
            new_ordered_summary.push(current_summary_map[item_code_from_detail]);
        }
    });

    // 4. Assign the new ordered array back to the child table
    frm.doc.plan_items_summary = new_ordered_summary;

    // --- END NEW LOGIC ---

    frm.refresh_field('plan_items_summary');
}

frappe.ui.form.on('Plan Items Detail', {
    qty(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const new_qty = flt(row.qty);

        // Get total plan_qty from plan_item_planned_wise for this item_code
        let planned_qty_total = 0;
        frm.doc.plan_item_planned_wise?.forEach(plan => {
            if (plan.item_code === row.item_code) {
                planned_qty_total += flt(plan.plan_qty);
            }
        });

        if (new_qty < planned_qty_total) {
            frappe.msgprint({
                title: __("Invalid Quantity"),
                message: __("Qty for item {0} cannot be less than total planned quantity ({1}) in Plan Item Planned Wise.", [
                    row.item_code, planned_qty_total
                ]),
                indicator: "red"
            });

            // Revert to previous value
            frappe.model.set_value(cdt, cdn, "qty", planned_qty_total);
            return;
        }

        // Proceed with summary update if valid
        sync_summary_row(frm, row.item_code);
    }
});





frappe.ui.form.on('Plan Items', {
    validate: function(frm) {
        const detail_item_codes = frm.doc.plan_items_detail.map(row => row.item_code);

        // Collect item_codes from Plan Item Planned Wise
        const planned_item_codes = (frm.doc.plan_item_planned_wise || []).map(row => row.item_code);

        // Final filter logic
        frm.doc.plan_items_summary = frm.doc.plan_items_summary.filter(row => {
            const in_detail = detail_item_codes.includes(row.item_code);
            const in_planned = planned_item_codes.includes(row.item_code);

            // Keep the row if item_code exists in detail or in planned
            return in_detail || in_planned;
        });

        frm.refresh_field('plan_items_summary');
    }
});


frappe.ui.form.on('Plan Items', {
    refresh: function (frm) {
        frm.fields_dict['plan_items_detail'].grid.get_field('bom').get_query = function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
            console.log("row",row);
            return {
                filters: {
                    item: row.item_code,
                    docstatus: 1
                }
            };
        };
    }
});

frappe.ui.form.on('Plan Items', {
    refresh: function(frm) {
       frm.set_df_property('plan_item_planned_wise', 'cannot_add_rows', true); // Hide add row button
       frm.set_df_property('plan_item_planned_wise', 'cannot_delete_rows', true); // Hide delete button
       frm.set_df_property('plan_item_planned_wise', 'cannot_delete_all_rows', true); // Hide delete all button

       frm.set_df_property('plan_items_summary', 'cannot_add_rows', true); // Hide add row button
       frm.set_df_property('plan_items_summary', 'cannot_delete_rows', true); // Hide delete button
       frm.set_df_property('plan_items_summary', 'cannot_delete_all_rows', true); // Hide delete all button
    }
});




// frappe.ui.form.on('Plan Items Detail', {
//     create_plan(frm, cdt, cdn) {
//         const row = locals[cdt][cdn];

//         if (!row.item_code || !row.bom || !row.qty) {
//             frappe.msgprint("Please fill Item Code, BOM and Qty before creating a Plan.");
//             return;
//         }

//         if (row.created_plan) {
//             frappe.msgprint(`A Plans document is already created: ${row.created_plan}`);
//             return;
//         }

//         frappe.call({
//             method: "frappe.client.insert",
//             args: {
//                 doc: {
//                     doctype: "Plans",
//                     item_code: row.item_code,
//                     bom: row.bom,
//                     plan_qty: row.qty,
//                     plan_items: frm.doc.name,
//                     posting_date: frappe.datetime.now_date(),
//                     plan_items_detail: row.name
//                 }
//             },
//             callback: function (r) {
//                 if (r.message) {
//                     // Update link in child table
//                     // frappe.model.set_value(cdt, cdn, "created_plan", r.message.name);

//                     frappe.msgprint(__('Plans document <a href="/app/plans/{0}" target="_blank">{0}</a> created successfully.', [r.message.name]));
//                     frappe.set_route("Form", "Plans", r.message.name);
//                 }
//             }
//         });
//     }
// });


function create_plans_doc(frm, cdt, cdn, source) {
    const row = locals[cdt][cdn];

    let item_code = row.item_code;
    let plan_qty = source === 'summary' ? row.need_to_plan_qty : row.qty;
    let bom = row.bom;

    if (!item_code || !plan_qty) {
        frappe.msgprint("Item Code and Quantity are required to create a Plan.");
        return;
    }

    // For summary table, get BOM from Plan Items Detail
    if (source === 'summary') {
        const detail_match = frm.doc.plan_items_detail.find(d => d.item_code === item_code );
        if (!detail_match) {
            frappe.msgprint(`No matching BOM found for item: ${item_code} in Plan Items Detail.`);
            return;
        }
        bom = detail_match.bom;
    }

    frappe.call({
        method: "frappe.client.insert",
        args: {
            doc: {
                doctype: "Plans",
                item_code: item_code,
                bom: bom,
                plan_qty: plan_qty,
                posting_date: frappe.datetime.now_date(),
                plan_items: frm.doc.name,
                plan_items_detail: source === 'detail' ? row.name : null,
                plan_items_summary: source === 'summary' ? row.name : null
            }
        },
        callback: function (r) {
            if (r.message) {
                frappe.model.set_value(cdt, cdn, "created_plan", r.message.name);

                // Open the created Plans document in a new tab
                const url = `/app/plans/${r.message.name}`;
                window.open(url, '_blank');

                // Optional: show message with clickable link
                let link = `<a href="${url}" target="_blank">${r.message.name}</a>`;
                frappe.msgprint({
                    title: __("Plans Document Created"),
                    message: __("Plans document {0} created successfully.", [link]),
                    indicator: "green"
                });
            }
        }
    });
}



// Button handler for Plan Items Detail
frappe.ui.form.on('Plan Items Detail', {
    create_plan(frm, cdt, cdn) {
        create_plans_doc(frm, cdt, cdn, 'detail');
    }
});

// Button handler for Plan Items Summary
frappe.ui.form.on('Plan Items Summary', {
    create_plan(frm, cdt, cdn) {
        create_plans_doc(frm, cdt, cdn, 'summary');
    }
});
