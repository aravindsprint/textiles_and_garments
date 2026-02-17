// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hang Tag Request", {
	sales_invoice(frm) {
		get_sales_invoice_items(frm);
	},

	validate(frm) {
        console.log("frm",frm.doc);
		// if (frm.doc.no_of_garments_per_kilo && frm.doc.tags_requested_wt) {
		// 	let number_of_tags = frm.doc.no_of_garments_per_kilo * frm.doc.tags_requested_wt;
		// 	frm.set_value("number_of_tags", Math.round(number_of_tags));
		// 	frm.refresh_field("number_of_tags");
		// }
	}
});



// Client Script for Hang Tag Request

frappe.ui.form.on('Hang Tag Request', {
    refresh: function(frm) {
        if(frm.doc.docstatus == 0){
            calculate_total_tags(frm);
        }
        
    },
    
    before_save: function(frm) {
        calculate_total_tags(frm);
    }
});

frappe.ui.form.on('Hang Tag Garments Item', {
    // Trigger when consumption_wt_in_kgs_per_garment changes
    consumption_wt_in_kgs_per_garment: function(frm, cdt, cdn) {
        calculate_no_of_qty(frm, cdt, cdn);
    },
    
    // Trigger when qty changes
    no_of_garments_required: function(frm, cdt, cdn) {
        calculate_no_of_qty(frm, cdt, cdn);
    },
    
    // Recalculate total when row is added
    hang_tag_garments_item_add: function(frm, cdt, cdn) {
        calculate_total_tags(frm);
    },
    
    // Recalculate total when row is removed
    hang_tag_garments_item_remove: function(frm, cdt, cdn) {
        calculate_total_tags(frm);
    }
});

// Function to calculate no_of_garments_required for a specific row
function calculate_no_of_qty(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    
    // Multiply qty and consumption_wt_in_kgs_per_garment
    let qty = (row.no_of_garments_required || 0) * (row.consumption_wt_in_kgs_per_garment || 0);
    
    // Set the calculated value in the row
    frappe.model.set_value(cdt, cdn, 'qty', qty);
    
    // Recalculate the total
    calculate_total_tags(frm);
}

// Function to calculate total_no_of_tags_required
function calculate_total_tags(frm) {
    let total = 0;
    let total_wt = 0;
    
    // Loop through all child table rows
    if (frm.doc.hang_tag_garments_item) {
        frm.doc.hang_tag_garments_item.forEach(function(row) {
            total += (row.no_of_garments_required || 0);
            total_wt += (row.qty || 0);
        });
    }
    
    // Set the total in parent field
    frm.set_value('total_no_of_tags_required', total);
    frm.set_value('total_weight', total_wt);
}






function get_sales_invoice_items(frm) {
    if (!frm.doc.sales_invoice) {
        frappe.msgprint("Please save the Sales Invoice first.");
        return;
    }
    frappe.call({ 
        method: "textiles_and_garments.textiles_and_garments.doctype.hang_tag_request.hang_tag_request.get_sales_invoice_items",
        args: {
            // You can pass any required arguments here if your method expects
            sales_invoice: frm.doc.sales_invoice
        },
        callback: function (res) {
            const items = res.message || [];

            if (items.length === 0) {
                frappe.msgprint("No items found.");
                return;
            }
            // Clear existing hang tag items first if you wish
            // frm.clear_table('hang_tag_request_item');  

            items.forEach(item => {
                frm.add_child('hang_tag_request_item', {
                    item_code: item.item_code,
                    warehouse: item.warehouse,
                    qty: item.qty,
                    rate: item.rate,
                    amount: item.amount,
                    commercial_name: item.commercial_name,
                    color: item.color
                });
            });

            frm.refresh_field('hang_tag_request_item');
            frappe.msgprint(`${items.length} item(s) added to Hang Tag Request.`);
        }
    });
}



