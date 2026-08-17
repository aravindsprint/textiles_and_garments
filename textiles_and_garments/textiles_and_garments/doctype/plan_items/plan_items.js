// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

frappe.ui.form.on("Plan Items", {
	refresh(frm) {
        frm.add_custom_button('Select Sales Order', () => {
            show_sales_order_multi_select_dialog(frm);
        });
        console.log("frm",frm.doc);
	},
});





// function show_sales_order_multi_select_dialog(frm) {
//     frappe.call({
//         method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_selected_sales_order",
//         args: {},
//         callback: function (res) {
//             const sales_orders = res.message || [];

//             // Create a custom dialog to display Sales Order details
//             const dialog = new frappe.ui.Dialog({
//                 title: __('Select Sales Orders'),
//                 fields: [
//                     {
//                         fieldtype: 'HTML',
//                         fieldname: 'filter_section'
//                     },
//                     {
//                         fieldtype: 'HTML',
//                         fieldname: 'results_section'
//                     }
//                 ],
//                 primary_action_label: 'Add Selected',
//                 primary_action: function() {
//                     const selected = [];
//                     dialog.$wrapper.find('input[type="checkbox"]:checked').each(function() {
//                         selected.push($(this).val());
//                     });

//                     if (selected.length === 0) {
//                         frappe.msgprint("Please select at least one Sales Order.");
//                         return;
//                     }

//                     const selected_sales_orders = sales_orders.filter(r => selected.includes(r.name));
//                     console.log("selected_sales_orders", selected_sales_orders);
                    
//                     const existing_sales_orders = (frm.doc.sales_order_item_details || []).map(row => row.sales_order);
//                     console.log("existing_sales_orders", existing_sales_orders);
                    
//                     const new_sales_orders = selected_sales_orders.filter(sales_order => !existing_sales_orders.includes(sales_order.name));
//                     console.log("new_sales_orders", new_sales_orders);

//                     if (new_sales_orders.length === 0) {
//                         frappe.msgprint("Selected Sales Orders are already added.");
//                         dialog.hide();
//                         return;
//                     }

//                     // Fetch Sales Order Items for each selected Sales Order
//                     frappe.call({
//                         method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_sales_order_items",
//                         args: {
//                             sales_orders: new_sales_orders.map(so => so.name)
//                         },
//                         callback: function(items_res) {
//                             const sales_order_items = items_res.message || [];
//                             console.log("sales_order_items", sales_order_items);

//                             // Get unique item codes to find BOMs
//                             const item_codes = [...new Set(sales_order_items.map(item => item.item_code))];
                            
//                             // Fetch latest BOM for each item
//                             frappe.call({
//                                 method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_latest_boms_for_items",
//                                 args: {
//                                     item_codes: item_codes
//                                 },
//                                 callback: function(boms_res) {
//                                     const boms_by_item = boms_res.message || {};
//                                     console.log("boms_by_item", boms_by_item);

//                                     // Group items by sales order
//                                     const items_by_sales_order = {};
//                                     sales_order_items.forEach(item => {
//                                         if (!items_by_sales_order[item.parent]) {
//                                             items_by_sales_order[item.parent] = [];
//                                         }
//                                         items_by_sales_order[item.parent].push(item);
//                                     });

//                                     // Add items to child table with BOM information
//                                     new_sales_orders.forEach(sales_order => {
//                                         const items = items_by_sales_order[sales_order.name] || [];
                                        
//                                         if (items.length > 0) {
//                                             items.forEach(item => {
//                                                 const latest_bom = boms_by_item[item.item_code] || null;
//                                                 frm.add_child('sales_order_item_details', {
//                                                     sales_order: sales_order.name,
//                                                     customer: sales_order.customer,
//                                                     date: sales_order.transaction_date,
//                                                     item_code: item.item_code,
//                                                     qty: item.qty,
//                                                     uom: item.uom,
//                                                     grand_total: sales_order.grand_total,
//                                                     bom: latest_bom ? latest_bom.name : null,
//                                                     bom_created: latest_bom ? latest_bom.creation : null
//                                                 });
//                                             });
//                                         } else {
//                                             // Add the sales order even if no items found
//                                             frm.add_child('sales_order_item_details', {
//                                                 sales_order: sales_order.name,
//                                                 customer: sales_order.customer,
//                                                 date: sales_order.transaction_date,
//                                                 grand_total: sales_order.grand_total
//                                             });
//                                         }
//                                     });

//                                     frm.refresh_field('sales_order_item_details');
//                                     frappe.msgprint(`${new_sales_orders.length} new Sales Order(s) with ${sales_order_items.length} items added.`);
//                                     dialog.hide();
//                                 },
//                                 error: function(err) {
//                                     console.error("Error fetching BOMs:", err);
//                                     frappe.msgprint("Error fetching BOM information. Please try again.");
//                                     dialog.hide();
//                                 }
//                             });
//                         },
//                         error: function(err) {
//                             console.error("Error fetching sales order items:", err);
//                             frappe.msgprint("Error fetching Sales Order items. Please try again.");
//                             dialog.hide();
//                         }
//                     });
//                 }
//             });

//             // ... rest of your dialog code remains the same ...
//             // Add filters
//             const filter_html = `
//                 <div class="row">
//                     <div class="col-sm-4">
//                         <div class="form-group">
//                             <label for="sales_order_filter">Sales Order</label>
//                             <input type="text" class="form-control" id="sales_order_filter" placeholder="Filter by Sales Order name">
//                         </div>
//                     </div>
//                     <div class="col-sm-4">
//                         <div class="form-group">
//                             <label for="customer_filter">Customer</label>
//                             <input type="text" class="form-control" id="customer_filter" placeholder="Filter by Customer">
//                         </div>
//                     </div>
//                     <div class="col-sm-4">
//                         <button class="btn btn-primary btn-sm" style="margin-top: 25px;" onclick="filterSalesOrders()">
//                             ${__('Filter')}
//                         </button>
//                         <button class="btn btn-default btn-sm" style="margin-top: 25px; margin-left: 5px;" onclick="clearFilters()">
//                             ${__('Clear')}
//                         </button>
//                     </div>
//                 </div>
//             `;
            
//             dialog.fields_dict.filter_section.$wrapper.html(filter_html);
            
//             // Add results table
//             let results_html = `
//                 <div class="results-section" style="margin-top: 20px; max-height: 400px; overflow-y: auto;">
//                     <table class="table table-bordered">
//                         <thead>
//                             <tr>
//                                 <th><input type="checkbox" id="select-all"></th>
//                                 <th>Sales Order</th>
//                                 <th>Date</th>
//                                 <th>Customer</th>
//                                 <th>Grand Total</th>
//                             </tr>
//                         </thead>
//                         <tbody>
//             `;
            
//             sales_orders.forEach(order => {
//                 results_html += `
//                     <tr>
//                         <td><input type="checkbox" value="${order.name}" class="sales-order-checkbox"></td>
//                         <td>${order.name}</td>
//                         <td>${order.transaction_date || ''}</td>
//                         <td>${order.customer || ''}</td>
//                         <td>${format_currency(order.grand_total || 0, order.currency || frappe.defaults.get_default("currency"))}</td>
//                     </tr>
//                 `;
//             });
            
//             results_html += `
//                         </tbody>
//                     </table>
//                 </div>
//             `;
            
//             dialog.fields_dict.results_section.$wrapper.html(results_html);
            
//             // Add select all functionality
//             dialog.$wrapper.find('#select-all').on('click', function() {
//                 const isChecked = $(this).is(':checked');
//                 dialog.$wrapper.find('.sales-order-checkbox').prop('checked', isChecked);
//             });
            
//             // Add filter function to window scope
//             window.filterSalesOrders = function() {
//                 const salesOrderFilter = dialog.$wrapper.find('#sales_order_filter').val().toLowerCase();
//                 const customerFilter = dialog.$wrapper.find('#customer_filter').val().toLowerCase();
                
//                 dialog.$wrapper.find('tbody tr').each(function() {
//                     const row = $(this);
//                     const salesOrderName = row.find('td:eq(1)').text().toLowerCase();
//                     const customerName = row.find('td:eq(3)').text().toLowerCase();
                    
//                     const showRow = 
//                         (salesOrderFilter === '' || salesOrderName.includes(salesOrderFilter)) &&
//                         (customerFilter === '' || customerName.includes(customerFilter));
                    
//                     row.toggle(showRow);
//                 });
//             };
            
//             // Add clear filters function
//             window.clearFilters = function() {
//                 dialog.$wrapper.find('#sales_order_filter').val('');
//                 dialog.$wrapper.find('#customer_filter').val('');
//                 dialog.$wrapper.find('tbody tr').show();
//             };
            
//             // Add real-time filtering as user types
//             dialog.$wrapper.find('#sales_order_filter, #customer_filter').on('keyup', function() {
//                 window.filterSalesOrders();
//             });
            
//             dialog.show();
//         }
//     });
// }


// function show_sales_order_multi_select_dialog(frm) {
//     frappe.call({
//         method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_selected_sales_order",
//         args: {},
//         callback: function (res) {
//             const sales_orders = res.message || [];

//             // Create a custom dialog to display Sales Order details
//             const dialog = new frappe.ui.Dialog({
//                 title: __('Select Sales Orders'),
//                 fields: [
//                     {
//                         fieldtype: 'HTML',
//                         fieldname: 'filter_section'
//                     },
//                     {
//                         fieldtype: 'HTML',
//                         fieldname: 'results_section'
//                     }
//                 ],
//                 primary_action_label: 'Add Selected',
//                 primary_action: function() {
//                     const selected = [];
//                     dialog.$wrapper.find('input[type="checkbox"]:checked').each(function() {
//                         selected.push($(this).val());
//                     });

//                     if (selected.length === 0) {
//                         frappe.msgprint("Please select at least one Sales Order.");
//                         return;
//                     }

//                     const selected_sales_orders = sales_orders.filter(r => selected.includes(r.name));
//                     console.log("selected_sales_orders", selected_sales_orders);
                    
//                     const existing_sales_orders = (frm.doc.sales_order_item_details || []).map(row => row.sales_order);
//                     console.log("existing_sales_orders", existing_sales_orders);
                    
//                     const new_sales_orders = selected_sales_orders.filter(sales_order => !existing_sales_orders.includes(sales_order.name));
//                     console.log("new_sales_orders", new_sales_orders);

//                     if (new_sales_orders.length === 0) {
//                         frappe.msgprint("Selected Sales Orders are already added.");
//                         dialog.hide();
//                         return;
//                     }

//                     // Fetch Sales Order Items for each selected Sales Order
//                     frappe.call({
//                         method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_sales_order_items",
//                         args: {
//                             sales_orders: new_sales_orders.map(so => so.name)
//                         },
//                         callback: function(items_res) {
//                             const sales_order_items = items_res.message || [];
//                             console.log("sales_order_items", sales_order_items);

//                             // Get unique item codes to find BOMs
//                             const item_codes = [...new Set(sales_order_items.map(item => item.item_code))];
                            
//                             // Fetch latest BOM for each item
//                             frappe.call({
//                                 method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_latest_boms_for_items",
//                                 args: {
//                                     item_codes: item_codes
//                                 },
//                                 callback: function(boms_res) {
//                                     const boms_by_item = boms_res.message || {};
//                                     console.log("boms_by_item", boms_by_item);

//                                     // Get BOMs that were found
//                                     const bom_names = Object.values(boms_by_item)
//                                         .filter(bom => bom !== null)
//                                         .map(bom => bom.name);
                                    
//                                     if (bom_names.length === 0) {
//                                         frappe.msgprint("No BOMs found for the selected items. Cannot create plan items.");
//                                         dialog.hide();
//                                         return;
//                                     }

//                                     // Fetch BOM items for all BOMs
//                                     frappe.call({
//                                         method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_bom_items",
//                                         args: {
//                                             bom_names: bom_names
//                                         },
//                                         callback: function(bom_items_res) {
//                                             const bom_items = bom_items_res.message || [];
//                                             console.log("bom_items", bom_items);

//                                             // Group BOM items by BOM name
//                                             const bom_items_by_bom = {};
//                                             bom_items.forEach(item => {
//                                                 if (!bom_items_by_bom[item.parent]) {
//                                                     bom_items_by_bom[item.parent] = [];
//                                                 }
//                                                 bom_items_by_bom[item.parent].push(item);
//                                             });

//                                             // Group sales order items by sales order
//                                             const items_by_sales_order = {};
//                                             sales_order_items.forEach(item => {
//                                                 if (!items_by_sales_order[item.parent]) {
//                                                     items_by_sales_order[item.parent] = [];
//                                                 }
//                                                 items_by_sales_order[item.parent].push(item);
//                                             });

//                                             frm.clear_table('sales_order_item_details');
//                                             frm.clear_table('plan_items_detail');

//                                             // Add items to both tables
//                                             new_sales_orders.forEach(sales_order => {
//                                                 const items = items_by_sales_order[sales_order.name] || [];
                                                
//                                                 if (items.length > 0) {
//                                                     items.forEach(item => {
//                                                         const latest_bom = boms_by_item[item.item_code] || null;
                                                        
//                                                         // Add to sales_order_item_details
//                                                         frm.add_child('sales_order_item_details', {
//                                                             sales_order: sales_order.name,
//                                                             customer: sales_order.customer,
//                                                             date: sales_order.transaction_date,
//                                                             item_code: item.item_code,
//                                                             qty: item.qty,
//                                                             uom: item.uom,
//                                                             grand_total: sales_order.grand_total,
//                                                             bom: latest_bom ? latest_bom.name : null,
//                                                             color: item.color,
//                                                             commercial_name: item.commercial_name
//                                                         });

//                                                         // Add BOM items to plan_items_detail
//                                                         if (latest_bom && bom_items_by_bom[latest_bom.name]) {
//                                                             bom_items_by_bom[latest_bom.name].forEach(bom_item => {
//                                                                 // Calculate required quantity based on BOM ratio
//                                                                 const required_qty = (bom_item.qty / latest_bom.quantity) * item.qty;
                                                                
//                                                                 frm.add_child('plan_items_detail', {
//                                                                     item_code: bom_item.item_code,
//                                                                     bom: latest_bom.name,
//                                                                     qty: required_qty,
//                                                                     uom: bom_item.uom,
//                                                                     source_item: item.item_code,
//                                                                     source_qty: item.qty
//                                                                 });
//                                                             });
//                                                         }
//                                                     });
//                                                 } else {
//                                                     // Add the sales order even if no items found
//                                                     frm.add_child('sales_order_item_details', {
//                                                         sales_order: sales_order.name,
//                                                         customer: sales_order.customer,
//                                                         date: sales_order.transaction_date,
//                                                         grand_total: sales_order.grand_total
//                                                     });
//                                                 }
//                                             });

//                                             frm.refresh_field('sales_order_item_details');
//                                             frm.refresh_field('plan_items_detail');
//                                             frappe.msgprint(`${new_sales_orders.length} new Sales Order(s) with ${sales_order_items.length} items added. BOM items have been added to plan items.`);
//                                             dialog.hide();
//                                         },
//                                         error: function(err) {
//                                             console.error("Error fetching BOM items:", err);
//                                             frappe.msgprint("Error fetching BOM items. Please try again.");
//                                             dialog.hide();
//                                         }
//                                     });
//                                 },
//                                 error: function(err) {
//                                     console.error("Error fetching BOMs:", err);
//                                     frappe.msgprint("Error fetching BOM information. Please try again.");
//                                     dialog.hide();
//                                 }
//                             });
//                         },
//                         error: function(err) {
//                             console.error("Error fetching sales order items:", err);
//                             frappe.msgprint("Error fetching Sales Order items. Please try again.");
//                             dialog.hide();
//                         }
//                     });
//                 }
//             });

//             // ... rest of your dialog code remains the same ...
//             // Add filters
//             const filter_html = `
//                 <div class="row">
//                     <div class="col-sm-4">
//                         <div class="form-group">
//                             <label for="sales_order_filter">Sales Order</label>
//                             <input type="text" class="form-control" id="sales_order_filter" placeholder="Filter by Sales Order name">
//                         </div>
//                     </div>
//                     <div class="col-sm-4">
//                         <div class="form-group">
//                             <label for="customer_filter">Customer</label>
//                             <input type="text" class="form-control" id="customer_filter" placeholder="Filter by Customer">
//                         </div>
//                     </div>
//                     <div class="col-sm-4">
//                         <button class="btn btn-primary btn-sm" style="margin-top: 25px;" onclick="filterSalesOrders()">
//                             ${__('Filter')}
//                         </button>
//                         <button class="btn btn-default btn-sm" style="margin-top: 25px; margin-left: 5px;" onclick="clearFilters()">
//                             ${__('Clear')}
//                         </button>
//                     </div>
//                 </div>
//             `;
            
//             dialog.fields_dict.filter_section.$wrapper.html(filter_html);
            
//             // Add results table
//             let results_html = `
//                 <div class="results-section" style="margin-top: 20px; max-height: 400px; overflow-y: auto;">
//                     <table class="table table-bordered">
//                         <thead>
//                             <tr>
//                                 <th><input type="checkbox" id="select-all"></th>
//                                 <th>Sales Order</th>
//                                 <th>Date</th>
//                                 <th>Customer</th>
//                                 <th>Grand Total</th>
//                             </tr>
//                         </thead>
//                         <tbody>
//             `;
            
//             sales_orders.forEach(order => {
//                 results_html += `
//                     <tr>
//                         <td><input type="checkbox" value="${order.name}" class="sales-order-checkbox"></td>
//                         <td>${order.name}</td>
//                         <td>${order.transaction_date || ''}</td>
//                         <td>${order.customer || ''}</td>
//                         <td>${format_currency(order.grand_total || 0, order.currency || frappe.defaults.get_default("currency"))}</td>
//                     </tr>
//                 `;
//             });
            
//             results_html += `
//                         </tbody>
//                     </table>
//                 </div>
//             `;
            
//             dialog.fields_dict.results_section.$wrapper.html(results_html);
            
//             // Add select all functionality
//             dialog.$wrapper.find('#select-all').on('click', function() {
//                 const isChecked = $(this).is(':checked');
//                 dialog.$wrapper.find('.sales-order-checkbox').prop('checked', isChecked);
//             });
            
//             // Add filter function to window scope
//             window.filterSalesOrders = function() {
//                 const salesOrderFilter = dialog.$wrapper.find('#sales_order_filter').val().toLowerCase();
//                 const customerFilter = dialog.$wrapper.find('#customer_filter').val().toLowerCase();
                
//                 dialog.$wrapper.find('tbody tr').each(function() {
//                     const row = $(this);
//                     const salesOrderName = row.find('td:eq(1)').text().toLowerCase();
//                     const customerName = row.find('td:eq(3)').text().toLowerCase();
                    
//                     const showRow = 
//                         (salesOrderFilter === '' || salesOrderName.includes(salesOrderFilter)) &&
//                         (customerFilter === '' || customerName.includes(customerFilter));
                    
//                     row.toggle(showRow);
//                 });
//             };
            
//             // Add clear filters function
//             window.clearFilters = function() {
//                 dialog.$wrapper.find('#sales_order_filter').val('');
//                 dialog.$wrapper.find('#customer_filter').val('');
//                 dialog.$wrapper.find('tbody tr').show();
//             };
            
//             // Add real-time filtering as user types
//             dialog.$wrapper.find('#sales_order_filter, #customer_filter').on('keyup', function() {
//                 window.filterSalesOrders();
//             });
            
//             dialog.show();
//         }
//     });
// }





// function show_sales_order_multi_select_dialog(frm) {
//     frappe.call({
//         method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_selected_sales_order",
//         args: {},
//         callback: function (res) {
//             const sales_orders = res.message || [];

//             // Create a custom dialog to display Sales Order details
//             const dialog = new frappe.ui.Dialog({
//                 title: __('Select Sales Orders'),
//                 fields: [
//                     {
//                         fieldtype: 'HTML',
//                         fieldname: 'filter_section'
//                     },
//                     {
//                         fieldtype: 'HTML',
//                         fieldname: 'results_section'
//                     }
//                 ],
//                 primary_action_label: 'Add Selected',
//                 primary_action: function() {
//                     const selected = [];
//                     dialog.$wrapper.find('input[type="checkbox"]:checked').each(function() {
//                         selected.push($(this).val());
//                     });

//                     if (selected.length === 0) {
//                         frappe.msgprint("Please select at least one Sales Order.");
//                         return;
//                     }

//                     const selected_sales_orders = sales_orders.filter(r => selected.includes(r.name));
//                     console.log("selected_sales_orders", selected_sales_orders);
                    
//                     const existing_sales_orders = (frm.doc.sales_order_item_details || []).map(row => row.sales_order);
//                     console.log("existing_sales_orders", existing_sales_orders);
                    
//                     const new_sales_orders = selected_sales_orders.filter(sales_order => !existing_sales_orders.includes(sales_order.name));
//                     console.log("new_sales_orders", new_sales_orders);

//                     if (new_sales_orders.length === 0) {
//                         frappe.msgprint("Selected Sales Orders are already added.");
//                         dialog.hide();
//                         return;
//                     }

//                     // Fetch Sales Order Items for each selected Sales Order
//                     frappe.call({
//                         method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_sales_order_items",
//                         args: {
//                             sales_orders: new_sales_orders.map(so => so.name)
//                         },
//                         callback: function(items_res) {
//                             const sales_order_items = items_res.message || [];
//                             console.log("sales_order_items", sales_order_items);

//                             // Get unique item codes to find BOMs
//                             const item_codes = [...new Set(sales_order_items.map(item => item.item_code))];
                            
//                             // Fetch latest BOM for each item
//                             frappe.call({
//                                 method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_latest_boms_for_items",
//                                 args: {
//                                     item_codes: item_codes
//                                 },
//                                 callback: function(boms_res) {
//                                     const boms_by_item = boms_res.message || {};
//                                     console.log("boms_by_item", boms_by_item);

//                                     // Get BOMs that were found
//                                     const bom_names = Object.values(boms_by_item)
//                                         .filter(bom => bom !== null)
//                                         .map(bom => bom.name);
//                                     console.log("bom_names",bom_names);
//                                     if (bom_names.length === 0) {
//                                         frappe.msgprint("No BOMs found for the selected items. Cannot create plan items.");
//                                         dialog.hide();
//                                         return;
//                                     }

//                                     // Fetch all BOM items recursively
//                                     frappe.call({
//                                         method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_all_bom_items_recursive",
//                                         args: {
//                                             bom_names: bom_names
//                                         },
//                                         callback: function(all_bom_items_res) {
//                                             const all_bom_items = all_bom_items_res.message || {};
//                                             console.log("all_bom_items", all_bom_items);

//                                             // Group sales order items by sales order
//                                             const items_by_sales_order = {};
//                                             sales_order_items.forEach(item => {
//                                                 if (!items_by_sales_order[item.parent]) {
//                                                     items_by_sales_order[item.parent] = [];
//                                                 }
//                                                 items_by_sales_order[item.parent].push(item);
//                                             });

//                                             frm.clear_table('sales_order_item_details');
//                                             frm.clear_table('plan_items_detail');

//                                             // Add items to both tables
//                                             new_sales_orders.forEach(sales_order => {
//                                                 const items = items_by_sales_order[sales_order.name] || [];
                                                
//                                                 if (items.length > 0) {
//                                                     items.forEach(item => {
//                                                         console.log("item",item);
//                                                         const latest_bom = boms_by_item[item.item_code] || null;
//                                                         console.log("latest_bom",latest_bom);
                                                        
//                                                         // Add to sales_order_item_details
//                                                         frm.add_child('sales_order_item_details', {
//                                                             sales_order: sales_order.name,
//                                                             customer: sales_order.customer,
//                                                             date: sales_order.transaction_date,
//                                                             item_code: item.item_code,
//                                                             qty: item.qty,
//                                                             uom: item.uom,
//                                                             grand_total: sales_order.grand_total,
//                                                             bom: latest_bom ? latest_bom.name : null,
//                                                             color: item.color,
//                                                             commercial_name: item.commercial_name
//                                                         });

//                                                         // Add BOM items to plan_items_detail recursively
//                                                         if (latest_bom && all_bom_items[latest_bom.name]) {
//                                                             processBomItemsRecursively(
//                                                                 frm, 
//                                                                 all_bom_items[latest_bom.name], 
//                                                                 item.qty, 
//                                                                 latest_bom.quantity, 
//                                                                 item.item_code,
//                                                                 1 // level 1
//                                                             );
//                                                         }
//                                                     });
//                                                 } else {
//                                                     // Add the sales order even if no items found
//                                                     frm.add_child('sales_order_item_details', {
//                                                         sales_order: sales_order.name,
//                                                         customer: sales_order.customer,
//                                                         date: sales_order.transaction_date,
//                                                         grand_total: sales_order.grand_total
//                                                     });
//                                                 }
//                                             });

//                                             frm.refresh_field('sales_order_item_details');
//                                             frm.refresh_field('plan_items_detail');
//                                             frappe.msgprint(`${new_sales_orders.length} new Sales Order(s) with ${sales_order_items.length} items added. All BOM levels have been processed.`);
//                                             dialog.hide();
//                                         },
//                                         error: function(err) {
//                                             console.error("Error fetching recursive BOM items:", err);
//                                             frappe.msgprint("Error fetching BOM items recursively. Please try again.");
//                                             dialog.hide();
//                                         }
//                                     });
//                                 },
//                                 error: function(err) {
//                                     console.error("Error fetching BOMs:", err);
//                                     frappe.msgprint("Error fetching BOM information. Please try again.");
//                                     dialog.hide();
//                                 }
//                             });
//                         },
//                         error: function(err) {
//                             console.error("Error fetching sales order items:", err);
//                             frappe.msgprint("Error fetching Sales Order items. Please try again.");
//                             dialog.hide();
//                         }
//                     });
//                 }
//             });

//             // Helper function to process BOM items recursively
//             function processBomItemsRecursively(frm, bom_items, source_qty, bom_quantity, source_item, level) {
//                 bom_items.forEach(bom_item => {
//                     // Calculate required quantity based on BOM ratio
//                     const required_qty = (bom_item.qty / bom_quantity) * source_qty;
                    
//                     // Add to plan_items_detail
//                     frm.add_child('plan_items_detail', {
//                         item_code: bom_item.item_code,
//                         bom: bom_item.bom_name,
//                         qty: required_qty,
//                         uom: bom_item.uom,
//                         source_item: source_item,
//                         source_qty: source_qty,
//                         level: level,
//                         is_final_item: bom_item.has_bom ? 0 : 1
//                     });

//                     // If this item has its own BOM, process it recursively
//                     if (bom_item.has_bom && bom_item.child_bom_items) {
//                         processBomItemsRecursively(
//                             frm,
//                             bom_item.child_bom_items,
//                             required_qty,
//                             bom_item.bom_quantity,
//                             bom_item.item_code,
//                             level + 1
//                         );
//                     }
//                 });
//             }

//             // ... rest of your dialog code remains the same ...
//             // Add filters
//             const filter_html = `
//                 <div class="row">
//                     <div class="col-sm-4">
//                         <div class="form-group">
//                             <label for="sales_order_filter">Sales Order</label>
//                             <input type="text" class="form-control" id="sales_order_filter" placeholder="Filter by Sales Order name">
//                         </div>
//                     </div>
//                     <div class="col-sm-4">
//                         <div class="form-group">
//                             <label for="customer_filter">Customer</label>
//                             <input type="text" class="form-control" id="customer_filter" placeholder="Filter by Customer">
//                         </div>
//                     </div>
//                     <div class="col-sm-4">
//                         <button class="btn btn-primary btn-sm" style="margin-top: 25px;" onclick="filterSalesOrders()">
//                             ${__('Filter')}
//                         </button>
//                         <button class="btn btn-default btn-sm" style="margin-top: 25px; margin-left: 5px;" onclick="clearFilters()">
//                             ${__('Clear')}
//                         </button>
//                     </div>
//                 </div>
//             `;
            
//             dialog.fields_dict.filter_section.$wrapper.html(filter_html);
            
//             // Add results table
//             let results_html = `
//                 <div class="results-section" style="margin-top: 20px; max-height: 400px; overflow-y: auto;">
//                     <table class="table table-bordered">
//                         <thead>
//                             <tr>
//                                 <th><input type="checkbox" id="select-all"></th>
//                                 <th>Sales Order</th>
//                                 <th>Date</th>
//                                 <th>Customer</th>
//                                 <th>Grand Total</th>
//                             </tr>
//                         </thead>
//                         <tbody>
//             `;
            
//             sales_orders.forEach(order => {
//                 results_html += `
//                     <tr>
//                         <td><input type="checkbox" value="${order.name}" class="sales-order-checkbox"></td>
//                         <td>${order.name}</td>
//                         <td>${order.transaction_date || ''}</td>
//                         <td>${order.customer || ''}</td>
//                         <td>${format_currency(order.grand_total || 0, order.currency || frappe.defaults.get_default("currency"))}</td>
//                     </tr>
//                 `;
//             });
            
//             results_html += `
//                         </tbody>
//                     </table>
//                 </div>
//             `;
            
//             dialog.fields_dict.results_section.$wrapper.html(results_html);
            
//             // Add select all functionality
//             dialog.$wrapper.find('#select-all').on('click', function() {
//                 const isChecked = $(this).is(':checked');
//                 dialog.$wrapper.find('.sales-order-checkbox').prop('checked', isChecked);
//             });
            
//             // Add filter function to window scope
//             window.filterSalesOrders = function() {
//                 const salesOrderFilter = dialog.$wrapper.find('#sales_order_filter').val().toLowerCase();
//                 const customerFilter = dialog.$wrapper.find('#customer_filter').val().toLowerCase();
                
//                 dialog.$wrapper.find('tbody tr').each(function() {
//                     const row = $(this);
//                     const salesOrderName = row.find('td:eq(1)').text().toLowerCase();
//                     const customerName = row.find('td:eq(3)').text().toLowerCase();
                    
//                     const showRow = 
//                         (salesOrderFilter === '' || salesOrderName.includes(salesOrderFilter)) &&
//                         (customerFilter === '' || customerName.includes(customerFilter));
                    
//                     row.toggle(showRow);
//                 });
//             };
            
//             // Add clear filters function
//             window.clearFilters = function() {
//                 dialog.$wrapper.find('#sales_order_filter').val('');
//                 dialog.$wrapper.find('#customer_filter').val('');
//                 dialog.$wrapper.find('tbody tr').show();
//             };
            
//             // Add real-time filtering as user types
//             dialog.$wrapper.find('#sales_order_filter, #customer_filter').on('keyup', function() {
//                 window.filterSalesOrders();
//             });
            
//             dialog.show();

//         }
//     });
// }



function show_sales_order_multi_select_dialog(frm) {
    frappe.call({
        method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_selected_sales_order",
        args: {},
        callback: function (res) {
            const sales_orders = res.message || [];

            // Create a custom dialog to display Sales Order details
            const dialog = new frappe.ui.Dialog({
                title: __('Select Sales Orders'),
                fields: [
                    {
                        fieldtype: 'HTML',
                        fieldname: 'filter_section'
                    },
                    {
                        fieldtype: 'HTML',
                        fieldname: 'results_section'
                    }
                ],
                primary_action_label: 'Add Selected',
                primary_action: function() {
                    const selected = [];
                    dialog.$wrapper.find('input[type="checkbox"]:checked').each(function() {
                        selected.push($(this).val());
                    });

                    if (selected.length === 0) {
                        frappe.msgprint("Please select at least one Sales Order.");
                        return;
                    }

                    const selected_sales_orders = sales_orders.filter(r => selected.includes(r.name));
                    
                    const existing_sales_orders = (frm.doc.sales_order_item_details || []).map(row => row.sales_order);
                    
                    const new_sales_orders = selected_sales_orders.filter(sales_order => !existing_sales_orders.includes(sales_order.name));

                    if (new_sales_orders.length === 0) {
                        frappe.msgprint("Selected Sales Orders are already added.");
                        dialog.hide();
                        return;
                    }

                    // Fetch Sales Order Items for each selected Sales Order
                    frappe.call({
                        method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_sales_order_items",
                        args: {
                            sales_orders: new_sales_orders.map(so => so.name)
                        },
                        callback: function(items_res) {
                            const sales_order_items = items_res.message || [];

                            // Get unique item codes to find BOMs
                            const item_codes = [...new Set(sales_order_items.map(item => item.item_code))];
                            
                            // Fetch latest BOM for each item
                            frappe.call({
                                method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_latest_boms_for_items",
                                args: {
                                    item_codes: item_codes
                                },
                                callback: function(boms_res) {
                                    const boms_by_item = boms_res.message || {};

                                    // Get BOMs that were found
                                    const bom_names = Object.values(boms_by_item)
                                        .filter(bom => bom !== null)
                                        .map(bom => bom.name);
                                    
                                    if (bom_names.length === 0) {
                                        frappe.msgprint("No BOMs found for the selected items. Cannot create plan items.");
                                        dialog.hide();
                                        return;
                                    }

                                    // Fetch all BOM items recursively
                                    frappe.call({
                                        method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_all_bom_items_recursive",
                                        args: {
                                            bom_names: bom_names
                                        },
                                        callback: function(all_bom_items_res) {
                                            const all_bom_items = all_bom_items_res.message || {};

                                            // Group sales order items by sales order
                                            const items_by_sales_order = {};
                                            sales_order_items.forEach(item => {
                                                if (!items_by_sales_order[item.parent]) {
                                                    items_by_sales_order[item.parent] = [];
                                                }
                                                items_by_sales_order[item.parent].push(item);
                                            });

                                            frm.clear_table('sales_order_item_details');
                                            frm.clear_table('plan_items_detail');

                                            // First, collect all unique item codes from all BOM levels
                                            const all_item_codes = new Set();
                                            Object.values(all_bom_items).forEach(bom_items => {
                                                extractAllItemCodes(bom_items, all_item_codes);
                                            });

                                            // Fetch latest BOMs for ALL items in the entire BOM hierarchy
                                            frappe.call({
                                                method: "textiles_and_garments.textiles_and_garments.doctype.plan_items.plan_items.get_latest_boms_for_items",
                                                args: {
                                                    item_codes: Array.from(all_item_codes)
                                                },
                                                callback: function(all_boms_res) {
                                                    const all_boms_by_item = all_boms_res.message || {};

                                                    // Add items to both tables
                                                    new_sales_orders.forEach(sales_order => {
                                                        const items = items_by_sales_order[sales_order.name] || [];
                                                        
                                                        if (items.length > 0) {
                                                            items.forEach(item => {
                                                                const latest_bom = boms_by_item[item.item_code] || null;
                                                                
                                                                // Add to sales_order_item_details
                                                                frm.add_child('sales_order_item_details', {
                                                                    sales_order: sales_order.name,
                                                                    customer: sales_order.customer,
                                                                    date: sales_order.transaction_date,
                                                                    item_code: item.item_code,
                                                                    qty: item.qty,
                                                                    uom: item.uom,
                                                                    grand_total: sales_order.grand_total,
                                                                    bom: latest_bom ? latest_bom.name : null,
                                                                    color: item.color,
                                                                    commercial_name: item.commercial_name
                                                                });

                                                                // Add BOM items to plan_items_detail recursively
                                                                if (latest_bom && all_bom_items[latest_bom.name]) {
                                                                    processBomItemsRecursively(
                                                                        frm, 
                                                                        all_bom_items[latest_bom.name], 
                                                                        item.qty, 
                                                                        latest_bom.quantity, 
                                                                        item.item_code,
                                                                        1, // level 1
                                                                        all_boms_by_item // Pass all BOMs mapping
                                                                    );
                                                                }
                                                            });
                                                        } else {
                                                            // Add the sales order even if no items found
                                                            frm.add_child('sales_order_item_details', {
                                                                sales_order: sales_order.name,
                                                                customer: sales_order.customer,
                                                                date: sales_order.transaction_date,
                                                                grand_total: sales_order.grand_total
                                                            });
                                                        }
                                                    });

                                                    frm.refresh_field('sales_order_item_details');
                                                    frm.refresh_field('plan_items_detail');
                                                    frappe.msgprint(`${new_sales_orders.length} new Sales Order(s) with ${sales_order_items.length} items added. All BOM levels have been processed.`);
                                                    dialog.hide();
                                                },
                                                error: function(err) {
                                                    console.error("Error fetching all BOMs:", err);
                                                    frappe.msgprint("Error fetching BOM information for all items. Please try again.");
                                                    dialog.hide();
                                                }
                                            });
                                        },
                                        error: function(err) {
                                            console.error("Error fetching recursive BOM items:", err);
                                            frappe.msgprint("Error fetching BOM items recursively. Please try again.");
                                            dialog.hide();
                                        }
                                    });
                                },
                                error: function(err) {
                                    console.error("Error fetching BOMs:", err);
                                    frappe.msgprint("Error fetching BOM information. Please try again.");
                                    dialog.hide();
                                }
                            });
                        },
                        error: function(err) {
                            console.error("Error fetching sales order items:", err);
                            frappe.msgprint("Error fetching Sales Order items. Please try again.");
                            dialog.hide();
                        }
                    });
                }
            });

            // Helper function to extract all item codes from BOM structure
            function extractAllItemCodes(bom_items, itemCodesSet) {
                bom_items.forEach(bom_item => {
                    itemCodesSet.add(bom_item.item_code);
                    if (bom_item.has_bom && bom_item.child_bom_items) {
                        extractAllItemCodes(bom_item.child_bom_items, itemCodesSet);
                    }
                });
            }

            // Helper function to process BOM items recursively - MODIFIED
            function processBomItemsRecursively(frm, bom_items, source_qty, bom_quantity, source_item, level, all_boms_by_item) {
                bom_items.forEach(bom_item => {
                    // Calculate required quantity based on BOM ratio
                    const required_qty = (bom_item.qty / bom_quantity) * source_qty;
                    
                    // Find the latest BOM for this specific item_code
                    const latest_bom = all_boms_by_item[bom_item.item_code] || null;
                    const bom_name = latest_bom ? latest_bom.name : bom_item.bom_name;
                    
                    // Add to plan_items_detail with the latest BOM
                    frm.add_child('plan_items_detail', {
                        item_code: bom_item.item_code,
                        bom: bom_name, // Use the latest BOM for this item_code
                        qty: required_qty,
                        uom: bom_item.uom,
                        source_item: source_item,
                        source_qty: source_qty,
                        level: level,
                        is_final_item: bom_item.has_bom ? 0 : 1
                    });

                    // If this item has its own BOM, process it recursively
                    if (bom_item.has_bom && bom_item.child_bom_items) {
                        processBomItemsRecursively(
                            frm,
                            bom_item.child_bom_items,
                            required_qty,
                            bom_item.bom_quantity,
                            bom_item.item_code,
                            level + 1,
                            all_boms_by_item
                        );
                    }
                });
            }

            // ... rest of your dialog code remains the same ...
            // [The rest of your dialog HTML and filtering code goes here]
            // ... rest of your dialog code remains the same ...
            // Add filters
            const filter_html = `
                <div class="row">
                    <div class="col-sm-4">
                        <div class="form-group">
                            <label for="sales_order_filter">Sales Order</label>
                            <input type="text" class="form-control" id="sales_order_filter" placeholder="Filter by Sales Order name">
                        </div>
                    </div>
                    <div class="col-sm-4">
                        <div class="form-group">
                            <label for="customer_filter">Customer</label>
                            <input type="text" class="form-control" id="customer_filter" placeholder="Filter by Customer">
                        </div>
                    </div>
                    <div class="col-sm-4">
                        <button class="btn btn-primary btn-sm" style="margin-top: 25px;" onclick="filterSalesOrders()">
                            ${__('Filter')}
                        </button>
                        <button class="btn btn-default btn-sm" style="margin-top: 25px; margin-left: 5px;" onclick="clearFilters()">
                            ${__('Clear')}
                        </button>
                    </div>
                </div>
            `;
            
            dialog.fields_dict.filter_section.$wrapper.html(filter_html);
            
            // Add results table
            let results_html = `
                <div class="results-section" style="margin-top: 20px; max-height: 400px; overflow-y: auto;">
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th><input type="checkbox" id="select-all"></th>
                                <th>Sales Order</th>
                                <th>Date</th>
                                <th>Customer</th>
                                <th>Grand Total</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            sales_orders.forEach(order => {
                results_html += `
                    <tr>
                        <td><input type="checkbox" value="${order.name}" class="sales-order-checkbox"></td>
                        <td>${order.name}</td>
                        <td>${order.transaction_date || ''}</td>
                        <td>${order.customer || ''}</td>
                        <td>${format_currency(order.grand_total || 0, order.currency || frappe.defaults.get_default("currency"))}</td>
                    </tr>
                `;
            });
            
            results_html += `
                        </tbody>
                    </table>
                </div>
            `;
            
            dialog.fields_dict.results_section.$wrapper.html(results_html);
            
            // Add select all functionality
            dialog.$wrapper.find('#select-all').on('click', function() {
                const isChecked = $(this).is(':checked');
                dialog.$wrapper.find('.sales-order-checkbox').prop('checked', isChecked);
            });
            
            // Add filter function to window scope
            window.filterSalesOrders = function() {
                const salesOrderFilter = dialog.$wrapper.find('#sales_order_filter').val().toLowerCase();
                const customerFilter = dialog.$wrapper.find('#customer_filter').val().toLowerCase();
                
                dialog.$wrapper.find('tbody tr').each(function() {
                    const row = $(this);
                    const salesOrderName = row.find('td:eq(1)').text().toLowerCase();
                    const customerName = row.find('td:eq(3)').text().toLowerCase();
                    
                    const showRow = 
                        (salesOrderFilter === '' || salesOrderName.includes(salesOrderFilter)) &&
                        (customerFilter === '' || customerName.includes(customerFilter));
                    
                    row.toggle(showRow);
                });
            };
            
            // Add clear filters function
            window.clearFilters = function() {
                dialog.$wrapper.find('#sales_order_filter').val('');
                dialog.$wrapper.find('#customer_filter').val('');
                dialog.$wrapper.find('tbody tr').show();
            };
            
            // Add real-time filtering as user types
            dialog.$wrapper.find('#sales_order_filter, #customer_filter').on('keyup', function() {
                window.filterSalesOrders();
            });

            
            dialog.show();
        }
    });
}


// Trigger this once on form load to make sure summary starts clean
frappe.ui.form.on('Plan Items', {
    onload(frm) {
        // Optional: you can refresh summary here initially if needed
    }
});

// --- Event handlers for Plan Items Detail ---
frappe.ui.form.on('Plan Items Detail', {
    item_code(frm, cdt, cdn) {
        const row = locals[cdt][cdn];

        // Check if item_code already exists (excluding current row)
        let duplicate = frm.doc.plan_items_detail.some(r => 
            r.item_code === row.item_code && r.name !== row.name
        );

        if (duplicate) {
            frappe.msgprint({
                title: __("Duplicate Item"),
                message: __("Item Code {0} is already added in Plan Items Detail.", [row.item_code]),
                indicator: 'red'
            });

            // Clear the duplicate value
            frappe.model.set_value(cdt, cdn, 'item_code', '');
            return;
        }

        sync_summary_row(frm, row.item_code);
    },

    qty(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        sync_summary_row(frm, row.item_code);
    }
});




// --- Core function to sync the summary table ---
// function sync_summary_row(frm, item_code) {
//     if (!item_code) return;

//     let total_qty = 0;

//     // Sum qty for all detail rows with the same item_code
//     frm.doc.plan_items_detail.forEach(row => {
//         if (row.item_code === item_code) {
//             total_qty += flt(row.qty);
//         }
//     });

//     // Find the matching summary row
//     let summary_row = frm.doc.plan_items_summary.find(r => r.item_code === item_code);

//     if (summary_row) {
//         if (total_qty === 0) {
//             // Remove the row if qty is 0
//             frm.doc.plan_items_summary = frm.doc.plan_items_summary.filter(r => r.item_code !== item_code);
//         } else {
//             summary_row.qty = total_qty;
//             summary_row.need_to_plan_qty = flt(total_qty) - flt(summary_row.planned_qty || 0);
//         }
//     } else if (total_qty > 0) {
//         // Add a new row
//         let new_row = frm.add_child('plan_items_summary', {
//             item_code: item_code,
//             qty: total_qty,
//             planned_qty: 0,
//             need_to_plan_qty: total_qty
//         });
//     }

//     frm.refresh_field('plan_items_summary');
// }
// This script is typically placed in ERPNext's Custom Scripts for a DocType.

function sync_summary_row(frm, item_code) {
    if (!item_code) return;

    let total_qty = 0;

    // Sum qty for all detail rows with the same item_code
    frm.doc.plan_items_detail.forEach(row => {
        if (row.item_code === item_code) {
            total_qty += flt(row.qty);
        }
    });

    // Find the matching summary row
    let summary_row = frm.doc.plan_items_summary.find(r => r.item_code === item_code);

    if (summary_row) {
        if (total_qty === 0) {
            // Remove the row if qty is 0
            frm.doc.plan_items_summary = frm.doc.plan_items_summary.filter(r => r.item_code !== item_code);
        } else {
            summary_row.qty = total_qty;
            summary_row.need_to_plan_qty = flt(total_qty) - flt(summary_row.planned_qty || 0);
        }
    } else if (total_qty > 0) {
        // Add a new row
        let new_row = frm.add_child('plan_items_summary', {
            item_code: item_code,
            qty: total_qty,
            planned_qty: 0,
            need_to_plan_qty: total_qty
        });
        // Note: frm.add_child automatically appends. We will reorder below.
    }

    // --- NEW LOGIC: Reorder plan_items_summary based on plan_items_detail order ---

    // 1. Get the desired order of item_codes from plan_items_detail
    const ordered_item_codes = frm.doc.plan_items_detail.map(detail_row => detail_row.item_code);

    // 2. Create a map for quick lookup of current summary rows
    const current_summary_map = {};
    frm.doc.plan_items_summary.forEach(summary_row => {
        current_summary_map[summary_row.item_code] = summary_row;
    });

    // 3. Build a new, ordered array for plan_items_summary
    const new_ordered_summary = [];
    ordered_item_codes.forEach(item_code_from_detail => {
        if (current_summary_map[item_code_from_detail]) {
            new_ordered_summary.push(current_summary_map[item_code_from_detail]);
        }
    });

    // 4. Assign the new ordered array back to the child table
    frm.doc.plan_items_summary = new_ordered_summary;

    // --- END NEW LOGIC ---

    frm.refresh_field('plan_items_summary');
}

frappe.ui.form.on('Plan Items Detail', {
    qty(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const new_qty = flt(row.qty);

        // Get total plan_qty from plan_item_planned_wise for this item_code
        let planned_qty_total = 0;
        frm.doc.plan_item_planned_wise?.forEach(plan => {
            if (plan.item_code === row.item_code) {
                planned_qty_total += flt(plan.plan_qty);
            }
        });

        if (new_qty < planned_qty_total) {
            frappe.msgprint({
                title: __("Invalid Quantity"),
                message: __("Qty for item {0} cannot be less than total planned quantity ({1}) in Plan Item Planned Wise.", [
                    row.item_code, planned_qty_total
                ]),
                indicator: "red"
            });

            // Revert to previous value
            frappe.model.set_value(cdt, cdn, "qty", planned_qty_total);
            return;
        }

        // Proceed with summary update if valid
        sync_summary_row(frm, row.item_code);
    }
});





frappe.ui.form.on('Plan Items', {
    validate: function(frm) {
        const detail_item_codes = frm.doc.plan_items_detail.map(row => row.item_code);

        // Collect item_codes from Plan Item Planned Wise
        const planned_item_codes = (frm.doc.plan_item_planned_wise || []).map(row => row.item_code);

        // Final filter logic
        frm.doc.plan_items_summary = frm.doc.plan_items_summary.filter(row => {
            const in_detail = detail_item_codes.includes(row.item_code);
            const in_planned = planned_item_codes.includes(row.item_code);

            // Keep the row if item_code exists in detail or in planned
            return in_detail || in_planned;
        });

        frm.refresh_field('plan_items_summary');
    }
});


frappe.ui.form.on('Plan Items', {
    refresh: function (frm) {
        frm.fields_dict['plan_items_detail'].grid.get_field('bom').get_query = function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
            console.log("row",row);
            return {
                filters: {
                    item: row.item_code,
                    docstatus: 1
                }
            };
        };
    }
});

frappe.ui.form.on('Plan Items', {
    refresh: function(frm) {
       frm.set_df_property('plan_item_planned_wise', 'cannot_add_rows', true); // Hide add row button
       frm.set_df_property('plan_item_planned_wise', 'cannot_delete_rows', true); // Hide delete button
       frm.set_df_property('plan_item_planned_wise', 'cannot_delete_all_rows', true); // Hide delete all button

       frm.set_df_property('plan_items_summary', 'cannot_add_rows', true); // Hide add row button
       frm.set_df_property('plan_items_summary', 'cannot_delete_rows', true); // Hide delete button
       frm.set_df_property('plan_items_summary', 'cannot_delete_all_rows', true); // Hide delete all button
    }
});




// frappe.ui.form.on('Plan Items Detail', {
//     create_plan(frm, cdt, cdn) {
//         const row = locals[cdt][cdn];

//         if (!row.item_code || !row.bom || !row.qty) {
//             frappe.msgprint("Please fill Item Code, BOM and Qty before creating a Plan.");
//             return;
//         }

//         if (row.created_plan) {
//             frappe.msgprint(`A Plans document is already created: ${row.created_plan}`);
//             return;
//         }

//         frappe.call({
//             method: "frappe.client.insert",
//             args: {
//                 doc: {
//                     doctype: "Plans",
//                     item_code: row.item_code,
//                     bom: row.bom,
//                     plan_qty: row.qty,
//                     plan_items: frm.doc.name,
//                     posting_date: frappe.datetime.now_date(),
//                     plan_items_detail: row.name
//                 }
//             },
//             callback: function (r) {
//                 if (r.message) {
//                     // Update link in child table
//                     // frappe.model.set_value(cdt, cdn, "created_plan", r.message.name);

//                     frappe.msgprint(__('Plans document <a href="/app/plans/{0}" target="_blank">{0}</a> created successfully.', [r.message.name]));
//                     frappe.set_route("Form", "Plans", r.message.name);
//                 }
//             }
//         });
//     }
// });


function create_plans_doc(frm, cdt, cdn, source) {
    const row = locals[cdt][cdn];

    let item_code = row.item_code;
    let plan_qty = source === 'summary' ? row.need_to_plan_qty : row.qty;
    let bom = row.bom;

    if (!item_code || !plan_qty) {
        frappe.msgprint("Item Code and Quantity are required to create a Plan.");
        return;
    }

    // For summary table, get BOM from Plan Items Detail
    if (source === 'summary') {
        const detail_match = frm.doc.plan_items_detail.find(d => d.item_code === item_code );
        if (!detail_match) {
            frappe.msgprint(`No matching BOM found for item: ${item_code} in Plan Items Detail.`);
            return;
        }
        bom = detail_match.bom;
    }

    frappe.call({
        method: "frappe.client.insert",
        args: {
            doc: {
                doctype: "Plans",
                item_code: item_code,
                bom: bom,
                plan_qty: plan_qty,
                posting_date: frappe.datetime.now_date(),
                plan_items: frm.doc.name,
                plan_items_detail: source === 'detail' ? row.name : null,
                plan_items_summary: source === 'summary' ? row.name : null
            }
        },
        callback: function (r) {
            if (r.message) {
                frappe.model.set_value(cdt, cdn, "created_plan", r.message.name);

                // Open the created Plans document in a new tab
                const url = `/app/plans/${r.message.name}`;
                window.open(url, '_blank');

                // Optional: show message with clickable link
                let link = `<a href="${url}" target="_blank">${r.message.name}</a>`;
                frappe.msgprint({
                    title: __("Plans Document Created"),
                    message: __("Plans document {0} created successfully.", [link]),
                    indicator: "green"
                });
            }
        }
    });
}



// Button handler for Plan Items Detail
frappe.ui.form.on('Plan Items Detail', {
    create_plan(frm, cdt, cdn) {
        create_plans_doc(frm, cdt, cdn, 'detail');
    }
});

// Button handler for Plan Items Summary
frappe.ui.form.on('Plan Items Summary', {
    create_plan(frm, cdt, cdn) {
        create_plans_doc(frm, cdt, cdn, 'summary');
    }
});
