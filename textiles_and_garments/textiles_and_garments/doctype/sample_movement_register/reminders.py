# Copyright (c) 2026, Aravind and contributors
"""Daily reminder / overdue / escalation ladder and weekly digest for
Sample Movement Register (replaces the "SMR Overdue Check" Server Script).

Ladder (thresholds live in Sample Movement Settings):
    due - N days        reminder to carrier
    1 .. cc-1 overdue   status -> Overdue, daily mail to carrier
    cc .. esc-1         daily mail to carrier + reporting manager
    esc .. stop         status -> Escalated; Dept Head / MD mailed once on the
                        escalation day with the outgoing gate photo attached;
                        carrier + manager keep getting daily mails
    > stop              no daily mails; stays in the weekly digest and the
                        Overdue Aging Report until returned / written off
"""

import frappe
from frappe import _
from frappe.utils import cint, date_diff, escape_html, formatdate, get_url, getdate, today

DOCTYPE = "Sample Movement Register"
ACTIVE_STATES = ("Out", "Partially Returned", "Overdue", "Escalated")


# ---------------------------------------------------------------- settings
def get_settings():
	s = frappe.get_cached_doc("Sample Movement Settings")
	return frappe._dict(
		reminder_days_before=cint(s.reminder_days_before) if s.reminder_days_before is not None else 1,
		manager_cc_after_days=cint(s.manager_cc_after_days) or 4,
		escalate_after_days=cint(s.escalate_after_days) or 8,
		stop_daily_after_days=cint(s.stop_daily_after_days) or 14,
		fallback_approver_role=s.fallback_approver_role or "Merchandising Manager",
		recipients=s.escalation_recipients or [],
	)


# --------------------------------------------------------------- contacts
def employee_contact(employee):
	"""(user, email) for an Employee — falls back to the Employee's own email
	when the employee has no ERP login, so nobody silently misses reminders."""
	if not employee:
		return (None, None)
	row = frappe.db.get_value(
		"Employee", employee, ["user_id", "prefered_email", "company_email", "personal_email"], as_dict=True
	)
	if not row:
		return (None, None)
	email = row.prefered_email or row.company_email or row.personal_email
	return (row.user_id, email)


def fallback_approver_contacts():
	role = get_settings().fallback_approver_role
	users = frappe.get_all(
		"Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent", distinct=True
	)
	enabled = frappe.get_all("User", filters={"name": ["in", users or [""]], "enabled": 1}, pluck="name")
	return [(u, None) for u in enabled]


def leadership_contacts(department):
	"""Dept Head(s) for the department plus all-department (MD) rows."""
	rows = get_settings().recipients
	users = [r.user for r in rows if not r.department or r.department == department]
	if not users:
		return fallback_approver_contacts()
	return [(u, None) for u in users]


# ------------------------------------------------------------------ notify
def notify(contacts, subject, message, docname, attachments=None):
	"""Bell notification for users + one email to every distinct address."""
	users, emails = [], []
	for user, email in contacts:
		if user and user not in users and frappe.db.get_value("User", user, "enabled"):
			users.append(user)
			email = email or frappe.db.get_value("User", user, "email")
		if email and email not in emails:
			emails.append(email)

	for user in users:
		try:
			frappe.get_doc(
				{
					"doctype": "Notification Log",
					"subject": subject,
					"email_content": message,
					"for_user": user,
					"type": "Alert",
					"document_type": DOCTYPE,
					"document_name": docname,
				}
			).insert(ignore_permissions=True)
		except Exception:
			frappe.log_error(title=f"Sample Movement notification failed: {docname}")

	if emails:
		link = get_url(f"/app/sample-movement-register/{docname}")
		frappe.sendmail(
			recipients=emails,
			subject=subject,
			message=f"{message}<br><br><a href='{link}'>{_('Open {0}').format(docname)}</a>",
			reference_doctype=DOCTYPE,
			reference_name=docname,
			attachments=attachments,
		)


def _gate_photo_attachment(reg):
	if not reg.gate_photo:
		return None
	fid = frappe.db.get_value(
		"File", {"file_url": reg.gate_photo, "attached_to_doctype": DOCTYPE, "attached_to_name": reg.name}, "name"
	) or frappe.db.get_value("File", {"file_url": reg.gate_photo}, "name")
	return [{"fid": fid}] if fid else None


def _items_html(name):
	rows = frappe.get_all(
		"Sample Movement Item",
		filters={"parent": name, "parenttype": DOCTYPE},
		fields=["item_code", "item_description", "quantity", "returned_qty", "unit", "written_off"],
		order_by="idx",
	)
	trs = "".join(
		f"<tr><td>{escape_html(r.item_code or '')}</td><td>{escape_html(r.item_description or '')}</td>"
		f"<td>{r.quantity:g} {escape_html(r.unit or '')}</td><td>{(r.returned_qty or 0):g}</td></tr>"
		for r in rows
	)
	return (
		"<table border='1' cellpadding='4' style='border-collapse:collapse'>"
		"<tr><th>Item</th><th>Description</th><th>Qty Out</th><th>Returned</th></tr>"
		f"{trs}</table>"
	)


# -------------------------------------------------------------- daily job
def send_daily_reminders():
	s = get_settings()
	now = getdate(today())
	registers = frappe.get_all(
		DOCTYPE,
		filters={"docstatus": 1, "status": ["in", ACTIVE_STATES]},
		fields=[
			"name", "status", "carried_by", "carried_by_name", "approved_by", "department",
			"party_name", "other_party_name", "expected_return_date", "gate_photo", "last_reminder_on",
		],
	)

	for reg in registers:
		if reg.last_reminder_on and getdate(reg.last_reminder_on) == now:
			continue  # already handled today (job re-run)
		try:
			_process(reg, s, now)
			frappe.db.commit()
		except Exception:
			frappe.db.rollback()
			frappe.log_error(title=f"Sample Movement reminder failed: {reg.name}")


def _process(reg, s, now):
	days_overdue = date_diff(now, reg.expected_return_date)
	party = reg.party_name or reg.other_party_name or "-"
	carrier = employee_contact(reg.carried_by)
	manager = employee_contact(reg.approved_by)

	if days_overdue < 0:
		if -days_overdue == s.reminder_days_before and reg.status in ("Out", "Partially Returned"):
			notify(
				[carrier],
				_("Reminder: samples {0} due back on {1}").format(reg.name, formatdate(reg.expected_return_date)),
				_("Samples taken to {0} under gate pass {1} are due back on {2}.").format(
					party, reg.name, formatdate(reg.expected_return_date)
				),
				reg.name,
			)
			_stamp(reg.name, last_reminder_on=now)
		return

	if days_overdue == 0:
		return  # due today; becomes Overdue tomorrow

	if reg.status in ("Out", "Partially Returned"):
		_stamp(reg.name, status="Overdue")
		_comment(reg.name, _("Marked Overdue — expected back on {0}.").format(formatdate(reg.expected_return_date)))
		reg.status = "Overdue"

	if days_overdue >= s.escalate_after_days and reg.status != "Escalated":
		_stamp(reg.name, status="Escalated", escalated_on=now)
		_comment(reg.name, _("Escalated — {0} days overdue.").format(days_overdue))
		notify(
			leadership_contacts(reg.department),
			_("ESCALATED: samples {0} are {1} days overdue").format(reg.name, days_overdue),
			_(
				"Samples carried by <b>{0}</b> ({1}) to <b>{2}</b> were due back on {3} and are now "
				"<b>{4} days overdue</b>. The outgoing gate photo is attached.<br><br>{5}"
			).format(
				escape_html(reg.carried_by_name or reg.carried_by), escape_html(reg.department or "-"),
				escape_html(party), formatdate(reg.expected_return_date), days_overdue, _items_html(reg.name),
			),
			reg.name,
			attachments=_gate_photo_attachment(reg),
		)

	if days_overdue > s.stop_daily_after_days:
		return  # weekly digest only

	recipients = [carrier]
	if days_overdue >= s.manager_cc_after_days:
		recipients.append(manager)
	notify(
		recipients,
		_("Overdue: samples {0} — {1} day(s)").format(reg.name, days_overdue),
		_("Samples taken to {0} under gate pass {1} were due back on {2} and are {3} day(s) overdue. "
		  "Please return them or ask your manager to write them off.").format(
			escape_html(party), reg.name, formatdate(reg.expected_return_date), days_overdue
		),
		reg.name,
	)
	_stamp(reg.name, last_reminder_on=now)


def _stamp(name, **values):
	frappe.db.set_value(DOCTYPE, name, values, update_modified=False)


def _comment(name, text):
	frappe.get_doc(
		{"doctype": "Comment", "comment_type": "Info", "reference_doctype": DOCTYPE, "reference_name": name, "content": text}
	).insert(ignore_permissions=True)


# ------------------------------------------------------------- weekly job
def send_weekly_digest():
	rows = frappe.db.sql(
		"""
		select name, carried_by_name, department, coalesce(party_name, other_party_name) as party,
			expected_return_date, status, datediff(curdate(), expected_return_date) as days_overdue
		from `tabSample Movement Register`
		where docstatus = 1 and status in ('Overdue', 'Escalated')
		order by days_overdue desc
		""",
		as_dict=True,
	)
	if not rows:
		return

	recipients = [r for r in get_settings().recipients if r.weekly_digest]
	if not recipients:
		recipients = [frappe._dict(user=u, department=None) for u, _e in fallback_approver_contacts()]

	for rec in recipients:
		mine = [r for r in rows if not rec.department or r.department == rec.department]
		if not mine:
			continue
		trs = "".join(
			f"<tr><td><a href='{get_url('/app/sample-movement-register/' + r.name)}'>{r.name}</a></td>"
			f"<td>{escape_html(r.carried_by_name or '')}</td><td>{escape_html(r.department or '')}</td>"
			f"<td>{escape_html(r.party or '')}</td><td>{formatdate(r.expected_return_date)}</td>"
			f"<td style='text-align:right'><b>{r.days_overdue}</b></td><td>{r.status}</td></tr>"
			for r in mine
		)
		email = frappe.db.get_value("User", rec.user, "email")
		if not email:
			continue
		frappe.sendmail(
			recipients=[email],
			subject=_("Weekly overdue samples: {0} open").format(len(mine)),
			message=(
				"<p>" + _("Samples still out past their return date, worst first:") + "</p>"
				"<table border='1' cellpadding='4' style='border-collapse:collapse'>"
				"<tr><th>Gate Pass</th><th>Employee</th><th>Department</th><th>Party</th>"
				"<th>Due</th><th>Days Overdue</th><th>Status</th></tr>"
				f"{trs}</table>"
			),
		)
