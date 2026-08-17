// Copyright (c) 2026, Aravind and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project Wise MRR", {
	refresh(frm) {

	},
	get_data: function (frm) {
        frappe.call({
            method: 'textiles_and_garments.textiles_and_garments.doctype.project_wise_mrr.project_wise_mrr.get_data',
            args: {
                docname: frm.doc.name,
                purchase_orders: frm.doc.purchase_orders
            },
            callback: function (response) {
                if (response.message && Array.isArray(response.message)) {
                    // console.log("Filtered stock items:", response.message);
                    // Reload the form to show the updated sent_details tables
                    frm.reload_doc();
                }
            }
        });
    },
});
