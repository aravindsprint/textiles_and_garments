// frappe.ui.form.on('Subcontracting Receipt', {
//     refresh(frm) {
//         console.log("Subcontracting Receipt", frm);

//         if (frm.doc.docstatus === 1) {
//             // Check if any items have subcontracting_order references
//             let has_subcontracting_orders = false;
//             let subcontracting_orders = [];
            
//             if (frm.doc.items) {
//                 frm.doc.items.forEach(item => {
//                     if (item.subcontracting_order) {
//                         has_subcontracting_orders = true;
//                         if (!subcontracting_orders.includes(item.subcontracting_order)) {
//                             subcontracting_orders.push(item.subcontracting_order);
//                         }
//                     }
//                 });
//             }
            
//             if (has_subcontracting_orders) {
//                 frm.add_custom_button(__('🔗 Remove Links & Cancel'), function() {
//                     remove_links_and_cancel_subcontracting_receipt(frm, subcontracting_orders);
//                 }).addClass('btn-warning');
//             }
            
//             // Also keep the regular cancel button
//             frm.add_custom_button(__('Cancel'), function() {
//                 frm.cancel();
//             });
//         }


//         const so_map = {}; // to avoid re-fetching the same Subcontracting Order multiple times
//         const receipt_items = frm.doc.items || [];

//         const unique_so_names = [
//             ...new Set(receipt_items.map(row => row.subcontracting_order).filter(Boolean))
//         ];

//         // Step 1: Load all unique Subcontracting Orders
//         frappe.call({
//             method: "frappe.client.get_list",
//             args: {
//                 doctype: "Subcontracting Order",
//                 filters: [
//                     ["name", "in", unique_so_names]
//                 ],
//                 fields: ["name"]
//             },
//             callback: function(list_response) {
//                 if (!list_response.message || list_response.message.length === 0) return;

//                 const fetch_promises = unique_so_names.map(so_name => {
//                     return new Promise((resolve) => {
//                         frappe.model.with_doc("Subcontracting Order", so_name, function() {
//                             const so_doc = frappe.model.get_doc("Subcontracting Order", so_name);
//                             so_map[so_name] = so_doc;
//                             resolve();
//                         });
//                     });
//                 });

//                 // Step 2: After all Subcontracting Orders are loaded
//                 Promise.all(fetch_promises).then(() => {
//                     receipt_items.forEach(receipt_row => {
//                         const so_doc = so_map[receipt_row.subcontracting_order];
//                         if (!so_doc) return;

//                         const matching_so_item = so_doc.items.find(
//                             so_item => so_item.name === receipt_row.subcontracting_order_item
//                         );

//                         if (matching_so_item) {
//                             receipt_row.custom_plans = matching_so_item.custom_plans;
//                         }
//                     });

//                     frm.refresh_field("items");
//                 });
//             }
//         });
//     }
// });

// function remove_links_and_cancel_subcontracting_receipt(frm, subcontracting_orders) {
//     let confirm_message = `This Subcontracting Receipt is linked to ${subcontracting_orders.length} Subcontracting Order(s):<br><br>`;
//     subcontracting_orders.forEach(order => {
//         confirm_message += `• ${order}<br>`;
//     });
//     confirm_message += `<br>All Subcontract Receipt milestone links will be removed before cancellation. Continue?`;
    
//     frappe.confirm(
//         confirm_message,
//         function() {
//             frappe.call({
//                 method: 'textiles_and_garments.time_and_action_milestones.remove_subcontracting_receipt_links_before_cancel',
//                 args: {
//                     receipt_name: frm.doc.name,
//                     subcontracting_orders: subcontracting_orders
//                 },
//                 callback: function(r) {
//                     if (r.message && r.message.success) {
//                         frappe.msgprint({
//                             title: __('Success'),
//                             indicator: 'green',
//                             message: __('Removed Subcontract Receipt links from {0} plan(s). Cancelling...', [r.message.removed_count])
//                         });
                        
//                         setTimeout(() => {
//                             frm.cancel();
//                         }, 1500);
//                     } else {
//                         frappe.msgprint({
//                             title: __('Error'),
//                             indicator: 'red',
//                             message: __('Failed to remove links: {0}', [r.message.error || 'Unknown error'])
//                         });
//                     }
//                 }
//             });
//         }
//     );
// }

frappe.ui.form.on('Subcontracting Receipt', {
    refresh(frm) {
        console.log("Subcontracting Receipt", frm);

        if (frm.doc.docstatus === 1) {
            let has_subcontracting_orders = false;
            let subcontracting_orders = [];
            
            if (frm.doc.items) {
                frm.doc.items.forEach(item => {
                    if (item.subcontracting_order) {
                        has_subcontracting_orders = true;
                        if (!subcontracting_orders.includes(item.subcontracting_order)) {
                            subcontracting_orders.push(item.subcontracting_order);
                        }
                    }
                });
            }
            
            if (has_subcontracting_orders) {
                frm.add_custom_button(__('🔗 Remove Links & Cancel'), function() {
                    remove_links_and_cancel_subcontracting_receipt(frm, subcontracting_orders);
                }).addClass('btn-warning');
            }
            
            frm.add_custom_button(__('Cancel'), function() {
                frm.cancel();
            });
        }


        const so_map = {};
        const receipt_items = frm.doc.items || [];

        const unique_so_names = [
            ...new Set(receipt_items.map(row => row.subcontracting_order).filter(Boolean))
        ];

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Subcontracting Order",
                filters: [
                    ["name", "in", unique_so_names]
                ],
                fields: ["name"]
            },
            callback: function(list_response) {
                if (!list_response.message || list_response.message.length === 0) return;

                const fetch_promises = unique_so_names.map(so_name => {
                    return new Promise((resolve) => {
                        frappe.model.with_doc("Subcontracting Order", so_name, function() {
                            const so_doc = frappe.model.get_doc("Subcontracting Order", so_name);
                            so_map[so_name] = so_doc;
                            resolve();
                        });
                    });
                });

                Promise.all(fetch_promises).then(() => {
                    receipt_items.forEach(receipt_row => {
                        const so_doc = so_map[receipt_row.subcontracting_order];
                        if (!so_doc) return;

                        const matching_so_item = so_doc.items.find(
                            so_item => so_item.name === receipt_row.subcontracting_order_item
                        );

                        if (matching_so_item) {
                            receipt_row.custom_plans = matching_so_item.custom_plans;
                        }
                    });

                    frm.refresh_field("items");
                });
            }
        });
    }
});

function remove_links_and_cancel_subcontracting_receipt(frm, subcontracting_orders) {
    let confirm_message = `This Subcontracting Receipt is linked to ${subcontracting_orders.length} Subcontracting Order(s):<br><br>`;
    subcontracting_orders.forEach(order => {
        confirm_message += `• ${order}<br>`;
    });
    confirm_message += `<br>All Subcontract Receipt milestone links will be removed before cancellation. Continue?`;
    
    frappe.confirm(
        confirm_message,
        function() {
            frappe.call({
                method: 'textiles_and_garments.time_and_action_milestones.remove_subcontracting_receipt_links_before_cancel',
                args: {
                    receipt_name: frm.doc.name,
                    subcontracting_orders: subcontracting_orders
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.msgprint({
                            title: __('Success'),
                            indicator: 'green',
                            message: __('Removed Subcontract Receipt links from {0} plan(s). Cancelling...', [r.message.removed_count])
                        });
                        
                        setTimeout(() => {
                            frm.cancel();
                        }, 1500);
                    } else {
                        frappe.msgprint({
                            title: __('Error'),
                            indicator: 'red',
                            message: __('Failed to remove links: {0}', [r.message.error || 'Unknown error'])
                        });
                    }
                }
            });
        }
    );
}



frappe.ui.form.on("Subcontracting Receipt Item", {
    custom_create_batch(frm, cdt, cdn) {
        var child = locals[cdt][cdn];

        if (child.__creating_batch) {
            return;
        }
        child.__creating_batch = true;

        var main_item_code = child.item_code;
        if (!main_item_code) {
            frappe.msgprint(__("Item Code is missing on this row."));
            child.__creating_batch = false;
            return;
        }

        var row_subcontracting_order = child.subcontracting_order;
        if (!row_subcontracting_order) {
            frappe.msgprint(__("Subcontracting Order is missing on this row — cannot trace the source Stock Entry."));
            child.__creating_batch = false;
            return;
        }

        if (child.batch_no) {
            frappe.confirm(
                __("This row already has Batch No <b>{0}</b>. Do you want to overwrite it?", [child.batch_no]),
                function () {
                    find_and_create_batch();
                },
                function () {
                    child.__creating_batch = false;
                }
            );
        } else {
            find_and_create_batch();
        }

        function extract_size_from_item_code() {
            // --- Collar/Cuff item codes carry their size as the LAST '/'-delimited
            // segment, e.g. "SKF11740/SUNSHINE YELLOW/16.5X3.5" -> "16.5X3.5" ---
            if (!main_item_code || typeof main_item_code !== 'string') {
                return null;
            }
            var parts = main_item_code.split('/');
            if (parts.length < 3) {
                // Not enough segments to contain a size - don't guess
                console.warn("[create_batch] item_code doesn't have expected 3+ segments for size extraction:", main_item_code);
                return null;
            }
            var size = parts[parts.length - 1].trim();
            return size.length ? size : null;
        }

        function get_suffix_segment() {
            // --- Suffix rule ---
            // WOC/WC: keyed off item_code + stock_uom, no size involved.
            // Collar/Cuff (Pcs, commercial_name-driven): size is inserted BEFORE the
            // C/U letter, e.g. ".../26-02323/16.5X3.5/C" - size comes from the item
            // code's last segment (see extract_size_from_item_code).
            var commercial_name = (child.commercial_name || '').toUpperCase();
            var item_upper = (main_item_code || '').toUpperCase();

            if (child.stock_uom === "Kgs" && item_upper.includes("WOC")) {
                return "WOC";
            } else if (child.stock_uom === "Kgs" && item_upper.includes("WC")) {
                return "WC";
            } else if (commercial_name.includes("COLLAR") && child.stock_uom === "Pcs") {
                var collar_size = extract_size_from_item_code();
                if (!collar_size) {
                    frappe.msgprint({
                        title: __("Missing Size"),
                        indicator: "orange",
                        message: __("Could not extract size from Item Code {0} for Collar batch naming. Proceeding without size.", [main_item_code])
                    });
                    return "C";
                }
                return collar_size + "/C";
            } else if (commercial_name.includes("CUFF") && child.stock_uom === "Pcs") {
                var cuff_size = extract_size_from_item_code();
                if (!cuff_size) {
                    frappe.msgprint({
                        title: __("Missing Size"),
                        indicator: "orange",
                        message: __("Could not extract size from Item Code {0} for Cuff batch naming. Proceeding without size.", [main_item_code])
                    });
                    return "U";
                }
                return cuff_size + "/U";
            }
            return null; // plain format, no suffix
        }

        function is_named_fabric() {
            var commercial_name = (child.commercial_name || '').toUpperCase().trim();
            return commercial_name.startsWith("MARS") ||
                   commercial_name.startsWith("POLO") ||
                   commercial_name.startsWith("VANTAGE");
        }

        function get_base_batch(rm_batch) {
            if (!rm_batch || typeof rm_batch !== 'string') {
                console.warn("get_base_batch received an invalid batch value, skipping transformation:", rm_batch);
                return null;
            }

            if (is_named_fabric()) {
                return rm_batch;
            }

            var parts = rm_batch.split('/');
            if (parts.length < 2) {
                return rm_batch;
            }

            var fiscal_year = parts[0].substring(0, 2);
            var wo_segment = parts[1];
            var new_segment = wo_segment.replace(/^WO/i, fiscal_year);
            parts[1] = new_segment;

            return parts.join('/');
        }

        function find_and_create_batch() {
            // --- Step 1: find matching RM item(s) from supplied_items where main_item_code == this row's item_code ---
            var matched_rm_items = (frm.doc.supplied_items || [])
                .filter(function (r) { return r.main_item_code === main_item_code; })
                .map(function (r) { return r.rm_item_code; })
                .filter(Boolean);

            matched_rm_items = matched_rm_items.filter(function (v, i, arr) { return arr.indexOf(v) === i; });

            console.log("[create_batch] main_item_code:", main_item_code);
            console.log("[create_batch] matched_rm_items:", matched_rm_items);

            if (!matched_rm_items.length) {
                frappe.msgprint(__("No matching Raw Material item found in Supplied Items for {0}.", [main_item_code]));
                child.__creating_batch = false;
                return;
            }

            // --- Step 2 & 3 combined: server-side lookup, bypasses field-level permission
            // masking on Stock Entry Detail (parent/batch_no were being silently dropped
            // by frappe.db.get_list for this role - confirmed via console diagnostics) ---
            frappe.call({
                method: "textiles_and_garments.utils.batch_lookup.get_rm_batch_details",
                args: {
                    subcontracting_order: row_subcontracting_order,
                    rm_item_codes: matched_rm_items
                }
            }).then(function (r) {
                var rows = r.message || [];
                console.log("[create_batch] rows from server:", rows);

                if (!rows.length) {
                    frappe.msgprint(__(
                        "No Stock Entry Detail rows found for Subcontracting Order {0} and Raw Material item(s): {1}.",
                        [row_subcontracting_order, matched_rm_items.join(", ")]
                    ));
                    child.__creating_batch = false;
                    return;
                }

                var valid_rows = rows.filter(function (r) {
                    return typeof r.batch_no === 'string' && r.batch_no.trim().length > 0;
                });

                console.log("[create_batch] valid_rows:", valid_rows);

                if (!valid_rows.length) {
                    var seen = rows.map(function (r) {
                        var parentVal = r.parent || "(missing)";
                        var itemVal = r.item_code || "(missing)";
                        var batchVal = r.batch_no ? ("'" + r.batch_no + "'") : "(missing)";
                        return "Stock Entry: " + parentVal + " | Item: " + itemVal + " | batch_no: " + batchVal;
                    }).join("<br>");

                    frappe.msgprint({
                        title: __("No usable Batch No found"),
                        indicator: "orange",
                        message: "Rows found, but none had a usable Batch No:<br><br>" + seen
                    });
                    child.__creating_batch = false;
                    return;
                }

                var suffix_segment = get_suffix_segment();
                var target_batches = valid_rows
                    .map(function (r) {
                        var base = get_base_batch(r.batch_no);
                        if (!base) {
                            return null;
                        }
                        return suffix_segment ? (base + '/' + suffix_segment) : base;
                    })
                    .filter(Boolean);

                if (!target_batches.length) {
                    frappe.msgprint(__("Could not construct a valid target Batch No from the available Stock Entry Detail rows."));
                    child.__creating_batch = false;
                    return;
                }

                var distinct_targets = target_batches.filter(function (v, i, arr) { return arr.indexOf(v) === i; });

                if (distinct_targets.length === 1) {
                    create_or_assign_batch(distinct_targets[0]);
                } else {
                    show_batch_selection_dialog(distinct_targets);
                }
            }).catch(function (err) {
                console.error("Error fetching RM batch details:", err);
                frappe.msgprint(__("Error looking up batch numbers. Please try again."));
                child.__creating_batch = false;
            });
        }

        function show_batch_selection_dialog(target_batches) {
            var dialog = new frappe.ui.Dialog({
                title: __("Select Batch No"),
                fields: [
                    {
                        fieldname: "selected_batch",
                        fieldtype: "Select",
                        label: __("Multiple batches possible — select one"),
                        options: target_batches,
                        reqd: 1
                    }
                ],
                primary_action_label: __("Create / Assign"),
                primary_action: function (values) {
                    dialog.hide();
                    create_or_assign_batch(values.selected_batch);
                },
                onhide: function () {
                    if (child.__creating_batch) {
                        child.__creating_batch = false;
                    }
                }
            });

            dialog.show();
        }

        function create_or_assign_batch(batch_no) {
            frappe.db.get_value("Batch", { batch_id: batch_no }, "name").then(function (res) {
                if (res && res.message && res.message.name) {
                    frappe.show_alert({
                        message: __("Batch {0} already exists, assigned to item {1}", [batch_no, main_item_code]),
                        indicator: "blue"
                    });
                    child.batch_no = batch_no;
                    frm.refresh_field("items");
                    child.__creating_batch = false;
                } else {
                    attempt_create(batch_no);
                }
            }).catch(function () {
                attempt_create(batch_no);
            });
        }

        function attempt_create(batch_no) {
            frappe.call({
                method: "frappe.client.insert",
                args: {
                    doc: {
                        doctype: "Batch",
                        batch_id: batch_no,
                        item: main_item_code,
                        manufacturing_date: frappe.datetime.now_date(),
                    },
                },
                callback: function (response) {
                    if (response.message) {
                        frappe.show_alert({
                            message: __("Batch {0} created successfully for Item {1}", [batch_no, main_item_code]),
                            indicator: "green"
                        });
                        child.batch_no = batch_no;
                        frm.refresh_field("items");
                    } else {
                        frappe.msgprint(__("Failed to create Batch for Item {0}", [main_item_code]));
                    }
                    child.__creating_batch = false;
                },
                error: function (err) {
                    console.error("Error creating Batch:", err);

                    var server_message = (err && err.exc) ? err.exc.toString() : "";
                    var already_exists = /already exists/i.test(server_message) ||
                                          (err && err._server_messages && /already exists/i.test(err._server_messages));

                    if (already_exists) {
                        frappe.db.get_value("Batch", batch_no, "item").then(function (res) {
                            var owner_item = res && res.message ? res.message.item : null;

                            if (owner_item === main_item_code) {
                                frappe.show_alert({
                                    message: __("Batch {0} already exists and is correctly linked to Item {1} — assigned.", [batch_no, main_item_code]),
                                    indicator: "blue"
                                });
                                child.batch_no = batch_no;
                                frm.refresh_field("items");
                            } else {
                                frappe.msgprint({
                                    title: __("Batch Conflict"),
                                    indicator: "red",
                                    message: __(
                                        "Batch {0} already exists but is assigned to a different item ({1}), not {2}. Not assigning it automatically — please check.",
                                        [batch_no, owner_item || __("unknown"), main_item_code]
                                    )
                                });
                            }
                            child.__creating_batch = false;
                        }).catch(function (lookupErr) {
                            console.error("Error verifying existing Batch ownership:", lookupErr);
                            frappe.msgprint(__("Batch {0} already exists, but its ownership could not be verified. Please check manually.", [batch_no]));
                            child.__creating_batch = false;
                        });
                    } else {
                        frappe.msgprint(__("Error creating batch. Please try again."));
                        child.__creating_batch = false;
                    }
                }
            });
        }
    },
});