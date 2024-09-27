frappe.ui.form.on("Job Card", {
    validate:function(frm){
        console.log("inside public", frm);
        // if(frm.doc.job_card){
        //     frm.doc.items.forEach(d => {
        //     frappe.model.set_value(d.doctype, d.name, "job_card", frm.doc.job_card);
        //     });

        // }
        
        var water_reading = 0;
        water_reading = frm.doc.custom_water_reading_at_end - frm.doc.custom_water_reading_at_start;
        frm.set_value("custom_water_reading_value", water_reading);

        if(frm.doc.bom_no){
            frappe.call({
                method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.create_bom_scrap_items",
                args: {
                    docname: frm.doc.bom_no,
                },
                callback: function(response) {
                    console.log("response",response);
                    if(response.message) {
                       
                            // Clear existing items from stock_entry_items table
                            frm.clear_table("scrap_items");

                            // Iterate through the returned items and add them to stock_entry_items
                            response.message.forEach(function(item) {
                                
                                
                                    let child = frm.add_child("scrap_items");
                                    child.item_code = item.item_code;
                                    child.stock_qty = item.stock_qty; // Or any other field mapping
                                    // Set other fields from item as needed
                                    child.stock_uom = item.stock_uom;
                                
                                    //child.uom = item.stock_uom;
                                    // child.conversion_factor = 1;
                                    // child.s_warehouse = "Stores - PSS";
                                    // child.t_warehouse = "Work In Progress - PSS";
                                    child.parentfield = "scrap_items";
                                    child.parenttype = "Job Card";
                                    //child.job_card_item = item.name;
                                    child.doctype = "Job Card Scrap Item";

                                
                                

                            });

                            // Refresh the field to update UI
                            frm.refresh_field("items");

                            //Save the form after setting items
                            //frm.save();

                        
                      
                        
                    }
                }
            });
        }
    },
    setup:function(frm){
        // if(frm.doc.job_card){
        //     frm.doc.items.forEach(d => {
        //     frappe.model.set_value(d.doctype, d.name, "custom_job_card", frm.doc.job_card);
        //     });

        // }

    }


});


