frappe.ui.form.on('Subcontracting Order', {
    refresh(frm) {
        console.log("Subcontracting", frm);

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
