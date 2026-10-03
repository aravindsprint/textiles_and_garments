"""
Seed the stock_integrity protected-voucher list with the documents whose ledger lines
were adjusted during the 3 Oct 2026 Stock_balance_checking clean-up, so they cannot be
cancelled or recalculated by a backdated repost.
"""

import frappe

from textiles_and_garments.stock_integrity.protect import protect

VOUCHERS = [("Stock Reconciliation", "SR/{0:05d}".format(n)) for n in range(21, 34)] + [
    ("Stock Entry", "ST/26/19895"),
]


def execute():
    for doctype, name in VOUCHERS:
        if frappe.db.get_value(doctype, name, "docstatus") == 1:
            protect(doctype, name)
