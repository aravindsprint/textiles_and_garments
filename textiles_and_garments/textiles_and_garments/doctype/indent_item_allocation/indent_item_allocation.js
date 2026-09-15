// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

frappe.ui.form.on("Indent Item Allocation", {
	refresh(frm) {
		console.log("frm",frm);
	},
	get_allocate_qty:function(frm){
		frappe.call({
                    method :'textiles_and_garments.textiles_and_garments.doctype.production_planning.production_planning.get_need_to_allocate_qty',
                    args: {
                    docname: frm.doc.name,
                    },
                    callback: function(response)
                    {
                        if(response.message) {
                        	console.log("response.message",response.message)
                        	// frm.doc.need_to_allocate_qty = response.message;
	                        // Update the field value
			                frm.set_value("need_to_allocate_qty", response.message);
			                frm.set_value("rm_allocated_qty", 0);
			                
			                // Save the document after updating the field
			                // frm.save();
                          
                    }
                    }
        });

    },
    validate:function(frm){
    	if(frm.doc.rm_allocated_qty > frm.doc.need_to_allocate_qty){
            frappe.throw(" 'RM allocated qty' should be less than the 'Need to allocate qty'"); 
            frappe.validated = false;
    	}
    },		
	on_submit:function(frm){
		console.log("frm.doc",frm.doc);
		frappe.call({
                    method :'textiles_and_garments.textiles_and_garments.doctype.production_planning.production_planning.set_production_plan',
                    args: {
                    docname: frm.doc.name,
                    },
                    callback: function(response)
                    {
                        if(response.message) {
                        	console.log("response.message",response.message);
                        	// frm.save();
                        // frm.refresh_field("work_order_payment_item");
                        // frm.reload_doc();
                          
                    }
                    }
        });

	}
});



