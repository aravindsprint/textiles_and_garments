frappe.ui.form.on('Material Request', {
    refresh: function(frm) {
        console.log("frm", frm);
        if (frm.doc.docstatus === 1 && frm.doc.material_request_type === "Manufacture") {
            // Add button to view created Work Orders
            frm.add_custom_button(__('View Work Orders'), function() {
                frappe.route_options = {
                    "material_request": frm.doc.name
                };
                frappe.set_route("List", "Work Order");
            });
        }
        
        // Add button to fetch BOM items
        if (frm.doc.docstatus === 0 && frm.doc.material_request_type === "Manufacture") {
            frm.add_custom_button(__('Auto-fill BOMs'), function() {
                auto_fill_boms(frm);
            });
            
            frm.add_custom_button(__('Fetch BOM Raw Materials'), function() {
                fetch_bom_raw_materials(frm);
            }, __('Actions'));
        }
        
        // Set batch query filter
        frm.set_query("batch", "custom_material_request_rm_items", function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.item_code) {
                return {
                    filters: {
                        'item': row.item_code,
                        'disabled': 0
                    }
                };
            } else {
                return {
                    filters: {
                        'item': ['=', '']
                    }
                };
            }
        });
    },
    
    before_save: function(frm) {
        // Auto-fetch BOM raw materials before saving
        if (frm.doc.material_request_type === "Manufacture") {
            // Use return to prevent saving until fetch completes
            return fetch_bom_raw_materials(frm);
        }
    },
    
    before_submit: function(frm) {
        if (frm.doc.material_request_type === "Manufacture") {
            let items_without_bom = [];
            
            frm.doc.items.forEach(function(item) {
                if (!item.bom_no) {
                    items_without_bom.push(`Row ${item.idx}: ${item.item_code}`);
                }
            });
            
            if (items_without_bom.length > 0) {
                frappe.msgprint({
                    title: __('Missing BOM'),
                    indicator: 'red',
                    message: __('The following items do not have a BOM assigned:') + 
                             '<br><br>' + items_without_bom.join('<br>') +
                             '<br><br>' + __('Please assign a BOM to these items before submitting.')
                });
                frappe.validated = false;
            }
        }
    }
});

// Fetch BOM raw materials and populate custom table
function fetch_bom_raw_materials(frm) {
    console.log("Starting fetch_bom_raw_materials");
    
    if (!frm.doc.items || frm.doc.items.length === 0) {
        frappe.msgprint(__('No items found in Material Request'));
        return Promise.resolve();
    }
    
    // Clear existing custom table data
    frm.doc.custom_material_request_rm_items = [];
    frm.refresh_field('custom_material_request_rm_items');
    
    let promises = [];
    let total_items_processed = 0;
    
    frm.doc.items.forEach(function(item) {
        if (item.bom_no) {
            console.log("Fetching BOM:", item.bom_no);
            
            // Fetch BOM items for each item with BOM
            let promise = frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'BOM',
                    name: item.bom_no
                }
            }).then(r => {
                console.log("BOM Response:", r);
                
                if (r.message && r.message.items) {
                    console.log("BOM Items found:", r.message.items.length);
                    
                    // Add each BOM item to custom table
                    r.message.items.forEach(function(bom_item) {
                        console.log("Adding BOM item:", bom_item.item_code);
                        
                        // Calculate required qty based on Material Request qty
                        let required_qty = (bom_item.qty / r.message.quantity) * item.qty;
                        
                        let child_row = {
                            'item_code': bom_item.item_code,
                            'item_name': bom_item.item_name,
                            'qty': required_qty,
                            'stock_uom': bom_item.stock_uom
                        };
                        
                        console.log("Child row data:", child_row);
                        
                        // Add to the array directly
                        frm.doc.custom_material_request_rm_items.push(child_row);
                        
                        total_items_processed++;
                    });
                }
            }).catch(err => {
                console.error("Error fetching BOM:", err);
            });
            
            promises.push(promise);
        }
    });
    
    return Promise.all(promises).then(() => {
        console.log("All BOMs fetched. Total items:", total_items_processed);
        console.log("Final table data:", frm.doc.custom_material_request_rm_items);
        
        frm.refresh_field('custom_material_request_rm_items');
        
        if (total_items_processed > 0) {
            frappe.show_alert({
                message: __('Fetched {0} raw material item(s) from BOM', [total_items_processed]),
                indicator: 'green'
            });
        } else {
            frappe.msgprint(__('No BOM items found'));
        }
    }).catch(err => {
        console.error("Error in fetch_bom_raw_materials:", err);
        frappe.msgprint({
            title: __('Error'),
            indicator: 'red',
            message: __('Failed to fetch BOM items: {0}', [err.message || err])
        });
    });
}

// Auto-fill BOMs from Item master default BOM
function auto_fill_boms(frm) {
    let items_updated = 0;
    let promises = [];
    
    frm.doc.items.forEach(function(item) {
        if (!item.bom_no) {
            let promise = frappe.db.get_value('Item', item.item_code, 'default_bom')
                .then(r => {
                    if (r.message && r.message.default_bom) {
                        frappe.model.set_value(item.doctype, item.name, 'bom_no', r.message.default_bom);
                        items_updated++;
                    }
                });
            promises.push(promise);
        }
    });
    
    Promise.all(promises).then(() => {
        if (items_updated > 0) {
            frappe.msgprint(__('Updated {0} item(s) with default BOM', [items_updated]));
            frm.refresh_field('items');
            // Auto-fetch BOM materials after filling BOMs
            setTimeout(() => {
                fetch_bom_raw_materials(frm);
            }, 500);
        } else {
            frappe.msgprint(__('No default BOMs found for items without BOM'));
        }
    });
}

// Validate BOM when item is selected
frappe.ui.form.on('Material Request Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (frm.doc.material_request_type === "Manufacture" && row.item_code) {
            // Auto-fetch default BOM
            frappe.db.get_value('Item', row.item_code, 'default_bom')
                .then(r => {
                    if (r.message && r.message.default_bom) {
                        frappe.model.set_value(cdt, cdn, 'bom_no', r.message.default_bom);
                    } else {
                        frappe.msgprint({
                            message: __('Item {0} does not have a default BOM. Please select a BOM manually.', [row.item_code]),
                            indicator: 'orange'
                        });
                    }
                });
        }
    },
    
    bom_no: function(frm, cdt, cdn) {
        // Refresh BOM materials when BOM is changed
        if (frm.doc.material_request_type === "Manufacture") {
            setTimeout(() => {
                fetch_bom_raw_materials(frm);
            }, 300);
        }
    },
    
    qty: function(frm, cdt, cdn) {
        // Recalculate when qty changes
        if (frm.doc.material_request_type === "Manufacture") {
            setTimeout(() => {
                fetch_bom_raw_materials(frm);
            }, 300);
        }
    }
});

// Filter batches based on item in custom_material_request_rm_items table
frappe.ui.form.on('Material Request RM Items', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        // Clear batch when item changes
        frappe.model.set_value(cdt, cdn, 'batch', '');
        
        // Refresh the form to apply the batch filter
        frm.refresh_field('custom_material_request_rm_items');
    }
});