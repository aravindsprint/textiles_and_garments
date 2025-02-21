frappe.ui.form.on("Work Order", {
    refresh:function(frm){
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

    after_save:function(frm){
        if(frm.doc.custom_include_loading_greige == 1){
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
    }

    // get_work_order:function(frm){
    //     console.log("get_work_order button clicked");

    // }
})        