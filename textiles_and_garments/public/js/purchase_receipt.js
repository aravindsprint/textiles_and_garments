frappe.ui.form.on("Purchase Receipt", {
    
    after_save:function(frm){
        if(frm.doc.custom_loading_and_unloading_greige_lot == 1||
            frm.doc.custom_loading_and_unloading_finished_lot == 1||
            frm.doc.custom_loading_and_unloading_wet_lot == 1
            ){
            console.log("custom_include_loading_greige");
            frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.set_operation_cost_in_purchase_receipt",
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
    
});

frappe.ui.form.on('Purchase Receipt', {
    refresh(frm) {
        console.log("Purchase Receipt", frm);

        const so_map = {}; // to avoid re-fetching the same Purchase Order multiple times
        const receipt_items = frm.doc.items || [];

        const unique_so_names = [
            ...new Set(receipt_items.map(row => row.purchase_order).filter(Boolean))
        ];

        // Step 1: Load all unique Purchase Orders
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Purchase Order",
                filters: [
                    ["name", "in", unique_so_names]
                ],
                fields: ["name"]
            },
            callback: function(list_response) {
                if (!list_response.message || list_response.message.length === 0) return;

                const fetch_promises = unique_so_names.map(so_name => {
                    return new Promise((resolve) => {
                        frappe.model.with_doc("Purchase Order", so_name, function() {
                            const so_doc = frappe.model.get_doc("Purchase Order", so_name);
                            so_map[so_name] = so_doc;
                            resolve();
                        });
                    });
                });

                // Step 2: After all Purchase Orders are loaded
                Promise.all(fetch_promises).then(() => {
                    receipt_items.forEach(receipt_row => {
                        const so_doc = so_map[receipt_row.purchase_order];
                        if (!so_doc) return;

                        const matching_so_item = so_doc.items.find(
                            so_item => so_item.name === receipt_row.purchase_order_item
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



