# Copyright (c) 2026, Aravind and contributors
# For license information, please see license.txt
"""Sample Movement Register — non-stock gate pass for reference samples.

Lifecycle (status is also the Workflow state field):

    Draft -> Pending Approval -> Approved (submitted, gate pass issued)
          -> Out (security confirmed exit with photo)
          -> Partially Returned / Overdue / Escalated
          -> Returned | Written Off

Never touches the Stock Ledger.
"""

import base64
import io

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, now_datetime, today

GATE_ROLES = {"Gate Security", "System Manager"}
OUT_STATES = ("Out", "Partially Returned", "Overdue", "Escalated")
CLOSED_STATES = ("Returned", "Written Off")
WHOLE_NUMBER_UNITS = ("Pcs", "Nos")
MAX_PHOTO_BYTES = 8 * 1024 * 1024


class SampleMovementRegister(Document):
	# ------------------------------------------------------------------ hooks
	def validate(self):
		self.set_carried_by_default()
		self.set_approver()
		self.validate_dates()
		self.validate_items()
		self.set_return_progress()
		self.set_title()
		if self.party_type == "Other":
			self.party_name = None

	def before_submit(self):
		# Gate pass is issued the moment the reporting manager approves.
		self.gate_pass_no = self.name
		if self.status not in ("Approved",):
			frappe.throw(_("A gate pass can only be issued through manager approval."))

	def on_submit(self):
		self.notify_carrier(
			_("Gate pass {0} approved").format(self.name),
			_("Your sample gate pass {0} has been approved. Show it at the gate; security will photograph the samples before exit.").format(self.name),
		)

	def before_update_after_submit(self):
		before = self.get_doc_before_save()
		prev_status = before.status if before else None

		self.validate_items(returns_only=True)
		self.set_return_progress()
		self.validate_photo_changes(before)
		self.validate_status_change(prev_status)

	def on_update(self):
		before = self.get_doc_before_save()
		prev_status = before.status if before else None
		if self.status == "Pending Approval" and prev_status != "Pending Approval":
			self.notify_approver()
		elif self.status == "Draft" and prev_status == "Pending Approval":
			self.notify_carrier(
				_("Gate pass {0} sent back").format(self.name),
				_("Your sample gate pass {0} was rejected / sent back by the approver. Please review and resubmit.").format(self.name),
			)

	def on_cancel(self):
		self.db_set("status", "Cancelled")

	# --------------------------------------------------------------- helpers
	def set_carried_by_default(self):
		if not self.carried_by:
			self.carried_by = frappe.db.get_value("Employee", {"user_id": frappe.session.user, "status": "Active"}, "name")
		if not self.carried_by:
			frappe.throw(_("Carried By is mandatory — your user is not linked to an Employee record."))

	def set_approver(self):
		"""Approver = Reports To of the carrier (never hard-coded)."""
		if self.docstatus != 0:
			return
		manager = frappe.db.get_value("Employee", self.carried_by, "reports_to")
		self.approved_by = manager
		self.approver_user = frappe.db.get_value("Employee", manager, "user_id") if manager else None

	def validate_dates(self):
		if self.date_out and self.expected_return_date and getdate(self.expected_return_date) < getdate(self.date_out):
			frappe.throw(_("Expected Return Date cannot be before Date Out."))
		if self.actual_return_date and self.date_out and getdate(self.actual_return_date) < getdate(self.date_out):
			frappe.throw(_("Actual Return Date cannot be before Date Out."))

	def validate_items(self, returns_only=False):
		if not self.items:
			frappe.throw(_("Add at least one sample item."))
		for row in self.items:
			if not returns_only and flt(row.quantity) <= 0:
				frappe.throw(_("Row #{0}: Quantity must be greater than zero.").format(row.idx))
			if row.unit in WHOLE_NUMBER_UNITS:
				for field in ("quantity", "returned_qty"):
					if flt(row.get(field)) % 1:
						frappe.throw(
							_("Row #{0}: {1} must be a whole number for unit {2}.").format(
								row.idx, row.meta.get_label(field), row.unit
							)
						)
			if flt(row.returned_qty) > flt(row.quantity):
				frappe.throw(_("Row #{0}: Returned Qty cannot exceed Quantity ({1}).").format(row.idx, row.quantity))
			if row.written_off and not (row.return_remarks or "").strip():
				frappe.throw(_("Row #{0}: Add a return remark explaining the write-off.").format(row.idx))
			if row.written_off and flt(row.returned_qty) < flt(row.quantity) and not row.condition_in:
				row.condition_in = "Not Returned"

	def set_return_progress(self):
		resolved, touched, wrote_off = 0, 0, False
		for row in self.items:
			fully_back = flt(row.returned_qty) >= flt(row.quantity)
			if fully_back or row.written_off:
				resolved += 1
			if flt(row.returned_qty) > 0 or row.written_off:
				touched += 1
			if row.written_off and not fully_back:
				wrote_off = True

		if self.items and resolved == len(self.items):
			self.return_progress = "Resolved with Write-off" if wrote_off else "Fully Returned"
		elif touched:
			self.return_progress = "Partially Returned"
		else:
			self.return_progress = "Not Returned"

	def set_title(self):
		party = self.party_name or self.other_party_name or ""
		self.title = f"{self.carried_by_name or self.carried_by} → {party}".strip(" →")

	def validate_photo_changes(self, before):
		if not before:
			return
		privileged = GATE_ROLES & set(frappe.get_roles())
		for field in ("gate_photo", "return_photo"):
			if self.get(field) != before.get(field) and not (privileged or self.flags.from_gate_check):
				frappe.throw(_("Only Gate Security can change the {0}.").format(self.meta.get_label(field)))
		if before.gate_photo and self.gate_photo != before.gate_photo and before.status != "Approved":
			frappe.throw(_("The outgoing gate photo cannot be replaced after the samples have left."))

	def validate_status_change(self, prev_status):
		status = self.status
		if prev_status == status:
			if status == "Approved" and self.return_progress != "Not Returned":
				frappe.throw(_("These samples have not left the gate yet — returns cannot be recorded."))
			return

		if status == "Out" and prev_status == "Approved":
			if not self.gate_photo:
				frappe.throw(_("A gate photo of the outgoing samples is mandatory before exit can be confirmed."))
			self.exit_confirmed_by = self.exit_confirmed_by or frappe.session.user
			self.exited_on = self.exited_on or now_datetime()

		expected = {
			"Partially Returned": "Partially Returned",
			"Returned": "Fully Returned",
			"Written Off": "Resolved with Write-off",
		}
		if status in expected and self.return_progress != expected[status]:
			frappe.throw(
				_("Cannot mark as {0}: item lines show {1}. Update Returned Qty / Written Off and save first.").format(
					frappe.bold(status), frappe.bold(self.return_progress)
				)
			)

		if status in ("Partially Returned", "Returned", "Written Off") and not self.actual_return_date:
			self.actual_return_date = today()

	# --------------------------------------------------------- notifications
	def notify_carrier(self, subject, message):
		from textiles_and_garments.textiles_and_garments.doctype.sample_movement_register.reminders import (
			employee_contact,
			notify,
		)

		notify([employee_contact(self.carried_by)], subject, message, self.name)

	def notify_approver(self):
		from textiles_and_garments.textiles_and_garments.doctype.sample_movement_register.reminders import (
			fallback_approver_contacts,
			notify,
		)

		recipients = [(self.approver_user, None)] if self.approver_user else fallback_approver_contacts()
		notify(
			recipients,
			_("Approval needed: sample gate pass {0}").format(self.name),
			_("{0} wants to take samples to {1} ({2}), returning by {3}. Please approve or reject.").format(
				self.carried_by_name or self.carried_by,
				self.party_name or self.other_party_name or "-",
				self.purpose,
				frappe.utils.formatdate(self.expected_return_date),
			),
			self.name,
		)


# ---------------------------------------------------------------- permissions
PRIVILEGED_ROLES = {"System Manager", "Merchandising Manager", "Merchandiser", "Gate Security", "Administrator"}


def _is_privileged(user):
	return user == "Administrator" or bool(PRIVILEGED_ROLES & set(frappe.get_roles(user)))


def _employees_of(user):
	return frappe.get_all("Employee", filters={"user_id": user}, pluck="name")


def get_permission_query_conditions(user=None):
	"""Staff (Viewer role) see only registers they created, carry, or approve."""
	user = user or frappe.session.user
	if _is_privileged(user):
		return ""
	quoted_user = frappe.db.escape(user)
	conditions = [
		f"`tabSample Movement Register`.owner = {quoted_user}",
		f"`tabSample Movement Register`.approver_user = {quoted_user}",
	]
	employees = _employees_of(user)
	if employees:
		emp_list = ", ".join(frappe.db.escape(e) for e in employees)
		conditions.append(f"`tabSample Movement Register`.carried_by in ({emp_list})")
	return "(" + " or ".join(conditions) + ")"


def has_permission(doc, ptype=None, user=None, debug=False):
	user = user or frappe.session.user
	if _is_privileged(user) or doc.is_new() or not doc.get("name"):
		return None
	if doc.owner == user or doc.approver_user == user:
		return True
	if doc.carried_by and doc.carried_by in _employees_of(user):
		return True
	return False


# ------------------------------------------------------------ gate check APIs
def _require_gate_role():
	if not GATE_ROLES & set(frappe.get_roles()):
		frappe.throw(_("Only Gate Security can use the gate check."), frappe.PermissionError)


def _find_register(gate_pass_no):
	gate_pass_no = (gate_pass_no or "").strip()
	if not gate_pass_no:
		frappe.throw(_("Enter or scan a gate pass number."))
	name = frappe.db.get_value("Sample Movement Register", {"gate_pass_no": gate_pass_no}, "name")
	if not name and frappe.db.exists("Sample Movement Register", gate_pass_no):
		name = gate_pass_no
	if not name:
		frappe.throw(_("No sample gate pass found for {0}.").format(frappe.bold(gate_pass_no)))
	return name


@frappe.whitelist()
def get_gate_pass(gate_pass_no):
	_require_gate_role()
	doc = frappe.get_doc("Sample Movement Register", _find_register(gate_pass_no))
	return {
		"name": doc.name,
		"gate_pass_no": doc.gate_pass_no,
		"status": doc.status,
		"docstatus": doc.docstatus,
		"carried_by": doc.carried_by,
		"carried_by_name": doc.carried_by_name,
		"department": doc.department,
		"party": doc.party_name or doc.other_party_name,
		"party_type": doc.party_type,
		"purpose": doc.purpose,
		"date_out": doc.date_out,
		"expected_return_date": doc.expected_return_date,
		"approved_by_name": doc.approved_by_name,
		"gate_photo": doc.gate_photo,
		"return_photo": doc.return_photo,
		"exited_on": doc.exited_on,
		"exit_confirmed_by": doc.exit_confirmed_by,
		"items": [
			{
				"idx": r.idx,
				"item_code": r.item_code,
				"description": r.item_description,
				"fabric_type": r.fabric_type,
				"color": r.color,
				"quantity": r.quantity,
				"unit": r.unit,
				"condition_out": r.condition_out,
				"returned_qty": r.returned_qty,
			}
			for r in doc.items
		],
	}


def _decode_photo(image_data):
	if not image_data or not isinstance(image_data, str) or not image_data.startswith("data:image/"):
		frappe.throw(_("Please capture a photo first."))
	header, _sep, b64 = image_data.partition(",")
	mime = header[5:].split(";")[0]
	if mime not in ("image/jpeg", "image/png", "image/webp"):
		frappe.throw(_("Unsupported image type {0}.").format(mime))
	content = base64.b64decode(b64)
	if len(content) > MAX_PHOTO_BYTES:
		frappe.throw(_("Photo is too large (max 8 MB)."))
	return content, {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}[mime]


def _attach_photo(doc, field, image_data, label):
	content, ext = _decode_photo(image_data)
	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": f"{doc.name}-{label}-{now_datetime().strftime('%Y%m%d%H%M%S')}.{ext}",
			"attached_to_doctype": doc.doctype,
			"attached_to_name": doc.name,
			"attached_to_field": field,
			"is_private": 1,
			"content": content,
		}
	)
	file_doc.flags.ignore_permissions = True
	file_doc.insert()
	return file_doc.file_url


@frappe.whitelist(methods=["POST"])
def confirm_exit(gate_pass_no, image_data):
	"""Security: attach the outgoing photo and move Approved -> Out."""
	_require_gate_role()
	doc = frappe.get_doc("Sample Movement Register", _find_register(gate_pass_no), for_update=True)
	if doc.status != "Approved":
		frappe.throw(_("Gate pass {0} is {1}; only Approved passes can exit.").format(doc.name, frappe.bold(doc.status)))
	doc.gate_photo = _attach_photo(doc, "gate_photo", image_data, "out")
	doc.exit_confirmed_by = frappe.session.user
	doc.exited_on = now_datetime()
	doc.status = "Out"
	doc.flags.from_gate_check = True
	doc.flags.ignore_permissions = True
	doc.save()
	doc.add_comment("Info", _("Exit confirmed at gate with photo by {0}").format(frappe.session.user))
	return {"name": doc.name, "status": doc.status, "gate_photo": doc.gate_photo}


@frappe.whitelist(methods=["POST"])
def save_return_photo(gate_pass_no, image_data):
	"""Security: optional photo of the samples when they come back in."""
	_require_gate_role()
	doc = frappe.get_doc("Sample Movement Register", _find_register(gate_pass_no), for_update=True)
	if doc.status not in OUT_STATES + CLOSED_STATES:
		frappe.throw(_("Gate pass {0} has not left the gate yet.").format(doc.name))
	doc.return_photo = _attach_photo(doc, "return_photo", image_data, "return")
	doc.return_photo_by = frappe.session.user
	doc.flags.from_gate_check = True
	doc.flags.ignore_permissions = True
	doc.save()
	return {"name": doc.name, "return_photo": doc.return_photo}


# ------------------------------------------------------------------ jinja
def gate_pass_qr(text, scale=4):
	"""Inline SVG data-URI QR code, used in the Gate Pass print format."""
	if not text:
		return ""
	try:
		import pyqrcode
	except ImportError:
		return ""
	stream = io.BytesIO()
	pyqrcode.create(str(text)).svg(stream, scale=cint(scale) or 4, quiet_zone=1, xmldecl=False, svgns=True)
	return "data:image/svg+xml;base64," + base64.b64encode(stream.getvalue()).decode()
