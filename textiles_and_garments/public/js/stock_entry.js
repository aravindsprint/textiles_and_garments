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
        // frm.add_custom_button(__('Update Batch'), function() {
        //     frappe.call({
        //         method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.update_batch",
        //         args: {
        //             docname: frm.doc.name,
        //             duplicate_stock_entry_name: frm.doc.custom_duplicate_stock_entry
        //         },
        //         callback: function(response) {
        //             console.log("response",response);
        //             if(response.message) {
        //                 console.log("response.message",response.message);
        //                 var resp = response.message;

        //                 // frm.refresh_field("custom_total_operating_cost_include_water");
        //                 // frm.reload_doc();

                       
        //                // frappe.db.set_value('Work Order', frm.doc.name, 'custom_total_operating_cost_include_water', response.message);

        //                // // frm.set_value("custom_total_operating_cost_include_water", response.message);
        //                // // //frm.save('Submit');
                        
        //                // // // frappe.db.set_value('Work Order', frm.doc.name, '', response.message)
        //                // // //  .then(() => {
        //                // // //      frappe.msgprint(__('Additional Operating Cost updated successfully.'));
        //                // // //  });
        //                //  frm.save('Update');
                        
                          
        //             }
        //         }
        //     });
        // });



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



        // if (frm.doc.custom_work_order) {
        //     console.log("inside validate");
            
        //     // frm.doc.items.forEach(d => {
        //     //     console.log("d", d);
        //     //     console.log("inside validate",frm.doc.custom_work_order);
        //     //     console.log("inside validate",d.batch_no);
        //     //     console.log("inside validate",d.qty);
        //     //     frappe.call({
        //     //         method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.update_work_order_in_stock_entry",
        //     //         args: {
        //     //             docname: d.batch_no,
        //     //             work_order: frm.doc.custom_work_order,
        //     //             qty: d.qty
        //     //         },
        //     //         callback: function(response) {
        //     //             console.log("inside response", response);
        //     //             if (response.message) {
        //     //                 // Iterate through the returned items (if needed)
        //     //                 response.message.forEach(function(item) {
        //     //                     console.log("item", item);
        //     //                 });
        //     //             }
        //     //         }
        //     //     });
        //     // });
        // }
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