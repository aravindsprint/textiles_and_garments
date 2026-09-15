// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

	// short_close_plans.js

frappe.ui.form.on("Short Close Plans", {
	refresh: function(frm) { // Or on `onload`, or directly in your script
		console.log("frm",frm.doc);
        frm.set_query("purchase_order", function() { // This anonymous function is correct here
            return {
                query: "textiles_and_garments.textiles_and_garments.doctype.short_close_plans.short_close_plans.get_purchase_orders_by_plan_no",
                filters: {
                    plans_no: frm.doc.plans_no,
                    item_code: frm.doc.item_code
                }
            };
        });

        frm.set_query("work_order", function() { // This anonymous function is correct here
            return {
                query: "textiles_and_garments.textiles_and_garments.doctype.short_close_plans.short_close_plans.get_work_order_orders_by_plan_no",
                filters: {
                    plans_no: frm.doc.plans_no
                }
            };
        });
    },
    purchase_order:function(frm){
    	frappe.call({
			method: 'textiles_and_garments.textiles_and_garments.doctype.short_close_plans.short_close_plans.get_po_item_details',
			args: {
				purchase_order: frm.doc.purchase_order,
				item_code: frm.doc.item_code
			},
			callback: function (response) {
				if (response.message) {
					console.log("Qty data received:", response.message);
					frm.set_value('po_qty', response.message); 
				
					frm.refresh_field("po_qty");
				} else {
					console.log("No Qty data received or data is not an array.");
					frm.set_value('po_qty', 0); 
				}
			},
			error: function(err) {
				console.error("Error fetching Qty:", err);
				frappe.msgprint(__("Error fetching PO Item details."));
			}
		});

    },
	plans_no: function (frm) {
		// your plans_no change logic
		console.log("plans_no changed:", frm.doc.plans_no);

		if (!frm.doc.plans_no) {
			frm.clear_table("sb_entries");
			frm.refresh_field("sb_entries");
			return;
		}

		frappe.call({
			method: 'textiles_and_garments.textiles_and_garments.doctype.short_close_plans.short_close_plans.get_psr_details',
			args: {
				plans_no: frm.doc.plans_no,
			},
			callback: function (response) {
				if (response.message && Array.isArray(response.message)) {
					console.log("SB Entries data received:", response.message);
					frm.clear_table("sb_entries");
					response.message.forEach(row => {
						let child = frm.add_child("sb_entries", {
							item_code: row.item_code, // Assuming 'item_code' in sb_entries
							batch_no: row.batch_no,   // Assuming 'batch_no' in sb_entries
							warehouse: row.warehouse, // Assuming 'warehouse' in sb_entries
							qty: row.qty,             // Assuming 'qty' in sb_entries
							actual_delivered_qty: row.actual_delivered_qty,  
							delivered_qty: row.delivered_qty,  
							need_to_deliver_qty: row.need_to_deliver_qty,  
							returned_qty: row.returned_qty,  
							uom: row.uom,
							plans: frm.doc.plans_no
						});
					});
					frm.refresh_field("sb_entries");
				} else {
					console.log("No SB Entries data received or data is not an array.");
					frm.clear_table("sb_entries");
					frm.refresh_field("sb_entries");
				}
			},
			error: function(err) {
				console.error("Error fetching SB entries:", err);
				frappe.msgprint(__("Error fetching production stock reservation details."));
			}
		});
	},
	validate: function (frm) {
	    if (frm.doc.sb_entries) {
	        let total_short_close_qty = 0;
	        frm.doc.sb_entries.forEach(function(row) {
	            total_short_close_qty += (row.short_close_qty || 0); // Add each row's quantity, defaulting to 0 if null/undefined
	        });
	        console.log("total_short_close_qty",total_short_close_qty);
	        frm.set_value('total_short_close_qty', total_short_close_qty); // Set the calculated total to the field
	    }
	    if (frm.doc.po_qty > 0 && (frm.doc.total_short_close_qty > frm.doc.po_qty)) {
            frappe.msgprint(__("Short close qty should not be greater than PO qty"));
            frappe.validated = false; // This is crucial for stopping submission
        }
        if (frm.doc.wo_qty > 0 && (frm.doc.total_short_close_qty > frm.doc.wo_qty)) {
            frappe.msgprint(__("Short close qty should not be greater than WO qty"));
            frappe.validated = false; // This is crucial for stopping submission
        }
	},

    on_submit: function(frm) {
    	if(frm.doc.po_qty > 0){
    		let short_close_plan_items = [];
	        console.log("frm on_submit",frm);

	        // Ensure fg_item and total_short_close_qty are directly on the main Short Close Plans DocType
	        // And that frm.doc.fg_item holds the value you want to match in PO.
	        if (frm.doc.item_code && frm.doc.total_short_close_qty > 0) {
	        	console.log("frm on_submit 2",frm);
	            short_close_plan_items.push({
	                // Change 'item_code' to 'item_code' here to match the PO Item's item_code
	                fg_item: frm.doc.item_code,
	                short_close_qty: frm.doc.total_short_close_qty || 0
	            });
	        } else {
	            console.warn("FG Item or Total Short Close Quantity is missing from the main document.");
	            frappe.msgprint(__("Cannot update Purchase Order: FG Item or Total Short Close Quantity is missing."));
	            return;
	        }

	        frappe.call({
	            method: 'textiles_and_garments.textiles_and_garments.doctype.short_close_plans.short_close_plans.update_purchase_order_quantities',
	            args: {
	                purchase_order_name: frm.doc.purchase_order,
	                short_close_plan_items: short_close_plan_items
	            },
	            callback: function(response) {
	                if (response.message) {
	                    console.log("Purchase Order update initiated successfully.");
	                } else {
	                    frappe.msgprint(__("Failed to initiate Purchase Order update."));
	                }
	            },
	            error: function(err) {
	                console.error("Error calling server method to update Purchase Order:", err);
	                frappe.msgprint(__("An error occurred while trying to update the Purchase Order. Please check server logs."));
	            }
	        });


	        // Assuming you have the plans_no and sb_entries data
			frappe.call({
			    method: 'textiles_and_garments.textiles_and_garments.doctype.short_close_plans.short_close_plans.update_production_stock_reservation',
			    args: {
			        plans_no: frm.doc.plans_no,  // The linked Production Stock Reservation name
			        // sb_entries: JSON.stringify()
			        sb_entries: frm.doc.sb_entries
			    },
			    callback: function(r) {
			        if (r.message) {
			            frappe.msgprint(__('Production Stock Reservation updated successfully'));
			        }
			    }
			});

    	}else{
    		// work_order
    		let short_close_plan_items = [];
	        console.log(" work_order frm on_submit",frm);

	        // Ensure fg_item and total_short_close_qty are directly on the main Short Close Plans DocType
	        // And that frm.doc.fg_item holds the value you want to match in PO.
	        if (frm.doc.item_code && frm.doc.total_short_close_qty > 0) {
	        	console.log("frm on_submit 2",frm);
	            short_close_plan_items.push({
	                // Change 'item_code' to 'item_code' here to match the PO Item's item_code
	                fg_item: frm.doc.item_code,
	                short_close_qty: frm.doc.total_short_close_qty || 0
	            });
	        } else {
	            console.warn(" Item or Total Short Close Quantity is missing from the main document.");
	            frappe.msgprint(__("Cannot update Work Order: Item or Total Short Close Quantity is missing."));
	            return;
	        }

	        frappe.call({
	            method: 'textiles_and_garments.textiles_and_garments.doctype.short_close_plans.short_close_plans.update_work_order_quantities',
	            args: {
	                work_order_name: frm.doc.work_order,
	                short_close_plan_items: short_close_plan_items
	            },
	            callback: function(response) {
	                if (response.message) {
	                    console.log("Work Order update initiated successfully.");
	                } else {
	                    frappe.msgprint(__("Failed to initiate Work Order update."));
	                }
	            },
	            error: function(err) {
	                console.error("Error calling server method to update Work Order:", err);
	                frappe.msgprint(__("An error occurred while trying to update the Work Order. Please check server logs."));
	            }
	        });

	        // Assuming you have the plans_no and sb_entries data
			frappe.call({
			    method: 'textiles_and_garments.textiles_and_garments.doctype.short_close_plans.short_close_plans.update_production_stock_reservation',
			    args: {
			        plans_no: frm.doc.plans_no,  // The linked Production Stock Reservation name
			        // sb_entries: JSON.stringify()
			        sb_entries: frm.doc.sb_entries
			    },
			    callback: function(r) {
			        if (r.message) {
			            frappe.msgprint(__('Production Stock Reservation updated successfully'));
			        }
			    }
			});
    	}
        
    },
    after_cancel: function(frm) {
    	if(frm.doc.po_qty > 0){
    		let short_close_plan_items = [];
	        console.log("frm on_submit",frm);

	        // Ensure fg_item and total_short_close_qty are directly on the main Short Close Plans DocType
	        // And that frm.doc.fg_item holds the value you want to match in PO.
	        if (frm.doc.item_code && frm.doc.total_short_close_qty > 0) {
	        	console.log("frm on_submit 2",frm);
	            short_close_plan_items.push({
	                // Change 'item_code' to 'item_code' here to match the PO Item's item_code
	                fg_item: frm.doc.item_code,
	                short_close_qty: 0
	            });
	        } else {
	            console.warn("FG Item or Total Short Close Quantity is missing from the main document.");
	            frappe.msgprint(__("Cannot update Purchase Order: FG Item or Total Short Close Quantity is missing."));
	            return;
	        }

	        frappe.call({
	            method: 'textiles_and_garments.textiles_and_garments.doctype.short_close_plans.short_close_plans.update_purchase_order_quantities',
	            args: {
	                purchase_order_name: frm.doc.purchase_order,
	                short_close_plan_items: short_close_plan_items
	            },
	            callback: function(response) {
	                if (response.message) {
	                    console.log("Purchase Order update initiated successfully.");
	                } else {
	                    frappe.msgprint(__("Failed to initiate Purchase Order update."));
	                }
	            },
	            error: function(err) {
	                console.error("Error calling server method to update Purchase Order:", err);
	                frappe.msgprint(__("An error occurred while trying to update the Purchase Order. Please check server logs."));
	            }
	        });

	        // Assuming you have the plans_no and sb_entries data
			frappe.call({
			    method: 'textiles_and_garments.textiles_and_garments.doctype.short_close_plans.short_close_plans.cancel_production_stock_reservation',
			    args: {
			        plans_no: frm.doc.plans_no,  // The linked Production Stock Reservation name
			        // sb_entries: JSON.stringify()
			        sb_entries: frm.doc.sb_entries
			    },
			    callback: function(r) {
			        if (r.message) {
			            frappe.msgprint(__('Production Stock Reservation updated successfully'));
			        }
			    }
			});

    	}else{
    		let short_close_plan_items = [];
	        console.log(" work_order frm after_cancel",frm);

	        // Ensure fg_item and total_short_close_qty are directly on the main Short Close Plans DocType
	        // And that frm.doc.fg_item holds the value you want to match in PO.
	        if (frm.doc.item_code && frm.doc.total_short_close_qty > 0) {
	        	console.log("frm on_submit 2",frm);
	            short_close_plan_items.push({
	                // Change 'item_code' to 'item_code' here to match the PO Item's item_code
	                fg_item: frm.doc.item_code,
	                short_close_qty:  0
	            });
	        } else {
	            console.warn(" Item or Total Short Close Quantity is missing from the main document.");
	            frappe.msgprint(__("Cannot update Work Order: Item or Total Short Close Quantity is missing."));
	            return;
	        }

	        frappe.call({
	            method: 'textiles_and_garments.textiles_and_garments.doctype.short_close_plans.short_close_plans.update_work_order_quantities',
	            args: {
	                work_order_name: frm.doc.work_order,
	                short_close_plan_items: short_close_plan_items
	            },
	            callback: function(response) {
	                if (response.message) {
	                    console.log("Work Order update initiated successfully.");
	                } else {
	                    frappe.msgprint(__("Failed to initiate Work Order update."));
	                }
	            },
	            error: function(err) {
	                console.error("Error calling server method to update Work Order:", err);
	                frappe.msgprint(__("An error occurred while trying to update the Work Order. Please check server logs."));
	            }
	        });

	        // Assuming you have the plans_no and sb_entries data
			frappe.call({
			    method: 'textiles_and_garments.textiles_and_garments.doctype.short_close_plans.short_close_plans.cancel_production_stock_reservation',
			    args: {
			        plans_no: frm.doc.plans_no,  // The linked Production Stock Reservation name
			        // sb_entries: JSON.stringify()
			        sb_entries: frm.doc.sb_entries
			    },
			    callback: function(r) {
			        if (r.message) {
			            frappe.msgprint(__('Production Stock Reservation updated successfully'));
			        }
			    }
			});

    	}
    	
        
    }

});

frappe.ui.form.on('Serial and Batch Entry Plans', {
    short_close_qty(frm, cdt, cdn) {
        validate_short_close_qty(frm, cdt, cdn);
    }
});

function validate_short_close_qty(frm, cdt, cdn){
	let total_short_close_qty = 0;

	frm.doc.sb_entries.forEach(row => {
        if (flt(row.short_close_qty) > flt(row.qty)) {
            // frappe.msgprint(__('Reserved Qty cannot be greater than Available Qty for item: {0}', [row.item_code || row.idx]));
            frappe.model.set_value(row.doctype, row.name, 'short_close_qty', 0);
        }
        total_short_close_qty += flt(row.short_close_qty);
    });
    frm.set_value('total_short_close_qty', total_short_close_qty);

}




