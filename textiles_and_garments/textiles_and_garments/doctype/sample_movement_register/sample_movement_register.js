// Copyright (c) 2026, Aravind and contributors

const SMR_GATE_ROLES = ["Gate Security", "System Manager"];
const SMR_OUT_STATES = ["Out", "Partially Returned", "Overdue", "Escalated"];

frappe.ui.form.on("Sample Movement Register", {
	setup(frm) {
		frm.set_query("carried_by", () => ({ filters: { status: "Active" } }));
	},

	onload(frm) {
		if (frm.is_new() && !frm.doc.carried_by) {
			frappe.db
				.get_value("Employee", { user_id: frappe.session.user, status: "Active" }, "name")
				.then(({ message }) => message && frm.set_value("carried_by", message.name));
		}
	},

	refresh(frm) {
		const is_gate = SMR_GATE_ROLES.some((r) => frappe.user.has_role(r));
		// Photos are taken on the Gate Check page; only security may touch them here.
		["gate_photo", "return_photo"].forEach((f) => frm.set_df_property(f, "read_only", is_gate ? 0 : 1));

		if (frm.doc.status === "Approved") {
			frm.dashboard.set_headline_alert(
				__("Gate pass issued — waiting for security to photograph the samples and confirm exit."),
				"orange"
			);
			if (is_gate) {
				frm.add_custom_button(__("Gate Check"), () =>
					frappe.set_route("sample-gate-check", frm.doc.gate_pass_no || frm.doc.name)
				).addClass("btn-primary");
			}
		}

		if (SMR_OUT_STATES.includes(frm.doc.status)) {
			const days = frappe.datetime.get_diff(frappe.datetime.get_today(), frm.doc.expected_return_date);
			if (days > 0) {
				frm.dashboard.set_headline_alert(__("{0} day(s) overdue", [days]), "red");
			}
			frm.add_custom_button(__("All Items Returned"), () => {
				(frm.doc.items || []).forEach((row) => {
					frappe.model.set_value(row.doctype, row.name, "returned_qty", row.quantity);
					if (!row.condition_in) frappe.model.set_value(row.doctype, row.name, "condition_in", row.condition_out || "Good");
				});
				frm.set_value("actual_return_date", frappe.datetime.get_today());
				frappe.show_alert({ message: __("Save, then use Actions → Mark Returned."), indicator: "blue" });
			}, __("Return"));
			if (is_gate) {
				frm.add_custom_button(__("Return Photo"), () =>
					frappe.set_route("sample-gate-check", frm.doc.gate_pass_no || frm.doc.name), __("Return"));
			}
		}

		if (frm.doc.docstatus === 1 && frm.doc.gate_photo) {
			frm.set_intro(
				`<img src="${encodeURI(frm.doc.gate_photo)}" style="max-height:160px;border-radius:6px;margin-right:12px">` +
					(frm.doc.return_photo
						? `<img src="${encodeURI(frm.doc.return_photo)}" style="max-height:160px;border-radius:6px">`
						: ""),
				false
			);
		}
	},

	party_type(frm) {
		frm.set_value("party_name", null);
		frm.set_value("other_party_name", null);
	},

	date_out(frm) {
		frm.trigger("validate_dates");
	},

	expected_return_date(frm) {
		frm.trigger("validate_dates");
	},

	validate_dates(frm) {
		if (frm.doc.date_out && frm.doc.expected_return_date && frm.doc.expected_return_date < frm.doc.date_out) {
			frappe.msgprint(__("Expected Return Date cannot be before Date Out."));
			frm.set_value("expected_return_date", null);
		}
	},
});

frappe.ui.form.on("Sample Movement Item", {
	item_code(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.item_code) return;
		frappe.db.get_value("Item", row.item_code, ["item_name", "description"]).then(({ message }) => {
			if (message && !row.item_description) {
				frappe.model.set_value(cdt, cdn, "item_description", message.item_name || message.description);
			}
		});
	},
	written_off(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.written_off && (row.returned_qty || 0) < row.quantity && !row.condition_in) {
			frappe.model.set_value(cdt, cdn, "condition_in", "Not Returned");
		}
	},
});
