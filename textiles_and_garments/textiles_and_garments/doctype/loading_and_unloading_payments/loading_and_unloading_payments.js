// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Loading and Unloading Payments", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Loading and Unloading Payments", {
    get_stock_entry:function(frm){
        console.log("get_stock_entry button clicked");
        frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_unpaid_stock_entry",
                args: {
                    docname: frm.doc.name,
                    from_date: frm.doc.from_date,
                    to_date: frm.doc.to_date,
                    contractor: frm.doc.contractor,
                },
                callback: function(response) {
                    console.log("response",response);
                    if(response.message) {
                        frm.refresh_field("stock_entry_payment_item");
                        // frm.refresh_field("purchase_receipt_payment_item");
                        frm.reload_doc();
                          
                    }
                }
        });

    },
    get_purchase_receipt:function(frm){
        console.log("get_purchase_receipt button clicked");
        frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_unpaid_purchase_receipt",
                args: {
                    docname: frm.doc.name,
                    from_date: frm.doc.from_date,
                    to_date: frm.doc.to_date,
                    contractor: frm.doc.contractor,
                },
                callback: function(response) {
                    console.log("response",response);
                    if(response.message) {
                        // frm.refresh_field("stock_entry_payment_item");
                        frm.refresh_field("purchase_receipt_payment_item");
                        frm.reload_doc();
                          
                    }
                }
        });

    },
    get_sales_invoice:function(frm){
        console.log("get_sales_invoice button clicked");
        frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.get_unpaid_sales_invoice",
                args: {
                    docname: frm.doc.name,
                    from_date: frm.doc.from_date,
                    to_date: frm.doc.to_date,
                    contractor: frm.doc.contractor,
                },
                callback: function(response) {
                    console.log("response",response);
                    if(response.message) {
                        // frm.refresh_field("stock_entry_payment_item");
                        frm.refresh_field("sales_invoice_payment_item");
                        frm.reload_doc();
                          
                    }
                }
        });

    },
    refresh: function(frm) {
        if(frm.doc.docstatus==0){
            frm.add_custom_button(__('Create JV'), function() {
                frappe.call({
                    method :'textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.create_jv_for_lup',
                    args: {
                    docname: frm.doc.name,
                    },
                    callback: function(response)
                    {
                        if(response.message) {
                        frm.refresh_field("stock_entry_payment_item");
                        frm.refresh_field("purchase_receipt_payment_item");
                        frm.reload_doc();
                          
                    }
                    }
                });
            })
        }
    },
    after_save: function(frm) {
        if(frm.doc.grand_total_for_stock_entry >=0 || frm.doc.grand_total_for_purchase_receipt >=0){
         frm.doc.grand_total = frm.doc.grand_total_for_stock_entry + frm.doc.grand_total_for_purchase_receipt + frm.doc.grand_total_for_sales_invoice;
         frm.doc.net_total = frm.doc.net_total_for_stock_entry + frm.doc.net_total_for_purchase_receipt + frm.doc.net_total_for_sales_invoice;
         frappe.model.set_value(frm.doctype, frm.name, "grand_total", frm.doc.grand_total);
         frappe.model.set_value(frm.doctype, frm.name, "net_total", frm.doc.net_total);
        }
        
    }  

    
})        
