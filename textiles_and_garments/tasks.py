import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import flt
from erpnext.setup.utils import get_exchange_rate
from bs4 import BeautifulSoup
import urllib.parse
from frappe_whatsapp.utils import run_server_script_for_doc_event
from datetime import date
from datetime import datetime



# def every_five_minutes():
#     print("\n\n\nevery_1_minutes\n\n\n")
#     customer = frappe.form_dict.customer
#     data = frappe.db.sql(f"""SELECT sum(grand_total), \
#     	docstatus, status FROM `tabSales Invoice` \
#     	WHERE customer= '{customer}' and docstatus = 1;\
#     	""", as_dict=True)
#     frappe.response['message'] =  data



def every_five_minutes():
    print("\n\nSending outstanding emails to customers...\n\n")
    
    # Define report date and company (customize as needed)
    report_date = date.today()  # Current date, or set a specific date
    company = "Pranera Services and Solutions Pvt. Ltd.,"  # Replace with your company name
    
    # Fetch all customers with outstanding amounts using frappe.db.get_all
    outstanding_data = frappe.db.get_all(
        "GL Entry",
        fields=["party", "sum(debit - credit) as outstanding"],
        filters={
            "posting_date": ("<=", report_date),
            "is_cancelled": 0,
            "company": company
        },
        group_by="party",
        as_list=1
    )

    print("\n\n\noutstanding_data\n\n\n",outstanding_data)
    
    for record in outstanding_data:
        customer = record[0]  # Party (Customer name)
        outstanding = record[1]  # Outstanding amount

        print("\n\nCustomer:\n", customer)
        print("\n\nOutstanding Amount:\n", outstanding)

        if customer:
            # Fetch customer email from Customer doctype
            customer_email = frappe.db.get_value("Customer", customer, "email_id")
            print("\n\nCustomer Email from Customer Doctype:\n\n", customer_email)

            # # Fetch email from Address master linked to the customer
            # address_email = frappe.db.get_value(
            #     "Address",
            #     {"customer": customer, "is_primary_address": 1},  # Filters for primary address of the customer
            #     "email_id"
            # )
            # print("\n\nCustomer Email from Address Master:\n\n", address_email)

            # # Fetch email from Contact master linked to the customer
            # contact_email = frappe.db.get_value(
            #     "Contact",
            #     {"link_doctype": "Customer", "link_name": customer},  # Filters for contact linked to the customer
            #     "email_id"
            # )
            # print("\n\nCustomer Email from Contact Master:\n\n", contact_email)

            # # Use a fallback if no email is found
            # final_email = customer_email or address_email or contact_email
            # print("\n\nFinal Email Selected:\n\n", final_email)

            
            sales_invoice_details = frappe.db.sql("""
                SELECT 
                    posting_date, 
                    name, 
                    outstanding_amount 
                FROM 
                    `tabSales Invoice` 
                WHERE 
                    customer = %s 
                    AND outstanding_amount > 0 
                    AND docstatus = 1
            """, (customer,), as_dict=True)


            print(f"\n\nSales Invoice Details for {customer}:\n", sales_invoice_details)
            total_outstanding = sum(invoice['outstanding_amount'] for invoice in sales_invoice_details)
            print("\n\ntotal_outstanding\n\n",total_outstanding)
            if customer_email:
                print(f"Customer Email: {customer_email}")
            if total_outstanding > 0:
                print(f"Total Outstanding: {total_outstanding}")
            if total_outstanding == outstanding:
                print(f"Total Outstanding matches Outstanding: {total_outstanding} == {outstanding}")


            if customer_email and total_outstanding > 0 and total_outstanding == outstanding:
                # Enqueue the email sending task
                frappe.enqueue(
                    send_outstanding_email_to_customers,
                    queue="long",
                    customer=customer,
                    outstanding=outstanding,
                    customer_email=customer_email,
                    sales_invoice_details=sales_invoice_details
                )
            else:
                frappe.enqueue(
                    send_outstanding_email_to_accounts_team,
                    queue="long",
                    customer=customer,
                    outstanding=outstanding,
                    customer_email="accounts@praneraservices.com, jose@praneraservices.com",
                    sales_invoice_details=sales_invoice_details
                )
                    

    print("\n\nEmail notifications have been enqueued.\n\n")

def send_outstanding_email_to_customers(customer, outstanding, customer_email, sales_invoice_details):
    """Function to send outstanding email to a customer."""
    subject = f"Outstanding Payment Reminder for {customer} from Pranera Services and Solutions Pvt Ltd"
    
    # # Create a detailed table of sales invoice data
    # invoice_table = "<br>".join(
    #     f"Date: {invoice['posting_date']}, Invoice: {invoice['name']}, Outstanding: {invoice['outstanding_amount']}" 
    #     for invoice in sales_invoice_details
    # )
    # Create a detailed HTML table for sales invoice data
    invoice_table = """
    <table style="border-collapse: collapse; width: 100%; text-align: left;">
        <thead>
            <tr>
                <th style="border: 1px solid black; padding: 8px;">Date</th>
                <th style="border: 1px solid black; padding: 8px;">Invoice</th>
                <th style="border: 1px solid black; padding: 8px;">Outstanding Amount</th>
            </tr>
        </thead>
        <tbody>
    """
    for invoice in sales_invoice_details:
        invoice_table += f"""
            <tr>
                <td style="border: 1px solid black; padding: 8px;">{invoice['posting_date']}</td>
                <td style="border: 1px solid black; padding: 8px;">{invoice['name']}</td>
                <td style="border: 1px solid black; padding: 8px;">{invoice['outstanding_amount']}</td>
            </tr>
        """
    invoice_table += """
        </tbody>
    </table>
    """


    message = f"""
        Dear {customer},<br><br>

        We hope this message finds you well. <br><br>
        
        As of now, your outstanding balance with us is <b>{outstanding}</b>. Please find the details of your outstanding invoices below:<br><br>

        {invoice_table}<br><br>

        Please make arrangements to clear this amount at the earliest.<br><br>

        If you have already made the payment, please disregard this message.<br><br>

        Thank you for your cooperation.<br><br>

        Best regards,  <br>
        Pranera Services and Solutions Pvt Ltd
    """
    
    # Send the email
    frappe.sendmail(
        recipients=customer_email,
        subject=subject,
        sender="jose@praneraservices.com",
        message=message
    )
    print(f"Email sent to {customer_email} for customer {customer}.")

def send_outstanding_email_to_accounts_team(customer, outstanding, customer_email, sales_invoice_details):
    """Function to send outstanding email to a customer."""
    subject = f"Need to do the payment reconciliation for Outstanding Payment of {customer} from Pranera Services and Solutions Pvt Ltd"
    
    # # Create a detailed table of sales invoice data
    # invoice_table = "<br>".join(
    #     f"Date: {invoice['posting_date']}, Invoice: {invoice['name']}, Outstanding: {invoice['outstanding_amount']}" 
    #     for invoice in sales_invoice_details
    # )
    # Create a detailed HTML table for sales invoice data
    invoice_table = """
    <table style="border-collapse: collapse; width: 100%; text-align: left;">
        <thead>
            <tr>
                <th style="border: 1px solid black; padding: 8px;">Date</th>
                <th style="border: 1px solid black; padding: 8px;">Invoice</th>
                <th style="border: 1px solid black; padding: 8px;">Outstanding Amount</th>
            </tr>
        </thead>
        <tbody>
    """
    for invoice in sales_invoice_details:
        invoice_table += f"""
            <tr>
                <td style="border: 1px solid black; padding: 8px;">{invoice['posting_date']}</td>
                <td style="border: 1px solid black; padding: 8px;">{invoice['name']}</td>
                <td style="border: 1px solid black; padding: 8px;">{invoice['outstanding_amount']}</td>
            </tr>
        """
    invoice_table += """
        </tbody>
    </table>
    """


    message = f"""
        Dear Accounts Team,<br><br>

        We hope this message finds you well. <br><br>
        
        As of now, the {customrt} outstanding balance is <b>{outstanding}</b>. Please find the details of your outstanding invoices below:<br><br>

        {invoice_table}<br><br>

        Please make arrangements to do reconciliation for this amount at the earliest.<br><br>

        If you have already made the payment reconciliation, please disregard this message.<br><br>

        Thank you for your cooperation.<br><br>

        Best regards,  <br>
        Pranera Services and Solutions Pvt Ltd
    """
    
    # Send the email
    frappe.sendmail(
        recipients=customer_email,
        subject=subject,
        sender="jose@praneraservices.com",
        message=message
    )
    print(f"Email sent to {customer_email} for customer {customer}.")    



# def every_five_minutes():
#     print("\n\nSending outstanding emails to customers...\n\n")
    
#     # Define report date and company (customize as needed)
#     report_date = date.today()  # Current date, or set a specific date
#     company = "Pranera Services and Solutions Pvt. Ltd.,"  # Replace with your company name
    
#     # Fetch all customers with outstanding amounts using frappe.db.get_all
#     outstanding_data = frappe.db.get_all(
#         "GL Entry",
#         fields=["party", "sum(debit - credit) as outstanding"],
#         filters={
#             "posting_date": ("<=", report_date),
#             "is_cancelled": 0,
#             "company": company
#         },
#         group_by="party",
#         as_list=1
#     )

#     print("\n\n\noutstanding_data\n\n\n",outstanding_data)
#     for record in outstanding_data:
#         customer = record[0]  # Party (Customer name)
#         outstanding = record[1]  # Outstanding amount
#         print("\n\n\ncustomer\n\n\n",customer)
#         print("\n\n\noutstanding\n\n\n",outstanding)
        
#         # Fetch customer email
#         customer_email = frappe.db.get_value("Customer", customer, "email_id")
        
#         if customer_email:
#             # Enqueue the email sending task
#             frappe.enqueue(
#                 send_outstanding_email,
#                 queue="long",
#                 customer=customer,
#                 outstanding=outstanding,
#                 customer_email=customer_email
#             )

#     print("\n\nEmail notifications have been enqueued.\n\n")

# def send_outstanding_email(customer, outstanding, customer_email):
#     """Function to send outstanding email to a customer."""
#     subject = f"Outstanding Payment Reminder for {customer} from Pranera Services and Solutions Pvt Ltd"
#     message = f"""
#         Dear {customer},<br><br>

#         We hope this message finds you well. <br><br>
        
#         As of now, your outstanding balance with us is <b>{outstanding}</b>.
#         Please make arrangements to clear this amount at the earliest.<br><br>

#         If you have already made the payment, please disregard this message.<br><br>

#         Thank you for your cooperation.<br><br>

#         Best regards,  <br>
#         Pranera Services and Solutions Pvt Ltd
#     """
    
#     # Send the email
#     frappe.sendmail(
#         recipients=customer_email,
#         subject=subject,
#         sender="jose@praneraservices.com",
#         message=message
#     )
#     print(f"Email sent to {customer_email} for customer {customer}.")


# def every_five_minutes():
#     print("\n\nSending outstanding emails to customers...\n\n")
    
#     # Define report date and company (customize as needed)
#     report_date = date.today()  # Current date, or set a specific date
#     company = "Pranera Services and Solutions Pvt. Ltd.,"  # Replace with your company name
    
#     # Fetch all customers with outstanding amounts using frappe.db.get_all
#     outstanding_data = frappe.db.get_all(
#         "GL Entry",
#         fields=["party", "sum(debit - credit) as outstanding"],
#         filters={
#             "posting_date": ("<=", report_date),
#             "is_cancelled": 0,
#             "company": company
#         },
#         group_by="party",
#         as_list=1
#     )

#     print("\n\n\noutstanding_data\n\n\n",outstanding_data)
    
#     # # Loop through the data and send emails
#     for record in outstanding_data:
#         customer = record[0]  # Party (Customer name)
#         outstanding = record[1]  # Outstanding amount
        
#         # Fetch customer email
#         customer_email = frappe.db.get_value("Customer", customer, "email_id")
        
#         if customer_email:
#             # Compose the email message
#             subject = f"Outstanding Payment Reminder for {customer} from Pranera Services and Solutions Pvt Ltd"
#             message = f"""
#                 Dear {customer},<br><br>

#                 We hope this message finds you well. <br><br>
                
#                 As of now, your outstanding balance with us is <b>{outstanding}</b>.
#                 Please make arrangements to clear this amount at the earliest.<br><br>

#                 If you have already made the payment, please disregard this message.<br><br>

#                 Thank you for your cooperation.<br><br>

#                 Best regards,  <br>
#                 Pranera Services and Solutions Pvt Ltd
#             """
            
#             # Send the email
#             frappe.sendmail(
#                 recipients=customer_email,
#                 subject=subject,
#                 sender="jose@praneraservices.com",
#                 message=message
#             )
#             print(f"Email sent to {customer_email} for customer {customer}.")

#     print("\n\nEmail notifications sent successfully.\n\n")





