// Copyright (c) 2026, Aravind and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project Wise MRR", {
    refresh(frm) {

    },
    get_data: function (frm) {
        frappe.call({
            method: 'textiles_and_garments.textiles_and_garments.doctype.project_wise_mrr.project_wise_mrr.calculate_process_loss_by_project',
            args: {
                doc: frm.doc
            },
            freeze: true,
            freeze_message: __('Fetching Data...'),
            callback: function (r) {
                if (r.message) {
                    frappe.model.sync(r.message);
                    frm.refresh();
                }
            }
        });
    },
});