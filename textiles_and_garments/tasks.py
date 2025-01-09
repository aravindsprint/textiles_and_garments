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

    # print("\n\n\noutstanding_data\n\n\n",outstanding_data)
    
    for record in outstanding_data:
        customer = record[0]  # Party (Customer name)
        outstanding = record[1]  # Outstanding amount

        # print("\n\nCustomer:\n", customer)
        # print("\n\nOutstanding Amount:\n", outstanding)

        if customer and outstanding > 0:
            # Fetch customer email from Customer doctype
            customer_email = frappe.db.get_value("Customer", customer, "email_id")
            print("\n\nCustomer Email from Customer Doctype:\n\n", customer_email)    
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
            if round(total_outstanding, 2) == round(float(outstanding), 2):
                print(f"Total Outstanding matches Outstanding: {total_outstanding} == {outstanding}")


            if customer_email and total_outstanding > 0 and round(total_outstanding, 2) == round(float(outstanding), 2):
                # Enqueue the email sending task
                print("\n\nsending mail for the customer\n\n", customer_email)
                frappe.enqueue(
                    send_outstanding_email_to_customers,
                    queue="short",
                    customer=customer,
                    outstanding=outstanding,
                    customer_email=customer_email,
                    sales_invoice_details=sales_invoice_details
                )
            else:
                print("\n\nsending mail for the accounts team\n\n", customer_email)
                frappe.enqueue(
                    send_outstanding_email_to_accounts_team,
                    queue="short",
                    customer=customer,
                    outstanding=outstanding,
                    customer_email="accounts@praneraservices.com, jose@praneraservices.com",
                    sales_invoice_details=sales_invoice_details
                )
                    

    print("\n\nEmail notifications have been enqueued.\n\n")

def send_outstanding_email_to_customers(customer, outstanding, customer_email, sales_invoice_details):
    """Function to send outstanding email to a customer."""
    print("\n\nsend_outstanding_email_to_customers\n\n", customer_email)
    subject = f"Outstanding Payment Reminder for {customer} from Pranera Services and Solutions Pvt Ltd"
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





# data =  [
#             {
#                 "docstatus": 0,
#                 "title": "LIC OF INDIA",
#                 "naming_series": "B/24/.#####",
#                 "customer": "LIC OF INDIA",
#                 "remarks": "No Remarks",
#                 "eway_bill_cancelled": 0,
#                 "irn_cancelled": 0,
#                 "customer_name": "LIC OF INDIA",
#                 "name_of_commodity": "",
#                 "company": "MANONMANI THANGAVELU",
#                 "posting_date": "2024-12-31",
#                 "posting_time": "13:45:06",
#                 "set_posting_time": 1,
#                 "due_date": "2024-12-31",
#                 "is_pos": 0,
#                 "pos_profile": null,
#                 "is_consolidated": 0,
#                 "is_return": 0,
#                 "return_against": null,
#                 "update_outstanding_for_self": 1,
#                 "update_billed_amount_in_sales_order": 0,
#                 "update_billed_amount_in_delivery_note": 1,
#                 "is_debit_note": 0,
#                 "is_reverse_charge": 0,
#                 "is_export_with_gst": 0,
#                 "proforma_invoice": null,
#                 "quotation": null,
#                 "amended_from": null,
#                 "cost_center": null,
#                 "income_account": null,
#                 "project": null,
#                 "currency": "INR",
#                 "conversion_rate": 1.0,
#                 "selling_price_list": "Standard Selling",
#                 "price_list_currency": "INR",
#                 "plc_conversion_rate": 1.0,
#                 "ignore_pricing_rule": 0,
#                 "default_warehouse": null,
#                 "scan_barcode": null,
#                 "update_stock": 0,
#                 "set_warehouse": null,
#                 "set_target_warehouse": null,
#                 "no_of_boxes_or_rolls": null,
#                 "total_quantity": 0.0,
#                 "total_qty": 1.0,
#                 "total_net_weight": 0.0,
#                 "base_total": 42693.0,
#                 "base_net_total": 42693.0,
#                 "total": 42693.0,
#                 "net_total": 42693.0,
#                 "tax_category": "",
#                 "taxes_and_charges": "Output GST In-state - MT",
#                 "shipping_rule": null,
#                 "incoterm": null,
#                 "named_place": null,
#                 "base_total_taxes_and_charges": 7684.74,
#                 "total_taxes_and_charges": 7684.74,
#                 "base_grand_total": 50377.74,
#                 "base_rounding_adjustment": 0.0,
#                 "base_rounded_total": 0.0,
#                 "base_in_words": "INR Fifty Thousand, Three Hundred And Seventy Seven and Seventy Four Paisa only.",
#                 "grand_total": 50377.74,
#                 "rounding_adjustment": 0.0,
#                 "use_company_roundoff_cost_center": 0,
#                 "rounded_total": 0.0,
#                 "in_words": "INR Fifty Thousand, Three Hundred And Seventy Seven and Seventy Four Paisa only.",
#                 "total_advance": 0.0,
#                 "outstanding_amount": 50377.74,
#                 "totaloutstanding_amount": 0.0,
#                 "disable_rounded_total": 1,
#                 "apply_discount_on": "Grand Total",
#                 "base_discount_amount": 0.0,
#                 "is_cash_or_non_trade_discount": 0,
#                 "additional_discount_account": null,
#                 "additional_discount_percentage": 0.0,
#                 "discount_amount": 0.0,
#                 "other_charges_calculation": "<div class=\"tax-break-up\" style=\"overflow-x: auto;\">\n\t<table class=\"table table-bordered table-hover\">\n\t\t<thead>\n\t\t\t<tr>\n\t\t\t\t\n\t\t\t\t\t\n\t\t\t\t\t\t<th class=\"text-left\">Item</th>\n\t\t\t\t\t\n\t\t\t\t\n\t\t\t\t\t\n\t\t\t\t\t\t<th class=\"text-right\">Taxable Amount</th>\n\t\t\t\t\t\n\t\t\t\t\n\t\t\t\t\t\n\t\t\t\t\t\t<th class=\"text-right\">SGST</th>\n\t\t\t\t\t\n\t\t\t\t\n\t\t\t\t\t\n\t\t\t\t\t\t<th class=\"text-right\">CGST</th>\n\t\t\t\t\t\n\t\t\t\t\n\t\t\t</tr>\n\t\t</thead>\n\t\t<tbody>\n\t\t\t\n\t\t\t\t<tr>\n\t\t\t\t\t<td>SERVICES/RENTAL 18%</td>\n\t\t\t\t\t<td class=\"text-right\">\n\t\t\t\t\t\t\n\t\t\t\t\t\t\t₹ 42,693.00\n\t\t\t\t\t\t\n\t\t\t\t\t</td>\n\t\t\t\t\t\n\t\t\t\t\t\t\n\t\t\t\t\t\t\n\t\t\t\t\t\t\t<td class=\"text-right\">\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t(9.0%)\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t₹ 3,842.37\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t</td>\n\t\t\t\t\t\t\n\t\t\t\t\t\n\t\t\t\t\t\t\n\t\t\t\t\t\t\n\t\t\t\t\t\t\t<td class=\"text-right\">\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t(9.0%)\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t₹ 3,842.37\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t</td>\n\t\t\t\t\t\t\n\t\t\t\t\t\n\t\t\t\t</tr>\n\t\t\t\n\t\t</tbody>\n\t</table>\n</div>",
#                 "total_billing_hours": 0.0,
#                 "total_billing_amount": 0.0,
#                 "cash_bank_account": null,
#                 "base_paid_amount": 0.0,
#                 "paid_amount": 0.0,
#                 "base_change_amount": 0.0,
#                 "change_amount": 0.0,
#                 "account_for_change_amount": null,
#                 "allocate_advances_automatically": 0,
#                 "only_include_allocated_payments": 0,
#                 "write_off_amount": 0.0,
#                 "base_write_off_amount": 0.0,
#                 "write_off_outstanding_amount_automatically": 0,
#                 "write_off_account": null,
#                 "write_off_cost_center": null,
#                 "redeem_loyalty_points": 0,
#                 "loyalty_points": 0,
#                 "loyalty_amount": 0.0,
#                 "loyalty_program": null,
#                 "loyalty_redemption_account": null,
#                 "loyalty_redemption_cost_center": null,
#                 "customer_address": "LIC OF INDIA-Billing",
#                 "address_display": "102, Life Insurance Corporation<br>Anna Salai, Chennai<br>Chennai<br>\nTamil Nadu,\nState Code: 33<br>PIN: 600002<br>India<br>\nPhone: 9943497999<br>Email: nomail@gmail.com<br>GSTIN: 33AAACL0582H1ZT<br>",
#                 "billing_address_gstin": "33AAACL0582H1ZT",
#                 "gst_category": "Registered Regular",
#                 "place_of_supply": "33-Tamil Nadu",
#                 "export_type": "",
#                 "contact_person": "LIC OF INDIA-LIC OF INDIA",
#                 "contact_display": "LIC OF INDIA",
#                 "contact_mobile": "9943497999",
#                 "contact_email": "nomail@gmail.com",
#                 "territory": null,
#                 "shipping_address_name": "LIC OF INDIA-Billing",
#                 "shipping_address": "102, Life Insurance Corporation<br>Anna Salai, Chennai<br>Chennai<br>\nTamil Nadu,\nState Code: 33<br>PIN: 600002<br>India<br>\nPhone: 9943497999<br>Email: nomail@gmail.com<br>GSTIN: 33AAACL0582H1ZT<br>",
#                 "port_address": null,
#                 "dispatch_address_name": null,
#                 "dispatch_address": null,
#                 "company_address": "MANONMANI THANGAVELU-Billing",
#                 "company_gstin": "33ADZPM4255D3ZA",
#                 "company_contact_person": null,
#                 "company_address_display": "Flat no 102<br>Athani Road<br>Sathya,angalam<br>\nTamil Nadu,\nState Code: 33<br>PIN: 638401<br>India<br>\nPhone: 919999999999<br>Email: nomail@gmail.com<br>GSTIN: 33ADZPM4255D3ZA<br>",
#                 "ignore_default_payment_terms_template": 0,
#                 "payment_terms_template": null,
#                 "tc_name": null,
#                 "payment_terms": null,
#                 "terms": null,
#                 "po_no": "",
#                 "po_date": null,
#                 "debit_to": "Debtors - MT",
#                 "party_account_currency": "INR",
#                 "is_opening": "No",
#                 "unrealized_profit_loss_account": null,
#                 "against_income_account": "Office Rent - MT",
#                 "unicommerce_order_code": null,
#                 "unicommerce_channel_id": null,
#                 "unicommerce_facility_code": null,
#                 "unicommerce_invoice_code": null,
#                 "unicommerce_shipping_package_code": null,
#                 "unicommerce_shipping_provider": null,
#                 "unicommerce_shipping_method": null,
#                 "unicommerce_tracking_code": null,
#                 "unicommerce_shipping_package_status": null,
#                 "unicommerce_manifest_generated": 0,
#                 "unicommerce_is_cod": 0,
#                 "unicommerce_return_code": null,
#                 "sales_partner": null,
#                 "amount_eligible_for_commission": 42693.0,
#                 "commission_rate": 0.0,
#                 "total_commission": 0.0,
#                 "letter_head": "CUSTOM__PSS JV_LOGO",
#                 "group_same_items": 0,
#                 "invoice_copy": "Original for Recipient",
#                 "reverse_charge": "N",
#                 "select_print_heading": null,
#                 "language": "en",
#                 "transporter": null,
#                 "gst_transporter_id": null,
#                 "driver": null,
#                 "lr_no": null,
#                 "vehicle_no": "-",
#                 "distance": 0,
#                 "transporter_name": null,
#                 "mode_of_transport": "Road",
#                 "driver_name": null,
#                 "gst_vehicle_type": "Regular",
#                 "ecommerce_gstin": null,
#                 "port_code": null,
#                 "shipping_bill_number": null,
#                 "shipping_bill_date": null,
#                 "ack_no": null,
#                 "ack_date": null,
#                 "irn_cancel_date": null,
#                 "signed_einvoice": null,
#                 "signed_qr_code": null,
#                 "qrcode_image": null,
#                 "transporter_address": null,
#                 "transporter_address_display": null,
#                 "subscription": null,
#                 "from_date": null,
#                 "auto_repeat": null,
#                 "to_date": null,
#                 "status": "Overdue",
#                 "einvoice_status": "Pending",
#                 "failure_description": null,
#                 "inter_company_invoice_reference": null,
#                 "campaign": null,
#                 "represents_company": null,
#                 "source": null,
#                 "customer_group": null,
#                 "is_internal_customer": 0,
#                 "is_discounted": 0,
#                 # "items" : items
#             }
#         ]




# items = [
#             {
#                 "idx": 1,
#                 "parentfield": "items",
#                 "parenttype": "Sales Invoice",
#                 "has_item_scanned": 0,
#                 "item_code": "SERVICES/RENTAL 18%",
#                 "gst_hsn_code": "997316",
#                 "item_group": "SERVICES_EXPENSES",
#                 "image": "",
#                 "qty": 1.0,
#                 "stock_uom": "Nos",
#                 "uom": "Nos",
#                 "conversion_factor": 1.0,
#                 "stock_qty": 1.0,
#                 "price_list_rate": 0.0,
#                 "base_price_list_rate": 0.0,
#                 "margin_type": "",
#                 "margin_rate_or_amount": 0.0,
#                 "rate_with_margin": 0.0,
#                 "discount_percentage": 0.0,
#                 "discount_amount": 0.0,
#                 "base_rate_with_margin": 0.0,
#                 "rate": 42693.0,
#                 "amount": 42693.0,
#                 "item_tax_template": "GST 18% - MT",
#                 "gst_treatment": "Taxable",
#                 "base_rate": 42693.0,
#                 "base_amount": 42693.0,
#                 "pricing_rules": "",
#                 "stock_uom_rate": 42693.0,
#                 "is_free_item": 0,
#                 "grant_commission": 1,
#                 "net_rate": 42693.0,
#                 "net_amount": 42693.0,
#                 "avg_rate": 0.0,
#                 "base_net_rate": 42693.0,
#                 "base_net_amount": 42693.0,
#                 "taxable_value": 42693.0,
#                 "igst_rate": 0.0,
#                 "cgst_rate": 9.0,
#                 "sgst_rate": 9.0,
#                 "cess_rate": 0.0,
#                 "cess_non_advol_rate": 0.0,
#                 "igst_amount": 0.0,
#                 "cgst_amount": 3842.37,
#                 "sgst_amount": 3842.37,
#                 "cess_amount": 0.0,
#                 "cess_non_advol_amount": 0.0,
#                 "delivered_by_supplier": 0,
#                 "income_account": "Office Rent - MT",
#                 "is_fixed_asset": 0,
#                 "expense_account": "Cost of Goods Sold - MT",
#                 "enable_deferred_revenue": 0,
#                 "weight_per_unit": 0.0,
#                 "total_weight": 0.0,
#                 "use_serial_batch_fields": 1,
#                 "blocked_qty": 0.0,
#                 "incoming_rate": 0.0,
#                 "allow_zero_valuation_rate": 0,
#                 "item_tax_rate": "{\"Output Tax SGST - MT\": 9.0, \"Output Tax CGST - MT\": 9.0, \"Output Tax IGST - MT\": 18.0, \"Output Tax SGST RCM - MT\": -9.0, \"Output Tax CGST RCM - MT\": -9.0, \"Output Tax IGST RCM - MT\": -18.0, \"Input Tax SGST - MT\": 9.0, \"Input Tax CGST - MT\": 9.0, \"Input Tax IGST - MT\": 18.0, \"Input Tax SGST RCM - MT\": 9.0, \"Input Tax CGST RCM - MT\": 9.0, \"Input Tax IGST RCM - MT\": 18.0}",
#                 "actual_batch_qty": 0.0,
#                 "actual_qty": 0.0,
#                 "company_total_stock": 0.0,
#                 "delivered_qty": 0.0,
#                 "cost_center": "Main - MT",
#                 "page_break": 0,
#                 "pcs": 0,
#                 "state": "",
#             }
#         ]

# taxes = [
#             {
#                 "docstatus": 1,
#                 "idx": 1,
#                 "parentfield": "taxes",
#                 "parenttype": "Sales Invoice",
#                 "charge_type": "On Net Total",
#                 "account_head": "Output Tax SGST - MT",
#                 "description": "SGST",
#                 "included_in_print_rate": 0,
#                 "included_in_paid_amount": 0,
#                 "cost_center": "Main - MT",
#                 "rate": 9.0,
#                 "gst_tax_type": "sgst",
#                 "tax_amount": 3842.37,
#                 "total": 46535.37,
#                 "tax_amount_after_discount_amount": 3842.37,
#                 "base_tax_amount": 3842.37,
#                 "base_total": 46535.37,
#                 "base_tax_amount_after_discount_amount": 3842.37,
#                 "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,3842.37]}",
#                 "dont_recompute_tax": 0
#             },
#             {
#                 "docstatus": 1,
#                 "idx": 2,
#                 "parentfield": "taxes",
#                 "parenttype": "Sales Invoice",
#                 "charge_type": "On Net Total",
#                 "account_head": "Output Tax CGST - MT",
#                 "description": "CGST",
#                 "included_in_print_rate": 0,
#                 "included_in_paid_amount": 0,
#                 "cost_center": "Main - MT",
#                 "rate": 9.0,
#                 "gst_tax_type": "cgst",
#                 "tax_amount": 3842.37,
#                 "total": 50377.74,
#                 "tax_amount_after_discount_amount": 3842.37,
#                 "base_tax_amount": 3842.37,
#                 "base_total": 50377.74,
#                 "base_tax_amount_after_discount_amount": 3842.37,
#                 "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,3842.37]}",
#                 "dont_recompute_tax": 0
#             }
#     ]

# sales_team = [
#                 {
#                     "docstatus": 1,
#                     "idx": 1,
#                     "parentfield": "sales_team",
#                     "parenttype": "Sales Invoice",
#                     "sales_person": "Sivabalan",
#                     "allocated_percentage": 100.0,
#                     "allocated_amount": 42693.0,
#                     "incentives": 0.0
#                 }
#             ]

# payment_schedule = [
#                         {
#                             "docstatus": 1,
#                             "idx": 1,
#                             "parentfield": "payment_schedule",
#                             "parenttype": "Sales Invoice",
#                             "due_date": frappe.utils.nowdate(),
#                             "invoice_portion": 100.0,
#                             "discount": 0.0,
#                             "payment_amount": 50377.74,
#                             "outstanding": 50377.74,
#                             "paid_amount": 0.0,
#                             "discounted_amount": 0.0,
#                             "base_payment_amount": 50377.74
#                         }
#                     ]           





def create_sales_invoice_for_LIC_in_MANONMANI(
    items=None, 
    taxes=None, 
    sales_team=None, 
    payment_schedule=None
):
    """
    Function to create a Sales Invoice in ERPNext.
    """
    items = items or [
            {
                "idx": 1,
                "parentfield": "items",
                "parenttype": "Sales Invoice",
                "has_item_scanned": 0,
                "item_code": "SERVICES/RENTAL 18%",
                "gst_hsn_code": "997316",
                "item_group": "SERVICES_EXPENSES",
                "image": "",
                "qty": 1.0,
                "stock_uom": "Nos",
                "uom": "Nos",
                "conversion_factor": 1.0,
                "stock_qty": 1.0,
                "price_list_rate": 0.0,
                "base_price_list_rate": 0.0,
                "margin_type": "",
                "margin_rate_or_amount": 0.0,
                "rate_with_margin": 0.0,
                "discount_percentage": 0.0,
                "discount_amount": 0.0,
                "base_rate_with_margin": 0.0,
                "rate": 42693.0,
                "amount": 42693.0,
                "item_tax_template": "GST 18% - MT",
                "gst_treatment": "Taxable",
                "base_rate": 42693.0,
                "base_amount": 42693.0,
                "pricing_rules": "",
                "stock_uom_rate": 42693.0,
                "is_free_item": 0,
                "grant_commission": 1,
                "net_rate": 42693.0,
                "net_amount": 42693.0,
                "avg_rate": 0.0,
                "base_net_rate": 42693.0,
                "base_net_amount": 42693.0,
                "taxable_value": 42693.0,
                "igst_rate": 0.0,
                "cgst_rate": 9.0,
                "sgst_rate": 9.0,
                "cess_rate": 0.0,
                "cess_non_advol_rate": 0.0,
                "igst_amount": 0.0,
                "cgst_amount": 3842.37,
                "sgst_amount": 3842.37,
                "cess_amount": 0.0,
                "cess_non_advol_amount": 0.0,
                "delivered_by_supplier": 0,
                "income_account": "Office Rent - MT",
                "is_fixed_asset": 0,
                "expense_account": "Cost of Goods Sold - MT",
                "enable_deferred_revenue": 0,
                "weight_per_unit": 0.0,
                "total_weight": 0.0,
                "use_serial_batch_fields": 1,
                "blocked_qty": 0.0,
                "incoming_rate": 0.0,
                "allow_zero_valuation_rate": 0,
                "item_tax_rate": "{\"Output Tax SGST - MT\": 9.0, \"Output Tax CGST - MT\": 9.0, \"Output Tax IGST - MT\": 18.0, \"Output Tax SGST RCM - MT\": -9.0, \"Output Tax CGST RCM - MT\": -9.0, \"Output Tax IGST RCM - MT\": -18.0, \"Input Tax SGST - MT\": 9.0, \"Input Tax CGST - MT\": 9.0, \"Input Tax IGST - MT\": 18.0, \"Input Tax SGST RCM - MT\": 9.0, \"Input Tax CGST RCM - MT\": 9.0, \"Input Tax IGST RCM - MT\": 18.0}",
                "actual_batch_qty": 0.0,
                "actual_qty": 0.0,
                "company_total_stock": 0.0,
                "delivered_qty": 0.0,
                "cost_center": "Main - MT",
                "page_break": 0,
                "pcs": 0,
                "state": "",
            }
        ]
    taxes = taxes or [
            {
                "docstatus": 1,
                "idx": 1,
                "parentfield": "taxes",
                "parenttype": "Sales Invoice",
                "charge_type": "On Net Total",
                "account_head": "Output Tax SGST - MT",
                "description": "SGST",
                "included_in_print_rate": 0,
                "included_in_paid_amount": 0,
                "cost_center": "Main - MT",
                "rate": 9.0,
                "gst_tax_type": "sgst",
                "tax_amount": 3842.37,
                "total": 46535.37,
                "tax_amount_after_discount_amount": 3842.37,
                "base_tax_amount": 3842.37,
                "base_total": 46535.37,
                "base_tax_amount_after_discount_amount": 3842.37,
                "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,3842.37]}",
                "dont_recompute_tax": 0
            },
            {
                "docstatus": 1,
                "idx": 2,
                "parentfield": "taxes",
                "parenttype": "Sales Invoice",
                "charge_type": "On Net Total",
                "account_head": "Output Tax CGST - MT",
                "description": "CGST",
                "included_in_print_rate": 0,
                "included_in_paid_amount": 0,
                "cost_center": "Main - MT",
                "rate": 9.0,
                "gst_tax_type": "cgst",
                "tax_amount": 3842.37,
                "total": 50377.74,
                "tax_amount_after_discount_amount": 3842.37,
                "base_tax_amount": 3842.37,
                "base_total": 50377.74,
                "base_tax_amount_after_discount_amount": 3842.37,
                "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,3842.37]}",
                "dont_recompute_tax": 0
            }
    ]
    sales_team = sales_team or [
                {
                    "docstatus": 1,
                    "idx": 1,
                    "parentfield": "sales_team",
                    "parenttype": "Sales Invoice",
                    "sales_person": "Sivabalan",
                    "allocated_percentage": 100.0,
                    "allocated_amount": 42693.0,
                    "incentives": 0.0
                }
            ]
    payment_schedule = payment_schedule or [
                        {
                            "docstatus": 1,
                            "idx": 1,
                            "parentfield": "payment_schedule",
                            "parenttype": "Sales Invoice",
                            "due_date": frappe.utils.nowdate(),
                            "invoice_portion": 100.0,
                            "discount": 0.0,
                            "payment_amount": 50377.74,
                            "outstanding": 50377.74,
                            "paid_amount": 0.0,
                            "discounted_amount": 0.0,
                            "base_payment_amount": 50377.74
                        }
                    ] 

    try:
        # Create a new Sales Invoice document
        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "posting_date": frappe.utils.nowdate(),
            "docstatus": 0,
            "title": "LIC OF INDIA",
            "naming_series": "B/24/.#####",
            "customer": "LIC OF INDIA",
            "company": "MANONMANI THANGAVELU",
            "remarks": "No Remarks",
            "items": items,
            "taxes": taxes,
            "sales_team": sales_team,
            "payment_schedule": payment_schedule,
        })

        # Insert the document into the database
        sales_invoice.insert()

        # Submit the Sales Invoice to finalize it
        sales_invoice.submit()

        frappe.msgprint(f"Sales Invoice {sales_invoice.name} created successfully!")
        return sales_invoice.name
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Auto Create Sales Invoice")
        frappe.throw(f"Error creating Sales Invoice: {str(e)}")






def create_sales_invoice_for_MIRAAI_in_MANONMANI(
    items=None, 
    taxes=None, 
    sales_team=None, 
    payment_schedule=None
):
    """
    Function to create a Sales Invoice in ERPNext.
    """
    items = items or [
            {
                "docstatus": 1,
                "idx": 1,
                "parentfield": "items",
                "parenttype": "Sales Invoice",
                "has_item_scanned": 0,
                "item_code": "SERVICES/RENTAL",
                "item_name": "RENTAL SERVICES",
                "description": "<div class=\"ql-editor read-mode\"><p>RENTAL SERVICES</p></div>",
                "gst_hsn_code": "997316",
                "item_group": "SERVICES_EXPENSES",
                "image": "",
                "qty": 1.0,
                "stock_uom": "Nos",
                "uom": "Nos",
                "conversion_factor": 1.0,
                "stock_qty": 1.0,
                "price_list_rate": 0.0,
                "base_price_list_rate": 0.0,
                "margin_type": "",
                "margin_rate_or_amount": 0.0,
                "rate_with_margin": 0.0,
                "discount_percentage": 0.0,
                "discount_amount": 0.0,
                "base_rate_with_margin": 0.0,
                "rate": 138500.0,
                "amount": 138500.0,
                "item_tax_template": "GST 18% - MT",
                "gst_treatment": "Taxable",
                "base_rate": 138500.0,
                "base_amount": 138500.0,
                "pricing_rules": "",
                "stock_uom_rate": 138500.0,
                "is_free_item": 0,
                "grant_commission": 1,
                "net_rate": 138500.0,
                "net_amount": 138500.0,
                "avg_rate": 0.0,
                "base_net_rate": 138500.0,
                "base_net_amount": 138500.0,
                "taxable_value": 138500.0,
                "igst_rate": 0.0,
                "cgst_rate": 9.0,
                "sgst_rate": 9.0,
                "cess_rate": 0.0,
                "cess_non_advol_rate": 0.0,
                "igst_amount": 0.0,
                "cgst_amount": 12465.0,
                "sgst_amount": 12465.0,
                "cess_amount": 0.0,
                "cess_non_advol_amount": 0.0,
                "delivered_by_supplier": 0,
                "income_account": "Office Rent - MT",
                "is_fixed_asset": 0,
                "expense_account": "Cost of Goods Sold - MT",
                "enable_deferred_revenue": 0,
                "weight_per_unit": 0.0,
                "total_weight": 0.0,
                "use_serial_batch_fields": 0,
                "blocked_qty": 0.0,
                "incoming_rate": 0.0,
                "allow_zero_valuation_rate": 0,
                "item_tax_rate": "{\"Output Tax SGST - MT\": 9.0, \"Output Tax CGST - MT\": 9.0, \"Output Tax IGST - MT\": 18.0, \"Output Tax SGST RCM - MT\": -9.0, \"Output Tax CGST RCM - MT\": -9.0, \"Output Tax IGST RCM - MT\": -18.0, \"Input Tax SGST - MT\": 9.0, \"Input Tax CGST - MT\": 9.0, \"Input Tax IGST - MT\": 18.0, \"Input Tax SGST RCM - MT\": 9.0, \"Input Tax CGST RCM - MT\": 9.0, \"Input Tax IGST RCM - MT\": 18.0}",
                "actual_batch_qty": 0.0,
                "actual_qty": 0.0,
                "company_total_stock": 0.0,
                "delivered_qty": 0.0,
                "cost_center": "Main - MT",
                "page_break": 0,
            }
        ]

    taxes = taxes or [
         {
           
            "docstatus": 1,
            "idx": 1,
            "parentfield": "taxes",
            "parenttype": "Sales Invoice",
            "charge_type": "On Net Total",
            "account_head": "Output Tax SGST - MT",
            "description": "Output Tax SGST - MT",
            "included_in_print_rate": 0,
            "included_in_paid_amount": 0,
            "cost_center": "Main - MT",
            "rate": 9.0,
            "gst_tax_type": "sgst",
            "tax_amount": 12465.0,
            "total": 150965.0,
            "tax_amount_after_discount_amount": 12465.0,
            "base_tax_amount": 12465.0,
            "base_total": 150965.0,
            "base_tax_amount_after_discount_amount": 12465.0,
            "item_wise_tax_detail": "{\"SERVICES/RENTAL\":[9.0,12465.0]}",
            "dont_recompute_tax": 0
        },
        {
            "docstatus": 1,
            "idx": 2,
            "parentfield": "taxes",
            "parenttype": "Sales Invoice",
            "charge_type": "On Net Total",
            "account_head": "Output Tax CGST - MT",
            "description": "Output Tax CGST - MT",
            "included_in_print_rate": 0,
            "included_in_paid_amount": 0,
            "cost_center": "Main - MT",
            "rate": 9.0,
            "gst_tax_type": "cgst",
            "tax_amount": 12465.0,
            "total": 163430.0,
            "tax_amount_after_discount_amount": 12465.0,
            "base_tax_amount": 12465.0,
            "base_total": 163430.0,
            "base_tax_amount_after_discount_amount": 12465.0,
            "item_wise_tax_detail": "{\"SERVICES/RENTAL\":[9.0,12465.0]}",
            "dont_recompute_tax": 0
        }
    ]


    sales_team = sales_team or [
                {
                    "docstatus": 1,
                    "idx": 1,
                    "parentfield": "sales_team",
                    "parenttype": "Sales Invoice",
                    "sales_person": "Sivabalan",
                    "allocated_percentage": 100.0,
                    "allocated_amount": 138500.0,
                    "incentives": 0.0
                }
            ]


    payment_schedule = payment_schedule or [
                        {
                            "docstatus": 1,
                            "idx": 1,
                            "parentfield": "payment_schedule",
                            "parenttype": "Sales Invoice",
                            "due_date": frappe.utils.nowdate(),
                            "invoice_portion": 100.0,
                            "discount": 0.0,
                            "payment_amount": 163430.0,
                            "outstanding": 163430.0,
                            "paid_amount": 0.0,
                            "discounted_amount": 0.0,
                            "base_payment_amount": 163430.0
                        }
                    ] 

    try:
        # Create a new Sales Invoice document
        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "posting_date": frappe.utils.nowdate(),
            "docstatus": 0,
            "title": "MIRAAI ADVANCED COMPOSITES PVT LTD",
            "naming_series": "B/24/.#####",
            "customer": "MIRAAI ADVANCED COMPOSITES PVT LTD",
            "company": "MANONMANI THANGAVELU",
            "remarks": "No Remarks",
            "items": items,
            "taxes": taxes,
            "sales_team": sales_team,
            "payment_schedule": payment_schedule,
        })

        # Insert the document into the database
        sales_invoice.insert()

        # Submit the Sales Invoice to finalize it
        sales_invoice.submit()

        frappe.msgprint(f"Sales Invoice {sales_invoice.name} created successfully!")
        return sales_invoice.name
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Auto Create Sales Invoice")
        frappe.throw(f"Error creating Sales Invoice: {str(e)}")        



def create_sales_invoice_for_VASANTH_in_P_THANGAVELU(
    items=None, 
    taxes=None, 
    sales_team=None, 
    payment_schedule=None
):
    """
    Function to create a Sales Invoice in ERPNext.
    """
    items = items or [
            {
                "docstatus": 1,
                "idx": 1,
                "parentfield": "items",
                "parenttype": "Sales Invoice",
                "has_item_scanned": 0,
                "item_code": "SERVICES/RENTAL 18%",
                "item_name": "RENTAL SERVICES 18%",
                "description": "<div class=\"ql-editor read-mode\"><p>RENTAL SERVICES 18%</p></div>",
                "gst_hsn_code": "997316",
                "item_group": "SERVICES_EXPENSES",
                "image": "",
                "qty": 1.0,
                "stock_uom": "Nos",
                "uom": "Nos",
                "conversion_factor": 1.0,
                "stock_qty": 1.0,
                "price_list_rate": 0.0,
                "base_price_list_rate": 0.0,
                "margin_rate_or_amount": 0.0,
                "rate_with_margin": 0.0,
                "discount_percentage": 0.0,
                "discount_amount": 0.0,
                "base_rate_with_margin": 0.0,
                "rate": 77703.0,
                "amount": 77703.0,
                "item_tax_template": "GST 18% - P",
                "gst_treatment": "Taxable",
                "base_rate": 77703.0,
                "base_amount": 77703.0,
                "pricing_rules": "",
                "stock_uom_rate": 77703.0,
                "is_free_item": 0,
                "grant_commission": 1,
                "net_rate": 77703.0,
                "net_amount": 77703.0,
                "avg_rate": 0.0,
                "base_net_rate": 77703.0,
                "base_net_amount": 77703.0,
                "taxable_value": 77703.0,
                "igst_rate": 0.0,
                "cgst_rate": 9.0,
                "sgst_rate": 9.0,
                "cess_rate": 0.0,
                "cess_non_advol_rate": 0.0,
                "igst_amount": 0.0,
                "cgst_amount": 6993.27,
                "sgst_amount": 6993.27,
                "cess_amount": 0.0,
                "cess_non_advol_amount": 0.0,
                "delivered_by_supplier": 0,
                "income_account": "Office Rent - P",
                "is_fixed_asset": 0,
                "expense_account": "Cost of Goods Sold - P",
                "enable_deferred_revenue": 0,
                "weight_per_unit": 0.0,
                "total_weight": 0.0,
                "use_serial_batch_fields": 1,
                "blocked_qty": 0.0,
                "incoming_rate": 0.0,
                "allow_zero_valuation_rate": 0,
                "item_tax_rate": "{\"Output Tax SGST - P\": 9.0, \"Output Tax CGST - P\": 9.0, \"Output Tax IGST - P\": 18.0, \"Output Tax SGST RCM - P\": -9.0, \"Output Tax CGST RCM - P\": -9.0, \"Output Tax IGST RCM - P\": -18.0, \"Input Tax SGST - P\": 9.0, \"Input Tax CGST - P\": 9.0, \"Input Tax IGST - P\": 18.0, \"Input Tax SGST RCM - P\": 9.0, \"Input Tax CGST RCM - P\": 9.0, \"Input Tax IGST RCM - P\": 18.0}",
                "actual_batch_qty": 0.0,
                "actual_qty": 0.0,
                "company_total_stock": 0.0,
                "delivered_qty": 0.0,
                "cost_center": "Main - P",
                "page_break": 0,
            }
        ]


    taxes = taxes or [
        {
            
            "docstatus": 1,
            "idx": 1,
            "parentfield": "taxes",
            "parenttype": "Sales Invoice",
            "charge_type": "On Net Total",
            "account_head": "Output Tax SGST - P",
            "description": "Output Tax SGST - P",
            "included_in_print_rate": 0,
            "included_in_paid_amount": 0,
            "cost_center": "Main - P",
            "rate": 9.0,
            "gst_tax_type": "sgst",
            "tax_amount": 6993.27,
            "total": 84696.27,
            "tax_amount_after_discount_amount": 6993.27,
            "base_tax_amount": 6993.27,
            "base_total": 84696.27,
            "base_tax_amount_after_discount_amount": 6993.27,
            "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,6993.2699999999995]}",
            "dont_recompute_tax": 0
        },
        {
            "docstatus": 1,
            "idx": 2,
            "parentfield": "taxes",
            "parenttype": "Sales Invoice",
            "charge_type": "On Net Total",
            "account_head": "Output Tax CGST - P",
            "description": "Output Tax CGST - P",
            "included_in_print_rate": 0,
            "included_in_paid_amount": 0,
            "cost_center": "Main - P",
            "rate": 9.0,
            "gst_tax_type": "cgst",
            "tax_amount": 6993.27,
            "total": 91689.54,
            "tax_amount_after_discount_amount": 6993.27,
            "base_tax_amount": 6993.27,
            "base_total": 91689.54,
            "base_tax_amount_after_discount_amount": 6993.27,
            "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,6993.2699999999995]}",
            "dont_recompute_tax": 0
        }
    ]

  

    sales_team = sales_team or [
                {
                    "docstatus": 1,
                    "idx": 1,
                    "parentfield": "sales_team",
                    "parenttype": "Sales Invoice",
                    "sales_person": "Sivabalan",
                    "allocated_percentage": 100.0,
                    "allocated_amount": 77703.0,
                    "incentives": 0.0
                }
            ]
    


    payment_schedule = payment_schedule or [
                        {
                            "docstatus": 1,
                            "idx": 1,
                            "parentfield": "payment_schedule",
                            "parenttype": "Sales Invoice",
                            "due_date": frappe.utils.nowdate(),
                            "invoice_portion": 100.0,
                            "discount": 0.0,
                            "payment_amount": 91689.54,
                            "outstanding": 91689.54,
                            "paid_amount": 0.0,
                            "discounted_amount": 0.0,
                            "base_payment_amount": 91689.54
                        }
                    ] 
              

    try:
        # Create a new Sales Invoice document
        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "posting_date": frappe.utils.nowdate(),
            "docstatus": 0,
            "title": "VASANTH & CO",
            "naming_series": "A/24/.#####",
            "customer": "VASANTH & CO",
            "company": "P.THANGAVELU",
            "remarks": "No Remarks",
            "items": items,
            "taxes": taxes,
            "sales_team": sales_team,
            "payment_schedule": payment_schedule,
        })

        # Insert the document into the database
        sales_invoice.insert()

        # Submit the Sales Invoice to finalize it
        sales_invoice.submit()

        frappe.msgprint(f"Sales Invoice {sales_invoice.name} created successfully!")
        return sales_invoice.name
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Auto Create Sales Invoice")
        frappe.throw(f"Error creating Sales Invoice: {str(e)}")  



def create_sales_invoice_for_RELIANCE_INDUSTRIES_LIMITED_in_P_THANGAVELU(
    items=None, 
    taxes=None, 
    sales_team=None, 
    payment_schedule=None
):
    """
    Function to create a Sales Invoice in ERPNext.
    """
    items = items or [
            {
                "docstatus": 1,
                "idx": 1,
                "parentfield": "items",
                "parenttype": "Sales Invoice",
                "has_item_scanned": 0,
                "item_code": "SERVICES/RENTAL 18%",
                "item_name": "RENTAL SERVICES 18%",
                "description": "<div class=\"ql-editor read-mode\"><p>RENTAL SERVICES 18%</p></div>",
                "gst_hsn_code": "997316",
                "item_group": "SERVICES_EXPENSES",
                "image": "",
                "qty": 1.0,
                "stock_uom": "Nos",
                "uom": "Nos",
                "conversion_factor": 1.0,
                "stock_qty": 1.0,
                "price_list_rate": 0.0,
                "base_price_list_rate": 0.0,
                "margin_type": "",
                "margin_rate_or_amount": 0.0,
                "rate_with_margin": 0.0,
                "discount_percentage": 0.0,
                "discount_amount": 0.0,
                "base_rate_with_margin": 0.0,
                "rate": 16580.0,
                "amount": 16580.0,
                "item_tax_template": "GST 18% - P",
                "gst_treatment": "Taxable",
                "base_rate": 16580.0,
                "base_amount": 16580.0,
                "pricing_rules": "",
                "stock_uom_rate": 16580.0,
                "is_free_item": 0,
                "grant_commission": 1,
                "net_rate": 16580.0,
                "net_amount": 16580.0,
                "avg_rate": 0.0,
                "base_net_rate": 16580.0,
                "base_net_amount": 16580.0,
                "taxable_value": 16580.0,
                "igst_rate": 0.0,
                "cgst_rate": 9.0,
                "sgst_rate": 9.0,
                "cess_rate": 0.0,
                "cess_non_advol_rate": 0.0,
                "igst_amount": 0.0,
                "cgst_amount": 1492.2,
                "sgst_amount": 1492.2,
                "cess_amount": 0.0,
                "cess_non_advol_amount": 0.0,
                "delivered_by_supplier": 0,
                "income_account": "Office Rent - P",
                "is_fixed_asset": 0,
                "expense_account": "Cost of Goods Sold - P",
                "enable_deferred_revenue": 0,
                "weight_per_unit": 0.0,
                "total_weight": 0.0,
                "use_serial_batch_fields": 1,
                "blocked_qty": 0.0,
                "incoming_rate": 0.0,
                "allow_zero_valuation_rate": 0,
                "item_tax_rate": "{\"Output Tax SGST - P\": 9.0, \"Output Tax CGST - P\": 9.0, \"Output Tax IGST - P\": 18.0, \"Output Tax SGST RCM - P\": -9.0, \"Output Tax CGST RCM - P\": -9.0, \"Output Tax IGST RCM - P\": -18.0, \"Input Tax SGST - P\": 9.0, \"Input Tax CGST - P\": 9.0, \"Input Tax IGST - P\": 18.0, \"Input Tax SGST RCM - P\": 9.0, \"Input Tax CGST RCM - P\": 9.0, \"Input Tax IGST RCM - P\": 18.0}",
                "actual_batch_qty": 0.0,
                "actual_qty": 0.0,
                "company_total_stock": 0.0,
                "delivered_qty": 0.0,
                "cost_center": "Main - P",
                "page_break": 0,
            }
        ]

    taxes = taxes or [
       {
            "docstatus": 1,
            "idx": 1,
            "parentfield": "taxes",
            "parenttype": "Sales Invoice",
            "charge_type": "On Net Total",
            "account_head": "Output Tax SGST - P",
            "description": "Output Tax SGST - P",
            "included_in_print_rate": 0,
            "included_in_paid_amount": 0,
            "cost_center": "Main - P",
            "rate": 9.0,
            "gst_tax_type": "sgst",
            "tax_amount": 1492.2,
            "total": 18072.2,
            "tax_amount_after_discount_amount": 1492.2,
            "base_tax_amount": 1492.2,
            "base_total": 18072.2,
            "base_tax_amount_after_discount_amount": 1492.2,
            "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,1492.2]}",
            "dont_recompute_tax": 0
        },
        {
            "docstatus": 1,
            "idx": 2,
            "parentfield": "taxes",
            "parenttype": "Sales Invoice",
            "charge_type": "On Net Total",
            "account_head": "Output Tax CGST - P",
            "description": "Output Tax CGST - P",
            "included_in_print_rate": 0,
            "included_in_paid_amount": 0,
            "cost_center": "Main - P",
            "rate": 9.0,
            "gst_tax_type": "cgst",
            "tax_amount": 1492.2,
            "total": 19564.4,
            "tax_amount_after_discount_amount": 1492.2,
            "base_tax_amount": 1492.2,
            "base_total": 19564.4,
            "base_tax_amount_after_discount_amount": 1492.2,
            "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,1492.2]}",
            "dont_recompute_tax": 0
        }
    ]
   
  

    sales_team = sales_team or [
                {
                    "docstatus": 1,
                    "idx": 1,
                    "parentfield": "sales_team",
                    "parenttype": "Sales Invoice",
                    "sales_person": "Sivabalan",
                    "allocated_percentage": 100.0,
                    "allocated_amount": 16580.0,
                    "incentives": 0.0
                }
            ]
  



    payment_schedule = payment_schedule or [
                        {
                            "docstatus": 1,
                            "idx": 1,
                            "parentfield": "payment_schedule",
                            "parenttype": "Sales Invoice",
                            "due_date": frappe.utils.nowdate(),
                            "invoice_portion": 100.0,
                            "discount": 0.0,
                            "payment_amount": 19564.4,
                            "outstanding": 19564.4,
                            "paid_amount": 0.0,
                            "discounted_amount": 0.0,
                            "base_payment_amount": 19564.4
                        }
                    ] 
         

    try:
        # Create a new Sales Invoice document
        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "posting_date": frappe.utils.nowdate(),
            "docstatus": 0,
            "title": "RELIANCE INDUSTRIES LIMITED",
            "naming_series": "A/24/.#####",
            "customer": "RELIANCE INDUSTRIES LIMITED",
            "company": "P.THANGAVELU",
            "remarks": "No Remarks",
            "items": items,
            "taxes": taxes,
            "sales_team": sales_team,
            "payment_schedule": payment_schedule,
        })

        # Insert the document into the database
        sales_invoice.insert()

        # Submit the Sales Invoice to finalize it
        sales_invoice.submit()

        frappe.msgprint(f"Sales Invoice {sales_invoice.name} created successfully!")
        return sales_invoice.name
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Auto Create Sales Invoice")
        frappe.throw(f"Error creating Sales Invoice: {str(e)}")



def create_sales_invoice_for_TAMILNADU_GENERATION_AND_DISTRIBUTION_in_P_THANGAVELU(
    items=None, 
    taxes=None, 
    sales_team=None, 
    payment_schedule=None
):
    """
    Function to create a Sales Invoice in ERPNext.
    """
    items = items or [
            {
                "docstatus": 1,
                "idx": 1,
                "parentfield": "items",
                "parenttype": "Sales Invoice",
                "has_item_scanned": 0,
                "item_code": "SERVICES/RENTAL 18%",
                "item_name": "RENTAL SERVICES 18%",
                "description": "<div class=\"ql-editor read-mode\"><p>RENTAL SERVICES 18%</p></div>",
                "gst_hsn_code": "997316",
                "item_group": "SERVICES_EXPENSES",
                "image": "",
                "qty": 1.0,
                "stock_uom": "Nos",
                "uom": "Nos",
                "conversion_factor": 1.0,
                "stock_qty": 1.0,
                "price_list_rate": 0.0,
                "base_price_list_rate": 0.0,
                "margin_rate_or_amount": 0.0,
                "rate_with_margin": 0.0,
                "discount_percentage": 0.0,
                "discount_amount": 0.0,
                "base_rate_with_margin": 0.0,
                "rate": 27720.0,
                "amount": 27720.0,
                "item_tax_template": "GST 18% - P",
                "gst_treatment": "Taxable",
                "base_rate": 27720.0,
                "base_amount": 27720.0,
                "pricing_rules": "",
                "stock_uom_rate": 27720.0,
                "is_free_item": 0,
                "grant_commission": 1,
                "net_rate": 27720.0,
                "net_amount": 27720.0,
                "avg_rate": 0.0,
                "base_net_rate": 27720.0,
                "base_net_amount": 27720.0,
                "taxable_value": 27720.0,
                "igst_rate": 0.0,
                "cgst_rate": 9.0,
                "sgst_rate": 9.0,
                "cess_rate": 0.0,
                "cess_non_advol_rate": 0.0,
                "igst_amount": 0.0,
                "cgst_amount": 2494.8,
                "sgst_amount": 2494.8,
                "cess_amount": 0.0,
                "cess_non_advol_amount": 0.0,
                "delivered_by_supplier": 0,
                "income_account": "Office Rent - P",
                "is_fixed_asset": 0,
                "expense_account": "Cost of Goods Sold - P",
                "enable_deferred_revenue": 0,
                "weight_per_unit": 0.0,
                "total_weight": 0.0,
                "use_serial_batch_fields": 1,
                "blocked_qty": 0.0,
                "incoming_rate": 0.0,
                "allow_zero_valuation_rate": 0,
                "item_tax_rate": "{\"Output Tax SGST - P\": 9.0, \"Output Tax CGST - P\": 9.0, \"Output Tax IGST - P\": 18.0, \"Output Tax SGST RCM - P\": -9.0, \"Output Tax CGST RCM - P\": -9.0, \"Output Tax IGST RCM - P\": -18.0, \"Input Tax SGST - P\": 9.0, \"Input Tax CGST - P\": 9.0, \"Input Tax IGST - P\": 18.0, \"Input Tax SGST RCM - P\": 9.0, \"Input Tax CGST RCM - P\": 9.0, \"Input Tax IGST RCM - P\": 18.0}",
                "actual_batch_qty": 0.0,
                "actual_qty": 0.0,
                "company_total_stock": 0.0,
                "delivered_qty": 0.0,
                "cost_center": "Main - P",
                "page_break": 0,
            }
        ]
    
  

    taxes = taxes or [
      {
        
            "docstatus": 1,
            "idx": 1,
            "parentfield": "taxes",
            "parenttype": "Sales Invoice",
            "charge_type": "On Net Total",
            "account_head": "Output Tax SGST - P",
            "description": "Output Tax SGST - P",
            "included_in_print_rate": 0,
            "included_in_paid_amount": 0,
            "cost_center": "Main - P",
            "rate": 9.0,
            "gst_tax_type": "sgst",
            "tax_amount": 2494.8,
            "total": 30214.8,
            "tax_amount_after_discount_amount": 2494.8,
            "base_tax_amount": 2494.8,
            "base_total": 30214.8,
            "base_tax_amount_after_discount_amount": 2494.8,
            "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,2494.7999999999997]}",
            "dont_recompute_tax": 0
        },
        {
            "docstatus": 1,
            "idx": 2,
            "parentfield": "taxes",
            "parenttype": "Sales Invoice",
            "charge_type": "On Net Total",
            "account_head": "Output Tax CGST - P",
            "description": "Output Tax CGST - P",
            "included_in_print_rate": 0,
            "included_in_paid_amount": 0,
            "cost_center": "Main - P",
            "rate": 9.0,
            "gst_tax_type": "cgst",
            "tax_amount": 2494.8,
            "total": 32709.6,
            "tax_amount_after_discount_amount": 2494.8,
            "base_tax_amount": 2494.8,
            "base_total": 32709.6,
            "base_tax_amount_after_discount_amount": 2494.8,
            "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,2494.7999999999997]}",
            "dont_recompute_tax": 0
        }
    ]

     

    sales_team = sales_team or [
                {
                    "docstatus": 1,
                    "idx": 1,
                    "parentfield": "sales_team",
                    "parenttype": "Sales Invoice",
                    "sales_person": "Sivabalan",
                    "allocated_percentage": 100.0,
                    "allocated_amount": 27720.0,
                    "incentives": 0.0
                }
            ]
 


    payment_schedule = payment_schedule or [
                        {
                            "docstatus": 1,
                            "idx": 1,
                            "parentfield": "payment_schedule",
                            "parenttype": "Sales Invoice",
                            "due_date": frappe.utils.nowdate(),
                            "invoice_portion": 100.0,
                            "discount": 0.0,
                            "payment_amount": 32709.6,
                            "outstanding": 32709.6,
                            "paid_amount": 0.0,
                            "discounted_amount": 0.0,
                            "base_payment_amount": 32709.6
                        }
                    ] 
         

    try:
        # Create a new Sales Invoice document
        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "posting_date": frappe.utils.nowdate(),
            "docstatus": 0,
            "title": "TAMILNADU GENERATION AND DISTRIBUTION",
            "naming_series": "A/24/.#####",
            "customer": "TAMILNADU GENERATION AND DISTRIBUTION",
            "company": "P.THANGAVELU",
            "remarks": "No Remarks",
            "items": items,
            "taxes": taxes,
            "sales_team": sales_team,
            "payment_schedule": payment_schedule,
        })

        # Insert the document into the database
        sales_invoice.insert()

        # Submit the Sales Invoice to finalize it
        sales_invoice.submit()

        frappe.msgprint(f"Sales Invoice {sales_invoice.name} created successfully!")
        return sales_invoice.name
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Auto Create Sales Invoice")
        frappe.throw(f"Error creating Sales Invoice: {str(e)}")                      


def create_sales_invoice_for_TAMILNADU_GENERATION_AND_DISTRIBUTION_2_in_P_THANGAVELU(
    items=None, 
    taxes=None, 
    sales_team=None, 
    payment_schedule=None
):
    """
    Function to create a Sales Invoice in ERPNext.
    """
    items = items or [
            {
                "docstatus": 1,
                "idx": 1,
                "parentfield": "items",
                "parenttype": "Sales Invoice",
                "has_item_scanned": 0,
                "item_code": "SERVICES/RENTAL 18%",
                "item_name": "RENTAL SERVICES 18%",
                "description": "<div class=\"ql-editor read-mode\"><p>RENTAL SERVICES 18%</p></div>",
                "gst_hsn_code": "997316",
                "item_group": "SERVICES_EXPENSES",
                "image": "",
                "qty": 1.0,
                "stock_uom": "Nos",
                "uom": "Nos",
                "conversion_factor": 1.0,
                "stock_qty": 1.0,
                "price_list_rate": 0.0,
                "base_price_list_rate": 0.0,
                "margin_type": "",
                "margin_rate_or_amount": 0.0,
                "rate_with_margin": 0.0,
                "discount_percentage": 0.0,
                "discount_amount": 0.0,
                "base_rate_with_margin": 0.0,
                "rate": 22770.0,
                "amount": 22770.0,
                "item_tax_template": "GST 18% - P",
                "gst_treatment": "Taxable",
                "base_rate": 22770.0,
                "base_amount": 22770.0,
                "pricing_rules": "",
                "stock_uom_rate": 22770.0,
                "is_free_item": 0,
                "grant_commission": 1,
                "net_rate": 22770.0,
                "net_amount": 22770.0,
                "avg_rate": 0.0,
                "base_net_rate": 22770.0,
                "base_net_amount": 22770.0,
                "taxable_value": 22770.0,
                "igst_rate": 0.0,
                "cgst_rate": 9.0,
                "sgst_rate": 9.0,
                "cess_rate": 0.0,
                "cess_non_advol_rate": 0.0,
                "igst_amount": 0.0,
                "cgst_amount": 2049.3,
                "sgst_amount": 2049.3,
                "cess_amount": 0.0,
                "cess_non_advol_amount": 0.0,
                "delivered_by_supplier": 0,
                "income_account": "Office Rent - P",
                "is_fixed_asset": 0,
                "expense_account": "Cost of Goods Sold - P",
                "enable_deferred_revenue": 0,
                "weight_per_unit": 0.0,
                "total_weight": 0.0,
                "use_serial_batch_fields": 1,
                "blocked_qty": 0.0,
                "incoming_rate": 0.0,
                "allow_zero_valuation_rate": 0,
                "item_tax_rate": "{\"Output Tax SGST - P\": 9.0, \"Output Tax CGST - P\": 9.0, \"Output Tax IGST - P\": 18.0, \"Output Tax SGST RCM - P\": -9.0, \"Output Tax CGST RCM - P\": -9.0, \"Output Tax IGST RCM - P\": -18.0, \"Input Tax SGST - P\": 9.0, \"Input Tax CGST - P\": 9.0, \"Input Tax IGST - P\": 18.0, \"Input Tax SGST RCM - P\": 9.0, \"Input Tax CGST RCM - P\": 9.0, \"Input Tax IGST RCM - P\": 18.0}",
                "actual_batch_qty": 0.0,
                "actual_qty": 0.0,
                "company_total_stock": 0.0,
                "delivered_qty": 0.0,
                "cost_center": "Main - P",
                "page_break": 0,
            }
        ]
    

    taxes = taxes or [
      {
            
            "docstatus": 1,
            "idx": 1,
            "parentfield": "taxes",
            "parenttype": "Sales Invoice",
            "charge_type": "On Net Total",
            "account_head": "Output Tax SGST - P",
            "description": "Output Tax SGST - P",
            "included_in_print_rate": 0,
            "included_in_paid_amount": 0,
            "cost_center": "Main - P",
            "rate": 9.0,
            "gst_tax_type": "sgst",
            "tax_amount": 2049.3,
            "total": 24819.3,
            "tax_amount_after_discount_amount": 2049.3,
            "base_tax_amount": 2049.3,
            "base_total": 24819.3,
            "base_tax_amount_after_discount_amount": 2049.3,
            "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,2049.2999999999997]}",
            "dont_recompute_tax": 0
        },
        {
           
            "docstatus": 1,
            "idx": 2,
            "parentfield": "taxes",
            "parenttype": "Sales Invoice",
            "charge_type": "On Net Total",
            "account_head": "Output Tax CGST - P",
            "description": "Output Tax CGST - P",
            "included_in_print_rate": 0,
            "included_in_paid_amount": 0,
            "cost_center": "Main - P",
            "rate": 9.0,
            "gst_tax_type": "cgst",
            "tax_amount": 2049.3,
            "total": 26868.6,
            "tax_amount_after_discount_amount": 2049.3,
            "base_tax_amount": 2049.3,
            "base_total": 26868.6,
            "base_tax_amount_after_discount_amount": 2049.3,
            "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,2049.2999999999997]}",
            "dont_recompute_tax": 0
        }
    ]

  

     

    sales_team = sales_team or [
                {
                    "docstatus": 1,
                    "idx": 1,
                    "parentfield": "sales_team",
                    "parenttype": "Sales Invoice",
                    "sales_person": "Sivabalan",
                    "allocated_percentage": 100.0,
                    "allocated_amount": 22770.0,
                    "incentives": 0.0
                }
            ]
 


    payment_schedule = payment_schedule or [
                        {
                            "docstatus": 1,
                            "idx": 1,
                            "parentfield": "payment_schedule",
                            "parenttype": "Sales Invoice",
                            "due_date": frappe.utils.nowdate(),
                            "invoice_portion": 100.0,
                            "discount": 0.0,
                            "payment_amount": 26868.6,
                            "outstanding": 26868.6,
                            "paid_amount": 0.0,
                            "discounted_amount": 0.0,
                            "base_payment_amount": 26868.6
                        }
                    ] 
         


    try:
        # Create a new Sales Invoice document
        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "posting_date": frappe.utils.nowdate(),
            "docstatus": 0,
            "title": "TAMILNADU GENERATION AND DISTRIBUTION",
            "naming_series": "A/24/.#####",
            "customer": "TAMILNADU GENERATION AND DISTRIBUTION",
            "company": "P.THANGAVELU",
            "remarks": "No Remarks",
            "items": items,
            "taxes": taxes,
            "sales_team": sales_team,
            "payment_schedule": payment_schedule,
        })

        # Insert the document into the database
        sales_invoice.insert()

        # Submit the Sales Invoice to finalize it
        sales_invoice.submit()

        frappe.msgprint(f"Sales Invoice {sales_invoice.name} created successfully!")
        return sales_invoice.name
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Auto Create Sales Invoice")
        frappe.throw(f"Error creating Sales Invoice: {str(e)}") 

     
def create_sales_invoice_for_LIC_OF_INDIA_in_P_THANGAVELU(
    items=None, 
    taxes=None, 
    sales_team=None, 
    payment_schedule=None
):
    """
    Function to create a Sales Invoice in ERPNext.
    """
    items = items or [
            {
                "docstatus": 1,
                "idx": 1,
                "parentfield": "items",
                "parenttype": "Sales Invoice",
                "has_item_scanned": 0,
                "item_code": "SERVICES/RENTAL 18%",
                "item_name": "RENTAL SERVICES 18%",
                "description": "<div class=\"ql-editor read-mode\"><p>RENTAL SERVICES 18%</p></div>",
                "gst_hsn_code": "997316",
                "item_group": "SERVICES_EXPENSES",
                "image": "",
                "qty": 1.0,
                "stock_uom": "Nos",
                "uom": "Nos",
                "conversion_factor": 1.0,
                "stock_qty": 1.0,
                "price_list_rate": 0.0,
                "base_price_list_rate": 0.0,
                "margin_type": "",
                "margin_rate_or_amount": 0.0,
                "rate_with_margin": 0.0,
                "discount_percentage": 0.0,
                "discount_amount": 0.0,
                "base_rate_with_margin": 0.0,
                "rate": 42693.0,
                "amount": 42693.0,
                "item_tax_template": "GST 18% - P",
                "gst_treatment": "Taxable",
                "base_rate": 42693.0,
                "base_amount": 42693.0,
                "pricing_rules": "",
                "stock_uom_rate": 42693.0,
                "is_free_item": 0,
                "grant_commission": 1,
                "net_rate": 42693.0,
                "net_amount": 42693.0,
                "avg_rate": 0.0,
                "base_net_rate": 42693.0,
                "base_net_amount": 42693.0,
                "taxable_value": 42693.0,
                "igst_rate": 0.0,
                "cgst_rate": 9.0,
                "sgst_rate": 9.0,
                "cess_rate": 0.0,
                "cess_non_advol_rate": 0.0,
                "igst_amount": 0.0,
                "cgst_amount": 3842.37,
                "sgst_amount": 3842.37,
                "cess_amount": 0.0,
                "cess_non_advol_amount": 0.0,
                "delivered_by_supplier": 0,
                "income_account": "Office Rent - P",
                "is_fixed_asset": 0,
                "expense_account": "Cost of Goods Sold - P",
                "enable_deferred_revenue": 0,
                "weight_per_unit": 0.0,
                "total_weight": 0.0,
                "use_serial_batch_fields": 1,
                "blocked_qty": 0.0,
                "incoming_rate": 0.0,
                "allow_zero_valuation_rate": 0,
                "item_tax_rate": "{\"Output Tax SGST - P\": 9.0, \"Output Tax CGST - P\": 9.0, \"Output Tax IGST - P\": 18.0, \"Output Tax SGST RCM - P\": -9.0, \"Output Tax CGST RCM - P\": -9.0, \"Output Tax IGST RCM - P\": -18.0, \"Input Tax SGST - P\": 9.0, \"Input Tax CGST - P\": 9.0, \"Input Tax IGST - P\": 18.0, \"Input Tax SGST RCM - P\": 9.0, \"Input Tax CGST RCM - P\": 9.0, \"Input Tax IGST RCM - P\": 18.0}",
                "actual_batch_qty": 0.0,
                "actual_qty": 0.0,
                "company_total_stock": 0.0,
                "delivered_qty": 0.0,
                "cost_center": "Main - P",
                "page_break": 0,
            }
        ]

    

    taxes = taxes or [
      {
            "docstatus": 1,
            "idx": 1,
            "parentfield": "taxes",
            "parenttype": "Sales Invoice",
            "charge_type": "On Net Total",
            "account_head": "Output Tax SGST - P",
            "description": "Output Tax SGST - P",
            "included_in_print_rate": 0,
            "included_in_paid_amount": 0,
            "cost_center": "Main - P",
            "rate": 9.0,
            "gst_tax_type": "sgst",
            "tax_amount": 3842.37,
            "total": 46535.37,
            "tax_amount_after_discount_amount": 3842.37,
            "base_tax_amount": 3842.37,
            "base_total": 46535.37,
            "base_tax_amount_after_discount_amount": 3842.37,
            "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,3842.37]}",
            "dont_recompute_tax": 0
        },
        {
            "docstatus": 1,
            "idx": 2,
            "parentfield": "taxes",
            "parenttype": "Sales Invoice",
            "charge_type": "On Net Total",
            "account_head": "Output Tax CGST - P",
            "description": "Output Tax CGST - P",
            "included_in_print_rate": 0,
            "included_in_paid_amount": 0,
            "cost_center": "Main - P",
            "rate": 9.0,
            "gst_tax_type": "cgst",
            "tax_amount": 3842.37,
            "total": 50377.74,
            "tax_amount_after_discount_amount": 3842.37,
            "base_tax_amount": 3842.37,
            "base_total": 50377.74,
            "base_tax_amount_after_discount_amount": 3842.37,
            "item_wise_tax_detail": "{\"SERVICES/RENTAL 18%\":[9.0,3842.37]}",
            "dont_recompute_tax": 0
        }
    ]

    

    sales_team = sales_team or [
                {
                    "docstatus": 1,
                    "idx": 1,
                    "parentfield": "sales_team",
                    "parenttype": "Sales Invoice",
                    "sales_person": "Sivabalan",
                    "allocated_percentage": 100.0,
                    "allocated_amount": 22770.0,
                    "incentives": 0.0
                }
            ]
    


    payment_schedule = payment_schedule or [
                        {
                            "docstatus": 1,
                            "idx": 1,
                            "parentfield": "payment_schedule",
                            "parenttype": "Sales Invoice",
                            "due_date": frappe.utils.nowdate(),
                            "invoice_portion": 100.0,
                            "discount": 0.0,
                            "payment_amount": 50377.74,
                            "outstanding": 50377.74,
                            "paid_amount": 0.0,
                            "discounted_amount": 0.0,
                            "base_payment_amount": 50377.74
                        }
                    ] 
         


    try:
        # Create a new Sales Invoice document
        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "posting_date": frappe.utils.nowdate(),
            "docstatus": 0,
            "title": "LIC OF INDIA",
            "naming_series": "A/24/.#####",
            "customer": "LIC OF INDIA",
            "company": "P.THANGAVELU",
            "remarks": "No Remarks",
            "items": items,
            "taxes": taxes,
            "sales_team": sales_team,
            "payment_schedule": payment_schedule,
        })

        # Insert the document into the database
        sales_invoice.insert()

        # Submit the Sales Invoice to finalize it
        sales_invoice.submit()

        frappe.msgprint(f"Sales Invoice {sales_invoice.name} created successfully!")
        return sales_invoice.name
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Auto Create Sales Invoice")
        frappe.throw(f"Error creating Sales Invoice: {str(e)}")         




