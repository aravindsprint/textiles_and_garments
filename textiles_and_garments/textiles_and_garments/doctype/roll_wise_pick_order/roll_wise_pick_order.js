// Copyright (c) 2025, Your Company and contributors
// For license information, please see license.txt

frappe.ui.form.on('Roll Wise Pick Order', {
    onload: function(frm) {
        // Set default company
        if (!frm.doc.company) {
            frm.set_value('company', frappe.defaults.get_user_default('Company'));
        }
        
        // Set default posting date
        if (!frm.doc.posting_date) {
            frm.set_value('posting_date', frappe.datetime.get_today());
        }
    },
    
    refresh: function(frm) {
        // Set field indicators
        set_field_indicators(frm);
        
        // Add custom buttons based on status
        add_custom_buttons(frm);
        
        // Set filters
        set_filters(frm);
        
        // Update button visibility
        update_button_visibility(frm);
    },
    
    pick_type: function(frm) {
        // Clear dependent fields when pick_type changes
        frm.set_value('document_name', '');
        frm.set_value('project', '');
        frm.set_value('source_warehouse', '');
        frm.set_value('target_warehouse', '');
        frm.set_value('batch', '');
        
        // Clear child tables
        frm.clear_table('required_items');
        frm.clear_table('roll_wise_pick_item');
        frm.clear_table('batch_wise_pick_item');
        frm.refresh_fields();
        
        // Set appropriate filters and field properties
        set_document_filters(frm);
        toggle_field_visibility(frm);
    },
    
    document_name: function(frm) {
        if (frm.doc.document_name && frm.doc.document_type) {
            // Trigger server-side validate to fetch required items
            frm.save().then(() => {
                frm.refresh_field('required_items');
                frappe.show_alert({
                    message: __('Required items loaded successfully'),
                    indicator: 'green'
                }, 3);
            });
        }
    },
    
    batch: function(frm) {
        if (frm.doc.batch) {
            // Set filter for rolls based on batch
            set_roll_batch_filter(frm);
            
            frappe.show_alert({
                message: __('Roll selection filtered by batch: {0}', [frm.doc.batch]),
                indicator: 'blue'
            }, 3);
        }
    },
    
    source_warehouse: function(frm) {
        // Filter rolls by source warehouse
        if (frm.doc.source_warehouse) {
            frm.fields_dict['roll_wise_pick_item'].grid.get_field('roll_no').get_query = function(doc, cdt, cdn) {
                return {
                    filters: {
                        'warehouse': frm.doc.source_warehouse
                    }
                };
            };
        }
    },
    
    validate: function(frm) {
        // Client-side validations
        
        // Check if rolls or batches are added
        if (!frm.doc.roll_wise_pick_item || frm.doc.roll_wise_pick_item.length === 0) {
            if (!frm.doc.batch_wise_pick_item || frm.doc.batch_wise_pick_item.length === 0) {
                frappe.msgprint(__('Please add at least one roll or batch'));
                frappe.validated = false;
                return false;
            }
        }
        
        // Validate warehouses
        if (!frm.doc.source_warehouse || !frm.doc.target_warehouse) {
            frappe.msgprint(__('Please select both Source and Target Warehouse'));
            frappe.validated = false;
            return false;
        }
        
        // Check if source and target warehouses are different
        if (frm.doc.source_warehouse === frm.doc.target_warehouse) {
            frappe.msgprint(__('Source and Target Warehouse cannot be the same'));
            frappe.validated = false;
            return false;
        }
    },
    
    before_submit: function(frm) {
        // Check for over-picking
        let over_picked = false;
        
        frm.doc.required_items.forEach(item => {
            if (item.remaining_qty < 0) {
                frappe.msgprint({
                    title: __('Over Picking Alert'),
                    message: __('Item {0} is over-picked by {1} {2}', 
                        [item.item_code, Math.abs(item.remaining_qty), item.stock_uom]),
                    indicator: 'orange'
                });
                over_picked = true;
            }
        });
        
        if (over_picked) {
            return new Promise((resolve, reject) => {
                frappe.confirm(
                    __('Some items are over-picked. Do you want to continue?'),
                    () => resolve(),
                    () => reject()
                );
            });
        }
    }
});

// ==================== CHILD TABLE: Roll Wise Pick Item ====================
frappe.ui.form.on('Roll Wise Pick Item', {
    roll_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.roll_no) {
            // Fetch roll details
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Roll',
                    name: row.roll_no
                },
                callback: function(r) {
                    if (r.message) {
                        let roll = r.message;
                        
                        // Auto-fill fields
                        frappe.model.set_value(cdt, cdn, 'item_code', roll.item_code);
                        frappe.model.set_value(cdt, cdn, 'warehouse', roll.warehouse || frm.doc.source_warehouse);
                        frappe.model.set_value(cdt, cdn, 'batch', roll.batch);
                        frappe.model.set_value(cdt, cdn, 'qty', roll.roll_weight);
                        frappe.model.set_value(cdt, cdn, 'uom', roll.stock_uom);
                        
                        // Validate batch if parent has batch selected
                        if (frm.doc.batch && roll.batch !== frm.doc.batch) {
                            frappe.msgprint({
                                title: __('Batch Mismatch'),
                                message: __('Roll batch {0} does not match selected batch {1}', 
                                    [roll.batch, frm.doc.batch]),
                                indicator: 'orange'
                            });
                        }
                        
                        frm.refresh_field('roll_wise_pick_item');
                    }
                }
            });
        }
    },
    
    roll_wise_pick_item_remove: function(frm, cdt, cdn) {
        // Recalculate totals when row is removed
        frm.trigger('calculate_totals');
    },
    
    qty: function(frm, cdt, cdn) {
        frm.trigger('calculate_totals');
    }
});

// ==================== CHILD TABLE: Batch Wise Pick Item ====================
frappe.ui.form.on('Batch Wise Pick Item', {
    batch: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.batch) {
            // Fetch batch details
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Batch',
                    name: row.batch
                },
                callback: function(r) {
                    if (r.message) {
                        let batch = r.message;
                        
                        // Auto-fill item code
                        frappe.model.set_value(cdt, cdn, 'item_code', batch.item);
                        frappe.model.set_value(cdt, cdn, 'warehouse', frm.doc.source_warehouse);
                        
                        frm.refresh_field('batch_wise_pick_item');
                    }
                }
            });
        }
    },
    
    batch_wise_pick_item_remove: function(frm, cdt, cdn) {
        frm.trigger('calculate_totals');
    },
    
    qty: function(frm, cdt, cdn) {
        frm.trigger('calculate_totals');
    }
});

// ==================== HELPER FUNCTIONS ====================

function set_field_indicators(frm) {
    // Set color indicators for required items table
    if (frm.doc.required_items) {
        frm.doc.required_items.forEach(item => {
            let row = frm.fields_dict['required_items'].grid.grid_rows_by_docname[item.name];
            if (row) {
                if (item.remaining_qty === 0) {
                    row.doc.__color = 'green'; // Complete
                } else if (item.remaining_qty < 0) {
                    row.doc.__color = 'red'; // Over-picked
                } else if (item.picked_qty > 0) {
                    row.doc.__color = 'orange'; // Partially picked
                }
            }
        });
        frm.refresh_field('required_items');
    }
}

function add_custom_buttons(frm) {
    // Clear existing custom buttons
    frm.clear_custom_buttons();
    
    if (frm.doc.docstatus === 1) {
        // Submitted document buttons
        
        if (frm.doc.status === 'Pending') {
            frm.add_custom_button(__('Start Picking'), function() {
                frappe.call({
                    method: 'frappe.client.set_value',
                    args: {
                        doctype: 'Roll Wise Pick Order',
                        name: frm.doc.name,
                        fieldname: 'status',
                        value: 'In Progress'
                    },
                    callback: function(r) {
                        frm.reload_doc();
                        frappe.show_alert({
                            message: __('Picking started'),
                            indicator: 'green'
                        }, 3);
                    }
                });
            }).addClass('btn-primary');
        }
        
        if (frm.doc.status === 'In Progress') {
            frm.add_custom_button(__('Complete Picking'), function() {
                complete_picking(frm);
            }).addClass('btn-success');
            
            frm.add_custom_button(__('Pause Picking'), function() {
                frappe.call({
                    method: 'frappe.client.set_value',
                    args: {
                        doctype: 'Roll Wise Pick Order',
                        name: frm.doc.name,
                        fieldname: 'status',
                        value: 'Pending'
                    },
                    callback: function(r) {
                        frm.reload_doc();
                        frappe.show_alert({
                            message: __('Picking paused'),
                            indicator: 'orange'
                        }, 3);
                    }
                });
            });
        }
        
        if (frm.doc.status === 'Completed') {
            frm.add_custom_button(__('View Stock Entry'), function() {
                // Find related stock entry
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Stock Entry',
                        filters: {
                            'custom_roll_pick_order': frm.doc.name
                        },
                        fields: ['name'],
                        limit: 1
                    },
                    callback: function(r) {
                        if (r.message && r.message.length > 0) {
                            frappe.set_route('Form', 'Stock Entry', r.message[0].name);
                        } else {
                            frappe.msgprint(__('No Stock Entry found'));
                        }
                    }
                });
            });
        }
        
        // Add "Create Stock Entry" button for completed picks
        if (frm.doc.status === 'In Progress' || frm.doc.status === 'Pending') {
            frm.add_custom_button(__('Create Stock Entry'), function() {
                create_stock_entry(frm);
            }, __('Create'));
        }
        
        // Add "Print Pick List" button
        frm.add_custom_button(__('Print Pick List'), function() {
            frappe.set_route('print', frm.doc.doctype, frm.doc.name, 'Standard');
        }, __('Print'));
    }
    
    // Draft document buttons
    if (frm.doc.docstatus === 0) {
        // Add "Scan Roll" button for mobile integration
        frm.add_custom_button(__('Scan Roll (Mobile)'), function() {
            scan_roll_dialog(frm);
        }, __('Actions'));
        
        // Add "Load from Batch" button
        if (frm.doc.batch) {
            frm.add_custom_button(__('Load All Rolls from Batch'), function() {
                load_rolls_from_batch(frm);
            }, __('Actions'));
        }
    }
}

function set_filters(frm) {
    // Set query filters for various fields
    
    // Warehouse filters
    frm.set_query('source_warehouse', function() {
        return {
            filters: {
                'company': frm.doc.company,
                'is_group': 0
            }
        };
    });
    
    frm.set_query('target_warehouse', function() {
        return {
            filters: {
                'company': frm.doc.company,
                'is_group': 0
            }
        };
    });
    
    // Batch filter
    frm.set_query('batch', function() {
        let filters = {};
        
        if (frm.doc.project) {
            filters['custom_project'] = frm.doc.project;
        }
        
        return { filters: filters };
    });
}

function set_document_filters(frm) {
    if (!frm.doc.pick_type) return;
    
    // Set document_name filters based on pick_type
    if (frm.doc.pick_type === 'From Work Order' || frm.doc.pick_type === 'To Work Order') {
        frm.set_query('document_name', function() {
            return {
                filters: {
                    'docstatus': 1,
                    'status': ['not in', ['Completed', 'Stopped', 'Cancelled']],
                    'company': frm.doc.company
                }
            };
        });
        
        // Filter for from_work_order
        frm.set_query('from_work_order', function() {
            return {
                filters: {
                    'docstatus': 1,
                    'status': ['not in', ['Completed', 'Stopped', 'Cancelled']],
                    'company': frm.doc.company
                }
            };
        });
    }
    
    if (frm.doc.pick_type === 'From Purchase Order') {
        frm.set_query('document_name', function() {
            return {
                filters: {
                    'docstatus': 1,
                    'status': ['not in', ['Completed', 'Closed', 'Cancelled']],
                    'company': frm.doc.company
                }
            };
        });
    }
    
    if (frm.doc.pick_type === 'To Subcontracting Order' || frm.doc.pick_type === 'From Subcontracting Order') {
        frm.set_query('document_name', function() {
            return {
                filters: {
                    'docstatus': 1,
                    'status': ['not in', ['Completed', 'Closed', 'Cancelled']],
                    'company': frm.doc.company
                }
            };
        });
        
        // Filter for from_subcontracting_order
        frm.set_query('from_subcontracting_order', function() {
            return {
                filters: {
                    'docstatus': 1,
                    'status': ['not in', ['Completed', 'Closed', 'Cancelled']],
                    'company': frm.doc.company
                }
            };
        });
    }
    
    if (frm.doc.pick_type === 'From Stock Entry') {
        frm.set_query('document_name', function() {
            return {
                filters: {
                    'docstatus': 1,
                    'company': frm.doc.company
                }
            };
        });
    }
}

function toggle_field_visibility(frm) {
    // Show/hide fields based on pick_type
    const hide_document_fields = ['Manual Roll Pick', 'From Batch'];
    
    if (hide_document_fields.includes(frm.doc.pick_type)) {
        frm.set_df_property('document_type', 'hidden', 1);
        frm.set_df_property('document_name', 'hidden', 1);
        frm.set_df_property('from_work_order', 'hidden', 1);
        frm.set_df_property('from_subcontracting_order', 'hidden', 1);
    } else {
        frm.set_df_property('document_type', 'hidden', 0);
        frm.set_df_property('document_name', 'hidden', 0);
    }
    
    // Show/hide from_work_order and from_subcontracting_order
    if (frm.doc.pick_type === 'To Subcontracting Order') {
        frm.set_df_property('from_work_order', 'hidden', 0);
        frm.set_df_property('from_subcontracting_order', 'hidden', 0);
    } else {
        frm.set_df_property('from_work_order', 'hidden', 1);
        frm.set_df_property('from_subcontracting_order', 'hidden', 1);
    }
}

function set_roll_batch_filter(frm) {
    if (frm.doc.batch) {
        frm.fields_dict['roll_wise_pick_item'].grid.get_field('roll_no').get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    'batch': frm.doc.batch,
                    'warehouse': frm.doc.source_warehouse || ['!=', '']
                }
            };
        };
    }
}

function update_button_visibility(frm) {
    // Update form layout based on status
    if (frm.doc.docstatus === 1) {
        frm.set_df_property('roll_wise_pick_item', 'read_only', 1);
        frm.set_df_property('batch_wise_pick_item', 'read_only', 1);
        frm.set_df_property('required_items', 'read_only', 1);
    }
}

function complete_picking(frm) {
    frappe.confirm(
        __('Are you sure you want to mark this picking as completed? This will create a Stock Entry.'),
        function() {
            frappe.call({
                method: 'your_app.api.complete_roll_picking',
                args: {
                    'pick_order': frm.doc.name
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frm.reload_doc();
                        frappe.msgprint({
                            title: __('Success'),
                            message: __('Stock Entry created: {0}', [r.message.stock_entry]),
                            indicator: 'green'
                        });
                    } else {
                        frappe.msgprint({
                            title: __('Error'),
                            message: r.message.message || __('Failed to complete picking'),
                            indicator: 'red'
                        });
                    }
                }
            });
        }
    );
}

function create_stock_entry(frm) {
    frappe.call({
        method: 'your_app.api.create_stock_entry_from_pick_order',
        args: {
            'pick_order': frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.msgprint({
                    title: __('Success'),
                    message: __('Stock Entry created: {0}', [r.message.stock_entry]),
                    indicator: 'green'
                });
                
                // Ask if user wants to open the Stock Entry
                frappe.confirm(
                    __('Do you want to open the Stock Entry?'),
                    function() {
                        frappe.set_route('Form', 'Stock Entry', r.message.stock_entry);
                    }
                );
            } else {
                frappe.msgprint({
                    title: __('Error'),
                    message: r.message.message || __('Failed to create Stock Entry'),
                    indicator: 'red'
                });
            }
        }
    });
}

function scan_roll_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Scan Roll Number'),
        fields: [
            {
                label: __('Roll Number'),
                fieldname: 'roll_no',
                fieldtype: 'Link',
                options: 'Roll',
                reqd: 1,
                get_query: function() {
                    let filters = {
                        'warehouse': frm.doc.source_warehouse || ['!=', '']
                    };
                    
                    if (frm.doc.batch) {
                        filters['batch'] = frm.doc.batch;
                    }
                    
                    return { filters: filters };
                }
            }
        ],
        primary_action_label: __('Add Roll'),
        primary_action(values) {
            // Check if roll already exists
            let exists = frm.doc.roll_wise_pick_item.some(item => item.roll_no === values.roll_no);
            
            if (exists) {
                frappe.msgprint(__('Roll {0} is already added', [values.roll_no]));
                return;
            }
            
            // Add roll to child table
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Roll',
                    name: values.roll_no
                },
                callback: function(r) {
                    if (r.message) {
                        let roll = r.message;
                        let child = frm.add_child('roll_wise_pick_item');
                        child.roll_no = roll.name;
                        child.item_code = roll.item_code;
                        child.warehouse = roll.warehouse || frm.doc.source_warehouse;
                        child.batch = roll.batch;
                        child.qty = roll.roll_weight;
                        child.uom = roll.stock_uom;
                        
                        frm.refresh_field('roll_wise_pick_item');
                        
                        frappe.show_alert({
                            message: __('Roll {0} added successfully', [roll.name]),
                            indicator: 'green'
                        }, 3);
                        
                        d.hide();
                    }
                }
            });
        }
    });
    
    d.show();
}

function load_rolls_from_batch(frm) {
    if (!frm.doc.batch) {
        frappe.msgprint(__('Please select a batch first'));
        return;
    }
    
    frappe.confirm(
        __('This will load all available rolls from batch {0}. Continue?', [frm.doc.batch]),
        function() {
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Roll',
                    filters: {
                        'batch': frm.doc.batch,
                        'warehouse': frm.doc.source_warehouse || ['!=', '']
                    },
                    fields: ['name', 'item_code', 'warehouse', 'batch', 'roll_weight', 'stock_uom']
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let added = 0;
                        
                        r.message.forEach(roll => {
                            // Check if already exists
                            let exists = frm.doc.roll_wise_pick_item.some(item => item.roll_no === roll.name);
                            
                            if (!exists) {
                                let child = frm.add_child('roll_wise_pick_item');
                                child.roll_no = roll.name;
                                child.item_code = roll.item_code;
                                child.warehouse = roll.warehouse;
                                child.batch = roll.batch;
                                child.qty = roll.roll_weight;
                                child.uom = roll.stock_uom;
                                added++;
                            }
                        });
                        
                        frm.refresh_field('roll_wise_pick_item');
                        
                        frappe.msgprint({
                            title: __('Success'),
                            message: __('Added {0} roll(s) from batch {1}', [added, frm.doc.batch]),
                            indicator: 'green'
                        });
                    } else {
                        frappe.msgprint(__('No rolls found for batch {0}', [frm.doc.batch]));
                    }
                }
            });
        }
    );
}