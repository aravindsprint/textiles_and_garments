# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class WorkOrderPayments(Document):
	def validate(self):
		self.validate_work_orders_submitted()

	def validate_work_orders_submitted(self):
		"""Only submitted Work Orders can be paid."""
		work_orders = [row.work_order for row in self.work_order_payment_item if row.work_order]
		if not work_orders:
			return

		docstatus_map = dict(
			frappe.get_all(
				"Work Order",
				filters={"name": ["in", work_orders]},
				fields=["name", "docstatus"],
				as_list=True,
			)
		)

		invalid = [
			_("Row {0}: {1}").format(row.idx, frappe.bold(row.work_order))
			for row in self.work_order_payment_item
			if row.work_order and docstatus_map.get(row.work_order) != 1
		]

		if invalid:
			frappe.throw(
				_("The following Work Orders are not submitted and cannot be paid:")
				+ "<br>" + "<br>".join(invalid),
				title=_("Unsubmitted Work Orders"),
			)
