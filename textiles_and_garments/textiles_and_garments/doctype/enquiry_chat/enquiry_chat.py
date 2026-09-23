# Copyright (c) 2026, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class EnquiryChat(Document):
	def validate(self):
		has_new_message = self.set_message_defaults()
		self.set_last_message(has_new_message)

	def set_message_defaults(self):
		"""Works for rows added via the API and rows typed in the Desk grid.
		Returns True if at least one new message row was added in this save."""
		has_new = False
		for row in self.messages:
			if row.sender not in ("customer", "admin"):
				frappe.throw(_("Row {0}: Sender must be 'customer' or 'admin'.").format(row.idx))

			if not row.sent_at:  # new row
				has_new = True
				row.sent_at = now_datetime()

				# The sender has always "seen" their own message
				if row.sender == "customer":
					row.seen_by_customer = 1
				else:
					row.seen_by_admin = 1
					row.sent_by = row.sent_by or frappe.session.user
		return has_new

	def set_last_message(self, has_new_message):
		if not self.messages:
			return
		last = self.messages[-1]
		self.last_message_at = last.sent_at
		self.last_message_by = last.sender

		# Only change status when a message is added, so a manual
		# "Closed" set from Desk is not overwritten on a plain save.
		if has_new_message:
			self.status = "Replied" if last.sender == "admin" else "Open"
