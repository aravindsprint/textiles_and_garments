// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt



frappe.ui.form.on("Production Planning", {
    refresh(frm) {
    	// cur_frm.fields_dict["production_planning_items"].$wrapper.find('.grid-body .rows').find(".grid-row").each(function(i, item) {
	    //         let d = locals[cur_frm.fields_dict["production_planning_items"].grid.doctype][$(item).attr('data-name')];
	    //         if(d["pending_qty"] >= 80){
		//             $(item).find('.grid-static-col').css({'background-color': 'yellow'});
	    //         }
	    //         else {
	    //             $(item).find('.grid-static-col').css({'background-color': 'transparent'});
	    //         }
        //     });

        // let lastRowMap = {}; // Store the last row reference for each raw_material_item

		// cur_frm.fields_dict["production_planning_items"].$wrapper.find('.grid-body .rows').find(".grid-row").each(function(i, item) {
		//     let d = locals[cur_frm.fields_dict["production_planning_items"].grid.doctype][$(item).attr('data-name')];

		//     if (d.raw_material_item) {
		//         lastRowMap[d.raw_material_item] = item; // Keep updating with the latest row
		//     }
		// });

		// // Loop through the last row of each raw_material_item and change the color
		// Object.values(lastRowMap).forEach(item => {
		// 	console.log("item",item);
		//     $(item).find('.grid-static-col').css({ 'background-color': 'yellow' });
		// });
		let lastRowMap = {}; // Store the last row reference for each raw_material_item

		cur_frm.fields_dict["production_planning_items"].$wrapper.find('.grid-body .rows').find(".grid-row").each(function(i, item) {
		    let d = locals[cur_frm.fields_dict["production_planning_items"].grid.doctype][$(item).attr('data-name')];

		    if (d.raw_material_item) {
		        lastRowMap[d.raw_material_item] = { row: item, to_allocate_qty: d.to_allocate_qty }; // Store row and qty
		    }
		});

		// Loop through the last row of each raw_material_item and change the color based on to_allocate_qty
		Object.values(lastRowMap).forEach(({ row, to_allocate_qty }) => {
		    let bgColor = to_allocate_qty == 0 ? '' : 'yellow'; // Set color based on to_allocate_qty
		    $(row).find('.grid-static-col').css({ 'background-color': bgColor });
		});


    	
        
    },
    get_summary:function(frm){
		console.log("get_summary");
		frappe.call({
                    method :'textiles_and_garments.textiles_and_garments.doctype.production_planning.production_planning.set_production_plan_item_summary',
                    args: {
                    docname: frm.doc.name,
                    },
                    callback: function(response)
                    {
                        if(response.message) {
                        	console.log("response.message",response.message);
                        	frm.save();
                        // frm.refresh_field("work_order_payment_item");
                        // frm.reload_doc();
                          
                    }
                    }
        });
	},
	get_process_summary:function(frm){
		console.log("get_summary");
		frappe.call({
                    method :'textiles_and_garments.textiles_and_garments.doctype.production_planning.production_planning.set_production_plan_process_summary',
                    args: {
                    docname: frm.doc.name,
                    },
                    callback: function(response)
                    {
                        if(response.message) {
                        	console.log("response.message",response.message);
                        	frm.save();
                        // frm.refresh_field("work_order_payment_item");
                        // frm.reload_doc();
                          
                    }
                    }
        });
	},
});


