frappe.ui.form.on('Subcontracting Order', {
    refresh(frm) {
        console.log("Subcontracting", frm);

        // Add custom button only for submitted Subcontracting Orders that aren't cancelled
        if (frm.doc.docstatus === 1) {
            // Check if there are linked plans
            let has_linked_plans = false;
            if (frm.doc.items) {
                frm.doc.items.forEach(item => {
                    if (item.custom_plans) {
                        has_linked_plans = true;
                    }
                });
            }
            
            if (has_linked_plans) {
                frm.add_custom_button(__('🔗 Remove Links & Cancel'), function() {
                    remove_links_and_cancel_sco(frm);
                }).addClass('btn-warning');
            }
            
            // Also keep the regular cancel button
            frm.add_custom_button(__('Cancel'), function() {
                frm.cancel();
            });
        }


        if (frm.doc.purchase_order) {
            frappe.model.with_doc("Purchase Order", frm.doc.purchase_order, function() {
                let po_doc = frappe.model.get_doc("Purchase Order", frm.doc.purchase_order);
                let po_items = po_doc.items || [];
                let so_items = frm.doc.items || [];

                console.log("po_items", po_items);
                console.log("so_items", so_items);

                so_items.forEach(so_row => {
                    let matching_po_item = po_items.find(po_row => po_row.name === so_row.purchase_order_item);
                    if (matching_po_item) {
                        so_row.custom_plans = matching_po_item.custom_plans;
                    }
                });

                frm.refresh_field("items");
            });
        }
    }
});

function remove_links_and_cancel_sco(frm) {
    // Get linked plans for confirmation message
    let linked_plans = [];
    frm.doc.items.forEach(item => {
        if (item.custom_plans && !linked_plans.includes(item.custom_plans)) {
            linked_plans.push(item.custom_plans);
        }
    });
    
    let confirm_message = `This Subcontracting Order is linked to ${linked_plans.length} plan(s):<br><br>`;
    linked_plans.forEach(plan => {
        confirm_message += `• ${plan}<br>`;
    });
    confirm_message += `<br>All milestone links will be removed before cancellation. Continue?`;
    
    frappe.confirm(
        confirm_message,
        function() {
            frappe.call({
                method: 'textiles_and_garments.time_and_action_milestones.remove_sco_links_before_cancel',
                args: {
                    sco_name: frm.doc.name,
                    plan_names: linked_plans
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.msgprint({
                            title: __('Success'),
                            indicator: 'green',
                            message: __('Removed links from {0} plan(s). Cancelling Subcontracting Order...', [linked_plans.length])
                        });
                        
                        // Cancel the Subcontracting Order after a brief delay to show the message
                        setTimeout(() => {
                            frm.cancel();
                        }, 1500);
                    } else {
                        frappe.msgprint({
                            title: __('Error'),
                            indicator: 'red',
                            message: __('Failed to remove links: {0}', [r.message.error || 'Unknown error'])
                        });
                    }
                }
            });
        }
    );
}


