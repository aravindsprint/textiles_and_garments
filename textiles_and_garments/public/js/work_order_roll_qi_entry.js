// textiles_and_garments/public/js/work_order_roll_qi_entry.js
// -----------------------------------------------------------------
// Child Table Client Script — Work Order Roll QI Entry
//
// NOTE: frappe.db.get_value is NOT used for Roll fields because
// Frappe's reportview validator blocks reserved words like "item".
// frappe.call → frappe.client.get is used instead.
//
// Roll DocType fieldnames (confirmed from DB):
//   item_code   → Link → Item
//   roll_weight → Float
//   total_qty   → Int
//   stock_uom   → Link → UOM
// -----------------------------------------------------------------

frappe.ui.form.on("Work Order Roll QI Entry", {

    // ----------------------------------------------------------
    // Roll selected: pull fields from Roll via frappe.call
    // ----------------------------------------------------------
    roll: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.roll) return;

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Roll",
                name: row.roll
            },
            callback: function (r) {
                if (!r.message) return;
                const roll = r.message;
                frappe.model.set_value(cdt, cdn, "item",        roll.item_code  || "");
                frappe.model.set_value(cdt, cdn, "roll_weight", roll.roll_weight || 0);
                frappe.model.set_value(cdt, cdn, "total_qty",   roll.total_qty  || 0);
                frappe.model.set_value(cdt, cdn, "uom",         roll.stock_uom  || "");
            }
        });
    },

    // ----------------------------------------------------------
    // QI linked: mirror the current QI status into this row
    // ----------------------------------------------------------
    quality_inspection: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.quality_inspection) return;

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Quality Inspection",
                name: row.quality_inspection
            },
            callback: function (r) {
                if (!r.message) return;
                const qi_status_map = {
                    "Accepted": "Accepted",
                    "Rejected": "Rejected"
                };
                const mapped = qi_status_map[r.message.status] || "Pending";
                frappe.model.set_value(cdt, cdn, "qi_status", mapped);
            }
        });
    }
});