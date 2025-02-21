frappe.ui.form.on("Work Order Payments", {
    get_work_order:function(frm){
        console.log("get_work_order button clicked");
        frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_unpaid_work_order",
                args: {
                    docname: frm.doc.name,
                    from_date: frm.doc.from_date,
                    to_date: frm.doc.to_date,
                    contractor: frm.doc.contractor,
                    stitching_contractor: frm.doc.stitching_contractor,
                    padding_contractor: frm.doc.padding_contractor,
                    contractor_category: frm.doc.contractor_category
                },
                callback: function(response) {
                    console.log("response",response);
                    if(response.message) {
                        frm.refresh_field("work_order_payment_item");
                        frm.reload_doc();
                          
                    }
                }
        });

    },
    refresh: function(frm) {
        if(frm.doc.docstatus==0){
            frm.add_custom_button(__('Create JV'), function() {
                frappe.call({
                    method :'textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.create_jv_for_wo',
                    args: {
                    docname: frm.doc.name,
                    },
                    callback: function(response)
                    {
                        if(response.message) {
                        frm.refresh_field("work_order_payment_item");
                        frm.reload_doc();
                          
                    }
                    }
                });
            })
        }
    }    
    
})        