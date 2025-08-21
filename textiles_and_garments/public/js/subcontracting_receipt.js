frappe.ui.form.on('Subcontracting Receipt', {
    refresh(frm) {
        console.log("Subcontracting Receipt", frm);

        const so_map = {}; // to avoid re-fetching the same Subcontracting Order multiple times
        const receipt_items = frm.doc.items || [];

        const unique_so_names = [
            ...new Set(receipt_items.map(row => row.subcontracting_order).filter(Boolean))
        ];

        // Step 1: Load all unique Subcontracting Orders
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Subcontracting Order",
                filters: [
                    ["name", "in", unique_so_names]
                ],
                fields: ["name"]
            },
            callback: function(list_response) {
                if (!list_response.message || list_response.message.length === 0) return;

                const fetch_promises = unique_so_names.map(so_name => {
                    return new Promise((resolve) => {
                        frappe.model.with_doc("Subcontracting Order", so_name, function() {
                            const so_doc = frappe.model.get_doc("Subcontracting Order", so_name);
                            so_map[so_name] = so_doc;
                            resolve();
                        });
                    });
                });

                // Step 2: After all Subcontracting Orders are loaded
                Promise.all(fetch_promises).then(() => {
                    receipt_items.forEach(receipt_row => {
                        const so_doc = so_map[receipt_row.subcontracting_order];
                        if (!so_doc) return;

                        const matching_so_item = so_doc.items.find(
                            so_item => so_item.name === receipt_row.subcontracting_order_item
                        );

                        if (matching_so_item) {
                            receipt_row.custom_plans = matching_so_item.custom_plans;
                        }
                    });

                    frm.refresh_field("items");
                });
            }
        });
    }
});
