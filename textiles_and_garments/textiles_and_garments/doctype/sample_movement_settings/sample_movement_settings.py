# Copyright (c) 2026, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SampleMovementSettings(Document):
	def validate(self):
		cc = self.manager_cc_after_days or 0
		esc = self.escalate_after_days or 0
		stop = self.stop_daily_after_days or 0
		if not (0 < cc <= esc <= stop):
			frappe.throw(_("Days must satisfy: 0 < Copy Manager ≤ Escalate ≤ Stop Daily Mails."))
		if (self.reminder_days_before or 0) < 0:
			frappe.throw(_("Reminder Days Before Due cannot be negative."))
