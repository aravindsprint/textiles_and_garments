"""Move Sample Movement Register from DB-only customisation into the app.

Idempotent — safe to re-run (bump the patch line in patches.txt to re-run).

* disables the old Server Scripts (logic now lives in the doctype controller
  and reminders.py)
* (re)builds the Workflow so approval routes to the carrier's reporting
  manager and exit needs a security photo
* creates Dashboard Charts, Number Cards and the "Sample Movements"
  workspace (these are not synced from app folders in v15)
* seeds Sample Movement Settings and backfills new fields on old records
"""

import json

import frappe

DT = "Sample Movement Register"
WORKFLOW = "Sample Movement Register Workflow"
STAFF = "Viewer"  # baseline role held by (almost) every staff user on this site
MANAGER = "Merchandising Manager"
GATE = "Gate Security"

OLD_SERVER_SCRIPTS = ("SMR Auto Fields", "SMR Overdue Check")

STATES = [
	# state, doc_status, allow_edit, style
	("Draft", "0", STAFF, ""),
	("Pending Approval", "0", MANAGER, "Warning"),
	("Approved", "1", GATE, "Primary"),
	("Out", "1", STAFF, "Info"),
	("Partially Returned", "1", STAFF, "Warning"),
	("Overdue", "1", STAFF, "Danger"),
	("Escalated", "1", STAFF, "Danger"),
	("Returned", "1", MANAGER, "Success"),
	("Written Off", "1", MANAGER, "Inverse"),
	("Cancelled", "2", MANAGER, "Danger"),
]

IS_APPROVER = "doc.approver_user == frappe.session.user"
NO_APPROVER = "not doc.approver_user"


def _transitions():
	t = [
		("Draft", "Send For Approval", "Pending Approval", STAFF, None, 1),
		("Pending Approval", "Approve", "Approved", STAFF, IS_APPROVER, 0),
		("Pending Approval", "Approve", "Approved", MANAGER, NO_APPROVER, 0),
		("Pending Approval", "Reject", "Draft", STAFF, IS_APPROVER, 0),
		("Pending Approval", "Reject", "Draft", MANAGER, NO_APPROVER, 0),
		("Approved", "Confirm Exit", "Out", GATE, None, 1),
		# lets an admin confirm from the Gate Check page; condition keeps it
		# from duplicating the button for users who also hold Gate Security
		("Approved", "Confirm Exit", "Out", "System Manager", "not frappe.db.get_value('Has Role', {'parent': frappe.session.user, 'parenttype': 'User', 'role': 'Gate Security'})", 1),
		("Approved", "Cancel", "Cancelled", MANAGER, None, 1),
	]
	for state in ("Out", "Overdue", "Escalated"):
		t.append((state, "Mark Partially Returned", "Partially Returned", STAFF,
			"doc.return_progress == 'Partially Returned'", 1))
	for state in ("Out", "Partially Returned", "Overdue", "Escalated"):
		t.append((state, "Mark Returned", "Returned", STAFF, "doc.return_progress == 'Fully Returned'", 1))
		wo = "doc.return_progress == 'Resolved with Write-off'"
		t.append((state, "Write Off", "Written Off", STAFF, f"{wo} and {IS_APPROVER}", 0))
		t.append((state, "Write Off", "Written Off", MANAGER, f"{wo} and doc.approver_user != frappe.session.user", 0))
	return t


def execute():
	frappe.reload_doc("textiles_and_garments", "doctype", "sample_movement_item")
	frappe.reload_doc("textiles_and_garments", "doctype", "sample_movement_escalation_recipient")
	frappe.reload_doc("textiles_and_garments", "doctype", "sample_movement_settings")
	frappe.reload_doc("textiles_and_garments", "doctype", "sample_movement_register")

	disable_old_scripts()
	ensure_roles()
	seed_settings()
	build_workflow()
	backfill()
	build_charts_cards_workspace()
	frappe.clear_cache(doctype=DT)


def disable_old_scripts():
	for name in OLD_SERVER_SCRIPTS:
		if frappe.db.exists("Server Script", name):
			frappe.db.set_value("Server Script", name, "disabled", 1)


def ensure_roles():
	for role in (STAFF, MANAGER, GATE, "Merchandiser"):
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)


def seed_settings():
	s = frappe.get_single("Sample Movement Settings")
	s.reminder_days_before = s.reminder_days_before or 1
	s.manager_cc_after_days = s.manager_cc_after_days or 4
	s.escalate_after_days = s.escalate_after_days or 8
	s.stop_daily_after_days = s.stop_daily_after_days or 14
	s.fallback_approver_role = s.fallback_approver_role or MANAGER
	s.flags.ignore_permissions = True
	s.save()


def build_workflow():
	styles = {s[0]: s[3] for s in STATES}
	for state, *_ in STATES:
		if not frappe.db.exists("Workflow State", state):
			frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": state, "style": styles[state]}).insert(
				ignore_permissions=True
			)
	for action in {t[1] for t in _transitions()}:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": action}).insert(
				ignore_permissions=True
			)

	wf = frappe.get_doc("Workflow", WORKFLOW) if frappe.db.exists("Workflow", WORKFLOW) else frappe.new_doc("Workflow")
	wf.workflow_name = WORKFLOW
	wf.document_type = DT
	wf.workflow_state_field = "status"
	wf.is_active = 1
	wf.override_status = 0
	# Our controller sends targeted mails (approver only); the built-in alert
	# would mail every Viewer who can see the document.
	wf.send_email_alert = 0
	wf.set("states", [])
	for state, doc_status, allow_edit, _style in STATES:
		wf.append("states", {"state": state, "doc_status": doc_status, "allow_edit": allow_edit})
	wf.set("transitions", [])
	for state, action, nxt, role, cond, self_ok in _transitions():
		wf.append("transitions", {
			"state": state, "action": action, "next_state": nxt, "allowed": role,
			"condition": cond, "allow_self_approval": self_ok,
		})
	wf.flags.ignore_permissions = True
	wf.save()


def backfill():
	rows = frappe.get_all(DT, fields=["name", "carried_by", "docstatus", "approved_by", "party_type"])
	for r in rows:
		values = {}
		emp = frappe.db.get_value("Employee", r.carried_by, ["employee_name", "department", "reports_to"], as_dict=True) or {}
		values["carried_by_name"] = emp.get("employee_name")
		manager = r.approved_by or emp.get("reports_to")
		if manager:
			values["approved_by"] = manager
			values["approved_by_name"] = frappe.db.get_value("Employee", manager, "employee_name")
			values["approver_user"] = frappe.db.get_value("Employee", manager, "user_id")
		frappe.db.set_value(DT, r.name, values, update_modified=False)
		doc = frappe.get_doc(DT, r.name)
		doc.set_return_progress()
		doc.set_title()
		frappe.db.set_value(DT, r.name, {"return_progress": doc.return_progress, "title": doc.title}, update_modified=False)


# ------------------------------------------------------- charts / workspace
OPEN_STATES = ["Out", "Partially Returned", "Overdue", "Escalated"]

NUMBER_CARDS = [
	("Samples Overdue", [["status", "in", ["Overdue", "Escalated"]]], "#E24C4C"),
	("Samples Currently Out", [["status", "in", OPEN_STATES]], "#2490EF"),
	("Sample Passes Awaiting Approval", [["status", "=", "Pending Approval"]], "#ECAD4B"),
	("Sample Passes Awaiting Gate Exit", [["status", "=", "Approved"]], "#7575FF"),
]

CHARTS = [
	{"chart_name": "Sample Registers by Status", "chart_type": "Group By", "group_by_type": "Count",
	 "group_by_based_on": "status", "type": "Donut", "filters": [["docstatus", "<", 2]]},
	{"chart_name": "Overdue Samples by Employee", "chart_type": "Group By", "group_by_type": "Count",
	 "group_by_based_on": "carried_by_name", "type": "Bar", "number_of_groups": 10,
	 "filters": [["status", "in", ["Overdue", "Escalated"]]]},
	{"chart_name": "Overdue Samples by Department", "chart_type": "Group By", "group_by_type": "Count",
	 "group_by_based_on": "department", "type": "Bar", "number_of_groups": 10,
	 "filters": [["status", "in", ["Overdue", "Escalated"]]]},
	{"chart_name": "Sample Movements - Monthly Trend", "chart_type": "Count", "based_on": "date_out",
	 "timeseries": 1, "timespan": "Last Year", "time_interval": "Monthly", "type": "Line",
	 "filters": [["docstatus", "=", 1]]},
]


def _filters_json(filters):
	return json.dumps([[DT, f, op, v, False] for f, op, v in filters])


def build_charts_cards_workspace():
	for label, filters, color in NUMBER_CARDS:
		card = frappe.get_doc("Number Card", label) if frappe.db.exists("Number Card", label) else frappe.new_doc("Number Card")
		card.update({
			"label": label, "type": "Document Type", "document_type": DT, "function": "Count",
			"filters_json": _filters_json(filters), "is_public": 1, "is_standard": 0,
			"show_percentage_stats": 0, "color": color, "module": "Textiles And Garments",
		})
		if card.is_new():
			card.name = label
		card.flags.ignore_permissions = True
		card.save()

	for spec in CHARTS:
		spec = dict(spec)
		filters = spec.pop("filters")
		name = spec["chart_name"]
		chart = frappe.get_doc("Dashboard Chart", name) if frappe.db.exists("Dashboard Chart", name) else frappe.new_doc("Dashboard Chart")
		chart.update({
			"document_type": DT, "filters_json": _filters_json(filters), "is_public": 1, "is_standard": 0,
			"module": "Textiles And Garments", "timeseries": 0, **spec,
		})
		chart.flags.ignore_permissions = True
		chart.save()

	# The old merchandiser-named chart is superseded by "Overdue Samples by Employee".
	if frappe.db.exists("Dashboard Chart", "Overdue Samples by Merchandiser"):
		frappe.db.set_value("Dashboard Chart", "Overdue Samples by Merchandiser", "is_public", 0)

	_build_workspace()


def _build_workspace():
	name = "Sample Movements"
	reports = ["Samples Currently Out", "Overdue Aging Report", "Monthly Sample Movement Summary", "Party-wise Sample Report"]

	blocks = [{"id": "smr-h1", "type": "header", "data": {"text": '<span class="h4"><b>Sample Movements</b></span>', "col": 12}}]
	blocks += [{"id": f"smr-nc{i}", "type": "number_card", "data": {"number_card_name": c[0], "col": 3}}
		for i, c in enumerate(NUMBER_CARDS)]
	blocks += [{"id": "smr-sp1", "type": "spacer", "data": {"col": 12}}]
	blocks += [{"id": f"smr-sc{i}", "type": "shortcut", "data": {"shortcut_name": s, "col": 3}}
		for i, s in enumerate(["New Gate Pass", "Sample Movement Register", "Sample Gate Check", "Samples Currently Out"])]
	blocks += [{"id": f"smr-ch{i}", "type": "chart", "data": {"chart_name": c["chart_name"], "col": 6}}
		for i, c in enumerate(CHARTS)]
	blocks += [{"id": "smr-card1", "type": "card", "data": {"card_name": "Reports", "col": 4}},
		{"id": "smr-card2", "type": "card", "data": {"card_name": "Setup", "col": 4}}]

	ws = frappe.get_doc("Workspace", name) if frappe.db.exists("Workspace", name) else frappe.new_doc("Workspace")
	ws.update({
		"label": name, "title": name, "module": "Textiles And Garments", "public": 1, "is_hidden": 0,
		"icon": "es-line-box", "content": json.dumps(blocks),
	})
	if ws.is_new():
		ws.name = name
	ws.set("number_cards", [{"number_card_name": c[0], "label": c[0]} for c in NUMBER_CARDS])
	ws.set("charts", [{"chart_name": c["chart_name"], "label": c["chart_name"]} for c in CHARTS])
	ws.set("shortcuts", [
		{"type": "URL", "url": "/app/sample-movement-register/new", "label": "New Gate Pass", "color": "Blue"},
		{"type": "DocType", "link_to": DT, "label": "Sample Movement Register", "doc_view": "List",
		 "stats_filter": json.dumps([[DT, "status", "in", ["Overdue", "Escalated"], False]]), "color": "Red"},
		{"type": "Page", "link_to": "sample-gate-check", "label": "Sample Gate Check", "color": "Grey"},
		{"type": "Report", "link_to": "Samples Currently Out", "label": "Samples Currently Out", "color": "Orange"},
	])
	links = [{"type": "Card Break", "label": "Reports", "link_count": len(reports)}]
	links += [{"type": "Link", "link_type": "Report", "link_to": r, "label": r, "is_query_report": 1,
		"dependencies": "", "onboard": 0} for r in reports]
	links += [{"type": "Card Break", "label": "Setup", "link_count": 2},
		{"type": "Link", "link_type": "DocType", "link_to": "Sample Movement Settings", "label": "Sample Movement Settings"},
		{"type": "Link", "link_type": "DocType", "link_to": "Employee", "label": "Employee (Reports To)"}]
	ws.set("links", links)
	ws.set("roles", [{"role": r} for r in ("System Manager", MANAGER, "Merchandiser", GATE, STAFF)])
	ws.flags.ignore_permissions = True
	ws.flags.ignore_links = False
	ws.save()
