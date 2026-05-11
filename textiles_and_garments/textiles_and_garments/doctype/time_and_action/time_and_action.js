frappe.ui.form.on("Time and Action Item", {
    start_date(frm, cdt, cdn) {
        // validate_date_sequence(frm, cdt, cdn);
        calculate_days(frm, cdt, cdn);
    },
    end_date(frm, cdt, cdn) {
        calculate_days(frm, cdt, cdn);
    },
    method(frm, cdt, cdn) {
        update_total(frm);
    },
    time_and_action_item_remove(frm) {
        update_total(frm);
    }
});

function validate_date_sequence(frm, cdt, cdn) {
    const row  = locals[cdt][cdn];
    const rows = frm.doc.time_and_action_item || [];
    const idx  = row.idx;

    if (idx <= 1) return;

    const prev = rows.find(r => r.idx === idx - 1);
    if (!prev || !prev.end_date || !row.start_date) return;

    const prevEnd   = frappe.datetime.str_to_obj(prev.end_date);
    const currStart = frappe.datetime.str_to_obj(row.start_date);

    if (currStart <= prevEnd) {
        frappe.msgprint({
            title: "Date Overlap",
            indicator: "red",
            message: `Row ${idx} <b>${row.process_name || "Current"}</b>: 
                      Start Date must be after Row ${prev.idx} 
                      <b>${prev.process_name || "Previous"}</b> End Date 
                      (${prev.end_date}).`
        });
        frappe.model.set_value(cdt, cdn, "start_date", "");
    }
}

function calculate_days(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (row.start_date && row.end_date) {
        const days = frappe.datetime.get_diff(
            frappe.datetime.str_to_obj(row.end_date),
            frappe.datetime.str_to_obj(row.start_date)
        );
        frappe.model.set_value(cdt, cdn, "no_of_days_to_deliver", days < 0 ? 0 : days);
    }
    update_total(frm);
}

function update_total(frm) {
    const total = (frm.doc.time_and_action_item || []).reduce((sum, row) => {
        if (row.method === "Parallel") return sum;
        return sum + (row.no_of_days_to_deliver || 0);
    }, 0);

    frm.set_value("total_no_of_days_to_deliver", total);
}