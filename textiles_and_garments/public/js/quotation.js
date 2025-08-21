frappe.ui.form.on('Quotation', {
    refresh(frm) {
        frm.add_custom_button('Create Sales Invoice', () => {
            console.log("Create Sales Invoice is clicked");
            create_sales_invoice_doc(frm);
        });
    }
});

function create_sales_invoice_doc(frm) {
    // Create a deep copy of the items to avoid modifying the original frm.doc.items directly
    // and ensure 'use_serial_batch_fields' is set for each item.
    const salesInvoiceItems = frm.doc.items.map(item => {
    	console.log("item",item);
        return {
            ...item, // Copy all existing properties from the original item
            use_serial_batch_fields: 1,// Set 'use_serial_batch_fields' to 1
            batch_no: item.batch
        };
    });

    frappe.call({
        method: "frappe.client.insert",
        args: {
            doc: {
                doctype: "Sales Invoice",
                items: salesInvoiceItems, // Use the modified items array
                posting_date: frappe.datetime.now_date(),
                due_date: frappe.datetime.now_date(),
                customer: frm.doc.party_name,
                purchase_by: "-",
                purchaser_mobile_no: "-",
                vehicle_no: "-",
                distance: 0,
                company_address: "Pranera Tirupur",
                stock_entry: frm.doc.stock_entry,
                update_stock: 1,
                // fg_warehouse: "DYE/LOT SECTION - PSS" // Uncomment if needed
            }
        },
        callback: function (r) {
            if (r.message) {
                // Open the Sales Invoice in a new tab
                const url = `/app/sales-invoice/${r.message.name}`;
                window.open(url, '_blank');

                // Optional: show a success message with clickable link
                let link = `<a href="${url}" target="_blank">${r.message.name}</a>`;
                frappe.msgprint({
                    title: __("Sales Invoice Created"),
                    message: __("Sales Invoice document {0} created successfully.", [link]),
                    indicator: "green"
                });
            } else if (r.exc) {
                // Handle server-side errors
                frappe.msgprint({
                    title: __("Error"),
                    message: __("Failed to create Sales Invoice: {0}", [r.exc]),
                    indicator: "red"
                });
                console.error("Error creating Sales Invoice:", r.exc);
            }
        },
        error: function(err) {
            // Handle client-side network or other errors
            frappe.msgprint({
                title: __("Error"),
                message: __("An error occurred while calling the server: {0}", [err.message]),
                indicator: "red"
            });
            console.error("Client-side error:", err);
        }
    });
}