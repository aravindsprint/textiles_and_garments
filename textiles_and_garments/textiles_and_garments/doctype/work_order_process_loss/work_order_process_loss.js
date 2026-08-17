// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Order Process Loss', {
    refresh: function(frm) {
        // Add custom styling or buttons if needed
    },
    
    calculate_process_loss: function(frm) {
        // Validate work orders exist
        if (!frm.doc.work_orders || frm.doc.work_orders.length === 0) {
            frappe.msgprint({
                title: __('Validation Error'),
                indicator: 'red',
                message: __('Please add Work Orders first')
            });
            return;
        }
        
        // Call the backend method
        frappe.call({
            method: 'textiles_and_garments.textiles_and_garments.doctype.work_order_process_loss.work_order_process_loss.calculate_process_loss',
            args: {
                doc: frm.doc
            },
            freeze: true,
            freeze_message: __('Fetching Stock Entry Data...'),
            callback: function(r) {
                if (r.message) {
                    // Clear existing tables
                    frm.clear_table('work_order_sent_details');
                    frm.clear_table('work_order_return_details');
                    frm.clear_table('work_order_received_details');
                    
                    // Populate Sent Details
                    if (r.message.work_order_sent_details && r.message.work_order_sent_details.length > 0) {
                        r.message.work_order_sent_details.forEach(function(row) {
                            let child = frm.add_child('work_order_sent_details');
                            Object.assign(child, row);
                        });
                        console.log('Sent Details:', r.message.work_order_sent_details.length, 'items');
                    }
                    
                    // Populate Return Details
                    if (r.message.work_order_return_details && r.message.work_order_return_details.length > 0) {
                        r.message.work_order_return_details.forEach(function(row) {
                            let child = frm.add_child('work_order_return_details');
                            Object.assign(child, row);
                        });
                        console.log('Return Details:', r.message.work_order_return_details.length, 'items');
                    }
                    
                    // Populate Received Details
                    if (r.message.work_order_received_details && r.message.work_order_received_details.length > 0) {
                        r.message.work_order_received_details.forEach(function(row) {
                            let child = frm.add_child('work_order_received_details');
                            Object.assign(child, row);
                        });
                        console.log('Received Details:', r.message.work_order_received_details.length, 'items');
                    }
                    
                    // Refresh all fields
                    frm.refresh_fields();
                    
                    // Show success message with details
                    let message = __('Process Loss data calculated successfully');
                    if (r.message.work_order_sent_details) {
                        message += '<br>' + __('Sent Items: {0}', [r.message.work_order_sent_details.length]);
                    }
                    if (r.message.work_order_return_details) {
                        message += '<br>' + __('Return Items: {0}', [r.message.work_order_return_details.length]);
                    }
                    if (r.message.work_order_received_details) {
                        message += '<br>' + __('Received Items: {0}', [r.message.work_order_received_details.length]);
                    }
                    
                    frappe.msgprint({
                        title: __('Success'),
                        indicator: 'green',
                        message: message
                    });
                }
            },
            error: function(r) {
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Failed to calculate process loss. Please check the console for details.')
                });
                console.error('Error:', r);
            }
        });
    },
    
    calculate_summary: function(frm) {
        // Validate work orders exist
        if (!frm.doc.work_orders || frm.doc.work_orders.length === 0) {
            frappe.msgprint({
                title: __('Validation Error'),
                indicator: 'red',
                message: __('Please add Work Orders first')
            });
            return;
        }
        
        // Validate that process loss has been calculated
        if ((!frm.doc.work_order_sent_details || frm.doc.work_order_sent_details.length === 0) &&
            (!frm.doc.work_order_received_details || frm.doc.work_order_received_details.length === 0)) {
            frappe.msgprint({
                title: __('Calculate Process Loss First'),
                indicator: 'orange',
                message: __('Please calculate process loss first by clicking "Calculate Process Loss" button')
            });
            return;
        }
        
        // Call the backend method
        frappe.call({
            method: 'textiles_and_garments.textiles_and_garments.doctype.work_order_process_loss.work_order_process_loss.calculate_summary',
            args: {
                doc: frm.doc
            },
            freeze: true,
            freeze_message: __('Calculating Process Loss Summary...'),
            callback: function(r) {
                if (r.message) {
                    // Clear existing summary table
                    frm.clear_table('work_order_process_loss_details');
                    
                    // Populate Summary Details
                    if (r.message.work_order_process_loss_details && r.message.work_order_process_loss_details.length > 0) {
                        r.message.work_order_process_loss_details.forEach(function(row) {
                            let child = frm.add_child('work_order_process_loss_details');
                            Object.assign(child, row);
                        });
                        
                        console.log('Process Loss Summary:', r.message.work_order_process_loss_details);
                    }
                    
                    // Refresh fields
                    frm.refresh_fields();
                    
                    // Calculate totals for display
                    let total_sent = 0;
                    let total_return = 0;
                    let total_received = 0;
                    let total_loss = 0;
                    
                    frm.doc.work_order_process_loss_details.forEach(function(row) {
                        total_sent += flt(row.sent_qty);
                        total_return += flt(row.return_qty);
                        total_received += flt(row.received_qty);
                        total_loss += flt(row.process_loss_qty);
                    });
                    
                    let avg_loss_pct = 0;
                    if (total_sent - total_return > 0) {
                        avg_loss_pct = (total_loss / (total_sent - total_return) * 100).toFixed(2);
                    }
                    
                    // Show success message with summary
                    frappe.msgprint({
                        title: __('Summary Calculated Successfully'),
                        indicator: 'green',
                        message: `
                            <div style="margin-top: 10px;">
                                <strong>${__('Summary Statistics:')}</strong><br>
                                ${__('Items Processed')}: ${frm.doc.work_order_process_loss_details.length}<br>
                                ${__('Total Sent')}: ${total_sent.toFixed(2)}<br>
                                ${__('Total Return')}: ${total_return.toFixed(2)}<br>
                                ${__('Total Received')}: ${total_received.toFixed(2)}<br>
                                ${__('Total Process Loss')}: ${total_loss.toFixed(2)}<br>
                                ${__('Average Loss %')}: ${avg_loss_pct}%
                            </div>
                        `
                    });
                }
            },
            error: function(r) {
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Failed to calculate summary. Please check the console for details.')
                });
                console.error('Error:', r);
            }
        });
    }
});

// Optional: Add validation or formatting to child table fields
frappe.ui.form.on('Work Order Process loss Details', {
    process_loss_percentage: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        // Format percentage to 2 decimal places
        if (row.process_loss_percentage) {
            row.process_loss_percentage = flt(row.process_loss_percentage, 2);
            frm.refresh_field('work_order_process_loss_details');
        }
    },
    
    process_loss_qty: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        // Highlight negative process loss (more received than sent)
        if (flt(row.process_loss_qty) < 0) {
            frappe.show_alert({
                message: __('Negative process loss detected for {0}', [row.item_code]),
                indicator: 'orange'
            });
        }
    }
});