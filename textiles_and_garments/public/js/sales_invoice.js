frappe.ui.form.on("Sales Invoice", {
    refresh:function(frm){
        console.log("inside public sales invoice", frm);    
     

    },

    after_save:function(frm){
        if(
            frm.doc.custom_loading_and_unloading_greige_lot == 1||
            frm.doc.custom_loading_and_unloading_finished_lot == 1||
            frm.doc.custom_loading_and_unloading_wet_lot == 1
           ){
            console.log("custom_include_loading_greige");
            frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.set_operation_cost_in_sales_invoice",
                args: {
                    docname: frm.doc.name,
                },
                callback: function(response) {
                    console.log("response",response);
                    if(response.message) {
                        frm.refresh_field("custom_loading_and_unloading_operations");
                        frm.reload_doc();
                          
                    }
                }
            });

        }

    // if(frm.doc.custom_include_loading_greige == 1||
    //         frm.doc.custom_loading_and_unloading_greige_lot == 1
    //         ){
    //         console.log("custom_include_loading_greige");
    //         frappe.call({
    //             method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.set_operation_cost_in_work_order",
    //             args: {
    //                 docname: frm.doc.name,
    //             },
    //             callback: function(response) {
    //                 console.log("response",response);
    //                 if(response.message) {
    //                     frm.refresh_field("custom_work_order_operations");
    //                     frm.reload_doc();
                          
    //                 }
    //             }
    //         });

    //     }

    }

    // get_work_order:function(frm){
    //     console.log("get_work_order button clicked");

    // }
});


frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        console.log("Sales Invoice Item frm",frm);
        frm.set_query('item_code', 'items', function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            console.log("row",row);
            return {
                query: 'textiles_and_garments.custom_queries.item_query_with_stock',
                filters: {
                    'is_sales_item': 1,
                    'warehouse': row.warehouse || '',
                    'company': doc.company
                }
            };
        });
    }
});




frappe.ui.form.on('Sales Invoice Item', {
    custom_view_history_btn: function(frm, cdt, cdn) {
        let item_row = frappe.get_doc(cdt, cdn);
        if (!item_row.item_code) {
            frappe.msgprint(__('Please select an item first'));
            return;
        }
        
        show_item_history(item_row.item_code, frm.doc.company);
    }
});

function show_item_history(item_code, company) {
    // Calculate 90% of screen dimensions with proper bounds
    const screenWidth = Math.min(window.innerWidth * 0.9, 1800);
    const screenHeight = Math.min(window.innerHeight * 0.9, 1000);
    
    let dialog = new frappe.ui.Dialog({
        title: __('Item History - ' + item_code),
        size: 'extra-large',
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'history_html'
            }
        ],
        primary_action_label: __('Close'),
        primary_action: function() {
            dialog.hide();
        }
    });
    
    // Override dialog dimensions for full 90% screen size
    setTimeout(() => {
        dialog.$wrapper.find('.modal-dialog').css({
            'width': screenWidth + 'px',
            'max-width': '90vw',
            'height': screenHeight + 'px',
            'max-height': '90vh'
        });
        
        dialog.$wrapper.find('.modal-content').css({
            'height': '100%'
        });
        
        dialog.$wrapper.find('.modal-body').css({
            'height': 'calc(100% - 120px)',
            'overflow': 'auto'
        });
    }, 100);
    
    dialog.fields_dict.history_html.$wrapper.html(`
        <div class="text-center" style="padding: 40px;">
            <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
                <span class="sr-only">Loading...</span>
            </div>
            <p class="mt-3">Loading purchase and sales history...</p>
        </div>
    `);
    
    dialog.show();
    
    frappe.call({
        method: 'textiles_and_garments.custom_queries.get_item_history',
        args: {
            item_code: item_code,
            company: company
        }
    }).then(r => {
        let data = r.message;
        render_history_table(dialog, data.purchase_history, data.sales_history);
    }).catch(error => {
        console.error('Error fetching history:', error);
        dialog.fields_dict.history_html.$wrapper.html(`
            <div class="text-center text-danger" style="padding: 40px;">
                <i class="fa fa-exclamation-triangle fa-2x mb-3"></i>
                <h5>Error loading history data</h5>
                <p class="text-muted">Please try again or contact support if the problem persists.</p>
            </div>
        `);
    });
}

function render_history_table(dialog, purchase_data, sales_data) {
    let html = `
        <div class="container-fluid">
            <!-- Purchase History Section -->
            <div class="row mb-4">
                <div class="col-12">
                    <h5 class="border-bottom pb-2 mb-3">
                        <i class="fa fa-shopping-cart text-primary"></i>
                        Purchase History
                        <span class="badge badge-primary ml-2">${purchase_data ? purchase_data.length : 0}</span>
                    </h5>
                    <div style="border: 1px solid #e3e3e3; border-radius: 4px; max-height: 40vh;">
                        ${render_purchase_table(purchase_data)}
                    </div>
                </div>
            </div>
            
            <!-- Sales History Section -->
            <div class="row">
                <div class="col-12">
                    <h5 class="border-bottom pb-2 mb-3">
                        <i class="fa fa-chart-line text-success"></i>
                        Sales History
                        <span class="badge badge-success ml-2">${sales_data ? sales_data.length : 0}</span>
                    </h5>
                    <div style="border: 1px solid #e3e3e3; border-radius: 4px; max-height: 40vh;">
                        ${render_sales_table(sales_data)}
                    </div>
                </div>
            </div>
            
            <!-- Footer Note -->
            <div class="row mt-4">
                <div class="col-12 text-center text-muted">
                    <small>Double-click on any record to open the document</small>
                </div>
            </div>
        </div>
    `;
    
    dialog.fields_dict.history_html.$wrapper.html(html);
    
    // Add double-click functionality to open documents
    add_double_click_handlers(dialog);
}

function render_purchase_table(data) {
    if (!data || data.length === 0) {
        return `
            <div class="alert alert-info d-flex align-items-center justify-content-center" style="height: 150px; margin: 0;">
                <div class="text-center">
                    <i class="fa fa-info-circle fa-2x mb-2"></i>
                    <p class="mb-0">No purchase history found for this item</p>
                </div>
            </div>
        `;
    }
    
    let html = `
        <div class="table-responsive" style="max-height: 38vh; overflow: auto;">
            <table class="table table-bordered table-sm table-hover mb-0">
                <thead class="thead-light" style="position: sticky; top: 0; z-index: 10; background: #f8f9fa !important;">
                    <tr>
                        <th style="min-width: 140px; position: sticky; top: 0; background: #f8f9fa;">PO No</th>
                        <th style="min-width: 180px; position: sticky; top: 0; background: #f8f9fa;">Supplier</th>
                        <th style="min-width: 120px; position: sticky; top: 0; background: #f8f9fa;">UOM</th>
                        <th style="min-width: 120px; position: sticky; top: 0; background: #f8f9fa;" class="text-right">Qty</th>
                        <th style="min-width: 120px; position: sticky; top: 0; background: #f8f9fa;" class="text-right">Rate</th>
                        <th style="min-width: 140px; position: sticky; top: 0; background: #f8f9fa;" class="text-right">Amount</th>
                        <th style="min-width: 140px; position: sticky; top: 0; background: #f8f9fa;">Date</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.forEach((row, index) => {
        html += `
            <tr class="purchase-row" data-doctype="Purchase Order" data-docname="${escape_html(row.purchase_order || '')}" style="cursor: pointer;">
                <td class="text-primary font-weight-bold">${escape_html(row.purchase_order || '')}</td>
                <td>${escape_html(row.supplier || '')}</td>
                <td>${escape_html(row.uom || '')}</td>
                <td class="text-right">${format_number(row.qty || 0)}</td>
                <td class="text-right">${format_currency(row.rate || 0)}</td>
                <td class="text-right font-weight-bold">${format_currency(row.amount || 0)}</td>
                <td>${frappe.datetime.str_to_user(row.date) || ''}</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    return html;
}

function render_sales_table(data) {
    if (!data || data.length === 0) {
        return `
            <div class="alert alert-info d-flex align-items-center justify-content-center" style="height: 150px; margin: 0;">
                <div class="text-center">
                    <i class="fa fa-info-circle fa-2x mb-2"></i>
                    <p class="mb-0">No sales history found for this item</p>
                </div>
            </div>
        `;
    }
    
    let html = `
        <div class="table-responsive" style="max-height: 38vh; overflow: auto;">
            <table class="table table-bordered table-sm table-hover mb-0">
                <thead class="thead-light" style="position: sticky; top: 0; z-index: 10; background: #f8f9fa !important;">
                    <tr>
                        <th style="min-width: 140px; position: sticky; top: 0; background: #f8f9fa;">Invoice No</th>
                        <th style="min-width: 180px; position: sticky; top: 0; background: #f8f9fa;">Customer</th>
                        <th style="min-width: 120px; position: sticky; top: 0; background: #f8f9fa;">UOM</th>
                        <th style="min-width: 120px; position: sticky; top: 0; background: #f8f9fa;" class="text-right">Qty</th>
                        <th style="min-width: 120px; position: sticky; top: 0; background: #f8f9fa;" class="text-right">Rate</th>
                        <th style="min-width: 140px; position: sticky; top: 0; background: #f8f9fa;" class="text-right">Amount</th>
                        <th style="min-width: 140px; position: sticky; top: 0; background: #f8f9fa;">Date</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.forEach((row, index) => {
        html += `
            <tr class="sales-row" data-doctype="Sales Invoice" data-docname="${escape_html(row.sales_invoice || '')}" style="cursor: pointer;">
                <td class="text-success font-weight-bold">${escape_html(row.sales_invoice || '')}</td>
                <td>${escape_html(row.customer || '')}</td>
                <td>${escape_html(row.uom || '')}</td>
                <td class="text-right">${format_number(row.qty || 0)}</td>
                <td class="text-right">${format_currency(row.rate || 0)}</td>
                <td class="text-right font-weight-bold">${format_currency(row.amount || 0)}</td>
                <td>${frappe.datetime.str_to_user(row.date) || ''}</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    return html;
}

// Add double-click handlers to open documents
function add_double_click_handlers(dialog) {
    setTimeout(() => {
        // Purchase order double-click
        $(dialog.$wrapper).find('.purchase-row').on('dblclick', function() {
            const doctype = $(this).data('doctype');
            const docname = $(this).data('docname');
            if (docname) {
                frappe.set_route('Form', doctype, docname);
                dialog.hide();
            }
        });
        
        // Sales invoice double-click
        $(dialog.$wrapper).find('.sales-row').on('dblclick', function() {
            const doctype = $(this).data('doctype');
            const docname = $(this).data('docname');
            if (docname) {
                frappe.set_route('Form', doctype, docname);
                dialog.hide();
            }
        });
        
        // Add hover effects
        $(dialog.$wrapper).find('.purchase-row, .sales-row').hover(
            function() { $(this).addClass('table-active'); },
            function() { $(this).removeClass('table-active'); }
        );
    }, 100);
}

// Utility functions
function format_currency(value) {
    return frappe.format(value, { fieldtype: 'Currency' });
}

function format_number(value) {
    return frappe.format(value, { fieldtype: 'Float' });
}

function escape_html(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}



