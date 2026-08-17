// Copyright (c) 2024, Aravind and contributors
// For license information, please see license.txt

frappe.ui.form.on("Dye Chart", {
	refresh(frm) {

		if(frm.doc.jobcard){
            // frappe.msgprint("Jobcard is there");
            // frappe.call({
	        //     method: "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.create_dye_chart",
	        //     args: {
	        //         docname: frm.doc.name
	        //     },
	        //     callback: function(response) {
	        //         if(response.message) {
	        //             frappe.msgprint(__('Dyechart created successfully.'));
	        //         }
	        //     }
	        // })
	        
			// frappe.call({
			// 	method :'set_values',
			// 	doc:frm.doc,
				
			// 	callback: function(r)
			// 	{
			// 	}
			// });
			    
		}
		if(frm.doc.docstatus==1|| frm.doc.docstatus==0){
			frm.add_custom_button(__('Create BOM'), function() {
				frappe.call({
					method :'make_BOM',
					doc:frm.doc,
					callback: function(r)
					{
					}
				});
			})
		}
		if(frm.doc.docstatus==1|| frm.doc.docstatus==0){
			frm.add_custom_button(__('Update JobCard'), function() {
				frappe.call({
					method :'update_jobcard',
					doc:frm.doc,
					callback: function(r)
					{
					}
				});
			})
		}

	},
	dye_receipe:function(frm){
		console.log("frm.doc.",frm.doc);
		frappe.model.with_doc("Dye Receipe", frm.doc.dye_receipe, function() {
	         var tabletransfer= frappe.model.get_doc("Dye Receipe", frm.doc.dye_receipe)
	          console.log("tabletransfer for dye_receipe ",tabletransfer);
	          frm.clear_table("dye_chart_item");
	         $.each(tabletransfer.dye_receipe_item, function(index, row){
	                console.log("inside tabletransfer",tabletransfer.dye_receipe_item);
	                console.log("inside tabletransfer",row);
	                
	                var d = frm.add_child("dye_chart_item");
	                console.log("d",d);
	                d.bath_no = row.bath_no;
	                d.mlr = row.mlr;
	                d.chemicals = row.function;
	                d.item = row.item;
	                d.dosage = row.dosage;
	                d.uom = row.uom;
	      
	                frm.refresh_field("dye_chart_item");
	               
	            }); 
	        });
		
	   
	},
	validate(frm){
		console.log("frm",frm);
	}
});
