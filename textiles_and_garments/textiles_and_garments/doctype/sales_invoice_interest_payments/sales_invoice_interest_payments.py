# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from collections import defaultdict
from datetime import datetime
from frappe.utils import today, flt

class SalesInvoiceInterestPayments(Document):
    @frappe.whitelist()
    def get_sales_invoice_data(self):
        print("\n\nget_sales_invoice_data\n",self)
        """Get sales invoice data based on filters"""
        filters = {
            "sales_invoice": None,  # We'll get all invoices for the customer/date range
            "customer": self.customer,
            "from_date": self.from_date,
            "to_date": self.to_date
        }
        
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

        if self.customer:
            conditions.append("si.customer = %(customer)s")
        if self.from_date:
            conditions.append("si.posting_date >= %(from_date)s")
        if self.to_date:
            conditions.append("si.posting_date <= %(to_date)s")

        # Add conditions to query if they exist
        if conditions:
            query += " AND " + " AND ".join(conditions)

        # Add ordering
        query += " ORDER BY si.name, pe.posting_date DESC"

        filter_values = {
            "customer": self.customer,
            "from_date": self.from_date,
            "to_date": self.to_date,
        }

        # Remove None values from filter_values
        filter_values = {k: v for k, v in filter_values.items() if v is not None}
        data = frappe.db.sql(query, filter_values, as_dict=1)
        print("\n\ndata\n\n",data)

        return frappe.db.sql(query, filter_values, as_dict=1)

    def group_by_sales_invoice(self, si_data):
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

    def calculate_total_allocated_amount(self, rows):
        """Calculate total allocated amount from all payment entries for a sales invoice"""
        total_allocated = 0.0
        for row in rows:
            if row.get('allocated_amount'):
                total_allocated += flt(row['allocated_amount'])
        return total_allocated

    def calculate_interest(self, row, rate_of_interest):
        """Calculate interest amount based on rate of interest and overdue days"""
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
        row['rate_of_interest'] = 18
        
        # Calculate interest amount
        # Formula: (Grand Total * Rate of Interest * Days Overdue) / (100 * 365)
        if days_overdue > 0 and rate_of_interest > 0 and row.get('grand_total'):
            grand_total = flt(row['grand_total'])
            interest_amount = (grand_total * rate_of_interest * days_overdue) / (100 * 365)
            row['interest_amount'] = flt(interest_amount, 2)
        else:
            row['interest_amount'] = 0.0
        
        return row

    def calculate_total_amount(self, row):
        """Calculate total amount (grand_total + interest_amount) for each row"""
        grand_total = flt(row.get('grand_total', 0))
        interest_amount = flt(row.get('interest_amount', 0))
        row['total_amount'] = grand_total + interest_amount
        return row

    @frappe.whitelist()
    def get_sales_invoice(self):
        """Main method to get sales invoices and calculate interest"""
        if not self.customer:
            frappe.throw("Please select a Customer first")
        
        # Get rate of interest from the doctype field or use default
        rate_of_interest = flt(self.get("rate_of_interest") or 18)
        
        # Get sales invoice data
        si_data = self.get_sales_invoice_data()
        
        if not si_data:
            frappe.msgprint("No sales invoices found for the selected criteria")
            return
        
        # Group by sales invoice and get latest payment entry
        grouped_data = self.group_by_sales_invoice(si_data)
        
        # Clear existing table
        self.set("sales_invoice_interest_payment_item", [])
        
        total_grand_total = 0
        total_interest_amount = 0
        total_net_amount = 0
        
        # Calculate interest for each unique sales invoice and add to table
        for sales_invoice, rows in grouped_data.items():
            # Use the first row (with latest payment) for calculations
            row = rows[0]
            row = self.calculate_interest(row, rate_of_interest)
            # Calculate total amount for each row
            row = self.calculate_total_amount(row)
            
            # Calculate total allocated amount
            total_allocated_amount = self.calculate_total_allocated_amount(rows)
            
            # Get latest payment date
            latest_payment_date = None
            for payment_row in rows:
                if payment_row.get('payment_posting_date'):
                    latest_payment_date = payment_row['payment_posting_date']
                    break
            
            # Add row to child table
            child_row = self.append("sales_invoice_interest_payment_item", {
                "sales_invoice": row['sales_invoice'],
                "posting_date": row['posting_date'],
                "due_date": row['due_date'],
                "customer": row['customer'],
                "grand_total": row['grand_total'],
                "interest_amount": row['interest_amount'],
                "total_amount": row['total_amount'],
                "rate_of_interest": rate_of_interest,
                "latest_payment_date": latest_payment_date,
                "latest_payment_entry_date": latest_payment_date,  # Same as above
                "total_allocation": total_allocated_amount,
                "days_overdue": row['days_overdue'],
                "total_payment_entries": len(rows)
            })
            
            # Update totals
            total_grand_total += flt(row['grand_total'])
            total_interest_amount += flt(row['interest_amount'])
            total_net_amount += flt(row['interest_amount'])
        
        # Update main totals
        self.grand_total = total_grand_total
        
        # # Calculate net total after deduct percentage
        # if self.deduct_percentage:
        #     deduct_amount = (total_net_amount * flt(self.deduct_percentage)) / 100
        #     self.total_amount_included_interest = total_net_amount - deduct_amount
        # else:
        #     self.total_amount_included_interest = total_net_amount
        
        # Save the document to refresh the table
        self.save()
        
        frappe.msgprint(f"Added {len(grouped_data)} sales invoices to the table")



@frappe.whitelist()
def get_total_of_sales_invoice_interest_payments(custom_sales_invoice_interest_payments):
    
    # Fetch the Sales Invoice Interest Payment document
    sales_invoice_interest_payment = frappe.get_doc("Sales Invoice Interest Payments", custom_sales_invoice_interest_payments)
    return sales_invoice_interest_payment.grand_total



@frappe.whitelist()
def create_jv_for_siip(docname):
    print("\n\ncreate_jv_for_siip\n\n")
    sales_invoice_interest_payments = frappe.get_doc("Sales Invoice Interest Payments", docname)
    print("\n\nsales_invoice_interest_payments\n\n",sales_invoice_interest_payments.total_amount_included_interest)
    print("\n\nsales_invoice_interest_payments\n\n",sales_invoice_interest_payments.grand_total)

    # sales_invoice_interest_payments_bonus = sales_invoice_interest_payments.grand_total - sales_invoice_interest_payments.total_amount_included_interest
    # print("\n\nsales_invoice_interest_payments_bonus\n\n",sales_invoice_interest_payments_bonus)

    if sales_invoice_interest_payments.customer:
        customer = sales_invoice_interest_payments.customer
        # contractors = sales_invoice_interest_payments.contractor + ','+ sales_invoice_interest_payments.contractor + ' (Reserved)'
    
    doc=frappe.new_doc("Journal Entry")
    doc.workflow_state="Draft"
    doc.docstatus=0
    doc.voucher_type="Journal Entry"
    doc.ineligibility_reason="As per rules 42 & 43 of CGST Rules"
    doc.naming_series = "JV/25/.#"
    doc.company="Pranera Services and Solutions Pvt. Ltd.,"
    doc.posting_date = datetime.today().strftime("%Y-%m-%d")  # Assigns current date in "YYYY-MM-DD" format
    doc.apply_tds=0
    doc.write_off_based_on="Accounts Receivable"
    doc.write_off_amount=0.0
    doc.letter_head="CUSTOM__PSS JV_LOGO"
    doc.is_opening="No"
    doc.doctype="Journal Entry"
    doc.custom_sales_invoice_interest_paymentss = docname

    doc.append("accounts", {
        "docstatus": 0,
        "idx": 1,
        "account": "Interest Received - PSS",
        "account_type": "",
        "party_type": "",
        "party": "",
        "cost_center": "Pranera Textiles - PSS",
        "account_currency": "INR",
        "exchange_rate": 1.0,
        "debit_in_account_currency": 0.0,
        "credit": sales_invoice_interest_payments.total_amount_included_interest,
        "credit_in_account_currency": sales_invoice_interest_payments.total_amount_included_interest,
        "debit": 0.0,
        "is_advance": "No",
        "against_account": "Debtors - PSS",
        "parentfield": "accounts",
        "parenttype": "Journal Entry",
        "doctype": "Journal Entry Account"
    })


    doc.append("accounts", {
        "docstatus": 0,
        "idx": 1,
        "account": "Debtors - PSS",
        "account_type": "Receivable",
        "party_type": "Customer",
        "party": customer,
        "cost_center": "Pranera Textiles - PSS",
        "account_currency": "INR",
        "exchange_rate": 1.0,
        "debit_in_account_currency": sales_invoice_interest_payments.total_amount_included_interest,
        "credit": 0.0,
        "credit_in_account_currency": 0.0,
        "debit": sales_invoice_interest_payments.total_amount_included_interest,
        "is_advance": "No",
        "against_account": "Interest Received - PSS",
        "parentfield": "accounts",
        "parenttype": "Journal Entry",
        "doctype": "Journal Entry Account"
    })
    doc.save(ignore_permissions=True)
    frappe.msgprint("JV Created")