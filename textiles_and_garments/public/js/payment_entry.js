frappe.ui.form.on("Payment Entry", {


    custom_work_order_payments:function(frm){
        console.log("custom_work_order_payments  clicked");
        frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_total_of_work_order_payments",
                args: {
                    // docname: frm.doc.name,
                    custom_work_order_payments: frm.doc.custom_work_order_payments
                },
                callback: function(response) {
                    console.log("response",response);
                    if(response.message) {
                        frm.set_value("paid_amount", response.message);
                        // frm.refresh_field("paid_amount");
                        // frm.reload_doc();
                          
                    }
                }
            });

    },
    // after_save: (frm) => {
    //     set_paid_status_to_work_orders(frm);
    // },
    validate: (frm) => {
        set_paid_status_to_work_orders(frm);
    }
})


function set_paid_status_to_work_orders(frm) {
    console.log("set_paid_status_to_work_orders", );
    
   
    
    if (frm.doc.custom_work_order_payments) {
        frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.set_paid_status_to_work_orders",
                args: {
                    docname: frm.doc.name,
                    custom_work_order_payments: frm.doc.custom_work_order_payments
                },
                callback: function(response) {
                    console.log("response",response);
                    if(response.message) {
                        // frm.refresh_field("work_order_payment_item");
                        frm.reload_doc();
                          
                    }
                }
        });
    } 
}        