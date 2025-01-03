# Copyright (c) 2024, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import flt
from erpnext.setup.utils import get_exchange_rate
from bs4 import BeautifulSoup
import urllib.parse
from frappe_whatsapp.utils import run_server_script_for_doc_event
from datetime import datetime


class DyeChart(Document):
    @frappe.whitelist()
    def set_values(self):
        # Fetch values from the "Job Card"
        doc1 = frappe.db.get_value("Job Card", {"name": self.jobcard}, ["production_item", "for_quantity"])
        
        # Debugging: Print the fetched values
        print("\n\n\njobcard\n\n\n", doc1)
        
        # Create a new "Dye Chart" document
        # doc = frappe.new_doc("Dye Chart")
        
        # Set the new document's fields
        self.item = doc1[0]  # production_item
        self.lot_weight = doc1[1]  # for_quantity
        
        # Save the new document
        self.save(ignore_permissions=True)


    def before_save(self):
        if self.lot_weight:
            print("\n\nlot_weight", self.lot_weight)
            items = self.dye_chart_item
            items_len = len(items)

            

            for i in range(items_len):
                # Ensure numeric conversion of dosage, mlr, and requested_qty
                dosage = float(items[i].dosage or 0)  # Default to 0 if None
                mlr = float(items[i].mlr or 0)  # Default to 0 if None
                requested_qty = float(self.lot_weight or 0)  # Default to 0 if None
                if items[i].uom == "Percentage":
                    items[i].total = (requested_qty * dosage) / 100
                else:
                    items[i].total = (requested_qty) * (dosage / 1000) * mlr
        else:
            print("")
            # frappe.msgprint(_("Enter the lot weight greater than 0 and the current lot weight is {0}").format(self.lot_weight))   

    @frappe.whitelist()
    def make_BOM(self):
        frappe.msgprint("BOM is clicked")
        bom=frappe.get_value("BOM",{"custom_dye_chart":self.name},["name"])
        if not bom:
            frappe.msgprint("can create the bom")
            doc=frappe.new_doc("BOM")
            # data = {
            #         "docstatus": 0,
            #         "idx": 0,
            #         "item": "SMF0019/JASMINE GREEN GLOW/54OW/W.AM",
            #         "company": "Pranera Services and Solutions Pvt. Ltd.,",
            #         "uom": "Kgs",
            #         "bom_for": "Purchase Order",
            #         "quantity": 25.0,
            #         "is_active": 1,
            #         "is_default": 0,
            #         "allow_alternative_item": 0,
            #         "set_rate_of_sub_assembly_item_based_on_bom": 1,
            #         "rm_cost_as_per": "Valuation Rate",
            #         "buying_price_list": "Standard Buying",
            #         "price_list_currency": "INR",
            #         "plc_conversion_rate": 1.0,
            #         "currency": "INR",
            #         "conversion_rate": 1.0,
            #         "with_operations": 1,
            #         "transfer_material_against": "Work Order",
            #         "fg_based_operating_cost": 0,
            #         "operating_cost_per_bom_quantity": 0.0,
            #         "process_loss_percentage": 0.0,
            #         "process_loss_qty": 0.0,
            #         "operating_cost": 0.0,
            #         "raw_material_cost": 7137.195,
            #         "scrap_material_cost": 0.0,
            #         "base_operating_cost": 0.0,
            #         "base_raw_material_cost": 7137.195,
            #         "base_scrap_material_cost": 0.0,
            #         "total_cost": 7137.195,
            #         "base_total_cost": 7137.195,
            #         "has_variants": 0,
            #         "inspection_required": 0,
            #         "show_in_website": 0,
            #         "show_items": 0,
            #         "show_operations": 0,
            #         "doctype": "BOM",
            #         "operations": [
            #             {
            #                 "docstatus": 1,
            #                 "idx": 1,
            #                 "sequence_id": 0,
            #                 "operation": "DYEING+STENTERING+WICKING+ANTIMICROBIAL",
            #                 "workstation": "Sub Contracting",
            #                 "time_in_mins": 0.0,
            #                 "fixed_time": 0,
            #                 "hour_rate": 0.0,
            #                 "base_hour_rate": 0.0,
            #                 "operating_cost": 0.0,
            #                 "base_operating_cost": 0.0,
            #                 "batch_size": 1,
            #                 "set_cost_based_on_bom_qty": 0,
            #                 "cost_per_unit": 0.0,
            #                 "base_cost_per_unit": 0.0,
            #                 "description": "Dyeing+Stentering+Wicking+Antimicrobial",
            #                 "parentfield": "operations",
            #                 "parenttype": "BOM",
            #                 "doctype": "BOM Operation"
            #             }
            #         ],
            #         "scrap_items": [],
            #         "items": [
            #             {
            #                 "docstatus": 1,
            #                 "idx": 1,
            #                 "item_code": "HMF0019/GREIGE/54OW",
            #                 "item_name": "100% Polyester 120GSM Warp Knitted Mesh Fabric (COCK RAIL)",
            #                 "do_not_explode": 0,
            #                 "allow_alternative_item": 0,
            #                 "is_stock_item": 1,
            #                 "image": "",
            #                 "qty": 26.0,
            #                 "uom": "Kgs",
            #                 "stock_qty": 26.0,
            #                 "stock_uom": "Kgs",
            #                 "conversion_factor": 1.0,
            #                 "rate": 250.0,
            #                 "base_rate": 250.0,
            #                 "amount": 6500.0,
            #                 "base_amount": 6500.0,
            #                 "qty_consumed_per_unit": 1.04,
            #                 "has_variants": 0,
            #                 "include_item_in_manufacturing": 1,
            #                 "sourced_by_supplier": 0,
            #                 "parentfield": "items",
            #                 "parenttype": "BOM",
            #                 "doctype": "BOM Item"
            #             },
            #             {
            #                 "docstatus": 1,
            #                 "idx": 2,
            #                 "item_code": "CHEM00020/NOSTAT TM",
            #                 "item_name": "NOSTAT TM Chemical",
            #                 "do_not_explode": 0,
            #                 "bom_no": "",
            #                 "allow_alternative_item": 0,
            #                 "is_stock_item": 1,
            #                 "description": "<div>NOSTAT TM Chemical</div>",
            #                 "image": "",
            #                 "qty": 0.52,
            #                 "uom": "Kgs",
            #                 "stock_qty": 0.52,
            #                 "stock_uom": "Kgs",
            #                 "conversion_factor": 1.0,
            #                 "rate": 299.193085151,
            #                 "base_rate": 299.193085151,
            #                 "amount": 155.5788,
            #                 "base_amount": 155.5788,
            #                 "qty_consumed_per_unit": 0.0208,
            #                 "has_variants": 0,
            #                 "include_item_in_manufacturing": 1,
            #                 "sourced_by_supplier": 0,
            #                 "parentfield": "items",
            #                 "parenttype": "BOM",
            #                 "doctype": "BOM Item"
            #             },
            #             {
            #                 "docstatus": 1,
            #                 "idx": 3,
            #                 "item_code": "CHEM0001/N9 PURE SILVER",
            #                 "item_name": "CHEMICAL - N9 PURE SILVER - MICRO PE",
            #                 "do_not_explode": 0,
            #                 "bom_no": "",
            #                 "allow_alternative_item": 0,
            #                 "is_stock_item": 1,
            #                 "description": "CHEMICAL - N9 PURE SILVER - MICRO PE",
            #                 "image": "",
            #                 "qty": 0.26,
            #                 "uom": "Kgs",
            #                 "stock_qty": 0.26,
            #                 "stock_uom": "Kgs",
            #                 "conversion_factor": 1.0,
            #                 "rate": 1852.365432567,
            #                 "base_rate": 1852.365432567,
            #                 "amount": 481.6162,
            #                 "base_amount": 481.6162,
            #                 "qty_consumed_per_unit": 0.0104,
            #                 "has_variants": 0,
            #                 "include_item_in_manufacturing": 1,
            #                 "sourced_by_supplier": 0,
            #                 "parentfield": "items",
            #                 "parenttype": "BOM",
            #                 "doctype": "BOM Item"
            #             }
            #         ]
            # }
            # doc.update(data)
            doc.save(ignore_permissions=True)
            frappe.msgprint("BOM is Created")

        else:
            frappe.msgprint("BOM is already created")


                 
    @frappe.whitelist()
    def update_jobcard(self):
        frappe.msgprint("update_jobcard is clicked")
        print("\n\n\nself\n\n\n", self.name)
        dye_chart = self.name
        # jobcard=frappe.get_value("Job Card",{"name":self.jobcard},[])
        jobcard = frappe.get_doc("Job Card", {"name": self.jobcard})
        frappe.msgprint("can create the bom")
        print("\n\n\njobcard\n\n\n",jobcard)
        # Get the list of existing custom_dye_chart_item_names in jobcard
        existing_custom_dye_chart_items = [item.custom_dye_chart_item_name for item in jobcard.items]

        # Add only new dye_chart_item entries that are not already present in the jobcard items
        for i in self.dye_chart_item:
            if i.name not in existing_custom_dye_chart_items:
                jobcard.append("items", {
                    "item_code": i.item,
                    "doctype": "Job Card Item",
                    "parenttype": "Job Card",
                    "source_warehouse": "DYE/CHEMICAL STORES - PSS",
                    "custom_dye_chart": self.name,
                    "custom_dye_chart_item_name": i.name,
                    "custom_mlr": i.mlr,
                    "custom_bath": i.bath_no,
                    "custom_dosage": i.dosage,
                    "custom_uoms": i.uom,
                    "custom_functions": i.chemicals,
                    "required_qty": i.total
                })

        # Save the Job Card document
        jobcard.save(ignore_permissions=True)
        frappe.msgprint("Jobcard Updated") 

@frappe.whitelist()
def create_bom_scrap_items(docname):
    print("\n\n\ncreate_bom_items\n\n\n")
    doc = frappe.get_doc('BOM', docname)
    
    # Return the items child table
    return doc.scrap_items

@frappe.whitelist()
def create_dye_chart(docname, item, lot_weight, custom_add_on_qty):
    doc = frappe.new_doc("Dye Chart")
    doc1 = frappe.db.get_value("Job Card", {"name": docname}, ["production_item", "for_quantity", "custom_add_on_qty"])
    print("\n\n\ndoc1\n\n\n",doc1)    
    # Set the new document's fields
    doc.jobcard = docname
    doc.item = doc1[0]  # production_item
    doc.lot_weight = doc1[1] + doc1[2] # for_quantity
    
    # Save the new document
    doc.save(ignore_permissions=True)
    return doc.name


@frappe.whitelist()
def create_stock_entry_items(docname):
    # Fetch the entire Job Card document
    doc = frappe.get_doc('Job Card', docname)
    
    # Return the items child table
    return doc.items

@frappe.whitelist()
def get_work_order_data(docname):
    # Fetch the entire Job Card document
    doc = frappe.get_doc('Work Order', docname)
    
    # Return the items child table
    return doc    

@frappe.whitelist()
def update_work_order_in_stock_entry(docname, work_order, qty):
    print("update_work_order_in_stock_entry")
    
    # Fetch the entire Batch document using frappe.get_doc
    doc1 = frappe.get_doc("Batch", docname)

    wo = work_order
    stock_qty = qty
    
    if doc1:
        print("\n\n\ndoc1\n\n\n", doc1)    
        # Set the new document's custom field for work order
        # doc1.custom_work_order = work_order
        
        # Check if the batch_reference child table exists and add a row
        doc1.append("custom_batch_reference", {
            "work_order": wo,
            "qty": stock_qty
        })
        
        # Save the document to apply changes
        doc1.save()
        
        # # Optionally submit the document if required
        # # doc1.submit()
        
        # frappe.db.commit()  # Ensure that the changes are saved to the database
    else:
        print("No document found with name:", docname)



# @frappe.whitelist()
# def update_work_order_in_stock_entry(docname, work_order, qty):
#     print("update_work_order_in_stock_entry")
    
#     # Fetch the entire Batch document using frappe.get_doc
#     doc1 = frappe.get_doc("Batch", docname)
    
#     if doc1:
#         print("\n\n\ndoc1\n\n\n", doc1)    
#         # Set the new document's field
#         doc1.custom_work_order = work_order
        
#         # Save the document to apply changes
#         doc1.save()
        
#         # Optionally submit the document if required
#         # doc1.submit()
        
#         frappe.db.commit()  # Ensure that the changes are saved to the database
#     else:
#         print("No document found with name:", docname)

#     # Save the new document
#     doc1.save(ignore_permissions=True)
#     return doc1    

# @frappe.whitelist()
# def set_additional_cost(docname):
#     # Fetch the Work Order document
#     work_order = frappe.get_doc('Work Order', docname)
    
#     # Initialize the total water reading value
#     total_water_reading_value = 0

#     # Fetch all Job Cards linked to the Work Order
#     job_cards = frappe.get_all('Job Card', filters={'work_order': docname}, fields=['name', 'custom_water_reading_value'])

#     # Sum the custom_water_reading_value from all linked Job Cards
#     for job_card in job_cards:
#         total_water_reading_value += job_card.get('custom_water_reading_value', 0)

#     j

#     # Return the total sum of custom_water_reading_value
#     print("\n\n\ntotal_water_reading_value\n\n\n", total_water_reading_value)
#     frappe.db.set_value("Work Order", docname, "custom_total_operating_cost_include_water", total_water_reading_value)
#     frappe.msgprint(f"Total Operating Cost Include Water updated to {total_water_reading_value}.")
#     return total_water_reading_value

@frappe.whitelist()
def set_additional_cost(docname):
    # Fetch the Work Order document
    work_order = frappe.get_doc('Work Order', docname)
    
    # Initialize the total water reading value
    total_water_reading_value = 0
    custom_total_outgoing_values = 0
    custom_planned_cost_per_kg = 0
    custom_actual_cost_per_kg = 0
    custom_profit_and_loss = 0
    custom_profit_and_loss_per_work_order = 0



    # Fetch all Job Cards linked to the Work Order
    job_cards = frappe.get_all('Job Card', filters={'work_order': docname}, fields=['name', 'custom_water_reading_value'])

    stock_entry = frappe.get_all('Stock Entry', filters={'work_order': docname, 'stock_entry_type': 'Manufacture'}, fields=['name', 'custom_total_outgoing_values'])

    # Loop through each Job Card to sum the water reading value and access the operations table
    for job_card in job_cards:
        # Get the Job Card document to access its child tables (operations)
        job_card_doc = frappe.get_doc('Job Card', job_card['name'])
        
        # Print the Job Card document for debugging purposes
        print("\n\n\n\nJob Card Document\n\n\n", job_card_doc)

        print("\n\n\n\nJob Card Document\n\n\n", job_card_doc.workstation)

        workstation_doc = frappe.get_doc('Workstation', job_card_doc.workstation)
        print("\n\n\nworkstation_doc\n\n\n", workstation_doc.custom_water_cost)
        
        # Sum the custom_water_reading_value from all linked Job Cards
        total_water_reading_value += job_card.get('custom_water_reading_value', 0) * workstation_doc.custom_water_cost

    # Loop through each Stock Entry and sum the custom_total_outgoing_values
    for stock_entries in stock_entry:
        custom_total_outgoing_values += stock_entries.get('custom_total_outgoing_values', 0)  # Corrected access

    # Update the total water reading value in the Work Order
    print(f"\n\nTotal Water Reading Value: {total_water_reading_value}\n\n")

    final_total_operting_cost = total_water_reading_value + work_order.actual_operating_cost

    custom_planned_cost_per_kg = (total_water_reading_value + work_order.actual_operating_cost)/work_order.produced_qty
    custom_actual_cost_per_kg = (final_total_operting_cost + custom_total_outgoing_values)/work_order.produced_qty
    # Ensure both variables are converted to float before performing subtraction
    custom_profit_and_loss = float(custom_planned_cost_per_kg) - float(custom_actual_cost_per_kg)
    custom_profit_and_loss_per_work_order = float(custom_profit_and_loss) * work_order.produced_qty

    print("\n\n\ncustom_profit_and_loss\n\n\n",custom_planned_cost_per_kg)
    print("\n\n\ncustom_profit_and_loss\n\n\n",custom_profit_and_loss)
    print("\n\n\ncustom_profit_and_loss\n\n\n",custom_profit_and_loss)
    # Update the Work Order with calculated costs
    frappe.db.set_value("Work Order", docname, "custom_total_operating_cost_include_water", total_water_reading_value)
    frappe.db.set_value("Work Order", docname, "total_operating_cost", final_total_operting_cost)
    frappe.db.set_value("Work Order", docname, "custom_total_consumption_cost", custom_total_outgoing_values)

    frappe.db.set_value("Work Order", docname, "custom_planned_cost_per_kg", custom_planned_cost_per_kg)
    frappe.db.set_value("Work Order", docname, "custom_actual_cost_per_kg", custom_actual_cost_per_kg)
    frappe.db.set_value("Work Order", docname, "custom_profit_and_loss", custom_profit_and_loss)
    frappe.db.set_value("Work Order", docname, "custom_profit_and_loss_per_work_order", custom_profit_and_loss_per_work_order)

    # Display a message for the user
    frappe.msgprint(f"Total Operating Cost Include Water updated to {total_water_reading_value}.")
    
    return total_water_reading_value



@frappe.whitelist()
def update_batch(custom_duplicate_stock_entry):
    # Fetch the Stock Entry document
    # stock_entry = frappe.get_doc('Stock Entry', docname)

    duplicate_stock_entry = frappe.get_doc('Stock Entry', custom_duplicate_stock_entry)

    return duplicate_stock_entry.items

@frappe.whitelist()
def update_batch_sbb(custom_duplicate_serial_and_batch_bundle):
    # Fetch the Stock Entry document
    # stock_entry = frappe.get_doc('Stock Entry', docname)

    duplicate_stock_entry = frappe.get_doc('Serial and Batch Bundle', custom_duplicate_serial_and_batch_bundle)

    return duplicate_stock_entry.entries    
    
    # # Iterate over the child table `items` (default fieldname for Stock Entry Details)
    # for duplicate_item in duplicate_stock_entry.items:
    #     print("\n\n\nitem\n\n\n",duplicate_item.item_code)
    #     print("\n\n\nbatch\n\n\n",duplicate_item.batch_no)
    #     return duplicate_item.
    #     for item in stock_entry.items:
    #         if(duplicate_item.item_code == item.item_code):
    #             return duplicate_item.batch_no


def every_five_minutes():
    print("\n\n\nevery_1_minutes\n\n\n")






    





    
             
              
