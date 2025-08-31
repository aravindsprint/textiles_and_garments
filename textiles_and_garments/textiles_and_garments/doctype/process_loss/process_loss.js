// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Process Loss", {
// 	refresh(frm) {

// 	},
// 	calculate_process_loss: function (frm) {
// 		frappe.call({
// 			method: 'textiles_and_garments.textiles_and_garments.doctype.process_loss.process_loss.calculate_process_loss',
// 			args: {
// 				docname: frm.doc.name,
// 				purchase_orders: frm.doc.purchase_orders
// 			},
// 			callback: function (response) {
// 				if (response.message && Array.isArray(response.message)) {
// 					console.log("Filtered stock items:", response.message);

// 					// // Clear existing child table entries
// 					// frm.clear_table("plans_stock_item");

// 					// // Add only rows with reserve_qty > 0
// 					// response.message.forEach(row => {
// 					// 	let child = frm.add_child("plans_stock_item", {
// 					// 		item: row.item,
// 					// 		batch: row.batch,
// 					// 		warehouse: row.warehouse,
// 					// 		stock_qty: row.stock_qty,
// 					// 		uom: row.uom,
// 					// 		reserve_qty: row.reserve_qty,
// 					// 		previous_reserved_qty: row.previous_reserved_qty,
// 					// 		avail_qty: row.avail_qty,
// 					// 	});
// 					// });

// 					// // Refresh the field to show changes
// 					// frm.refresh_field("plans_stock_item");
// 				}
// 			}
// 		});
// 	}
// });


frappe.ui.form.on("Process Loss", {
    refresh(frm) {

    },
    calculate_process_loss: function (frm) {
        frappe.call({
            method: 'textiles_and_garments.textiles_and_garments.doctype.process_loss.process_loss.calculate_process_loss',
            args: {
                docname: frm.doc.name,
                purchase_orders: frm.doc.purchase_orders
            },
            callback: function (response) {
                if (response.message && Array.isArray(response.message)) {
                    console.log("Filtered stock items:", response.message);
                    // Reload the form to show the updated sent_details table
                    frm.reload_doc();
                    frappe.show_alert({
                        message: __("Sent details updated successfully"),
                        indicator: 'green'
                    }, 3000);
                }
            }
        });
    },
    calculate_summary: function (frm) {
        frappe.call({
            method: 'textiles_and_garments.textiles_and_garments.doctype.process_loss.process_loss.calculate_summary',
            args: {
                docname: frm.doc.name,
                // purchase_orders: frm.doc.purchase_orders
            },
            callback: function (response) {
                if (response.message && Array.isArray(response.message)) {
                    console.log("Filtered stock items:", response.message);
                    // Reload the form to show the updated sent_details table
                    // frm.reload_doc();
                    // frappe.show_alert({
                    //     message: __("Sent details updated successfully"),
                    //     indicator: 'green'
                    // }, 3000);
                }
            }
        });
    }
});
