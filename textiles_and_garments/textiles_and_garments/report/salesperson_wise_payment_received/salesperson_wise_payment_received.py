from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    columns = [
        {
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "label": _("Payment Entry"),
            "fieldname": "payment_entry",
            "fieldtype": "Link",
            "options": "Payment Entry",
            "width": 150,
        },
        {
            "label": _("Party Type"),
            "fieldname": "party_type",
            "width": 120,
        },
        {
            "label": _("Party"),
            "fieldname": "party",
            "width": 150,
        },
        {
            "label": _("Customer Name"),
            "fieldname": "customer_name",
            "width": 150,
        },
        {
            "label": _("Sales Person"),
            "fieldname": "sales_person",
            "width": 200,
        },
        {
            "label": _("Amount Received"),
            "fieldname": "received_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Mode of Payment"),
            "fieldname": "mode_of_payment",
            "width": 120,
        }
    ]
    return columns

def get_data(filters):
    data = get_payment_entry_data(filters)
    return data

def get_payment_entry_data(filters):
    query = """
        SELECT 
            pe.posting_date,
            pe.name as payment_entry,
            pe.party_type,
            pe.party,
            cust.customer_name,
            pe.received_amount,
            pe.mode_of_payment,
            GROUP_CONCAT(DISTINCT IFNULL(inv_sales_person, cust_sales_person) SEPARATOR ', ') as sales_person
        FROM `tabPayment Entry` AS pe
        LEFT JOIN `tabCustomer` AS cust ON pe.party = cust.name
        LEFT JOIN (
            SELECT 
                ref.parent as payment_entry,
                st.sales_person as inv_sales_person
            FROM `tabPayment Entry Reference` AS ref
            LEFT JOIN `tabSales Invoice` AS si ON ref.reference_name = si.name
            LEFT JOIN `tabSales Team` AS st ON si.name = st.parent AND st.parenttype = 'Sales Invoice'
            WHERE ref.reference_doctype = 'Sales Invoice'
        ) AS inv ON inv.payment_entry = pe.name
        LEFT JOIN (
            SELECT 
                parent as customer,
                sales_person as cust_sales_person
            FROM `tabSales Team`
            WHERE parenttype = 'Customer'
        ) AS cust_st ON cust_st.customer = pe.party
        WHERE pe.payment_type = 'Receive'
    """

    conditions = []

    if filters.get("from_date"):
        conditions.append("pe.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("pe.posting_date <= %(to_date)s")
    if filters.get("party"):
        conditions.append("pe.party = %(party)s")
    if filters.get("mode_of_payment"):
        conditions.append("pe.mode_of_payment = %(mode_of_payment)s")
    if filters.get("docstatus") is not None:
        conditions.append("pe.docstatus = %(docstatus)s")

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " GROUP BY pe.name"

    filter_values = {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "party": filters.get("party"),
        "mode_of_payment": filters.get("mode_of_payment"),
        "docstatus": int(filters.get("docstatus")) if filters.get("docstatus") else None,
    }

    return frappe.db.sql(query, filter_values, as_dict=1)