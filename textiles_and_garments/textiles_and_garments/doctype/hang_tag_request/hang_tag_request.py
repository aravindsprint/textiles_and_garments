# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today
import json


class HangTagRequest(Document):
	pass



@frappe.whitelist()
def get_sales_invoice_items(sales_invoice):
    """Fetch all items from the given sales invoice."""
    if not sales_invoice:
        return []

    items = frappe.get_all(
        "Sales Invoice Item",
        filters={"parent": sales_invoice},
        # fields=["item_code", "warehouse", "qty", "rate", "amount", "commercial_name", "color"]
        fields=["item_code", "warehouse", "qty", "rate", "amount"]
    )
    return items