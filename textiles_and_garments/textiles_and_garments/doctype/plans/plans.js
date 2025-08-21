// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt


frappe.ui.form.on("Plans", {
	refresh(frm) {
		console.log("Plans frm", frm);
		frm.set_query("bom", function() {
            return {
                filters: {
                    item: frm.doc.item_code,
                    docstatus: 1
                    // plan_items: frm.doc.plan_items
                }
            };
        });


	},

	bom: function (frm) {
		if (!frm.doc.bom) 
			return;

		// frappe.call({
		// 	method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.get_bom_details',
		// 	args: {
		// 		docname: frm.doc.name,
		// 		bom: frm.doc.bom
		// 	},
		// 	callback: function (response) {
		// 		if (response.message && Array.isArray(response.message)) {
		// 			console.log("Stock data received:", response.message);

		// 			// Clear existing child table entries
		// 			frm.clear_table("plans_stock_item");

		// 			// Add each row from the response
		// 			response.message.forEach(row => {
		// 				let child = frm.add_child("plans_stock_item", {
		// 					item: row.item_code,
		// 					batch: row.batch_no,
		// 					warehouse: row.warehouse,
		// 					stock_qty: row.balance_qty,
		// 					previous_reserved_qty: row.previous_reserved_qty,
		// 					avail_qty: row.avail_qty,
		// 					uom: row.stock_uom
		// 				});
		// 			});

		// 			// Refresh the field to show changes
		// 			frm.refresh_field("plans_stock_item");
		// 		}
		// 	}
		// });
	},
	// get_stock: function (frm) {
	// 	if (!frm.doc.bom) 
	// 		return;

	// 	frappe.call({
	// 		method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.get_bom_details',
	// 		args: {
	// 			docname: frm.doc.name,
	// 			bom: frm.doc.bom
	// 		},
	// 		callback: function (response) {
	// 			if (response.message && Array.isArray(response.message)) {
	// 				console.log("Stock data received:", response.message);

	// 				// Clear existing child table entries
	// 				frm.clear_table("plans_stock_item");

	// 				// Add each row from the response
	// 				response.message.forEach(row => {
	// 					let child = frm.add_child("plans_stock_item", {
	// 						item: row.item_code,
	// 						batch: row.batch_no,
	// 						warehouse: row.warehouse,
	// 						stock_qty: row.balance_qty,
	// 						avail_qty: row.previous_reserved_qty
	// 						uom: row.stock_uom
	// 					});
	// 				});

	// 				// Refresh the field to show changes
	// 				frm.refresh_field("plans_stock_item");
	// 			}
	// 		}
	// 	});
	// },
	purchase_or_manufacture: function(frm) {
		if (frm.doc.plans_stock_item && frm.doc.plans_stock_item.length > 0) {
			frm.clear_table("plans_stock_item");
			frm.refresh_field("plans_stock_item");
		}
	},
	uom_conversion_factor: function(frm){
		if (frm.doc.uom_conversion_factor != 1) {
			plan_qty_after_changed_uom = frm.doc.plan_qty * frm.doc.uom_conversion_factor;
			// frm.set_value('plan_qty_after_changed_uom', plan_qty_after_changed_uom);
			frm.doc.plan_qty_after_changed_uom = parseFloat(parseFloat(plan_qty_after_changed_uom || 0).toFixed(3));
            frm.refresh_field("plan_qty_after_changed_uom");
			
		}
	},
	get_stock: function (frm) {
		if (!frm.doc.bom) return;

		frappe.call({
			method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.get_bom_details',
			args: {
				docname: frm.doc.name,
				bom: frm.doc.bom,
				search_batch: frm.doc.search_batch || '',
				indent: frm.doc.indent || ''
			},
			callback: function (response) {
				if (response.message && Array.isArray(response.message)) {
					console.log("Stock data received:", response.message);

					frm.clear_table("plans_stock_item");

					response.message.forEach(row => {
						let child = frm.add_child("plans_stock_item", {
							item: row.item_code,
							batch: row.batch_no,
							warehouse: row.warehouse,
							stock_qty: row.balance_qty,
							previous_reserved_qty: row.previous_reserved_qty,
							avail_qty: row.avail_qty,
							uom: row.stock_uom
						});
					});

					frm.refresh_field("plans_stock_item");
				}
			}
		});
	},
	remove_zero_reserve_rows: function (frm) {
		frappe.call({
			method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.remove_zero_reserve_rows',
			args: {
				docname: frm.doc.name,
				plans_stock_item: frm.doc.plans_stock_item
			},
			callback: function (response) {
				if (response.message && Array.isArray(response.message)) {
					console.log("Filtered stock items:", response.message);

					// Clear existing child table entries
					frm.clear_table("plans_stock_item");

					// Add only rows with reserve_qty > 0
					response.message.forEach(row => {
						let child = frm.add_child("plans_stock_item", {
							item: row.item,
							batch: row.batch,
							warehouse: row.warehouse,
							stock_qty: row.stock_qty,
							uom: row.uom,
							reserve_qty: row.reserve_qty,
							previous_reserved_qty: row.previous_reserved_qty,
							avail_qty: row.avail_qty,
						});
					});

					// Refresh the field to show changes
					frm.refresh_field("plans_stock_item");
				}
			}
		});
	},
	get_wip: function (frm) {
		console.log("frm get_wip",frm);
		

		// frappe.call({
		// 	method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.get_wip_details',
		// 	args: {
		// 		docname: frm.doc.name,
		// 		item_code: frm.doc.item_code,
		// 		bom: frm.doc.bom
		// 	},
		// 	callback: function (response) {
		// 		if (response.message && Array.isArray(response.message)) {
		// 			console.log("Stock data received:", response.message);

		// 			// Clear existing child table entries
		// 			frm.clear_table("plans_wip_item");

		// 			// Add each row from the response
		// 			response.message.forEach(row => {
		// 				// let child = frm.add_child("plans_wip_item", {
		// 				// 	item: row.item_code,
		// 				// 	plan: row.name,
		// 				// 	plan_items: row.plan_items,
		// 				// 	qty: row.plan_qty,
		// 				// 	reserve_qty: row.reserved_qty,
		// 				// 	unreserve_qty: row.unreserved_qty
		// 				// });
		// 				let child = frm.add_child("plans_wip_item", {
		// 				    item: row.item_code,
		// 				    plan: row.name,
		// 				    plan_items: row.plan_items,
		// 				    qty: row.plan_qty,
		// 				    // Conditional logic for reserve_qty
		// 				    to_reserve_qty: (row.unreserved_qty === 0 ? 0 : row.plan_qty - row.reserved_qty),
		// 				    unreserve_qty: row.unreserved_qty,
		// 				    reserve_qty: row.reserved_qty
		// 				});
		// 			});

		// 			// Refresh the field to show changes
		// 			frm.refresh_field("plans_wip_item");
		// 		}
		// 	}
		// });

		frappe.call({
		    method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.get_wip_details',
		    args: {
		        docname: frm.doc.name,
		        item_code: frm.doc.item_code,
		        bom: frm.doc.bom
		    },
		    callback: function (response) {
		        if (response.message && Array.isArray(response.message)) {
		            console.log("Stock data received:", response.message);

		            // Clear existing child table entries
		            frm.clear_table("plans_wip_item");

		            // Add each row from the response
		            response.message.forEach(row => {
		            	console.log("row",row);
		                let child = frm.add_child("plans_wip_item", {
		                    item: row.item_code,
		                    plan: row.name,
		                    plan_items: row.plan_items,
		                    qty: row.plan_qty,
		                    reserve_qty: row.reserved_qty,
		                    unreserved_received_qty: row.unreserved_received_qty,
		                    // reserve_qty_via_stock: row.received_qty || 0,
		                    // to_reserve_qty: (row.unreserved_qty === 0 ? 0 : row.plan_qty - row.reserved_qty),
		                    // to_reserve_qty: (row.reserved_qty === 0 ? row.plan_qty - row.received_qty : row.plan_qty - row.received_qty - row.reserved_qty),
		                    unreserve_qty: row.to_reserve_qty,
		                    to_reserve_qty: row.to_reserve_qty    
		                });
		            });

		            // Refresh the field to show changes
		            frm.refresh_field("plans_wip_item");
		        }
		    }
		});
	},
	set_zero_rows: function (frm) {
		console.log("set_zero_rows get_wip",frm);
		

		frappe.call({
			method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.get_wip_details ',
			args: {
				docname: frm.doc.name,
				item_code: frm.doc.item_code,
				bom: frm.doc.bom
			},
			callback: function (response) {
				if (response.message && Array.isArray(response.message)) {
					console.log("Stock data received:", response.message);

					// Clear existing child table entries
					frm.clear_table("plans_wip_item");

					// Add each row from the response
					response.message.forEach(row => {
						// let child = frm.add_child("plans_wip_item", {
						//     item: row.item_code,
						//     plan: row.name,
						//     plan_items: row.plan_items,
						//     qty: row.plan_qty,
						//     // Conditional logic for reserve_qty
						//     to_reserve_qty: 0,
						//     unreserve_qty: row.unreserved_qty,
						//     reserve_qty: row.reserved_qty
						// });

						let child = frm.add_child("plans_wip_item", {
		                    item: row.item_code,
		                    plan: row.name,
		                    plan_items: row.plan_items,
		                    qty: row.plan_qty,
		                    unreserved_received_qty: row.unreserved_received_qty,
		                    // reserve_qty_via_stock: row.received_qty || 0,
		                    // to_reserve_qty: (row.unreserved_qty === 0 ? 0 : row.plan_qty - row.reserved_qty),
		                    to_reserve_qty: 0,
		                    unreserve_qty: row.unreserved_qty,
		                    reserve_qty: row.reserved_qty
		                });
					});

					// Refresh the field to show changes
					frm.refresh_field("plans_wip_item");
				}
			}
		});
	},
	validate: function (frm) {
		console.log("validate frm",frm);
		if (frm.doc.uom_conversion_factor == 1 && frm.doc.purchase_or_manufacture != "Purchase" && frm.doc.plan_qty != frm.doc.rm_reserved_qty) {
	        frappe.msgprint(__('Plan Qty and Reserve Qty should be Equal'));
	        frappe.validated = false;
	    }
	    if(frm.doc.uom_conversion_factor != 1 && frm.doc.purchase_or_manufacture != "Purchase" && frm.doc.plan_qty_after_changed_uom != frm.doc.rm_reserved_qty){
	    	console.log("frm.doc.uom_conversion_factor",frm.doc.uom_conversion_factor);
	    	console.log("frm.doc.purchase_or_manufacture",frm.doc.purchase_or_manufacture);
	    	console.log("frm.doc.plan_qty_after_changed_uom",frm.doc.plan_qty_after_changed_uom);
	    	console.log("frm.doc.rm_reserved_qty",frm.doc.rm_reserved_qty);
	    	frappe.msgprint(__('Plan Qty After Changed UOM and Reserve Qty should be Equal'));
	        frappe.validated = false;
	    }
	    if(frm.doc.plans_wip_item){
	    	frappe.call({
				method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.remove_zero_reserve_rows_in_wip ',
				args: {
					docname: frm.doc.name,
					plans_wip_item: frm.doc.plans_wip_item
				},
				callback: function (response) {
					if (response.message && Array.isArray(response.message)) {
						console.log("Stock data received:", response.message);

						// Clear existing child table entries
						frm.clear_table("plans_wip_item");

						// Add each row from the response
						response.message.forEach(row => {
							console.log("row",row);
							// let child = frm.add_child("plans_wip_item", {
							// 	item: row.item_code,
							// 	plan: row.name,
							// 	plan_items: row.plan_items,
							// 	qty: row.plan_qty,
							// 	reserve_qty: 0,
							// 	unreserve_qty: row.unreserved_qty
							// });
							let child = frm.add_child("plans_wip_item", {
							    item: row.item,
							    plan: row.plan,
							    plan_items: row.plan_items,
							    qty: row.qty,
							    unreserved_received_qty: row.unreserved_received_qty,
							    // Conditional logic for reserve_qty
							    to_reserve_qty: row.to_reserve_qty,
							    unreserve_qty: row.unreserve_qty,
							    reserve_qty: row.reserve_qty
							});
						});

						// Refresh the field to show changes
						frm.refresh_field("plans_wip_item");
					}
				}
			});
	    }
	},
	// validate: function (frm) {
	//     console.log("validate frm", frm);

	//     // Check if any row has reserve_qty < stock_qty
	//     const shouldCall = frm.doc.plans_stock_item.some(row => {
	//         return flt(row.reserve_qty) > 0 && flt(row.reserve_qty) <= flt(row.stock_qty) && flt(row.reserve_qty) <= (frm.doc.plan_qty);
	//     });

	//     if (shouldCall) {
	//     	console.log("shouldCall",shouldCall);
	//         frappe.call({
	//             method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.update_plan_items_planned_wise',
	//             args: {
	//                 docname: frm.doc.name
	//             },
	//             callback: function (response) {
	//                 if (response.message) {
	//                     frappe.msgprint(__('Updated the Plan Item documents successfully.'));
	//                 }
	//             }
	//         });
	//     } else {
	//     	console.log("else shouldCall",shouldCall);
	//         frappe.msgprint(__('No data qualify for Plan Item documents to be update.'));
	//     }
	// },

	// validate: function (frm) {
	//     console.log("on_submit frm", frm);
	    

	//     // Check if any row qualifies based on to_reserve_qty logic
	//     const shouldCallForStock = frm.doc.plans_stock_item.some(row => {
	//         return flt(row.to_reserve_qty) > 0 &&
	//                flt(row.to_reserve_qty) <= flt(row.avail_qty) &&
	//                flt(row.to_reserve_qty) <= flt(frm.doc.plan_qty);
	//     });

	//     // Check if any row qualifies based on to_reserve_qty logic
	//     const shouldCallForWIP = frm.doc.plans_wip_item.some(row => {
	//     	console.log("row.to_reserve_qty",row.to_reserve_qty);
	//     	console.log("row.unreserve_qty",row.unreserve_qty);
	//     	console.log("frm.doc.plan_qty",frm.doc.plan_qty);
	//         return flt(row.to_reserve_qty) > 0 &&
	//                flt(row.to_reserve_qty) <= flt(row.unreserve_qty) &&
	//                flt(row.to_reserve_qty) <= flt(frm.doc.plan_qty);
	//     });

	//     const shouldCallForPurchase = frm.doc.purchase_or_manufacture === "Purchase";

	//     console.log("shouldCallForStock1",shouldCallForStock);
	//     console.log("shouldCallForWIP1",shouldCallForWIP);
	//     console.log("shouldCallForPurchase1",shouldCallForPurchase);
	    


	//     if (shouldCallForStock || shouldCallForWIP || shouldCallForPurchase) {
	//         console.log("shouldCallForStock", shouldCallForStock);
	//         console.log("shouldCallForWIP", shouldCallForWIP);
	//         console.log("shouldCallForPurchase", shouldCallForPurchase);

	//         // Call 1: update_plan_items_planned_wise
	//         frappe.call({
	//             method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.update_plan_items_planned_wise',
	//             args: {
	//                 docname: frm.doc.name
	//             },
	//             callback: function (response1) {
	//                 console.log('update_plan_items_planned_wise response', response1);

	//                 // Call 2: create_production_stock_reservation (only for stock items)
	//                 if (shouldCallForStock) {
	//                     frappe.call({
	//                         method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.create_production_stock_reservation',
	//                         args: {
	//                             docname: frm.doc.name,
	//                             plans_stock_item: frm.doc.plans_stock_item
	//                         },
	//                         callback: function (response2) {
	//                             console.log('create_production_stock_reservation response', response2);
	//                             if (response2.message) {
	//                                 frappe.msgprint(__('Production Stock Reservations created successfully.'));
	//                             }
	//                         }
	//                     });
	//                 }

	//                 // You can add additional calls here for WIP or Purchase if needed
	//                 // For example:
	//                 if (shouldCallForPurchase) {
	//                     // Your purchase logic here
	//                     frappe.msgprint(__('This plan is marked for Purchase.'));
	//                 }
	//             }
	//         });
	//     } else {
	//         console.log("No items qualify for reservation or purchase.");
	//         frappe.msgprint(__('No stock, WIP, or purchase items qualify for processing.'));
	//     }
	// },

	on_submit: function (frm) {
	    console.log("on_submit frm", frm);
	    

	    // Check if any row qualifies based on to_reserve_qty logic
	    const shouldCallForStock = frm.doc.plans_stock_item.some(row => {
	        return flt(row.reserve_qty) > 0 &&
	               flt(row.reserve_qty) <= flt(row.avail_qty) &&
	               flt(row.reserve_qty) <= flt(frm.doc.plan_qty);
	    });

	    // Check if any row qualifies based on to_reserve_qty logic
	    const shouldCallForWIP = frm.doc.plans_wip_item.some(row => {
	        return flt(row.to_reserve_qty) > 0 &&
	               flt(row.to_reserve_qty) <= flt(row.unreserve_qty) &&
	               flt(row.to_reserve_qty) <= flt(frm.doc.plan_qty);
	    });

	    const shouldCallForPurchase = frm.doc.purchase_or_manufacture === "Purchase";

	    console.log("shouldCallForStock",shouldCallForStock);
	    console.log("shouldCallForWIP",shouldCallForWIP);
	    console.log("shouldCallForPurchase",shouldCallForPurchase);
	    


	    if (shouldCallForStock || shouldCallForWIP || shouldCallForPurchase) {
	        console.log("shouldCallForStock", shouldCallForStock);
	        console.log("shouldCallForWIP", shouldCallForWIP);
	        console.log("shouldCallForPurchase", shouldCallForPurchase);

	        // Call 1: update_plan_items_planned_wise
	        frappe.call({
	            method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.update_plan_items_planned_wise',
	            args: {
	                docname: frm.doc.name
	            },
	            callback: function (response1) {
	                console.log('update_plan_items_planned_wise response', response1);

	                // Call 2: create_production_stock_reservation (only for stock items)
	                if (shouldCallForStock) {
	                    frappe.call({
	                        method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.create_production_stock_reservation',
	                        args: {
	                            docname: frm.doc.name,
	                            plans_stock_item: frm.doc.plans_stock_item
	                        },
	                        callback: function (response2) {
	                            console.log('create_production_stock_reservation response', response2);
	                            if (response2.message) {
	                                frappe.msgprint(__('Production Stock Reservations created successfully.'));
	                            }
	                        }
	                    });
	                }

	                // You can add additional calls here for WIP or Purchase if needed
	                // For example:
	                if (shouldCallForPurchase) {
	                    // Your purchase logic here
	                    frappe.msgprint(__('This plan is marked for Purchase.'));
	                }
	            }
	        });
	    } else {
	        console.log("No items qualify for reservation or purchase.");
	        frappe.msgprint(__('No stock, WIP, or purchase items qualify for processing.'));
	    }
	},

	// on_cancel: function(frm){
	// 	// console.log("response",on_cancel);
	// 	// frappe.call({
    //     //     method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.cancel_production_stock_reservation',
    //     //     args: {
    //     //         docname: frm.doc.name,
    //     //     },
    //     //     callback: function (response) {
    //     //         if (response.message) {
    //     //             frappe.msgprint(__('Production Stock Reservations cancelled successfully.'));
    //     //         }
    //     //     }
    //     // });

    //     // frappe.call({
	//     //     method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.unlink_plan_item_planned_wise_references',
	//     //     args: {
	//     //         docname: frm.doc.name,
	//     //     },
	//     //     callback: function(response) {
	//     //     	console.log("response",response);
	//     //         if (response.message) {
	//     //             frappe.msgprint(__('Plans Items removed the plan item planned wise data successfully.'));
	//     //         }
	//     //     }
	//     // });

    //     // frappe.call({
	//     //     method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.cancel_plan_dependencies',
	//     //     args: {
	//     //         docname: frm.doc.name,
	//     //     },
	//     //     callback: function(response) {
	//     //         if (response.message) {
	//     //             frappe.msgprint(__('Plans Items removed the plan item planned wise data successfully.'));
	//     //         }
	//     //     }
	//     // });

        

	// },
	update_wip_plans: function (frm) {
		console.log("validate frm",frm);
		frappe.call({
			method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.update_production_wip_plans',
			args: {
				docname: frm.doc.name,
				plans_wip_item: frm.doc.plans_wip_item
			},
			callback: function (response) {
				if (response.message) {
					frappe.msgprint(__('Production WIP Plans updated successfully.'));
				}
				
			}
		});
	},
	update_plan_items: function (frm) {
		console.log("validate frm",frm);
		frappe.call({
	        method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.unlink_plan_item_planned_wise_referencess',
	        args: {
	            docname: frm.doc.name,
	        },
	        callback: function(response) {
	        	console.log("response",response);
	            if (response.message) {
	                frappe.msgprint(__('Plans Items removed the plan item planned wise data successfully.'));
	            }
	        }
	    });
	}
});

// frappe.ui.form.on('Plans', {
//     after_cancel: function(frm) {
//         console.log("✅ Plans on_cancel hook triggered");
//         frappe.msgprint("Cancel hook called!");
//         frappe.call({
// 	        method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.unlink_plan_item_planned_wise_references',
// 	        args: {
// 	            docname: frm.doc.name,
// 	        },
// 	        callback: function(response) {
// 	        	console.log("response",response);
// 	            if (response.message) {
// 	                frappe.msgprint(__('Plans Items removed the plan item planned wise data successfully.'));
// 	            }
// 	        }
// 	    });
//     }
// });

// frappe.ui.form.on('Plans Stock Item', {
//     reserve_qty(frm, cdt, cdn) {
//         // Get all rows in the child table
//         let total_reserved_qty = 0;

//         frm.doc.plans_stock_item.forEach(row => {
//             total_reserved_qty += flt(row.reserve_qty);
//         });

//         // Set the total in the parent field
//         frm.set_value('rm_reserved_qty', total_reserved_qty);
//     }
// });
// frappe.ui.form.on('Plans Stock Item', {
//     reserve_qty(frm, cdt, cdn) {
//         let total_reserved_qty = 0;

//         frm.doc.plans_stock_item.forEach(row => {
//             // Validate reserve_qty <= avail_qty
//             if (flt(row.reserve_qty) > flt(row.avail_qty)) {
//                 frappe.msgprint(__('Reserved Qty cannot be greater than Available Qty for item: {0}', [row.item_code || row.idx]));
//                 frappe.model.set_value(cdt, cdn, 'reserve_qty', 0);
//             } else {
//                 total_reserved_qty += flt(row.reserve_qty);
//             }
//         });

//         // Update the total in the parent field
//         frm.set_value('rm_reserved_qty', total_reserved_qty);
//     }
// });

// frappe.ui.form.on('Plans Stock Item', {
//     reserve_qty(frm, cdt, cdn) {
//         let total_reserved_qty = 0;

//         frm.doc.plans_stock_item.forEach(row => {
//             // Validate reserve_qty <= avail_qty
//             if (flt(row.reserve_qty) > flt(row.avail_qty)) {
//                 frappe.msgprint(__('Reserved Qty cannot be greater than Available Qty for item: {0}', [row.item_code || row.idx]));
//                 frappe.model.set_value(row.doctype, row.name, 'reserve_qty', 0);
//             } else {
//                 total_reserved_qty += flt(row.reserve_qty);
//             }
//         });

//         // Validate total reserved qty <= plan_qty
//         if (flt(total_reserved_qty) > flt(frm.doc.plan_qty)) {
//             frappe.msgprint(__('Total Reserved Qty ({0}) cannot be greater than Plan Qty ({1}).', 
//                 [total_reserved_qty, frm.doc.plan_qty]));
//             // Optionally reset the triggering row's value if over-limit
//             frappe.model.set_value(cdt, cdn, 'reserve_qty', 0);

//             // Recalculate total_reserved_qty after resetting
//             total_reserved_qty = 0;
//             frm.doc.plans_stock_item.forEach(row => {
//                 total_reserved_qty += flt(row.reserve_qty);
//             });
//         }

//         // Update the total in the parent field
//         frm.set_value('rm_reserved_qty', total_reserved_qty);
//     }
// });


// frappe.ui.form.on('Plans WIP Item', {
//     reserve_qty(frm, cdt, cdn) {
//         let total_reserved_qty = 0;

//         frm.doc.plans_wip_item.forEach(row => {
//             // Validate reserve_qty <= unreserve_qty
//             if (flt(row.unreserve_qty) !== 0 && flt(row.reserve_qty) > flt(row.unreserve_qty)) {
//                 frappe.msgprint(__('Reserved Qty cannot be greater than Unreserve Qty for item: {0}', [row.idx]));
//                 frappe.model.set_value(row.doctype, row.name, 'reserve_qty', 0);
//             } else {
//                 total_reserved_qty += flt(row.reserve_qty);
//             }
//         });

//         // Validate total reserved qty <= plan_qty
//         if (flt(total_reserved_qty) > flt(frm.doc.plan_qty)) {
//             frappe.msgprint(__('Total Reserved Qty ({0}) cannot be greater than Plan Qty ({1}).', 
//                 [total_reserved_qty, frm.doc.plan_qty]));

//             // Reset the current row's reserve_qty to 0
//             frappe.model.set_value(cdt, cdn, 'reserve_qty', 0);

//             // Recalculate the total after reset
//             total_reserved_qty = 0;
//             frm.doc.plans_wip_item.forEach(row => {
//                 total_reserved_qty += flt(row.reserve_qty);
//             });
//         }

//         // Optionally, update a total field (if exists)
//         frm.set_value('rm_reserved_qty', total_reserved_qty);
//     }
// });


function validate_total_reserved_qty(frm, cdt, cdn, child_table_type) {
    let total_reserved_qty = 0;
    let current_row = locals[cdt][cdn];

    // Validate Plans Stock Item Table
    frm.doc.plans_stock_item.forEach(row => {
        if (flt(row.reserve_qty) > flt(row.avail_qty)) {
            // frappe.msgprint(__('Reserved Qty cannot be greater than Available Qty for item: {0}', [row.item_code || row.idx]));
            frappe.model.set_value(row.doctype, row.name, 'reserve_qty', 0);
        }
        total_reserved_qty += flt(row.reserve_qty);
    });

    // Validate Plans WIP Item Table
    frm.doc.plans_wip_item.forEach(row => {
    	console.log("row",row);
        if (flt(row.to_reserve_qty) !== 0 && flt(row.to_reserve_qty) > flt(row.unreserve_qty)) {
            // frappe.msgprint(__('Reserved Qty cannot be greater than Unreserve Qty for item: {0}', [row.idx]));
            frappe.model.set_value(row.doctype, row.name, 'to_reserve_qty', 0);
        }
        total_reserved_qty += flt(row.to_reserve_qty);
    });

    // Validate combined total reserved qty
    if (flt(total_reserved_qty) > flt(frm.doc.plan_qty)) {
        frappe.msgprint(__('Total Reserved Qty ({0}) cannot be greater than Plan Qty ({1}).', 
            [total_reserved_qty, frm.doc.plan_qty]));

        // Reset current row's reserve_qty
        frappe.model.set_value(cdt, cdn, 'reserve_qty', 0);

        // Recalculate total after reset
        total_reserved_qty = 0;

        frm.doc.plans_stock_item.forEach(row => {
            total_reserved_qty += flt(row.reserve_qty);
        });
        frm.doc.plans_wip_item.forEach(row => {
            total_reserved_qty += flt(row.to_reserve_qty);
        });
    }

    // Update parent field with combined reserved qty
    frm.set_value('rm_reserved_qty', total_reserved_qty);

    if(frm.doc.uom_conversion_factor == 1){
       frm.set_value('rm_unreserved_qty', frm.doc.plan_qty - total_reserved_qty);
    }
    else{
    	frm.set_value('rm_unreserved_qty', frm.doc.plan_qty_after_changed_uom - total_reserved_qty);
    }
    
}

function validate_to_reserve_qty(frm, cdt, cdn, child_table_type) {
    
    let current_row = locals[cdt][cdn];

    // Validate Plans WIP Item Table
    frm.doc.plans_wip_item.forEach(row => {
    	console.log("row",row);
        if (flt(row.to_reserve_qty) !== 0 && flt(row.to_reserve_qty) > flt(row.unreserve_qty)) {
            frappe.msgprint(__('Reserved Qty {0} cannot be greater than Unreserve Qty {1} for item: {2}', [row.to_reserve_qty,row.unreserve_qty, row.idx]));
            
        }
        
    });
        
}

// Stock Table Trigger
frappe.ui.form.on('Plans Stock Item', {
    reserve_qty(frm, cdt, cdn) {
        validate_total_reserved_qty(frm, cdt, cdn, 'stock');
    }
});

// WIP Table Trigger
frappe.ui.form.on('Plans WIP Item', {
    to_reserve_qty(frm, cdt, cdn) {
        // validate_to_reserve_qty(frm, cdt, cdn, 'wip');
        validate_total_reserved_qty(frm, cdt, cdn, 'wip');
    }
});

// frappe.ui.form.on('Plans', {
//     on_submit: function(frm) {
//     	validate_total_reserved_qty(frm, cdt, cdn, 'stock');
//     	validate_total_reserved_qty(frm, cdt, cdn, 'wip');
      
//     }
// });


frappe.ui.form.on('Plans', {
    on_submit: function(frm) {
    	frappe.call({
			method: 'textiles_and_garments.textiles_and_garments.doctype.plans.plans.update_production_wip_plans',
			args: {
				docname: frm.doc.name,
				plans_wip_item: frm.doc.plans_wip_item
			},
			callback: function (response) {
				if (response.message) {
					frappe.msgprint(__('Production WIP Plans updated successfully.'));
				}
				
			}
		});
      
    }
});





frappe.ui.form.on('Plans', {
    refresh: function(frm) {
       frm.set_df_property('plans_wip_item', 'cannot_add_rows', true); // Hide add row button
       frm.set_df_property('plans_wip_item', 'cannot_delete_rows', true); // Hide delete button
       frm.set_df_property('plans_wip_item', 'cannot_delete_all_rows', true); // Hide delete all button
    }
});



// function to create a Work Order document
function create_work_order_doc(frm, cdt, cdn) {
    const row = locals[cdt][cdn];

    let item_code = frm.doc.item_code;
    let qty = frm.doc.plan_qty;
    if(frm.doc.short_close_wo_qty > 0){
    	let short_close_wo_qty = frm.doc.short_close_wo_qty;
    }
    
    let bom = frm.doc.bom;
    let plans = frm.doc.name;
    console.log("frm.doc.name",frm.doc.name)

    if (!item_code || !qty) {
        frappe.msgprint("Item Code and Quantity are required to create a Work Order.");
        return;
    }

    
    if (frm.doc.short_close_wo_qty > 0) {
	    frappe.call({
	        method: "frappe.client.insert",
	        args: {
	            doc: {
	                doctype: "Work Order",
	                production_item: item_code,
	                bom_no: bom,
	                custom_plans: plans,
	                custom_plan_items: frm.doc.plan_items,
	                qty: frm.doc.short_close_wo_qty,
	                posting_date: frappe.datetime.now_date(),
	                fg_warehouse: "DYE/LOT SECTION - PSS"
	            }
	        },
	        callback: function (r) {
	            if (r.message) {
	                // Open the Work Order in a new tab
	                const url = `/app/work-order/${r.message.name}`;
	                window.open(url, '_blank');

	                // Optional: show a success message with clickable link
	                let link = `<a href="${url}" target="_blank">${r.message.name}</a>`;
	                frappe.msgprint({
	                    title: __("Work Order Created"),
	                    message: __("Work Order document {0} created successfully.", [link]),
	                    indicator: "green"
	                });
	            }
	        }
	    });
	} else {
	    frappe.call({
	        method: "frappe.client.insert",
	        args: {
	            doc: {
	                doctype: "Work Order",
	                production_item: item_code,
	                bom_no: bom,
	                custom_plans: plans,
	                custom_plan_items: frm.doc.plan_items,
	                qty: qty,
	                posting_date: frappe.datetime.now_date(),
	                fg_warehouse: "DYE/LOT SECTION - PSS"
	            }
	        },
	        callback: function (r) {
	            if (r.message) {
	                // Open the Work Order in a new tab
	                const url = `/app/work-order/${r.message.name}`;
	                window.open(url, '_blank');

	                // Optional: show a success message with clickable link
	                let link = `<a href="${url}" target="_blank">${r.message.name}</a>`;
	                frappe.msgprint({
	                    title: __("Work Order Created"),
	                    message: __("Work Order document {0} created successfully.", [link]),
	                    indicator: "green"
	                });
	            }
	        }
	    });
	}


    
}



// Button handler for Plan Items Summary
frappe.ui.form.on('Plans', {
    create_work_order(frm, cdt, cdn) {
        create_work_order_doc(frm, cdt, cdn);
    }
});





