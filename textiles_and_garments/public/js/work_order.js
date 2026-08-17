frappe.ui.form.on("Work Order", {
    refresh:function(frm){

        
       
        // frm.set_query("custom_parent_fabric_work_order", function() {
        //     return {
        //         filters: {
        //             docstatus: 1,
        //             custom_plan_items: frm.doc.custom_plan_items
        //         }
        //     };
        // });
        let production_item_full = frm.doc.production_item; // Get the full production_item value

        if (production_item_full) {
            let parts = production_item_full.split('/');
            let filter_production_item = production_item_full; // Default filter value

            // Ensure there are at least two parts to apply the specific pattern
            if (parts.length >= 2) {
                let firstSegment = parts[0];  // e.g., "DKF12187"
                let secondSegment = parts[1]; // e.g., "SC BLACK"

                // Extract the leading alphabetic characters from the first segment.
                // This regex matches one or more letters at the beginning of the string.
                let alphaPrefixMatch = firstSegment.match(/^[A-Za-z]+/);
                let modifiedFirstSegment;

                if (alphaPrefixMatch && alphaPrefixMatch[0].length > 0) {
                    // If an alphabetic prefix is found, use it followed by '%'
                    modifiedFirstSegment = alphaPrefixMatch[0] + '%'; // e.g., "DKF%"
                } else {
                    // If no alphabetic prefix (e.g., "12345/ABC"), or it's just letters,
                    // use the entire first segment followed by '%'
                    modifiedFirstSegment = firstSegment + '%'; // e.g., "12345%" or "ABC%"
                }

                // Construct the new filter pattern: "ModifiedFirstPart/SecondPart/%"
                filter_production_item = modifiedFirstSegment + '/' + secondSegment + '/%';
            }
            // If parts.length is less than 2, the `filter_production_item` remains the
            // original `production_item_full`, and the `like` filter will effectively
            // search for "%original_value%" as a fallback.

            frm.set_query("custom_parent_fabric_work_order", function() {
                return {
                    filters: [
                        ["docstatus", "=", 1],
                        ["custom_plan_items", "=", frm.doc.custom_plan_items],
                        // Use the dynamically constructed filter_production_item
                        ["production_item", "like", filter_production_item]
                    ]
                };
            });

            // frm.set_query("custom_parent_purchase_order", function() {
            //     return {
            //         filters: [
            //             ["docstatus", "=", 1],
            //             // ["custom_plan_items", "=", frm.doc.custom_plan_items],
            //             // // Use the dynamically constructed filter_production_item
            //             // ["production_item", "like", filter_production_item]
            //         ]
            //     };
            // });

            // frm.set_query("custom_parent_purchase_order", function() {
            //     const production_item = frm.doc.production_item;
            //     const custom_plan_items = frm.doc.custom_plan_items;
                
            //     return {
            //         filters: [
            //             ["docstatus", "=", 1],
            //             ["custom_plan_items", "=", custom_plan_items],
            //             ["name", "in", frappe.model.with_doctype("Purchase Order", function() {
            //                 return frappe.call({
            //                     method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_matching_po_items",
            //                     args: {
            //                         production_item: production_item
            //                     },
            //                     callback: function(r) {
            //                         return r.message;
            //                     },
            //                     async: false
            //                 }).message;
            //             })]
            //         ]
            //     };
            // });
            // po_response = []

            // frappe.call({
            //     method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_matching_po_items",
            //     args: {
            //         production_item: frm.doc.production_item,
            //     },
            //     callback: function(response) {
            //         console.log("response get_matching_po_items",response);
            //         if(response.message) {
            //             // frm.refresh_field("custom_work_order_operations");
            //             // frm.reload_doc();
            //             po_response = response.message;
            //             console.log("po_response",po_response);
                          
            //         }
            //     }
            // });

            // frm.set_query("custom_parent_purchase_order", function() {
            //     const production_item = frm.doc.production_item;
            //     const custom_plan_items = frm.doc.custom_plan_items;
                
            //     return {
            //         filters: [
            //             ["docstatus", "=", 1],
            //             ["custom_plan_items", "=", custom_plan_items],

            //             // ["name", "in", frappe.db.get_list("Purchase Order Item", {
            //             //     filters: {
            //             //         "item_code": production_item,
            //             //         "docstatus": 1
            //             //     },
            //             //     fields: ["parent"],
            //             //     distinct: true,
            //             //     pluck: "parent"
            //             // })]
            //         ]
            //     };
            // });

            frm.set_query("custom_parent_purchase_order", function() {
                const production_item = frm.doc.production_item;
                const custom_plan_items = frm.doc.custom_plan_items;
                let responseData = []; // Store response here

                frappe.call({
                    method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_matching_po_items",
                    args: { 
                        production_item: production_item,
                        custom_plan_items: custom_plan_items 
                    },
                    async: false, // Forces synchronous call (avoid in production)
                    callback: function(response) {
                        responseData = response.message || [];
                        console.log("\nresponseData\n",responseData);
                    }
                });

                return {
                    filters: [
                        // ["docstatus", "=", 1],
                        // ["custom_plan_items", "=", custom_plan_items],
                        ["name", "in", responseData] // Use stored response
                    ]
                };
            });
            
            // frm.set_query("custom_parent_purchase_order", function() {
            //     const production_item = frm.doc.production_item;
            //     const custom_plan_items = frm.doc.custom_plan_items;

            //     return new Promise((resolve) => {
            //         frappe.call({
            //             method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_matching_po_items",
            //             args: { production_item: production_item },
            //             callback: function(response) {
            //                 resolve({
            //                     filters: [
            //                         ["docstatus", "=", 1],
            //                         ["custom_plan_items", "=", custom_plan_items],
            //                         ["name", "in", response.message || []]
            //                     ]
            //                 });
            //             }
            //         });
            //     });
            // });

            // frm.set_query("custom_parent_purchase_order", function() {
            //     return {
            //         query: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_filtered_purchase_orders",
            //         filters: {
            //             production_item: frm.doc.production_item,
            //             plan_items: frm.doc.custom_plan_items // optional filter
            //         }
            //     };
            // });

            // frm.set_query("custom_parent_purchase_order", function() {
            //     // Get the production_item from the work order
            //     const production_item = frm.doc.production_item;
                
            //     return {
            //         filters: [
            //             query: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_filtered_purchase_orders",
            //             ["docstatus", "=", 1],
            //             ["name", "in", 
            //                 frappe.db.get_list("Purchase Order Item", {
            //                     filters: {
            //                         "item_code": production_item
            //                     },
            //                     fields: ["parent"],
            //                     distinct: true
            //                 }).then(items => 
                            
            //                 items.map(i => i.parent))

            //             ]
            //         ]
            //     };
            // });
        }


 

        console.log("inside public work order", frm);
        frm.add_custom_button(__('Update Cost'), function() {
            frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.set_additional_cost",
                args: {
                    docname: frm.doc.name,
                },
                callback: function(response) {
                    console.log("response",response);
                    if(response.message) {
                        frm.refresh_field("custom_total_operating_cost_include_water");
                        frm.reload_doc();

                       
                       // frappe.db.set_value('Work Order', frm.doc.name, 'custom_total_operating_cost_include_water', response.message);

                       // // frm.set_value("custom_total_operating_cost_include_water", response.message);
                       // // //frm.save('Submit');
                        
                       // // // frappe.db.set_value('Work Order', frm.doc.name, '', response.message)
                       // // //  .then(() => {
                       // // //      frappe.msgprint(__('Additional Operating Cost updated successfully.'));
                       // // //  });
                       //  frm.save('Update');
                        
                          
                    }
                }
            });
        });    
     

    },
    before_submit: function(frm) {
        let value = frm.doc.production_item;
        console.log("frm",frm.doc);
        console.log("/[.X]/i.test(value)",/[.X]/i.test(value));

        if (/[.X]/i.test(value) && frm.doc.sales_order === undefined ) {
            console.log("The string contains '.' or 'X'");
            console.log("The string contains '.' or 'X'", );
            if((frm.doc.custom_parent_fabric_work_order == undefined || 
                frm.doc.custom_parent_fabric_work_order == null ||
                frm.doc.custom_parent_fabric_work_order == "")
                && (frm.doc.custom_parent_purchase_order == undefined ||
                    frm.doc.custom_parent_purchase_order == null ||
                    frm.doc.custom_parent_purchase_order == ""
                    ))
            {
                frappe.msgprint(__('Parent Fabric Work Order or Purchase Order is mandatory for Collar and Cuff WO'));
                frappe.validated = false;
            }
        } 
    },

    after_save:function(frm){
        if(frm.doc.custom_include_loading_greige == 1||
            frm.doc.custom_loading_and_unloading_greige_lot == 1||
            frm.doc.custom_loading_and_unloading_finished_lot == 1||
            frm.doc.custom_loading_and_unloading_wet_lot == 1||
            frm.doc.custom_sample_dyeing == 1||
            frm.doc.custom_cotton_dyeing_colour == 1||
            frm.doc.custom_cotton_washing == 1||
            frm.doc.custom_cotton_white == 1||
            frm.doc.custom_collar_padding == 1||
            frm.doc.custom_poly_cotton_double_dyeing == 1||
            frm.doc.custom_polyester_double_dyeing == 1||
            frm.doc.custom_polyester_dyeing_colour == 1||
            frm.doc.custom_polyester_dyeing_white == 1||
            frm.doc.custom_stitching_overlock == 1||
            frm.doc.custom_polyester_re_dyeing_colour == 1||
            frm.doc.custom_polyester_re_dyeing_white == 1||
            frm.doc.custom_polyester_re_washing == 1||
            frm.doc.custom_polyester_washing == 1||
            frm.doc.custom_tubular_stitching_overlock ==1||
            frm.doc.custom_sample_washing ==1||
            frm.doc.custom_sample_double_dyeing ==1){
            console.log("custom_include_loading_greige");
            frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.set_operation_cost_in_work_order",
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

    // if(frm.doc.custom_include_loading_greige == 1||
    //         frm.doc.custom_loading_and_unloading_greige_lot == 1
    //         ){
    //         console.log("custom_include_loading_greige");
    //         frappe.call({
    //             method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.set_operation_cost_in_work_order",
    //             args: {
    //                 docname: frm.doc.name,
    //             },
    //             callback: function(response) {
    //                 console.log("response",response);
    //                 if(response.message) {
    //                     frm.refresh_field("custom_work_order_operations");
    //                     frm.reload_doc();
                          
    //                 }
    //             }
    //         });

    //     }

    }

    // get_work_order:function(frm){
    //     console.log("get_work_order button clicked");

    // }
})  



