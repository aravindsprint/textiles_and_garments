frappe.ui.form.on("Sales Invoice", {
    refresh:function(frm){
        console.log("inside public sales invoice", frm);    
     

    },

    after_save:function(frm){
        if(
            frm.doc.custom_loading_and_unloading_greige_lot == 1||
            frm.doc.custom_loading_and_unloading_finished_lot == 1||
            frm.doc.custom_loading_and_unloading_wet_lot == 1
           ){
            console.log("custom_include_loading_greige");
            frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.set_operation_cost_in_sales_invoice",
                args: {
                    docname: frm.doc.name,
                },
                callback: function(response) {
                    console.log("response",response);
                    if(response.message) {
                        frm.refresh_field("custom_loading_and_unloading_operations");
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