frappe.ui.form.on('Stock Entry', {
    setup(frm) {
        console.log("Stock Entry custom_create_psr_for_all_reserved_wip_plans", frm);

        if (
            frm.doc.custom_create_psr_for_all_reserved_wip_plans == 0 &&
            (
                frm.doc.stock_entry_type == "Send to Subcontractor" ||
                frm.doc.stock_entry_type == "Material Transfer for Manufacture"
            )
        ) {
            frm.doc.items.forEach(so_row => {
                   
                so_row.custom_create_psr_for_all_reserved_wip_plans = 1;
                    
            });
            frm.doc.custom_create_psr_for_all_reserved_wip_plans = 1;
            frm.refresh_field("items");
        }
    }
});


frappe.ui.form.on('Stock Entry', {
    refresh(frm) {
        console.log("Stock Entry", frm);

        // // Add custom button only for submitted Stock Entries that aren't cancelled and are 'Send to Subcontractor' type
        // if (frm.doc.docstatus === 1 && frm.doc.stock_entry_type === "Send to Subcontractor") {
        //     // Check if there's a subcontracting order reference
        //     let has_subcontracting_order = frm.doc.subcontracting_order ? true : false;
            
        //     if (has_subcontracting_order) {
        //         frm.add_custom_button(__('🔗 Remove Links & Cancel'), function() {
        //             remove_links_and_cancel_stock_entry(frm);
        //         }).addClass('btn-warning');
        //     }
            
        //     // Also keep the regular cancel button
        //     frm.add_custom_button(__('Cancel'), function() {
        //         frm.cancel();
        //     });
        // }
        // Add custom button only for submitted Stock Entries that aren't cancelled and are supported types
        if (frm.doc.docstatus === 1) {
            let supported_types = ["Material Transfer for Manufacture", "Manufacture", "Send to Subcontractor"];
            let is_supported_type = supported_types.includes(frm.doc.stock_entry_type);
            
            if (is_supported_type) {
                frm.add_custom_button(__('🔗 Remove Links & Cancel'), function() {
                    remove_links_and_cancel_stock_entry(frm);
                }).addClass('btn-warning');
            }
            
            // Also keep the regular cancel button
            frm.add_custom_button(__('Cancel'), function() {
                frm.cancel();
            });
        }


        if (frm.doc.items && frm.doc.stock_entry_type == "Send to Subcontractor") {
            frappe.model.with_doc("Subcontracting Order", frm.doc.subcontracting_order, function() {
                let po_doc = frappe.model.get_doc("Subcontracting Order", frm.doc.subcontracting_order);
                let po_items = po_doc.items || [];
                let so_items = frm.doc.items || [];

                console.log("po_items", po_items);
                console.log("so_items", so_items);

                so_items.forEach(so_row => {
                    let matching_po_item = po_items.find(po_row => po_row.item_code === so_row.subcontracted_item);
                    if (matching_po_item) {
                        so_row.custom_plans = matching_po_item.custom_plans;
                    }
                });

                frm.refresh_field("items");
            });
        }
    }
});

frappe.ui.form.on('Stock Entry', {
    validate(frm) {
        console.log("Stock Entry", frm);

        if (frm.doc.items && frm.doc.stock_entry_type == "Send to Subcontractor") {
            frappe.model.with_doc("Subcontracting Order", frm.doc.subcontracting_order, function() {
                let po_doc = frappe.model.get_doc("Subcontracting Order", frm.doc.subcontracting_order);
                let po_items = po_doc.items || [];
                let so_items = frm.doc.items || [];

                console.log("po_items", po_items);
                console.log("so_items", so_items);

                so_items.forEach(so_row => {
                    let matching_po_item = po_items.find(po_row => po_row.item_code === so_row.subcontracted_item);
                    if (matching_po_item) {
                        so_row.custom_plans = matching_po_item.custom_plans;
                    }
                });

                frm.refresh_field("items");
            });
        }
    }
});

frappe.ui.form.on('Stock Entry', {
    refresh(frm) {
        console.log("Stock Entry", frm);

        if (frm.doc.items && frm.doc.work_order && frm.doc.stock_entry_type == "Material Transfer for Manufacture" || frm.doc.stock_entry_type == "Manufacture") {
            frappe.model.with_doc("Work Order", frm.doc.work_order, function() {
                let wo_doc = frappe.model.get_doc("Work Order", frm.doc.work_order);
                

                console.log("wo_doc", wo_doc);
               
                frm.doc.items.forEach(so_row => {
                    so_row.custom_plans = wo_doc.custom_plans;
                });

                frm.refresh_field("items");
            });
        }
    }
});

frappe.ui.form.on('Stock Entry', {
    validate(frm) {
        console.log("Stock Entry", frm);

        // Handle Material Transfer for Manufacture
        if (frm.doc.items && frm.doc.work_order && frm.doc.stock_entry_type == "Material Transfer for Manufacture") {
            frappe.model.with_doc("Work Order", frm.doc.work_order, function() {
                let wo_doc = frappe.model.get_doc("Work Order", frm.doc.work_order);
                console.log("wo_doc", wo_doc);
                
                // Set custom_plans for all items
                frm.doc.items.forEach(item => {
                    frappe.model.set_value(item.doctype, item.name, "custom_plans", wo_doc.custom_plans);
                });
                
                frm.refresh_field("items");
            });
        }

        // Handle Manufacture entry validation
        if (frm.doc.items && frm.doc.work_order && frm.doc.stock_entry_type == "Manufacture") {
            frappe.model.with_doc("Work Order", frm.doc.work_order, function() {
                let wo_doc = frappe.model.get_doc("Work Order", frm.doc.work_order);
                console.log("wo_doc", wo_doc);
                
                let work_order_item = wo_doc.production_item;
                let work_order_qty = wo_doc.qty;
                let work_order_short_close_qty = wo_doc.custom_short_close_wo_qty || 0;
                let work_order_final_qty = work_order_qty - work_order_short_close_qty;
                
                // Find the manufactured item in stock entry
                let manufactured_item = frm.doc.items.find(item => item.item_code === work_order_item);
                
                if (manufactured_item) {
                    if (manufactured_item.qty > work_order_final_qty) {
                        frappe.msgprint({
                            title: __('Validation Error'),
                            indicator: 'red',
                            message: __(`Manufactured quantity (${manufactured_item.qty}) cannot exceed the work order's final quantity (${work_order_final_qty}) after accounting for short close quantity.`)
                        });
                        frappe.validated = false; // Prevent form submission
                    }
                }
            });
        }
    }
});

frappe.ui.form.on("Stock Entry", {
    refresh: function(frm) {
        console.log("inside public in js", frm);

        if (frm.doc.job_card) {
            frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.create_stock_entry_items",
                args: {
                    docname: frm.doc.job_card,
                },
                callback: function(response) {
                    console.log("inside response", response);
                    if (response.message) {
                        if (frm.doc.stock_entry_type.includes("Material Transfer for Manufacture") && !frm.doc.name.includes("MTM/")) {
                            // Clear existing items from the stock_entry_items table
                            frm.clear_table("items");

                            // Iterate through the returned items and add them to stock_entry_items
                            response.message.forEach(function(item) {
                                console.log("item", item);
                                let qty = item.required_qty - item.transferred_qty;
                                if (qty > 0) {
                                    let child = frm.add_child("items");
                                    child.item_code = item.item_code;
                                    child.qty = qty;
                                    // Set other fields from item as needed
                                    child.stock_uom = item.stock_uom;
                                    child.transfer_qty = qty;
                                    child.uom = item.stock_uom;
                                    child.conversion_factor = 1;
                                    child.s_warehouse = "DYE/LOT SECTION - PSS";
                                    // child.t_warehouse = "Work In Progress - PSS";
                                    child.parentfield = "items";
                                    child.parenttype = "Stock Entry";
                                    child.job_card_item = item.name;
                                    child.doctype = "Stock Entry Detail";
                                }
                            });

                            // Refresh the field to update the UI
                            frm.refresh_field("items");

                            // Optionally save the form after setting items
                            //frm.save();
                        }
                    }
                }
            });
        }


    },

    refresh: function(frm) {
        console.log("frm",frm);
        frm.add_custom_button(__('Update Batch'), function() {
            frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.update_batch",
                args: {
                    // docname: frm.doc.name,
                    custom_duplicate_stock_entry: frm.doc.custom_duplicate_stock_entry
                },
                callback: function(response) {
                    console.log("response", response);
                    if (response.message) {
                        var resp = response.message;

                        console.log("resp", resp);

                        // Loop through frm.doc.items
                        frm.doc.items.forEach(item => {
                            // Find the matching item in the response array
                            let matchingRespItem = resp.find(respItem => respItem.item_code === item.item_code);

                            let matchingRespQty = resp.find(respItem => respItem.qty === item.qty);
                            
                            if (matchingRespItem && matchingRespQty) {
                                // Update the batch_no from the response
                                item.batch_no = matchingRespItem.batch_no;
                            }
                        });

                        // Refresh the field to reflect changes in the UI
                        frm.refresh_field('items');
                    }
                }
            });
        });

    },
    after_save:function(frm){
        if(frm.doc.custom_loading_and_unloading_greige_lot == 1||
            frm.doc.custom_loading_and_unloading_finished_lot == 1||
            frm.doc.custom_loading_and_unloading_wet_lot == 1
            ){
            console.log("custom_include_loading_greige");
            frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.set_operation_cost_in_stock_entry",
                args: {
                    docname: frm.doc.name,
                },
                callback: function(response) {
                    console.log("response",response);
                    if(response.message) {
                        frm.refresh_field("custom_work_order_operations");
                        frm.reload_doc();
                          
                    }
                }
            });

        }
    },  
    work_order: function(frm){
        if (frm.doc.work_order) {
            frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_work_order_data",
                args: {
                    docname: frm.doc.work_order,
                },
                callback: function(response) {
                    console.log("inside response", response);
                    if (response.message) {
                        console.log("response.message",response.message);
                    }
                }
            })
        }                

    }
});

function remove_links_and_cancel_stock_entry(frm) {
    let confirm_message = '';
    let args = {
        stock_entry_name: frm.doc.name
    };
    
    // Set confirmation message and arguments based on stock entry type
    if (frm.doc.stock_entry_type === "Send to Subcontractor") {
        confirm_message = `This Stock Entry (Material Transfer to Subcontractor) is linked to Subcontracting Order: <strong>${frm.doc.subcontracting_order}</strong><br><br>`;
        confirm_message += `All milestone links will be removed before cancellation. Continue?`;
        args.subcontracting_order = frm.doc.subcontracting_order;
    } 
    else if (frm.doc.stock_entry_type === "Material Transfer for Manufacture") {
        confirm_message = `This Stock Entry (Material Transfer for Manufacture) is linked to Work Order: <strong>${frm.doc.work_order}</strong><br><br>`;
        confirm_message += `All milestone links will be removed before cancellation. Continue?`;
        args.work_order = frm.doc.work_order;
    }
    else if (frm.doc.stock_entry_type === "Manufacture") {
        confirm_message = `This Stock Entry (Manufacture) is linked to Work Order: <strong>${frm.doc.work_order}</strong><br><br>`;
        confirm_message += `All milestone links will be removed before cancellation. Continue?`;
        args.work_order = frm.doc.work_order;
    }
    
    frappe.confirm(
        confirm_message,
        function() {
            frappe.call({
                method: 'textiles_and_garments.time_and_action_milestones.remove_stock_entry_links_before_cancel',
                args: args,
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.msgprint({
                            title: __('Success'),
                            indicator: 'green',
                            message: __('Removed {0} links from {1} plan(s). Cancelling Stock Entry...', 
                                [r.message.milestone_name, r.message.removed_count])
                        });
                        
                        // Cancel the Stock Entry after a brief delay to show the message
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


// function remove_links_and_cancel_stock_entry(frm) {
//     let confirm_message = `This Stock Entry (Material Transfer to Subcontractor) is linked to Subcontracting Order: <strong>${frm.doc.subcontracting_order}</strong><br><br>`;
//     confirm_message += `All milestone links will be removed before cancellation. Continue?`;
    
//     frappe.confirm(
//         confirm_message,
//         function() {
//             frappe.call({
//                 method: 'textiles_and_garments.time_and_action_milestones.remove_stock_entry_links_before_cancel',
//                 args: {
//                     stock_entry_name: frm.doc.name,
//                     subcontracting_order: frm.doc.subcontracting_order
//                 },
//                 callback: function(r) {
//                     if (r.message && r.message.success) {
//                         frappe.msgprint({
//                             title: __('Success'),
//                             indicator: 'green',
//                             message: __('Removed Material Transfer links from {0} plan(s). Cancelling Stock Entry...', [r.message.removed_count])
//                         });
                        
//                         // Cancel the Stock Entry after a brief delay to show the message
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



// frappe.ui.form.on("Stock Entry", {
//     refresh:function(frm){
//         console.log("inside public in js", frm);
//         // if(frm.doc.job_card){
//         //     frm.doc.items.forEach(d => {
//         //     frappe.model.set_value(d.doctype, d.name, "job_card", frm.doc.job_card);
//         //     });
//         // }
//         if(frm.doc.job_card){
//             frappe.call({
//                 method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.create_stock_entry_items",
//                 args: {
//                     docname: frm.doc.job_card,
//                 },
//                 callback: function(response) {
//                     console.log("inside response",response);
//                     if(response.message) {
//                         if(frm.doc.stock_entry_type.includes("Material Transfer for Manufacture") ){
//                             // Clear existing items from stock_entry_items table
//                             frm.clear_table("items");
//                             // Iterate through the returned items and add them to stock_entry_items
//                             response.message.forEach(function(item) {
//                                 console.log("item",item);
//                                 var qty = 0;
//                                 qty = item.required_qty - item.transferred_qty;
//                                 if(qty > 0){
//                                     let child = frm.add_child("items");
//                                     child.item_code = item.item_code;
//                                     child.qty = item.required_qty - item.transferred_qty; // Or any other field mapping
//                                     // Set other fields from item as needed
//                                     child.stock_uom = item.stock_uom;
//                                     child.transfer_qty = item.required_qty - item.transferred_qty;
//                                     child.uom = item.stock_uom;
//                                     child.conversion_factor = 1;
//                                     child.s_warehouse = "Stores - PSS";
//                                     child.t_warehouse = "Work In Progress - PSS";
//                                     child.parentfield = "items";
//                                     child.parenttype = "Stock Entry";
//                                     child.job_card_item = item.name;
//                                     child.doctype = "Stock Entry Detail";
//                                 } 
//                             });
//                             // Refresh the field to update UI
//                             frm.refresh_field("items");
//                             //Save the form after setting items
//                             //frm.save();
//                         }                       
//                     }
//                 }
//             });
//         }
//           },
//     validate:function(frm){
//         if(frm.doc.custom_work_order){
//             console.log("inside validate");
//             frm.doc.items.forEach(d => {
//                 console.log("d",d);
//                 frappe.call({
//                 method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.update_work_order_in_stock_entry",
//                 args: {
//                     // docname: frm.doc.job_card,
//                     docname: d.batch_no,
//                     work_order: frm.doc.custom_work_order
//                 },
//                 callback: function(response) {
//                     console.log("inside response",response);
//                     if(response.message) {   
//                             // Iterate through the returned items and add them to stock_entry_items
//                             response.message.forEach(function(item) {
//                                 console.log("item",item);
//                             });
//                     }
//                 }
//                 // frappe.model.set_value("Batch", d.batch_no, "custom_work_order", frm.doc.custom_work_order);
//             });
//         })
//         }
//     })
// });



// frappe.ui.form.on("Stock Entry Item", {
//     custom_create_batch(frm, cdt, cdn) {
//         // Get the specific row in the child table
//         let row = frappe.get_doc(cdt, cdn);

//         // Perform actions when the button is clicked
//         frappe.msgprint(`Button clicked for Item Code: ${row.item_code}`);
//         console.log("Row data:", row);

//         // Example: Perform any other logic or actions here
//         // You can access and manipulate row properties like row.qty, row.rate, etc.
//     }   
// });  

// frappe.ui.form.on("Stock Entry Detail", {
//     custom_create_batch(frm, cdt, cdn) {
//         console.log("frm Stock Entry Detail",frm);
//         var child = locals[cdt][cdn];
        
//         // // Perform actions when the button is clicked
//         // // frappe.model.set_value("Batch", d.batch_no, "custom_work_order", frm.doc.custom_work_order);
//         // frappe.msgprint(`Button clicked for Item Code: ${child.item_code}`);
//         // console.log("Row data:", child);
//         // Example: Set the batch_no value

//         if(frm.doc.work_order){
//            // console.log("work_order",work_order);
//            // console.log("project",project);
//         }
//         item = child.item_code;
//         child.batch_no = "BATCH-001"; // Replace with the desired batch number or logic to generate it
        
//         // Refresh the field to reflect changes in the UI
//         frm.refresh_field("items"); // Ensure "items" 
        
//     },
// });


// frappe.ui.form.on("Stock Entry Detail", {
//     custom_create_batch(frm, cdt, cdn) {
//         console.log("frm Stock Entry Detail", frm);
//         var child = locals[cdt][cdn];
//         var work_order;
//         var project;
//         var batchNo;
//         var item;

//         if (frm.doc.work_order) {
//             // Additional logic if needed
//              work_order = frm.doc.work_order;
//              project = frm.doc.project;
//         }

//         item = child.item_code;
//         console.log("item",item);
//         if (child.commercial_name && (child.commercial_name.includes("POLO") 
//             || child.commercial_name.includes("MARS")) &&
//             child.stock_uom == "Kgs" && item.includes("WOC")) {
//         // if(child){    
//             // Your logic here
//             batchNo = project +'/'+ work_order +'/'+ 'WOC'; // Replace with the desired batch number or logic to generate it
//             child.batch_no = batchNo;
//         }else if(child.commercial_name && (child.commercial_name.includes("POLO") 
//             || child.commercial_name.includes("MARS")) &&
//             child.stock_uom == "Kgs" && item.includes("WC")){
//             batchNo = project +'/'+ work_order +'/'+ 'WC'; 
//             child.batch_no = batchNo;
//         }else if(child.commercial_name && (child.commercial_name.includes("COLLAR")) &&
//             child.stock_uom == "Pcs"){
//             batchNo = project +'/'+ work_order +'/'+ 'C'; 
//             child.batch_no = batchNo;
//         }else if(child.commercial_name && (child.commercial_name.includes("CUFF")) &&
//             child.stock_uom == "Pcs"){
//             batchNo = project +'/'+ work_order +'/'+ 'U'; 
//             child.batch_no = batchNo;
//         }else{
//             batchNo = project +'/'+ work_order; 
//             child.batch_no = batchNo;
//         }    

//         // let batchNo = "BATCH-001"; // Replace with the desired batch number or logic to generate it
//         // child.batch_no = batchNo;

//         // Call server-side method to create the Batch document
//         frappe.call({
//             method: "frappe.client.insert",
//             args: {
//                 doc: {
//                     doctype: "Batch",
//                     batch_id: batchNo,
//                     item: item,
//                     manufacturing_date: frappe.datetime.now_date(), // Example: Set the manufacturing date
//                     // expiry_date: frappe.datetime.add_days(frappe.datetime.now_date(), 365), // Example: Set expiry date
//                 },
//             },
//             callback: function(response) {
//                 if (response.message) {
//                     frappe.msgprint(`Batch ${batchNo} created successfully for Item ${item}`);
//                     console.log("Batch created:", response.message);
//                 } else {
//                     frappe.msgprint(`Failed to create Batch for Item ${item}`);
//                 }
//             },
//             error: function(err) {
//                 console.error("Error creating Batch:", err);
//             }
//         });

//         // Refresh the field to reflect changes in the UI
//         frm.refresh_field("items");
//     },
// });


// frappe.ui.form.on("Stock Entry Detail", {
//     custom_create_batch(frm, cdt, cdn) {
//         console.log("frm Stock Entry Detail", frm);
//         var child = locals[cdt][cdn];
//         var work_order;
//         var project;
//         var batchNo;
//         var item;

//         // FIX 1: Properly handle work_order and project assignment
//         if (frm.doc.work_order && !frm.doc.custom_reprocess_work_order_reference) {
//             work_order = frm.doc.work_order;
//             project = frm.doc.project;
//         } else if (frm.doc.custom_reprocess_work_order_reference) {
//             work_order = frm.doc.custom_reprocess_work_order_reference + '/' + frm.doc.work_order;
//             project = frm.doc.project;
//         } else {
//             // FIX 2: Provide fallback values to avoid undefined in batchNo
//             work_order = frm.doc.work_order || 'NO_WO';
//             project = frm.doc.project || 'NO_PROJECT';
//         }

//         item = child.item_code;
//         console.log("item", item);
        
//         // FIX 3: Add null checks for commercial_name to prevent errors
//         const commercial_name = child.commercial_name || '';
        
//         if (commercial_name && (commercial_name.includes("POLO") || commercial_name.includes("MARS")) &&
//             child.stock_uom == "Kgs" && item.includes("WOC")) {
//             batchNo = project + '/' + work_order + '/' + 'WOC';
//             child.batch_no = batchNo;
//         } else if (commercial_name && (commercial_name.includes("POLO") || commercial_name.includes("MARS")) &&
//             child.stock_uom == "Kgs" && item.includes("WC")) {
//             batchNo = project + '/' + work_order + '/' + 'WC';
//             child.batch_no = batchNo;
//         } else if (commercial_name && commercial_name.includes("COLLAR") &&
//             child.stock_uom == "Pcs") {
//             batchNo = project + '/' + work_order + '/' + 'C';
//             child.batch_no = batchNo;
//         } else if (commercial_name && commercial_name.includes("CUFF") &&
//             child.stock_uom == "Pcs") {
//             batchNo = project + '/' + work_order + '/' + 'U';
//             child.batch_no = batchNo;
//         } else {
//             batchNo = project + '/' + work_order;
//             child.batch_no = batchNo;
//         }

//         console.log("Creating batch:", batchNo, "for item:", item);

//         // FIX 4: Check if batch already exists before creating
//         frappe.call({
//             method: "frappe.client.get_value",
//             args: {
//                 doctype: "Batch",
//                 filters: { batch_id: batchNo },
//                 fieldname: ["name"]
//             },
//             callback: function(response) {
//                 if (response.message && response.message.name) {
//                     // Batch already exists, just assign it
//                     frappe.msgprint(__("Batch {0} already exists, assigned to item {1}", [batchNo, item]));
//                     child.batch_no = batchNo;
//                     frm.refresh_field("items");
//                 } else {
//                     // Create new batch
//                     frappe.call({
//                         method: "frappe.client.insert",
//                         args: {
//                             doc: {
//                                 doctype: "Batch",
//                                 batch_id: batchNo,
//                                 item: item,
//                                 manufacturing_date: frappe.datetime.now_date(),
//                             },
//                         },
//                         callback: function(response) {
//                             if (response.message) {
//                                 frappe.msgprint(__("Batch {0} created successfully for Item {1}", [batchNo, item]));
//                                 console.log("Batch created:", response.message);
//                                 child.batch_no = batchNo;
//                                 frm.refresh_field("items");
//                             } else {
//                                 frappe.msgprint(__("Failed to create Batch for Item {0}", [item]));
//                             }
//                         },
//                         error: function(err) {
//                             console.error("Error creating Batch:", err);
//                             frappe.msgprint(__("Error creating batch. Please try again."));
//                         }
//                     });
//                 }
//             },
//             error: function(err) {
//                 console.error("Error checking batch existence:", err);
//             }
//         });
//     },
// });

frappe.ui.form.on("Stock Entry Detail", {
    custom_create_batch(frm, cdt, cdn) {
        console.log("frm Stock Entry Detail", frm);
        var child = locals[cdt][cdn];
        var work_order;
        var project;
        var batchNo;
        var item;

        // First, get the work_order document to fetch custom_reprocess_work_order_reference
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Work Order",
                name: frm.doc.work_order
            },
            callback: function(response) {
                if (response.message) {
                    var work_order_doc = response.message;
                    var reprocess_reference = work_order_doc.custom_reprocess_work_order_reference;
                    
                    // Now determine work_order and project based on the reprocess reference
                    if (frm.doc.work_order && !reprocess_reference) {
                        work_order = frm.doc.work_order;
                        project = frm.doc.project;
                    } else if (reprocess_reference) {
                        work_order = reprocess_reference + '/' + frm.doc.work_order;
                        project = frm.doc.project;
                    } else {
                        work_order = frm.doc.work_order || 'NO_WO';
                        project = frm.doc.project || 'NO_PROJECT';
                    }

                    item = child.item_code;
                    console.log("item", item);
                    
                    // Add null checks for commercial_name to prevent errors
                    const commercial_name = child.commercial_name || '';
                    
                    if (commercial_name && (commercial_name.includes("POLO") || commercial_name.includes("MARS")) &&
                        child.stock_uom == "Kgs" && item.includes("WOC")) {
                        batchNo = project + '/' + work_order + '/' + 'WOC';
                        child.batch_no = batchNo;
                    } else if (commercial_name && (commercial_name.includes("POLO") || commercial_name.includes("MARS")) &&
                        child.stock_uom == "Kgs" && item.includes("WC")) {
                        batchNo = project + '/' + work_order + '/' + 'WC';
                        child.batch_no = batchNo;
                    } else if (commercial_name && commercial_name.includes("COLLAR") &&
                        child.stock_uom == "Pcs") {
                        batchNo = project + '/' + work_order + '/' + 'C';
                        child.batch_no = batchNo;
                    } else if (commercial_name && commercial_name.includes("CUFF") &&
                        child.stock_uom == "Pcs") {
                        batchNo = project + '/' + work_order + '/' + 'U';
                        child.batch_no = batchNo;
                    } else {
                        batchNo = project + '/' + work_order;
                        child.batch_no = batchNo;
                    }

                    console.log("Creating batch:", batchNo, "for item:", item);

                    // Check if batch already exists before creating
                    frappe.call({
                        method: "frappe.client.get_value",
                        args: {
                            doctype: "Batch",
                            filters: { batch_id: batchNo },
                            fieldname: ["name"]
                        },
                        callback: function(response) {
                            if (response.message && response.message.name) {
                                // Batch already exists, just assign it
                                frappe.msgprint(__("Batch {0} already exists, assigned to item {1}", [batchNo, item]));
                                child.batch_no = batchNo;
                                frm.refresh_field("items");
                            } else {
                                // Create new batch
                                frappe.call({
                                    method: "frappe.client.insert",
                                    args: {
                                        doc: {
                                            doctype: "Batch",
                                            batch_id: batchNo,
                                            item: item,
                                            manufacturing_date: frappe.datetime.now_date(),
                                        },
                                    },
                                    callback: function(response) {
                                        if (response.message) {
                                            frappe.msgprint(__("Batch {0} created successfully for Item {1}", [batchNo, item]));
                                            console.log("Batch created:", response.message);
                                            child.batch_no = batchNo;
                                            frm.refresh_field("items");
                                        } else {
                                            frappe.msgprint(__("Failed to create Batch for Item {0}", [item]));
                                        }
                                    },
                                    error: function(err) {
                                        console.error("Error creating Batch:", err);
                                        frappe.msgprint(__("Error creating batch. Please try again."));
                                    }
                                });
                            }
                        },
                        error: function(err) {
                            console.error("Error checking batch existence:", err);
                        }
                    });
                } else {
                    frappe.msgprint(__("Work Order {0} not found", [frm.doc.work_order]));
                }
            },
            error: function(err) {
                console.error("Error fetching Work Order:", err);
                frappe.msgprint(__("Error fetching Work Order details. Please try again."));
            }
        });
    },
});