// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

frappe.ui.form.on("Roll Packing List", {
	refresh(frm) {
		console.log("frm",frm);

	},
});


frappe.ui.form.on("Roll Packing List", "validate", function(frm) { 
    var total_qty = 0; 
    $.each(frm.doc.roll_packing_list_item || [], function(i, d) { 
        total_qty += flt(d.roll_weight || 0);
        console.log("total_qty", total_qty);
    });
    frm.set_value("total_roll_weight", total_qty); // Changed from roll_weight to total_qty
});

frappe.ui.form.on("Roll Packing List", "on_submit", function(frm) { 
    var total_qty = 0; 
    $.each(frm.doc.roll_packing_list_item || [], function(i, d) { 
        total_qty += flt(d.roll_weight || 0);
        console.log("total_qty", total_qty);
    });
    frm.set_value("total_roll_weight", total_qty); // Changed from roll_weight to total_qty
});

frappe.ui.form.on("Roll Packing List", "after_save", function(frm) { 
    var total_qty = 0; 
    $.each(frm.doc.roll_packing_list_item || [], function(i, d) { 
        total_qty += flt(d.roll_weight || 0);
        console.log("total_qty", total_qty);
    });
    frm.set_value("total_roll_weight", total_qty); // Changed from roll_weight to total_qty
});




frappe.ui.form.on('Roll Packing List', {
    refresh: function(frm) {
        // Only show button if document is submitted
        if (frm.doc.docstatus === 0 || frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Create Manufacture Entry'), function() {
                create_manufacture_entry(frm);
            }, __('Actions'));
        }
        
        // If stock entry already exists, show a button to view it
        // if (frm.doc.custom_stock_entry) {
        //     frm.add_custom_button(__('View Stock Entry'), function() {
        //         frappe.set_route('Form', 'Stock Entry', frm.doc.custom_stock_entry);
        //     }, __('Actions'));
        // }
    }
});

function create_manufacture_entry(frm) {
    frappe.confirm(
        __('Are you sure you want to create a Manufacture Stock Entry for this Roll Packing List?'),
        function() {
            // User confirmed
            frappe.call({
                method: 'textiles_and_garments.textiles_and_garments.doctype.roll_packing_list.roll_packing_list.create_manufacture_entry_from_roll_packing',
                args: {
                    doc: frm.doc
                },
                freeze: true,
                freeze_message: __('Creating Manufacture Entry...'),
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('Manufacture Stock Entry {0} created successfully', [r.message]),
                            indicator: 'green'
                        }, 5);
                        
                        // Reload the form to show the stock entry reference
                        frm.reload_doc();
                    }
                },
                error: function(r) {
                    frappe.msgprint({
                        title: __('Error'),
                        message: __('Failed to create Manufacture Stock Entry. Please check the error log.'),
                        indicator: 'red'
                    });
                }
            });
        },
        function() {
            // User cancelled
            frappe.show_alert({
                message: __('Operation cancelled'),
                indicator: 'orange'
            }, 3);
        }
    );
}