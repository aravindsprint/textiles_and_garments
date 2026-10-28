// Sample Gate Check — the simplified screen for gate security.
// Look up a gate pass (type or scan the QR on the print), see the expected
// items, photograph the outgoing samples and confirm exit. Also takes an
// optional return photo when samples come back in.

const SGC_API = "textiles_and_garments.textiles_and_garments.doctype.sample_movement_register.sample_movement_register";
const SGC_OUT_STATES = ["Out", "Partially Returned", "Overdue", "Escalated", "Returned", "Written Off"];

frappe.pages["sample-gate-check"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Sample Gate Check"), single_column: true });
	wrapper.sgc = new SampleGateCheck(page);
};

frappe.pages["sample-gate-check"].on_page_show = function (wrapper) {
	const route_arg = frappe.get_route()[1];
	if (route_arg && wrapper.sgc) wrapper.sgc.lookup(decodeURIComponent(route_arg));
};

class SampleGateCheck {
	constructor(page) {
		this.page = page;
		this.photo = null;
		this.pass = null;
		this.make();
	}

	make() {
		const $body = $(`
			<div class="sgc">
				<style>
					.sgc { max-width: 720px; margin: 0 auto; }
					.sgc-search { display: flex; gap: 8px; margin: 12px 0 16px; }
					.sgc-search input { flex: 1; font-size: 18px; height: 48px; }
					.sgc-search .btn { height: 48px; min-width: 56px; }
					.sgc-card { border: 1px solid var(--border-color); border-radius: 10px; padding: 16px; background: var(--card-bg); }
					.sgc-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap; }
					.sgc-head h3 { margin: 0; font-size: 20px; }
					.sgc-meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px 16px; margin: 12px 0; font-size: 14px; }
					.sgc-meta .lbl { color: var(--text-muted); font-size: 12px; }
					.sgc-items { width: 100%; font-size: 14px; border-collapse: collapse; }
					.sgc-items th, .sgc-items td { border-bottom: 1px solid var(--border-color); padding: 6px 4px; text-align: left; vertical-align: top; }
					.sgc-photo-btn { width: 100%; height: 56px; font-size: 17px; margin-top: 16px; }
					.sgc-preview { width: 100%; max-height: 420px; object-fit: contain; border-radius: 8px; margin-top: 12px; background: var(--subtle-fg); }
					.sgc-confirm { width: 100%; height: 56px; font-size: 18px; margin-top: 12px; }
					.sgc-msg { padding: 12px; border-radius: 8px; margin-top: 12px; font-size: 15px; }
					.sgc-msg.ok { background: var(--green-highlight-color, #e4f5e9); }
					.sgc-msg.bad { background: var(--red-highlight-color, #fde8e8); }
					.sgc-photos { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
					.sgc-photos img { max-height: 180px; border-radius: 8px; }
				</style>
				<div class="sgc-search">
					<input type="text" class="form-control sgc-input" placeholder="${__("Gate pass no, e.g. SMR-2026-00012")}" autocomplete="off">
					<button class="btn btn-default sgc-scan" title="${__("Scan QR")}">${frappe.utils.icon("scan", "md")}</button>
					<button class="btn btn-primary sgc-find">${__("Find")}</button>
				</div>
				<div class="sgc-result"></div>
				<input type="file" accept="image/*" capture="environment" class="sgc-file" hidden>
			</div>
		`).appendTo(this.page.body);

		this.$input = $body.find(".sgc-input");
		this.$result = $body.find(".sgc-result");
		this.$file = $body.find(".sgc-file");

		$body.find(".sgc-find").on("click", () => this.lookup(this.$input.val()));
		this.$input.on("keydown", (e) => e.key === "Enter" && this.lookup(this.$input.val()));
		$body.find(".sgc-scan").on("click", () => this.scan());
		this.$file.on("change", (e) => this.on_file(e.target.files[0]));
		setTimeout(() => this.$input.focus(), 300);
	}

	scan() {
		if (!frappe.ui.Scanner) {
			frappe.msgprint(__("QR scanning is not available in this browser — type the gate pass number."));
			return;
		}
		new frappe.ui.Scanner({
			dialog: true,
			multiple: false,
			on_scan: (result) => {
				const text = (result && (result.decodedText || result.text)) || "";
				this.$input.val(text);
				this.lookup(text);
			},
		});
	}

	lookup(value) {
		value = (value || "").trim();
		if (!value) return;
		this.$input.val(value);
		this.photo = null;
		frappe.call({
			method: `${SGC_API}.get_gate_pass`,
			args: { gate_pass_no: value },
			freeze: true,
			callback: (r) => {
				this.pass = r.message;
				this.render();
			},
			error: () => {
				this.pass = null;
				this.$result.empty();
			},
		});
	}

	render() {
		const p = this.pass;
		if (!p) return this.$result.empty();
		const esc = frappe.utils.escape_html;
		const can_exit = p.status === "Approved";
		const can_return_photo = SGC_OUT_STATES.includes(p.status);
		const status_color = { Approved: "orange", Out: "blue", Returned: "green", Overdue: "red", Escalated: "red" }[p.status] || "gray";

		let banner = "";
		if (["Draft", "Pending Approval"].includes(p.status)) {
			banner = `<div class="sgc-msg bad">${__("NOT APPROVED — do not allow these samples out.")}</div>`;
		} else if (p.status === "Cancelled") {
			banner = `<div class="sgc-msg bad">${__("This gate pass is CANCELLED.")}</div>`;
		} else if (p.status === "Out" || (p.exited_on && !can_exit)) {
			banner = `<div class="sgc-msg ok">${__("Exit already confirmed on {0} by {1}.", [
				frappe.datetime.str_to_user(p.exited_on) || "-",
				esc(p.exit_confirmed_by || "-"),
			])}</div>`;
		}

		const items = (p.items || [])
			.map(
				(i) => `<tr>
					<td>${i.idx}</td>
					<td><b>${esc(i.description || "")}</b>${i.item_code ? `<br><small>${esc(i.item_code)}</small>` : ""}
						${i.fabric_type || i.color ? `<br><small>${esc([i.fabric_type, i.color].filter(Boolean).join(" · "))}</small>` : ""}</td>
					<td style="white-space:nowrap">${i.quantity} ${esc(i.unit || "")}</td>
					<td>${esc(i.condition_out || "")}</td>
				</tr>`
			)
			.join("");

		const photos = [p.gate_photo && `<img src="${encodeURI(p.gate_photo)}" title="${__("Outgoing")}">`,
			p.return_photo && `<img src="${encodeURI(p.return_photo)}" title="${__("Return")}">`].filter(Boolean).join("");

		this.$result.html(`
			<div class="sgc-card">
				<div class="sgc-head">
					<h3>${esc(p.gate_pass_no || p.name)}</h3>
					<span class="indicator-pill ${status_color}">${__(p.status)}</span>
				</div>
				${banner}
				<div class="sgc-meta">
					<div><div class="lbl">${__("Employee")}</div>${esc(p.carried_by_name || p.carried_by)}</div>
					<div><div class="lbl">${__("Department")}</div>${esc(p.department || "-")}</div>
					<div><div class="lbl">${__("Party")}</div>${esc(p.party || "-")} <small>(${esc(p.party_type || "")})</small></div>
					<div><div class="lbl">${__("Purpose")}</div>${esc(p.purpose || "-")}</div>
					<div><div class="lbl">${__("Expected Back")}</div>${frappe.datetime.str_to_user(p.expected_return_date)}</div>
					<div><div class="lbl">${__("Approved By")}</div>${esc(p.approved_by_name || "-")}</div>
				</div>
				<table class="sgc-items">
					<thead><tr><th>#</th><th>${__("Item")}</th><th>${__("Qty")}</th><th>${__("Cond.")}</th></tr></thead>
					<tbody>${items}</tbody>
				</table>
				${photos ? `<div class="sgc-photos">${photos}</div>` : ""}
				${can_exit ? `<button class="btn btn-default sgc-photo-btn">${frappe.utils.icon("camera", "md")} ${__("Take Photo of Outgoing Samples")}</button>` : ""}
				${can_return_photo ? `<button class="btn btn-default sgc-photo-btn">${frappe.utils.icon("camera", "md")} ${__("Take Return Photo")}</button>` : ""}
				<img class="sgc-preview" hidden>
				${can_exit ? `<button class="btn btn-primary sgc-confirm" disabled>${__("Confirm Exit")}</button>` : ""}
				${can_return_photo ? `<button class="btn btn-primary sgc-confirm" disabled>${__("Save Return Photo")}</button>` : ""}
			</div>
		`);

		this.$result.find(".sgc-photo-btn").on("click", () => this.$file.val("").trigger("click"));
		this.$result.find(".sgc-confirm").on("click", () => (can_exit ? this.confirm_exit() : this.save_return_photo()));
	}

	on_file(file) {
		if (!file) return;
		this.compress(file).then((data_url) => {
			this.photo = data_url;
			this.$result.find(".sgc-preview").attr("src", data_url).prop("hidden", false);
			this.$result.find(".sgc-confirm").prop("disabled", false);
		});
	}

	// Phone cameras produce 4–12 MB photos; shrink to ~1600px JPEG before upload.
	compress(file, max = 1600, quality = 0.8) {
		return new Promise((resolve, reject) => {
			const reader = new FileReader();
			reader.onerror = reject;
			reader.onload = () => {
				const img = new Image();
				img.onerror = () => resolve(reader.result);
				img.onload = () => {
					const scale = Math.min(1, max / Math.max(img.width, img.height));
					const canvas = document.createElement("canvas");
					canvas.width = Math.round(img.width * scale);
					canvas.height = Math.round(img.height * scale);
					canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
					resolve(canvas.toDataURL("image/jpeg", quality));
				};
				img.src = reader.result;
			};
			reader.readAsDataURL(file);
		});
	}

	confirm_exit() {
		if (!this.photo) return frappe.msgprint(__("Take a photo of the outgoing samples first."));
		frappe.confirm(__("Items and quantities match what is physically leaving?"), () => {
			frappe.call({
				method: `${SGC_API}.confirm_exit`,
				args: { gate_pass_no: this.pass.name, image_data: this.photo },
				freeze: true,
				freeze_message: __("Uploading photo…"),
				callback: () => {
					frappe.show_alert({ message: __("Exit confirmed for {0}", [this.pass.name]), indicator: "green" }, 6);
					this.lookup(this.pass.name);
				},
			});
		});
	}

	save_return_photo() {
		if (!this.photo) return;
		frappe.call({
			method: `${SGC_API}.save_return_photo`,
			args: { gate_pass_no: this.pass.name, image_data: this.photo },
			freeze: true,
			freeze_message: __("Uploading photo…"),
			callback: () => {
				frappe.show_alert({ message: __("Return photo saved for {0}", [this.pass.name]), indicator: "green" }, 6);
				this.lookup(this.pass.name);
			},
		});
	}
}
