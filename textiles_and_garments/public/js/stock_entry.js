frappe.ui.form.on("Stock Entry", {
    refresh:function(frm){
        console.log("inside public in js", frm);
        // if(frm.doc.job_card){
        //     frm.doc.items.forEach(d => {
        //     frappe.model.set_value(d.doctype, d.name, "job_card", frm.doc.job_card);
        //     });

        // }
        if(frm.doc.job_card){
            frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.create_stock_entry_items",
                args: {
                    docname: frm.doc.job_card,
                },
                callback: function(response) {
                    console.log("inside response",response);
                    if(response.message) {
                        if(!frm.doc.name.includes("MAT-STE") ){
                            // Clear existing items from stock_entry_items table
                            frm.clear_table("items");

                            // Iterate through the returned items and add them to stock_entry_items
                            response.message.forEach(function(item) {
                                
                                qty = item.required_qty - item.transferred_qty;
                                if(qty > 0){
                                    let child = frm.add_child("items");
                                    child.item_code = item.item_code;
                                    child.qty = item.required_qty - item.transferred_qty; // Or any other field mapping
                                    // Set other fields from item as needed
                                    child.stock_uom = item.stock_uom;
                                    child.transfer_qty = item.required_qty - item.transferred_qty;
                                    child.uom = item.stock_uom;
                                    child.conversion_factor = 1;
                                    child.s_warehouse = "Stores - PSS";
                                    child.t_warehouse = "Work In Progress - PSS";
                                    child.parentfield = "items";
                                    child.parenttype = "Stock Entry";
                                    child.job_card_item = item.name;
                                    child.doctype = "Stock Entry Detail";

                                }
                                

                            });

                            // Refresh the field to update UI
                            frm.refresh_field("items");

                            //Save the form after setting items
                            //frm.save();

                        }
                      
                        
                    }
                }
            });
        }
          },
    // validate:function(frm){
    //     if(frm.doc.job_card){
    //         frm.doc.items.forEach(d => {
    //         frappe.model.set_value(d.doctype, d.name, "custom_job_card", frm.doc.job_card);
    //         });

    //     }

    // }


});