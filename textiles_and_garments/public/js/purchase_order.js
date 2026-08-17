


frappe.ui.form.on("Purchase Order", { 
    custom_parent_fabric_work_order: function (frm) { 
        frm.doc.items.forEach(d => { 
            frappe.model.set_value(d.doctype, d.name, "custom_parent_fabric_work_order", frm.doc.custom_parent_fabric_work_order); 
        }) 
    }
});

frappe.ui.form.on('Purchase Order', {
    refresh(frm) {
        frm.add_custom_button('Select Plans', () => {
            show_plans_multi_select_dialog(frm);
        });


        frm.set_query("custom_parent_fabric_work_order", function() {
                return {
                    filters: [
                        ["docstatus", "=", 1],
                        ["custom_plan_items", "=", frm.doc.custom_plan_items],
                        // Use the dynamically constructed filter_production_item
                        // ["production_item", "like", filter_production_item]
                    ]
                };
        });


    },
    before_submit(frm){
        let requiresValidation = false;

        // Check each item in the items table
        (frm.doc.items || []).forEach(item => {
            const itemCode = item.item_code;
            console.log("Checking item:", itemCode, "Type:", item.custom_item_type);
            
            // Skip validation if custom_item_type is "Fabric"
            if (item.custom_item_type !== "Fabric" && /[.X]/i.test(itemCode)) {
                console.log("Item contains '.' or 'X' and is not Fabric");
                requiresValidation = true;
            }
        });

        if (requiresValidation) {
            console.log("Validation required for items containing '.' or 'X'");
            if (!frm.doc.custom_parent_fabric_work_order || 
                frm.doc.custom_parent_fabric_work_order === "") {
                
                frappe.msgprint(__('Parent Fabric Work Order is mandatory for Collar and Cuff WO'));
                frappe.validated = false;
            }
        }

    }
});




     

function show_plans_multi_select_dialog(frm) {
    const custom_plan_items = frm.doc.custom_plan_items;

    if (!custom_plan_items) {
        frappe.msgprint("Please select at least one Plan Item.");
        return;
    }

    let item_list = [];

    if (Array.isArray(custom_plan_items)) {
        item_list = custom_plan_items;
    } else if (typeof custom_plan_items === "string") {
        item_list = custom_plan_items.includes(",")
            ? custom_plan_items.split(",").map(s => s.trim())
            : [custom_plan_items.trim()];
    }

    frappe.call({
        method: "textiles_and_garments.textiles_and_garments.doctype.plans.plans.get_selected_plans",
        args: {
            custom_plan_items: item_list
        },
        callback: function (res) {
            const all_plans = res.message || [];
            const plan_options = all_plans.map(r => r.name);

            new frappe.ui.form.MultiSelectDialog({
                doctype: "Plans",
                target: frm,
                setters: {
                    item_code: null,
                    plan_qty: null
                },
                add_filters_group: 1,

                get_query() {
                    const filters = {};
                    const item_code = this.dialog.get_value('item_code');
                    const plan_qty = this.dialog.get_value('plan_qty');

                    if (item_code) filters.item_code = item_code;
                    if (plan_qty) filters.plan_qty = plan_qty;

                    filters.name = ["in", plan_options];

                    return { filters };
                },

                primary_action_label: 'Add to Purchase Order',

                action(selected_names) {
                    if (!selected_names || selected_names.length === 0) return;

                    const selected_plans = all_plans.filter(r => selected_names.includes(r.name));

                    const existing_plans = (frm.doc.items || []).map(row => row.custom_plans);
                    console.log("existing_plans",existing_plans);

                    const new_plans = selected_plans.filter(plan => !existing_plans.includes(plan.name));
                    console.log("new_plans",new_plans);

                    if (new_plans.length === 0) {
                        frappe.msgprint("Selected Plans are already added.");
                        this.dialog.hide();
                        return;
                    }

                    frm.clear_table('items');

                    if(frm.doc.is_subcontracted == 1){
                        new_plans.forEach(plan => {
                        frm.add_child('items', {
                                fg_item: plan.item_code,
                                custom_plans: plan.name,
                                fg_item_qty: plan.plan_qty,
                                qty: plan.plan_qty
                            });
                        });

                        frm.refresh_field('items');

                        frappe.msgprint(`${new_plans.length} new plan(s) added to the Purchase Order Item.`);
                        this.dialog.hide();

                    }
                    else{
                        new_plans.forEach(plan => {
                        frm.add_child('items', {
                                item_code: plan.item_code,
                                custom_plans: plan.name,
                                // fg_item_qty: plan.plan_qty,
                                qty: plan.plan_qty
                            });
                        });

                        frm.refresh_field('items');

                        frappe.msgprint(`${new_plans.length} new plan(s) added to the Purchase Order Item.`);
                        this.dialog.hide();

                    }

                    
                }
            });
        }
    });
}




