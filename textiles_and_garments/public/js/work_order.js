// textiles_and_garments/public/js/work_order.js
// -----------------------------------------------------------------
// Parent Form Client Script — Work Order
//
// Behaviour:
//   • On every refresh, reads the custom_roll_qi_entries child table
//     and displays a colour-coded summary banner:
//       "Rolls: N total │ X Accepted │ Y Pending │ Z Rejected"
//   • Banner is green when all rolls are Accepted, orange otherwise.
//   • Adds a helper button "Create QI for Selected Roll" that opens
//     a new Quality Inspection pre-linked to the highlighted row.
// -----------------------------------------------------------------

frappe.ui.form.on("Work Order", {

    // ----------------------------------------------------------
    // Refresh: render roll QI summary banner
    // ----------------------------------------------------------
    refresh: function (frm) {
        _render_roll_qi_summary(frm);
        _add_create_qi_button(frm);
    },

    // Re-render after child table is modified
    custom_roll_qi_entries_add:    function (frm) { _render_roll_qi_summary(frm); },
    custom_roll_qi_entries_remove: function (frm) { _render_roll_qi_summary(frm); }
});

// ------------------------------------------------------------------
// Render summary intro banner above the form
// ------------------------------------------------------------------
function _render_roll_qi_summary(frm) {
    const entries = frm.doc.custom_roll_qi_entries || [];

    if (entries.length === 0) {
        frm.set_intro("", "");  // clear any previous banner
        return;
    }

    const total    = entries.length;
    const accepted = entries.filter(r => r.qi_status === "Accepted").length;
    const rejected = entries.filter(r => r.qi_status === "Rejected").length;
    const pending  = entries.filter(r => r.qi_status === "Pending" || !r.qi_status).length;

    const all_done = accepted === total;
    const colour   = all_done ? "green" : (rejected > 0 ? "red" : "orange");

    frm.set_intro(
        `🧵 Roll QI Summary — `
        + `<b>${total}</b> total &nbsp;│&nbsp; `
        + `<span style="color:green"><b>${accepted}</b> Accepted</span> &nbsp;│&nbsp; `
        + `<span style="color:orange"><b>${pending}</b> Pending</span> &nbsp;│&nbsp; `
        + `<span style="color:red"><b>${rejected}</b> Rejected</span>`,
        colour
    );
}

// ------------------------------------------------------------------
// Add convenience button to open a new QI for a selected roll row
// ------------------------------------------------------------------
function _add_create_qi_button(frm) {
    if (frm.doc.docstatus !== 1) return;   // only on submitted WOs

    frm.add_custom_button(
        __("Create QI for Roll"),
        function () {
            // Identify the first Pending row without a linked QI
            const pending_row = (frm.doc.custom_roll_qi_entries || [])
                .find(r => (!r.quality_inspection) && r.roll);

            if (!pending_row) {
                frappe.msgprint(__("All rolls already have a Quality Inspection linked."));
                return;
            }

            frappe.new_doc("Quality Inspection", {
                custom_roll:     pending_row.roll,
                reference_type:  "Work Order",
                reference_name:  frm.doc.name,
                item_code:       pending_row.item_code || frm.doc.production_item
            });
        },
        __("Quality Inspection")
    );
}


// frappe.ui.form.on("Work Order", {
//     refresh:function(frm){

//         if (frm.doc.docstatus === 1) {
//             // Check if there are linked plans
//             let has_linked_plans = false;
            
//             // For Work Order, check custom_plans field directly (not in items)
//             if (frm.doc.custom_plans) {
//                 has_linked_plans = true;
//             }
            
//             if (has_linked_plans) {
//                 frm.add_custom_button(__('🔗 Remove Links & Cancel'), function() {
//                     remove_wo_links_and_cancel(frm);
//                 }).addClass('btn-warning');
//             }
            
//             // Also keep the regular cancel button
//             frm.add_custom_button(__('Cancel'), function() {
//                 frm.cancel();
//             });
//         }

        
       
//         // frm.set_query("custom_parent_fabric_work_order", function() {
//         //     return {
//         //         filters: {
//         //             docstatus: 1,
//         //             custom_plan_items: frm.doc.custom_plan_items
//         //         }
//         //     };
//         // });
//         let production_item_full = frm.doc.production_item; // Get the full production_item value

//         if (production_item_full) {
//             let parts = production_item_full.split('/');
//             let filter_production_item = production_item_full; // Default filter value

//             // Ensure there are at least two parts to apply the specific pattern
//             if (parts.length >= 2) {
//                 let firstSegment = parts[0];  // e.g., "DKF12187"
//                 let secondSegment = parts[1]; // e.g., "SC BLACK"

//                 // Extract the leading alphabetic characters from the first segment.
//                 // This regex matches one or more letters at the beginning of the string.
//                 let alphaPrefixMatch = firstSegment.match(/^[A-Za-z]+/);
//                 let modifiedFirstSegment;

//                 if (alphaPrefixMatch && alphaPrefixMatch[0].length > 0) {
//                     // If an alphabetic prefix is found, use it followed by '%'
//                     modifiedFirstSegment = alphaPrefixMatch[0] + '%'; // e.g., "DKF%"
//                 } else {
//                     // If no alphabetic prefix (e.g., "12345/ABC"), or it's just letters,
//                     // use the entire first segment followed by '%'
//                     modifiedFirstSegment = firstSegment + '%'; // e.g., "12345%" or "ABC%"
//                 }

//                 // Construct the new filter pattern: "ModifiedFirstPart/SecondPart/%"
//                 filter_production_item = modifiedFirstSegment + '/' + secondSegment + '/%';
//             }
//             // If parts.length is less than 2, the `filter_production_item` remains the
//             // original `production_item_full`, and the `like` filter will effectively
//             // search for "%original_value%" as a fallback.

//             frm.set_query("custom_parent_fabric_work_order", function() {
//                 return {
//                     filters: [
//                         ["docstatus", "=", 1],
//                         ["custom_plan_items", "=", frm.doc.custom_plan_items],
//                         // Use the dynamically constructed filter_production_item
//                         ["production_item", "like", filter_production_item]
//                     ]
//                 };
//             });

//             // frm.set_query("custom_parent_purchase_order", function() {
//             //     return {
//             //         filters: [
//             //             ["docstatus", "=", 1],
//             //             // ["custom_plan_items", "=", frm.doc.custom_plan_items],
//             //             // // Use the dynamically constructed filter_production_item
//             //             // ["production_item", "like", filter_production_item]
//             //         ]
//             //     };
//             // });

//             // frm.set_query("custom_parent_purchase_order", function() {
//             //     const production_item = frm.doc.production_item;
//             //     const custom_plan_items = frm.doc.custom_plan_items;
                
//             //     return {
//             //         filters: [
//             //             ["docstatus", "=", 1],
//             //             ["custom_plan_items", "=", custom_plan_items],
//             //             ["name", "in", frappe.model.with_doctype("Purchase Order", function() {
//             //                 return frappe.call({
//             //                     method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_matching_po_items",
//             //                     args: {
//             //                         production_item: production_item
//             //                     },
//             //                     callback: function(r) {
//             //                         return r.message;
//             //                     },
//             //                     async: false
//             //                 }).message;
//             //             })]
//             //         ]
//             //     };
//             // });
//             // po_response = []

//             // frappe.call({
//             //     method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_matching_po_items",
//             //     args: {
//             //         production_item: frm.doc.production_item,
//             //     },
//             //     callback: function(response) {
//             //         console.log("response get_matching_po_items",response);
//             //         if(response.message) {
//             //             // frm.refresh_field("custom_work_order_operations");
//             //             // frm.reload_doc();
//             //             po_response = response.message;
//             //             console.log("po_response",po_response);
                          
//             //         }
//             //     }
//             // });

//             // frm.set_query("custom_parent_purchase_order", function() {
//             //     const production_item = frm.doc.production_item;
//             //     const custom_plan_items = frm.doc.custom_plan_items;
                
//             //     return {
//             //         filters: [
//             //             ["docstatus", "=", 1],
//             //             ["custom_plan_items", "=", custom_plan_items],

//             //             // ["name", "in", frappe.db.get_list("Purchase Order Item", {
//             //             //     filters: {
//             //             //         "item_code": production_item,
//             //             //         "docstatus": 1
//             //             //     },
//             //             //     fields: ["parent"],
//             //             //     distinct: true,
//             //             //     pluck: "parent"
//             //             // })]
//             //         ]
//             //     };
//             // });

//             frm.set_query("custom_parent_purchase_order", function() {
//                 const production_item = frm.doc.production_item;
//                 const custom_plan_items = frm.doc.custom_plan_items;
//                 let responseData = []; // Store response here

//                 frappe.call({
//                     method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_matching_po_items",
//                     args: { 
//                         production_item: production_item,
//                         custom_plan_items: custom_plan_items 
//                     },
//                     async: false, // Forces synchronous call (avoid in production)
//                     callback: function(response) {
//                         responseData = response.message || [];
//                         console.log("\nresponseData\n",responseData);
//                     }
//                 });

//                 return {
//                     filters: [
//                         // ["docstatus", "=", 1],
//                         // ["custom_plan_items", "=", custom_plan_items],
//                         ["name", "in", responseData] // Use stored response
//                     ]
//                 };
//             });
            
//             // frm.set_query("custom_parent_purchase_order", function() {
//             //     const production_item = frm.doc.production_item;
//             //     const custom_plan_items = frm.doc.custom_plan_items;

//             //     return new Promise((resolve) => {
//             //         frappe.call({
//             //             method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_matching_po_items",
//             //             args: { production_item: production_item },
//             //             callback: function(response) {
//             //                 resolve({
//             //                     filters: [
//             //                         ["docstatus", "=", 1],
//             //                         ["custom_plan_items", "=", custom_plan_items],
//             //                         ["name", "in", response.message || []]
//             //                     ]
//             //                 });
//             //             }
//             //         });
//             //     });
//             // });

//             // frm.set_query("custom_parent_purchase_order", function() {
//             //     return {
//             //         query: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_filtered_purchase_orders",
//             //         filters: {
//             //             production_item: frm.doc.production_item,
//             //             plan_items: frm.doc.custom_plan_items // optional filter
//             //         }
//             //     };
//             // });

//             // frm.set_query("custom_parent_purchase_order", function() {
//             //     // Get the production_item from the work order
//             //     const production_item = frm.doc.production_item;
                
//             //     return {
//             //         filters: [
//             //             query: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_filtered_purchase_orders",
//             //             ["docstatus", "=", 1],
//             //             ["name", "in", 
//             //                 frappe.db.get_list("Purchase Order Item", {
//             //                     filters: {
//             //                         "item_code": production_item
//             //                     },
//             //                     fields: ["parent"],
//             //                     distinct: true
//             //                 }).then(items => 
                            
//             //                 items.map(i => i.parent))

//             //             ]
//             //         ]
//             //     };
//             // });
//         }


 

//         console.log("inside public work order", frm);
//         frm.add_custom_button(__('Update Cost'), function() {
//             frappe.call({
//                 method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.set_additional_cost",
//                 args: {
//                     docname: frm.doc.name,
//                 },
//                 callback: function(response) {
//                     console.log("response",response);
//                     if(response.message) {
//                         frm.refresh_field("custom_total_operating_cost_include_water");
//                         frm.reload_doc();

                       
//                        // frappe.db.set_value('Work Order', frm.doc.name, 'custom_total_operating_cost_include_water', response.message);

//                        // // frm.set_value("custom_total_operating_cost_include_water", response.message);
//                        // // //frm.save('Submit');
                        
//                        // // // frappe.db.set_value('Work Order', frm.doc.name, '', response.message)
//                        // // //  .then(() => {
//                        // // //      frappe.msgprint(__('Additional Operating Cost updated successfully.'));
//                        // // //  });
//                        //  frm.save('Update');
                        
                          
//                     }
//                 }
//             });
//         });    
     

//     },
//     before_submit: function(frm) {
//         let value = frm.doc.production_item;
//         console.log("frm",frm.doc);
//         console.log("/[.X]/i.test(value)",/[.X]/i.test(value));

//         if (/[.X]/i.test(value) && frm.doc.sales_order === undefined ) {
//             console.log("The string contains '.' or 'X'");
//             console.log("The string contains '.' or 'X'", );
//             if((frm.doc.custom_parent_fabric_work_order == undefined || 
//                 frm.doc.custom_parent_fabric_work_order == null ||
//                 frm.doc.custom_parent_fabric_work_order == "")
//                 && (frm.doc.custom_parent_purchase_order == undefined ||
//                     frm.doc.custom_parent_purchase_order == null ||
//                     frm.doc.custom_parent_purchase_order == ""
//                     ))
//             {
//                 frappe.msgprint(__('Parent Fabric Work Order or Purchase Order is mandatory for Collar and Cuff WO'));
//                 frappe.validated = false;
//             }
//         } 
//     },

//     after_save:function(frm){
//         if(frm.doc.custom_include_loading_greige == 1||
//             frm.doc.custom_loading_and_unloading_greige_lot == 1||
//             frm.doc.custom_loading_and_unloading_finished_lot == 1||
//             frm.doc.custom_loading_and_unloading_wet_lot == 1||
//             frm.doc.custom_sample_dyeing == 1||
//             frm.doc.custom_cotton_dyeing_colour == 1||
//             frm.doc.custom_cotton_washing == 1||
//             frm.doc.custom_cotton_white == 1||
//             frm.doc.custom_collar_padding == 1||
//             frm.doc.custom_poly_cotton_double_dyeing == 1||
//             frm.doc.custom_polyester_double_dyeing == 1||
//             frm.doc.custom_polyester_dyeing_colour == 1||
//             frm.doc.custom_polyester_dyeing_white == 1||
//             frm.doc.custom_stitching_overlock == 1||
//             frm.doc.custom_polyester_re_dyeing_colour == 1||
//             frm.doc.custom_polyester_re_dyeing_white == 1||
//             frm.doc.custom_polyester_re_washing == 1||
//             frm.doc.custom_polyester_washing == 1||
//             frm.doc.custom_tubular_stitching_overlock ==1||
//             frm.doc.custom_sample_washing ==1||
//             frm.doc.custom_sample_double_dyeing ==1){
//             console.log("custom_include_loading_greige");
//             frappe.call({
//                 method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.set_operation_cost_in_work_order",
//                 args: {
//                     docname: frm.doc.name,
//                 },
//                 callback: function(response) {
//                     console.log("response",response);
//                     if(response.message) {
//                         frm.refresh_field("custom_work_order_operations");
//                         frm.reload_doc();
                          
//                     }
//                 }
//             });

//         }

//     // if(frm.doc.custom_include_loading_greige == 1||
//     //         frm.doc.custom_loading_and_unloading_greige_lot == 1
//     //         ){
//     //         console.log("custom_include_loading_greige");
//     //         frappe.call({
//     //             method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.set_operation_cost_in_work_order",
//     //             args: {
//     //                 docname: frm.doc.name,
//     //             },
//     //             callback: function(response) {
//     //                 console.log("response",response);
//     //                 if(response.message) {
//     //                     frm.refresh_field("custom_work_order_operations");
//     //                     frm.reload_doc();
                          
//     //                 }
//     //             }
//     //         });

//     //     }

//     }

//     // get_work_order:function(frm){
//     //     console.log("get_work_order button clicked");

//     // }
// })

// function remove_wo_links_and_cancel(frm) {
//     // Get linked plan for confirmation message
//     let linked_plan = frm.doc.custom_plans;
    
//     let confirm_message = `This Work Order is linked to plan: <strong>${linked_plan}</strong><br><br>`;
//     confirm_message += `All milestone links will be removed before cancellation. Continue?`;
    
//     frappe.confirm(
//         confirm_message,
//         function() {
//             frappe.call({
//                 method: 'textiles_and_garments.time_and_action_milestones.remove_wo_links_before_cancel',
//                 args: {
//                     wo_name: frm.doc.name,
//                     plan_names: [linked_plan]  // Pass as array with single element
//                 },
//                 callback: function(r) {
//                     if (r.message && r.message.success) {
//                         frappe.msgprint({
//                             title: __('Success'),
//                             indicator: 'green',
//                             message: __('Removed links from plan {0}. Cancelling Work Order...', [linked_plan])
//                         });
                        
//                         // Cancel the Work Order after a brief delay to show the message
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

  



