# Copyright (c) 2026, Aravind and contributors

import frappe
from frappe import _
from frappe.utils import date_diff, escape_html, getdate, today

STATES = ("Approved", "Out", "Partially Returned", "Overdue", "Escalated")


def execute(filters=None):
	filters = frappe._dict(filters or {})
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Gate Pass No"), "fieldname": "name", "fieldtype": "Link", "options": "Sample Movement Register", "width": 150},
		{"label": _("Photo"), "fieldname": "photo", "fieldtype": "HTML", "width": 80},
		{"label": _("Employee"), "fieldname": "carried_by_name", "fieldtype": "Data", "width": 160},
		{"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 140},
		{"label": _("Party"), "fieldname": "party", "fieldtype": "Data", "width": 170},
		{"label": _("Items"), "fieldname": "items", "fieldtype": "Data", "width": 220},
		{"label": _("Date Out"), "fieldname": "date_out", "fieldtype": "Date", "width": 100},
		{"label": _("Expected Return"), "fieldname": "expected_return_date", "fieldtype": "Date", "width": 120},
		{"label": _("Days Overdue"), "fieldname": "days_overdue", "fieldtype": "Int", "width": 110},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 130},
		{"label": _("Return Progress"), "fieldname": "return_progress", "fieldtype": "Data", "width": 140},
	]


def get_data(filters):
	conditions = {"docstatus": 1, "status": ["in", [filters.status] if filters.status else list(STATES)]}
	for key in ("department", "carried_by", "party_type"):
		if filters.get(key):
			conditions[key] = filters.get(key)

	rows = frappe.get_all(
		"Sample Movement Register",
		filters=conditions,
		fields=[
			"name", "gate_photo", "carried_by_name", "department", "party_name", "other_party_name",
			"date_out", "expected_return_date", "status", "return_progress",
		],
		order_by="expected_return_date asc",
	)
	if not rows:
		return []

	items = {}
	for it in frappe.get_all(
		"Sample Movement Item",
		filters={"parenttype": "Sample Movement Register", "parent": ["in", [r.name for r in rows]]},
		fields=["parent", "item_description", "quantity", "unit"],
		order_by="idx",
	):
		items.setdefault(it.parent, []).append(f"{it.item_description} ({it.quantity:g} {it.unit or ''})".strip())

	now = getdate(today())
	data = []
	for r in rows:
		days = date_diff(now, r.expected_return_date)
		if filters.only_overdue and days <= 0:
			continue
		data.append(
			{
				**r,
				"party": r.party_name or r.other_party_name,
				"items": "; ".join(items.get(r.name, [])),
				"days_overdue": max(days, 0),
				"photo": (
					f'<a href="{escape_html(r.gate_photo)}" target="_blank">'
					f'<img src="{escape_html(r.gate_photo)}" style="height:28px;border-radius:3px"></a>'
					if r.gate_photo
					else ""
				),
			}
		)
	return data
