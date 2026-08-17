// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Invoice Interest Payments", {
	get_sales_invoice:function(frm){
		frm.call({
                method: 'get_sales_invoice',
                doc: frm.doc,
                callback: function(r) {
                    if (!r.exc) {
                        frm.refresh_field('sales_invoice_interest_payment_item');
                        frm.refresh_fields();
                    }
                }
            });
    },
    refresh(frm) {
    	if(frm.doc.docstatus==1){
            frm.add_custom_button(__('Create JV'), function() {
                frappe.call({
                    method :'textiles_and_garments.textiles_and_garments.doctype.sales_invoice_interest_payments.sales_invoice_interest_payments.create_jv_for_siip',
                    args: {
                    docname: frm.doc.name,
                    },
                    callback: function(response)
                    {
                        if(response.message) {
                        // frm.refresh_field("work_order_payment_item");
                        frm.reload_doc();
                          
                    }
                    }
                });
            })
        }

        
    },

    customer: function(frm) {
        // Optional: Auto-fetch when customer is selected
        if (frm.doc.customer && frm.doc.from_date && frm.doc.to_date) {
            // You can auto-trigger here if needed
        }
    },

    from_date: function(frm) {
        if (frm.doc.customer && frm.doc.from_date && frm.doc.to_date) {
            // You can auto-trigger here if needed
        }
    },

    to_date: function(frm) {
        if (frm.doc.customer && frm.doc.from_date && frm.doc.to_date) {
            // You can auto-trigger here if needed
        }
    },

    deduct_percentage: function(frm) {
        // Recalculate net total when deduct percentage changes
        if (frm.doc.grand_total && frm.doc.deduct_percentage) {
            let deduct_amount = (frm.doc.grand_total * frm.doc.deduct_percentage) / 100;
            frm.set_value('total_amount_included_interest', frm.doc.grand_total - deduct_amount);
        }
    }
});

// Child table field formatting
frappe.ui.form.on("Sales Invoice Interest Payment Item", {
    interest_amount: function(frm, cdt, cdn) {
        // Recalculate totals when interest amount changes
        calculate_totals(frm);
    },
    
    grand_total: function(frm, cdt, cdn) {
        // Recalculate totals when grand total changes
        calculate_totals(frm);
    }
});

function calculate_totals(frm) {
    let grand_total = 0;
    let interest_amount = 0;
    let total_amount = 0;
    
    // Calculate totals from child table
    $.each(frm.doc.sales_invoice_interest_payment_item || [], function(i, row) {
        grand_total += flt(row.grand_total);
        interest_amount += flt(row.interest_amount);
        total_amount += flt(row.interest_amount);
    });
    
    // Update main fields
    frm.set_value('grand_total', grand_total);
    
    // Calculate net total after deduct percentage
    if (frm.doc.deduct_percentage) {
        let deduct_amount = (total_amount * flt(frm.doc.deduct_percentage)) / 100;
        console.log("deduct_amount",deduct_amount);
        frm.set_value('total_amount_included_interest', total_amount - deduct_amount);
    } else {
        frm.set_value('total_amount_included_interest', total_amount);
    }
}
