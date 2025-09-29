// frappe.ui.form.on('Quotation', {
//     refresh(frm) {
//         frm.add_custom_button('Create Sales Invoice', () => {
//             console.log("Create Sales Invoice is clicked");
//             create_sales_invoice_doc(frm);
//         });
//     }
// });

// function create_sales_invoice_doc(frm) {
//     // Create a deep copy of the items to avoid modifying the original frm.doc.items directly
//     // and ensure 'use_serial_batch_fields' is set for each item.
//     const salesInvoiceItems = frm.doc.items.map(item => {
//     	console.log("item",item);
//         return {
//             ...item, // Copy all existing properties from the original item
//             use_serial_batch_fields: 1,// Set 'use_serial_batch_fields' to 1
//             batch_no: item.batch
//         };
//     });

//     frappe.call({
//         method: "frappe.client.insert",
//         args: {
//             doc: {
//                 doctype: "Sales Invoice",
//                 items: salesInvoiceItems, // Use the modified items array
//                 posting_date: frappe.datetime.now_date(),
//                 due_date: frappe.datetime.now_date(),
//                 customer: frm.doc.party_name,
//                 purchase_by: "-",
//                 purchaser_mobile_no: "-",
//                 vehicle_no: "-",
//                 distance: 0,
//                 company_address: "Pranera Tirupur",
//                 stock_entry: frm.doc.stock_entry,
//                 update_stock: 1,
//                 // fg_warehouse: "DYE/LOT SECTION - PSS" // Uncomment if needed
//             }
//         },
//         callback: function (r) {
//             if (r.message) {
//                 // Open the Sales Invoice in a new tab
//                 const url = `/app/sales-invoice/${r.message.name}`;
//                 window.open(url, '_blank');

//                 // Optional: show a success message with clickable link
//                 let link = `<a href="${url}" target="_blank">${r.message.name}</a>`;
//                 frappe.msgprint({
//                     title: __("Sales Invoice Created"),
//                     message: __("Sales Invoice document {0} created successfully.", [link]),
//                     indicator: "green"
//                 });
//             } else if (r.exc) {
//                 // Handle server-side errors
//                 frappe.msgprint({
//                     title: __("Error"),
//                     message: __("Failed to create Sales Invoice: {0}", [r.exc]),
//                     indicator: "red"
//                 });
//                 console.error("Error creating Sales Invoice:", r.exc);
//             }
//         },
//         error: function(err) {
//             // Handle client-side network or other errors
//             frappe.msgprint({
//                 title: __("Error"),
//                 message: __("An error occurred while calling the server: {0}", [err.message]),
//                 indicator: "red"
//             });
//             console.error("Client-side error:", err);
//         }
//     });
// }


frappe.ui.form.on('Quotation', {
    refresh(frm) {
        console.log("Quotation frm", frm.doc);
        frm.add_custom_button('Create Sales Invoice', () => {
            console.log("Create Sales Invoice is clicked");
            create_sales_invoice_doc(frm);
        });
    }
});

function create_sales_invoice_doc(frm) {
    // Show loading indicator
    frappe.show_alert({
        message: __('Creating Sales Invoice...'),
        indicator: 'blue'
    });

    frappe.model.with_doctype('Sales Invoice', function() {
        try {
            const sales_invoice = frappe.model.get_new_doc('Sales Invoice');
            
            // Set main fields
            sales_invoice.customer = frm.doc.party_name;
            sales_invoice.company = frm.doc.company;
            sales_invoice.posting_date = frappe.datetime.now_date();
            sales_invoice.due_date = frappe.datetime.now_date();
            sales_invoice.quotation = frm.doc.name;
            sales_invoice.purchase_by = "-";
            sales_invoice.purchaser_mobile_no = "-";
            sales_invoice.vehicle_no = "-";
            sales_invoice.distance = 0;
            sales_invoice.company_address = "Pranera Tirupur";
            sales_invoice.stock_entry = frm.doc.stock_entry;
            sales_invoice.update_stock = 1;
            
            // Add items
            if (frm.doc.items && frm.doc.items.length > 0) {
                frm.doc.items.forEach(item => {
                    let child = frappe.model.add_child(sales_invoice, 'items');
                    Object.assign(child, {
                        item_code: item.item_code,
                        item_name: item.item_name,
                        qty: item.qty,
                        rate: item.rate,
                        amount: item.amount,
                        uom: item.uom,
                        stock_uom: item.stock_uom,
                        conversion_factor: item.conversion_factor || 1,
                        use_serial_batch_fields: 1,
                        batch_no: item.batch,
                        warehouse: item.warehouse,
                        description: item.description
                    });
                });
            }
            
            // Add taxes
            if (frm.doc.taxes && frm.doc.taxes.length > 0) {
                frm.doc.taxes.forEach(tax => {
                    let child = frappe.model.add_child(sales_invoice, 'taxes');
                    Object.assign(child, {
                        charge_type: tax.charge_type,
                        account_head: tax.account_head,
                        description: tax.description,
                        rate: tax.rate,
                        tax_amount: tax.tax_amount,
                        total: tax.total,
                        cost_center: tax.cost_center,
                        included_in_print_rate: tax.included_in_print_rate
                    });
                });
            }
            
            // Add sales team
            if (frm.doc.sales_team && frm.doc.sales_team.length > 0) {
                frm.doc.sales_team.forEach(team => {
                    let child = frappe.model.add_child(sales_invoice, 'sales_team');
                    Object.assign(child, {
                        sales_person: team.sales_person,
                        contact_no: team.contact_no || "",
                        allocated_percentage: team.allocated_percentage || 0,
                        allocated_amount: team.allocated_amount || 0,
                        commission_rate: team.commission_rate || 0,
                        incentives: team.incentives || 0
                    });
                });
            }

            // Save the document
            frappe.call({
                method: 'frappe.client.save',
                args: {
                    doc: sales_invoice
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('Sales Invoice {0} created successfully', [r.message.name]),
                            indicator: 'green'
                        });
                        
                        // Open in new tab
                        const url = `/app/sales-invoice/${r.message.name}`;
                        window.open(url, '_blank');
                        
                        frm.reload_doc();
                    } else {
                        frappe.msgprint({
                            title: __('Error'),
                            message: __('Failed to create Sales Invoice'),
                            indicator: 'red'
                        });
                    }
                },
                error: function(err) {
                    frappe.msgprint({
                        title: __('Error'),
                        message: __('Error creating Sales Invoice: {0}', [err.message]),
                        indicator: 'red'
                    });
                    console.error('Error:', err);
                }
            });
            
        } catch (error) {
            frappe.msgprint({
                title: __('Error'),
                message: __('Error preparing Sales Invoice: {0}', [error.message]),
                indicator: 'red'
            });
            console.error('Error:', error);
        }
    });
}