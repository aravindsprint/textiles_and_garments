frappe.ui.form.on("Serial and Batch Bundle", {

    refresh: function(frm) {
        console.log("frm",frm);
         frm.add_custom_button(__('Update Batch'), function() {
            frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.update_batch_sbb",
                args: {
                    docname: frm.doc.name,
                    duplicate_stock_entry_name: frm.doc.custom_duplicate_stock_entry
                },
                callback: function(response) {
                    console.log("response", response);
                    if (response.message) {
                        var resp = response.message;

                        console.log("resp", resp);

                        // Loop through frm.doc.items
                        resp.forEach(item => {
                            console.log("item",item);
                            frm.clear_table("entries");
                            let newRow = frm.add_child('entries');
                            
                            // newRow.item_code = item.item_code; // Example: Set item_code
                            newRow.batch_no = item.batch_no;   // Example: Set batch_no
                            newRow.qty = item.qty * -1;            // Example: Set qty
                            newRow.warehouse = frm.doc.warehouse; // 
                            
                        });

                        // Refresh the field to reflect changes in the UI
                        frm.refresh_field('entries');
                    }
                }
            });
        });

    },

});
