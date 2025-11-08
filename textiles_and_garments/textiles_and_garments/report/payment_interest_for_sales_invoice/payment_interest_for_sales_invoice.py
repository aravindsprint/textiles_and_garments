# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt


# from collections import defaultdict
# import frappe
# from frappe import _
# from frappe.query_builder.functions import Sum
# from frappe.utils import flt, today
# from datetime import datetime

# def execute(filters=None):
#     columns, data = [], []
#     data = get_data(filters)
#     columns = get_columns(filters)
#     return columns, data

# def get_columns(filters):
#     columns = [
#         {
#             "label": _("Sales Invoice"),
#             "fieldname": "sales_invoice",
#             "fieldtype": "Link",
#             "options": "Sales Invoice",
#             "width": 120,
#         },
#         {
#             "label": _("Posting Date"),
#             "fieldname": "posting_date",
#             "fieldtype": "Date",
#             "width": 100,
#         },
#         {
#             "label": _("Due Date"),
#             "fieldname": "due_date",
#             "fieldtype": "Date",
#             "width": 100,
#         },
#         {
#             "label": _("Customer"),
#             "fieldname": "customer",
#             "fieldtype": "Link",
#             "options": "Customer",
#             "width": 120,
#         },
#         {
#             "label": _("Grand Total"),
#             "fieldname": "grand_total",
#             "fieldtype": "Currency",
#             "width": 120,
#         },
#         {
#             "label": _("Interest Amount"),
#             "fieldname": "interest_amount",
#             "fieldtype": "Currency",
#             "width": 120,
#         },
#         {
#             "label": _("Rate of Interest (%)"),
#             "fieldname": "rate_of_interest",
#             "fieldtype": "Float",
#             "width": 100,
#             "precision": 2
#         },
#         {
#             "label": _("Payment Entry"),
#             "fieldname": "payment_entry",
#             "fieldtype": "Link",
#             "options": "Payment Entry",
#             "width": 120,
#         },
#         {
#             "label": _("Payment Posting Date"),
#             "fieldname": "payment_posting_date",
#             "fieldtype": "Date",
#             "width": 120,
#         },
#         {
#             "label": _("Days Overdue"),
#             "fieldname": "days_overdue",
#             "fieldtype": "Int",
#             "width": 100,
#         }
#     ]

#     return columns

# def get_data(filters):
#     data = []
#     si_data = get_sales_invoice_data(filters)
    
#     # Calculate interest for each sales invoice
#     for row in si_data:
#         row = calculate_interest(row, filters)
#         data.append(row)
    
#     return data

# def calculate_interest(row, filters):
#     """Calculate interest amount based on rate of interest and overdue days"""
#     rate_of_interest = flt(filters.get("rate_of_interest", 0))
    
#     # Get today's date for calculation
#     today_date = today()
    
#     # Calculate days overdue (if due_date is in the past)
#     if row.get('due_date'):
#         due_date = row['due_date']
#         if isinstance(due_date, str):
#             due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        
#         days_overdue = (datetime.now().date() - due_date).days
#         days_overdue = max(0, days_overdue)  # Only positive values (overdue)
#     else:
#         days_overdue = 0
    
#     row['days_overdue'] = days_overdue
#     row['rate_of_interest'] = rate_of_interest
    
#     # Calculate interest amount
#     # Formula: (Grand Total * Rate of Interest * Days Overdue) / (100 * 365)
#     if days_overdue > 0 and rate_of_interest > 0 and row.get('grand_total'):
#         grand_total = flt(row['grand_total'])
#         interest_amount = (grand_total * rate_of_interest * days_overdue) / (100 * 365)
#         row['interest_amount'] = flt(interest_amount, 2)
#     else:
#         row['interest_amount'] = 0.0
    
#     return row

# def get_sales_invoice_data(filters):
#     query = """
#         SELECT 
#             si.name as sales_invoice,
#             si.due_date,
#             si.customer,
#             si.grand_total,
#             si.posting_date,
#             si.outstanding_amount,
#             pr.parent as payment_entry,
#             pr.reference_name,
#             pr.allocated_amount,
#             pe.posting_date as payment_posting_date
#         FROM `tabSales Invoice` AS si
#         LEFT JOIN `tabPayment Entry Reference` AS pr ON pr.reference_name = si.name
#         LEFT JOIN `tabPayment Entry` AS pe ON pe.name = pr.parent
#         WHERE si.docstatus = 1 AND si.outstanding_amount > 0
#     """

#     conditions = []

#     if filters.get("sales_invoice"):
#         conditions.append("si.name = %(sales_invoice)s")
#     if filters.get("customer"):
#         conditions.append("si.customer = %(customer)s")
#     if filters.get("from_date"):
#         conditions.append("si.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("si.posting_date <= %(to_date)s")
#     if filters.get("payment_entry"):
#         conditions.append("pr.parent = %(payment_entry)s")
#     if filters.get("payment_posting_date"):
#         conditions.append("pe.posting_date = %(payment_posting_date)s")

#     # Add conditions to query if they exist
#     if conditions:
#         query += " AND " + " AND ".join(conditions)

#     # Add ordering
#     query += " ORDER BY si.posting_date DESC, si.name"

#     filter_values = {
#         "sales_invoice": filters.get("sales_invoice"),
#         "customer": filters.get("customer"),
#         "from_date": filters.get("from_date"),
#         "to_date": filters.get("to_date"),
#         "payment_entry": filters.get("payment_entry"),
#         "payment_posting_date": filters.get("payment_posting_date"),
#     }

#     # Remove None values from filter_values
#     filter_values = {k: v for k, v in filter_values.items() if v is not None}

#     return frappe.db.sql(query, filter_values, as_dict=1)



# from collections import defaultdict
# import frappe
# from frappe import _
# from frappe.query_builder.functions import Sum
# from frappe.utils import flt, today
# from datetime import datetime

# def execute(filters=None):
#     columns, data = [], []
#     data = get_data(filters)
#     columns = get_columns(filters)
#     return columns, data

# def get_columns(filters):
#     columns = [
#         {
#             "label": _("Sales Invoice"),
#             "fieldname": "sales_invoice",
#             "fieldtype": "Link",
#             "options": "Sales Invoice",
#             "width": 120,
#         },
#         {
#             "label": _("Posting Date"),
#             "fieldname": "posting_date",
#             "fieldtype": "Date",
#             "width": 100,
#         },
#         {
#             "label": _("Due Date"),
#             "fieldname": "due_date",
#             "fieldtype": "Date",
#             "width": 100,
#         },
#         {
#             "label": _("Customer"),
#             "fieldname": "customer",
#             "fieldtype": "Link",
#             "options": "Customer",
#             "width": 120,
#         },
#         {
#             "label": _("Grand Total"),
#             "fieldname": "grand_total",
#             "fieldtype": "Currency",
#             "width": 120,
#         },
#         {
#             "label": _("Interest Amount"),
#             "fieldname": "interest_amount",
#             "fieldtype": "Currency",
#             "width": 120,
#         },
#         {
#             "label": _("Total Amount"),
#             "fieldname": "total_amount",
#             "fieldtype": "Currency",
#             "width": 120,
#         },
#         {
#             "label": _("Rate of Interest (%)"),
#             "fieldname": "rate_of_interest",
#             "fieldtype": "Float",
#             "width": 100,
#             "precision": 2
#         },
#         {
#             "label": _("Payment Entry"),
#             "fieldname": "payment_entry",
#             "fieldtype": "Link",
#             "options": "Payment Entry",
#             "width": 120,
#         },
#         {
#             "label": _("Payment Posting Date"),
#             "fieldname": "payment_posting_date",
#             "fieldtype": "Date",
#             "width": 120,
#         },
#         {
#             "label": _("Days Overdue"),
#             "fieldname": "days_overdue",
#             "fieldtype": "Int",
#             "width": 100,
#         }
#     ]

#     return columns

# def get_data(filters):
#     data = []
#     si_data = get_sales_invoice_data(filters)
    
#     # Calculate interest for each sales invoice
#     for row in si_data:
#         row = calculate_interest(row, filters)
#         # Calculate total amount for each row
#         row = calculate_total_amount(row)
#         data.append(row)
    
#     return data

# def calculate_interest(row, filters):
#     """Calculate interest amount based on rate of interest and overdue days"""
#     rate_of_interest = flt(filters.get("rate_of_interest", 0))
    
#     # Get today's date for calculation
#     today_date = today()
    
#     # Calculate days overdue (if due_date is in the past)
#     if row.get('due_date'):
#         due_date = row['due_date']
#         if isinstance(due_date, str):
#             due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        
#         days_overdue = (datetime.now().date() - due_date).days
#         days_overdue = max(0, days_overdue)  # Only positive values (overdue)
#     else:
#         days_overdue = 0
    
#     row['days_overdue'] = days_overdue
#     row['rate_of_interest'] = rate_of_interest
    
#     # Calculate interest amount
#     # Formula: (Grand Total * Rate of Interest * Days Overdue) / (100 * 365)
#     if days_overdue > 0 and rate_of_interest > 0 and row.get('grand_total'):
#         grand_total = flt(row['grand_total'])
#         interest_amount = (grand_total * rate_of_interest * days_overdue) / (100 * 365)
#         row['interest_amount'] = flt(interest_amount, 2)
#     else:
#         row['interest_amount'] = 0.0
    
#     return row

# def calculate_total_amount(row):
#     """Calculate total amount (grand_total + interest_amount) for each row"""
#     grand_total = flt(row.get('grand_total', 0))
#     interest_amount = flt(row.get('interest_amount', 0))
#     row['total_amount'] = grand_total + interest_amount
#     return row

# def get_sales_invoice_data(filters):
#     query = """
#         SELECT 
#             si.name as sales_invoice,
#             si.due_date,
#             si.customer,
#             si.grand_total,
#             si.posting_date,
#             si.outstanding_amount,
#             pr.parent as payment_entry,
#             pr.reference_name,
#             pr.allocated_amount,
#             pe.posting_date as payment_posting_date
#         FROM `tabSales Invoice` AS si
#         LEFT JOIN `tabPayment Entry Reference` AS pr ON pr.reference_name = si.name
#         LEFT JOIN `tabPayment Entry` AS pe ON pe.name = pr.parent
#         WHERE si.docstatus = 1 AND si.outstanding_amount > 0
#     """

#     conditions = []

#     if filters.get("sales_invoice"):
#         conditions.append("si.name = %(sales_invoice)s")
#     if filters.get("customer"):
#         conditions.append("si.customer = %(customer)s")
#     if filters.get("from_date"):
#         conditions.append("si.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("si.posting_date <= %(to_date)s")
#     if filters.get("payment_entry"):
#         conditions.append("pr.parent = %(payment_entry)s")
#     if filters.get("payment_posting_date"):
#         conditions.append("pe.posting_date = %(payment_posting_date)s")

#     # Add conditions to query if they exist
#     if conditions:
#         query += " AND " + " AND ".join(conditions)

#     # Add ordering
#     query += " ORDER BY si.posting_date DESC, si.name"

#     filter_values = {
#         "sales_invoice": filters.get("sales_invoice"),
#         "customer": filters.get("customer"),
#         "from_date": filters.get("from_date"),
#         "to_date": filters.get("to_date"),
#         "payment_entry": filters.get("payment_entry"),
#         "payment_posting_date": filters.get("payment_posting_date"),
#     }

#     # Remove None values from filter_values
#     filter_values = {k: v for k, v in filter_values.items() if v is not None}

#     return frappe.db.sql(query, filter_values, as_dict=1)





# from collections import defaultdict
# import frappe
# from frappe import _
# from frappe.query_builder.functions import Sum
# from frappe.utils import flt, today
# from datetime import datetime

# def execute(filters=None):
#     columns, data = [], []
#     data = get_data(filters)
#     columns = get_columns(filters)
#     return columns, data

# def get_columns(filters):
#     columns = [
#         {
#             "label": _("Sales Invoice"),
#             "fieldname": "sales_invoice",
#             "fieldtype": "Link",
#             "options": "Sales Invoice",
#             "width": 120,
#         },
#         {
#             "label": _("Posting Date"),
#             "fieldname": "posting_date",
#             "fieldtype": "Date",
#             "width": 100,
#         },
#         {
#             "label": _("Due Date"),
#             "fieldname": "due_date",
#             "fieldtype": "Date",
#             "width": 100,
#         },
#         {
#             "label": _("Customer"),
#             "fieldname": "customer",
#             "fieldtype": "Link",
#             "options": "Customer",
#             "width": 120,
#         },
#         {
#             "label": _("Grand Total"),
#             "fieldname": "grand_total",
#             "fieldtype": "Currency",
#             "width": 120,
#         },
#         {
#             "label": _("Interest Amount"),
#             "fieldname": "interest_amount",
#             "fieldtype": "Currency",
#             "width": 120,
#         },
#         {
#             "label": _("Total Amount"),
#             "fieldname": "total_amount",
#             "fieldtype": "Currency",
#             "width": 120,
#         },
#         {
#             "label": _("Rate of Interest (%)"),
#             "fieldname": "rate_of_interest",
#             "fieldtype": "Float",
#             "width": 100,
#             "precision": 2
#         },
#         {
#             "label": _("Latest Payment Entry"),
#             "fieldname": "payment_entry",
#             "fieldtype": "Link",
#             "options": "Payment Entry",
#             "width": 120,
#         },
#         {
#             "label": _("Latest Payment Date"),
#             "fieldname": "payment_posting_date",
#             "fieldtype": "Date",
#             "width": 120,
#         },
#         {
#             "label": _("Days Overdue"),
#             "fieldname": "days_overdue",
#             "fieldtype": "Int",
#             "width": 100,
#         },
#         {
#             "label": _("Total Payment Entries"),
#             "fieldname": "total_payment_entries",
#             "fieldtype": "Int",
#             "width": 100,
#         }
#     ]

#     return columns

# def get_data(filters):
#     data = []
#     si_data = get_sales_invoice_data(filters)
    
#     # Group by sales invoice and get latest payment entry
#     grouped_data = group_by_sales_invoice(si_data)
    
#     # Calculate interest for each unique sales invoice
#     for sales_invoice, rows in grouped_data.items():
#         # Use the first row (with latest payment) for calculations
#         row = rows[0]
#         row = calculate_interest(row, filters)
#         # Calculate total amount for each row
#         row = calculate_total_amount(row)
#         # Add count of payment entries
#         row['total_payment_entries'] = len(rows)
#         data.append(row)
    
#     return data

# def group_by_sales_invoice(si_data):
#     """Group data by sales invoice and sort payment entries by date"""
#     grouped = defaultdict(list)
    
#     for row in si_data:
#         grouped[row['sales_invoice']].append(row)
    
#     # For each sales invoice, sort payment entries by posting_date (latest first)
#     for sales_invoice in grouped:
#         grouped[sales_invoice].sort(
#             key=lambda x: x['payment_posting_date'] or datetime.min, 
#             reverse=True
#         )
    
#     return grouped

# def calculate_interest(row, filters):
#     """Calculate interest amount based on rate of interest and overdue days"""
#     rate_of_interest = flt(filters.get("rate_of_interest", 0))
    
#     # Get today's date for calculation
#     today_date = today()
    
#     # Calculate days overdue (if due_date is in the past)
#     if row.get('due_date'):
#         due_date = row['due_date']
#         if isinstance(due_date, str):
#             due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        
#         days_overdue = (datetime.now().date() - due_date).days
#         days_overdue = max(0, days_overdue)  # Only positive values (overdue)
#     else:
#         days_overdue = 0
    
#     row['days_overdue'] = days_overdue
#     row['rate_of_interest'] = rate_of_interest
    
#     # Calculate interest amount
#     # Formula: (Grand Total * Rate of Interest * Days Overdue) / (100 * 365)
#     if days_overdue > 0 and rate_of_interest > 0 and row.get('grand_total'):
#         grand_total = flt(row['grand_total'])
#         interest_amount = (grand_total * rate_of_interest * days_overdue) / (100 * 365)
#         row['interest_amount'] = flt(interest_amount, 2)
#     else:
#         row['interest_amount'] = 0.0
    
#     return row

# def calculate_total_amount(row):
#     """Calculate total amount (grand_total + interest_amount) for each row"""
#     grand_total = flt(row.get('grand_total', 0))
#     interest_amount = flt(row.get('interest_amount', 0))
#     row['total_amount'] = grand_total + interest_amount
#     return row

# def get_sales_invoice_data(filters):
#     query = """
#         SELECT 
#             si.name as sales_invoice,
#             si.due_date,
#             si.customer,
#             si.grand_total,
#             si.posting_date,
#             si.outstanding_amount,
#             pr.parent as payment_entry,
#             pr.reference_name,
#             pr.allocated_amount,
#             pe.posting_date as payment_posting_date
#         FROM `tabSales Invoice` AS si
#         LEFT JOIN `tabPayment Entry Reference` AS pr ON pr.reference_name = si.name
#         LEFT JOIN `tabPayment Entry` AS pe ON pe.name = pr.parent
#         WHERE si.docstatus = 1 AND si.outstanding_amount > 0
#     """

#     conditions = []

#     if filters.get("sales_invoice"):
#         conditions.append("si.name = %(sales_invoice)s")
#     if filters.get("customer"):
#         conditions.append("si.customer = %(customer)s")
#     if filters.get("from_date"):
#         conditions.append("si.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("si.posting_date <= %(to_date)s")
#     if filters.get("payment_entry"):
#         conditions.append("pr.parent = %(payment_entry)s")
#     if filters.get("payment_posting_date"):
#         conditions.append("pe.posting_date = %(payment_posting_date)s")

#     # Add conditions to query if they exist
#     if conditions:
#         query += " AND " + " AND ".join(conditions)

#     # Add ordering
#     query += " ORDER BY si.name, pe.posting_date DESC"

#     filter_values = {
#         "sales_invoice": filters.get("sales_invoice"),
#         "customer": filters.get("customer"),
#         "from_date": filters.get("from_date"),
#         "to_date": filters.get("to_date"),
#         "payment_entry": filters.get("payment_entry"),
#         "payment_posting_date": filters.get("payment_posting_date"),
#     }

#     # Remove None values from filter_values
#     filter_values = {k: v for k, v in filter_values.items() if v is not None}

#     return frappe.db.sql(query, filter_values, as_dict=1)



from collections import defaultdict
import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today
from datetime import datetime

def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    columns = get_columns(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {
            "label": _("Sales Invoice"),
            "fieldname": "sales_invoice",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 120,
        },
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "label": _("Due Date"),
            "fieldname": "due_date",
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 120,
        },
        {
            "label": _("Grand Total"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Interest Amount"),
            "fieldname": "interest_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Total Amount"),
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Rate of Interest (%)"),
            "fieldname": "rate_of_interest",
            "fieldtype": "Float",
            "width": 100,
            "precision": 2
        },
        {
            "label": _("Latest Payment Entry"),
            "fieldname": "payment_entry",
            "fieldtype": "Link",
            "options": "Payment Entry",
            "width": 120,
        },
        {
            "label": _("Latest Payment Date"),
            "fieldname": "payment_posting_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Total Allocated Amount"),
            "fieldname": "total_allocated_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Days Overdue"),
            "fieldname": "days_overdue",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": _("Total Payment Entries"),
            "fieldname": "total_payment_entries",
            "fieldtype": "Int",
            "width": 100,
        }
    ]

    return columns

def get_data(filters):
    data = []
    si_data = get_sales_invoice_data(filters)
    
    # Group by sales invoice and get latest payment entry
    grouped_data = group_by_sales_invoice(si_data)
    
    # Calculate interest for each unique sales invoice
    for sales_invoice, rows in grouped_data.items():
        # Use the first row (with latest payment) for calculations
        row = rows[0]
        row = calculate_interest(row, filters)
        # Calculate total amount for each row
        row = calculate_total_amount(row)
        # Add count of payment entries
        row['total_payment_entries'] = len(rows)
        # Calculate total allocated amount
        row['total_allocated_amount'] = calculate_total_allocated_amount(rows)
        data.append(row)
    
    return data

def group_by_sales_invoice(si_data):
    """Group data by sales invoice and sort payment entries by date"""
    grouped = defaultdict(list)
    
    for row in si_data:
        grouped[row['sales_invoice']].append(row)
    
    # For each sales invoice, sort payment entries by posting_date (latest first)
    for sales_invoice in grouped:
        grouped[sales_invoice].sort(
            key=lambda x: x['payment_posting_date'] or datetime.min, 
            reverse=True
        )
    
    return grouped

def calculate_total_allocated_amount(rows):
    """Calculate total allocated amount from all payment entries for a sales invoice"""
    total_allocated = 0.0
    for row in rows:
        if row.get('allocated_amount'):
            total_allocated += flt(row['allocated_amount'])
    return total_allocated

def calculate_interest(row, filters):
    """Calculate interest amount based on rate of interest and overdue days"""
    rate_of_interest = flt(filters.get("rate_of_interest", 0))
    
    # Get today's date for calculation
    today_date = today()
    
    # Calculate days overdue (if due_date is in the past)
    if row.get('due_date'):
        due_date = row['due_date']
        if isinstance(due_date, str):
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        
        days_overdue = (datetime.now().date() - due_date).days
        days_overdue = max(0, days_overdue)  # Only positive values (overdue)
    else:
        days_overdue = 0
    
    row['days_overdue'] = days_overdue
    row['rate_of_interest'] = rate_of_interest
    
    # Calculate interest amount
    # Formula: (Grand Total * Rate of Interest * Days Overdue) / (100 * 365)
    if days_overdue > 0 and rate_of_interest > 0 and row.get('grand_total'):
        grand_total = flt(row['grand_total'])
        interest_amount = (grand_total * rate_of_interest * days_overdue) / (100 * 365)
        row['interest_amount'] = flt(interest_amount, 2)
    else:
        row['interest_amount'] = 0.0
    
    return row

def calculate_total_amount(row):
    """Calculate total amount (grand_total + interest_amount) for each row"""
    grand_total = flt(row.get('grand_total', 0))
    interest_amount = flt(row.get('interest_amount', 0))
    row['total_amount'] = grand_total + interest_amount
    return row

def get_sales_invoice_data(filters):
    query = """
        SELECT 
            si.name as sales_invoice,
            si.due_date,
            si.customer,
            si.grand_total,
            si.posting_date,
            si.outstanding_amount,
            pr.parent as payment_entry,
            pr.reference_name,
            pr.allocated_amount,
            pe.posting_date as payment_posting_date
        FROM `tabSales Invoice` AS si
        LEFT JOIN `tabPayment Entry Reference` AS pr ON pr.reference_name = si.name
        LEFT JOIN `tabPayment Entry` AS pe ON pe.name = pr.parent
        WHERE si.docstatus = 1
    """

    conditions = []

    if filters.get("sales_invoice"):
        conditions.append("si.name = %(sales_invoice)s")
    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
    if filters.get("payment_entry"):
        conditions.append("pr.parent = %(payment_entry)s")
    if filters.get("payment_posting_date"):
        conditions.append("pe.posting_date = %(payment_posting_date)s")

    # Add conditions to query if they exist
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Add ordering
    query += " ORDER BY si.name, pe.posting_date DESC"

    filter_values = {
        "sales_invoice": filters.get("sales_invoice"),
        "customer": filters.get("customer"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "payment_entry": filters.get("payment_entry"),
        "payment_posting_date": filters.get("payment_posting_date"),
    }

    # Remove None values from filter_values
    filter_values = {k: v for k, v in filter_values.items() if v is not None}

    return frappe.db.sql(query, filter_values, as_dict=1)

