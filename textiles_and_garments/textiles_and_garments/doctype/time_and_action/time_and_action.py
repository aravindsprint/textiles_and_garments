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
        rows = self.time_and_action_item

        # Per-row days: inclusive count (diff + 1)
        for row in rows:
            if row.start_date and row.end_date:
                row.no_of_days_to_deliver = date_diff(row.end_date, row.start_date) + 1
            else:
                row.no_of_days_to_deliver = 0

        # Total: handle Sequential vs Parallel groups
        sequential_rows = [r for r in rows if r.method == "Sequential"]
        parallel_rows   = [r for r in rows if r.method == "Parallel"]

        # Sequential total = sum of individual days
        sequential_total = sum(r.no_of_days_to_deliver for r in sequential_rows)

        # Parallel total = span from earliest start to latest end (inclusive)
        parallel_total = 0
        if parallel_rows:
            starts = [getdate(r.start_date) for r in parallel_rows if r.start_date]
            ends   = [getdate(r.end_date)   for r in parallel_rows if r.end_date]
            if starts and ends:
                parallel_total = date_diff(max(ends), min(starts)) + 1

        self.total_no_of_days_to_deliver = sequential_total + parallel_total