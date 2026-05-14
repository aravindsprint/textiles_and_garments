frappe.ui.form.on("Time and Action", {
    validate(frm) {
        validate_all_sequential_dates(frm);
    }
});

frappe.ui.form.on("Time and Action Item", {
    start_date(frm, cdt, cdn) {
        calculate_days(frm, cdt, cdn);
        validate_date_sequence(frm, cdt, cdn);
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

    // Only validate Sequential rows
    if (row.method !== "Sequential") return;
    if (!row.start_date) return;

    // Find the last Sequential row before this one
    const prevSequential = rows
        .filter(r => r.idx < row.idx && r.method === "Sequential" && r.end_date)
        .sort((a, b) => b.idx - a.idx)[0];  // highest idx before current

    if (!prevSequential) return;

    const prevEnd   = frappe.datetime.str_to_obj(prevSequential.end_date);
    const currStart = frappe.datetime.str_to_obj(row.start_date);

    if (currStart <= prevEnd) {
        frappe.msgprint({
            title: "Date Overlap",
            indicator: "red",
            message: `Row ${row.idx} <b>${row.process_name || "Current"}</b>: 
                      Start Date must be after Row ${prevSequential.idx} 
                      <b>${prevSequential.process_name || "Previous"}</b> End Date 
                      (${prevSequential.end_date}).`
        });
        frappe.model.set_value(cdt, cdn, "start_date", "");
    }
}

// Called on form validate (submit guard)
function validate_all_sequential_dates(frm) {
    const rows = frm.doc.time_and_action_item || [];
    const sequential = rows
        .filter(r => r.method === "Sequential")
        .sort((a, b) => a.idx - b.idx);

    for (let i = 1; i < sequential.length; i++) {
        const prev = sequential[i - 1];
        const curr = sequential[i];
        if (!prev.end_date || !curr.start_date) continue;

        const prevEnd   = frappe.datetime.str_to_obj(prev.end_date);
        const currStart = frappe.datetime.str_to_obj(curr.start_date);

        if (currStart <= prevEnd) {
            frappe.throw(
                `Row ${curr.idx} <b>${curr.process_name}</b>: Start Date must be after 
                 Row ${prev.idx} <b>${prev.process_name}</b> End Date (${prev.end_date}).`
            );
        }
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