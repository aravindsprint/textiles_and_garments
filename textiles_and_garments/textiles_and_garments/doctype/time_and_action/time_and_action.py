# Copyright (c) 2026, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, getdate

class TimeandAction(Document):
    def validate(self):
        self.validate_date_sequence()
        self.calculate_delivery_days()

    def validate_date_sequence(self):
        items = self.time_and_action_item
        sequential = [r for r in items if r.method == "Sequential"]
        sequential.sort(key=lambda r: r.idx)

        for i in range(1, len(sequential)):
            prev = sequential[i - 1]
            curr = sequential[i]

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
            total += row.no_of_days_to_deliver
        self.total_no_of_days_to_deliver = total