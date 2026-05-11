# Copyright (c) 2026, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, getdate

class TimeandAction(Document):
    def validate(self):
        # self.validate_date_sequence()
        self.calculate_delivery_days()

    def validate_date_sequence(self):
        items = self.time_and_action_item
        for i in range(1, len(items)):
            prev = items[i - 1]
            curr = items[i]

            if not prev.end_date or not curr.start_date:
                continue

            if getdate(curr.start_date) <= getdate(prev.end_date):
                frappe.throw(
                    f"Row {curr.idx} <b>{curr.process_name}</b>: "
                    f"Start Date ({curr.start_date}) must be after "
                    f"Row {prev.idx} <b>{prev.process_name}</b> End Date ({prev.end_date}).",
                    title="Date Overlap Error"
                )

    def calculate_delivery_days(self):
        total = 0
        for row in self.time_and_action_item:
            if row.start_date and row.end_date:
                row.no_of_days_to_deliver = date_diff(row.end_date, row.start_date)
            else:
                row.no_of_days_to_deliver = 0

            if row.method == "Parallel":
                continue

            total += row.no_of_days_to_deliver

        self.total_no_of_days_to_deliver = total