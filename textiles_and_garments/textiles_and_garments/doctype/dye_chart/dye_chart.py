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
    # @frappe.whitelist()
    # def create_jv_for_wo(self):
    #     print("\n\ncreate_jv_for_wo\n\n")


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

# @frappe.whitelist()
# def set_operation_cost_in_work_order(docname):
#     # Fetch the Work Order document
#     work_order = frappe.get_doc('Work Order', docname)

#     # Ensure the operation is only added if the flag is enabled
#     if work_order.custom_include_loading_greige == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Loading Greige"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Loading Greige"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Loading Greige",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })

#     if work_order.custom_loading_and_unloading_greige_lot == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Loading and Unloading Greige Lot"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Loading and Unloading Greige Lot"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Loading and Unloading Greige Lot",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })

#     if work_order.custom_loading_and_unloading_finished_lot == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Loading and Unloading Finished Lot"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Loading and Unloading Finished Lot"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Loading and Unloading Finished Lot",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })

#     if work_order.custom_loading_and_unloading_wet_lot == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Loading and Unloading Finished Lot"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Loading and Unloading Wet Lot"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Loading and Unloading Wet Lot",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })

#     if work_order.custom_sample_dyeing == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Sample - Dyeing"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Sample - Dyeing"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Sample - Dyeing",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })

#     if work_order.custom_cotton_dyeing_colour == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Cotton - Dyeing Colour"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Cotton - Dyeing Colour"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Cotton - Dyeing Colour",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })
    
#     if work_order.custom_cotton_washing == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Cotton - Washing"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Cotton - Washing"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Cotton - Washing",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })

#     if work_order.custom_cotton_white == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Cotton - White"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Cotton - White"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Cotton - White",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })
            
#     if work_order.custom_poly_cotton_double_dyeing == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Poly Cotton - Double Dyeing"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Poly Cotton - Double Dyeing"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Poly Cotton - Double Dyeing",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })
            
#     if work_order.custom_polyester_double_dyeing == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Polyester - Double Dyeing"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Polyester - Double Dyeing"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Polyester - Double Dyeing",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })

#     if work_order.custom_polyester_dyeing_colour == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Polyester - Dyeing  Colour"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Polyester - Dyeing  Colour"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Polyester - Dyeing  Colour",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })
            
#     if work_order.custom_polyester_dyeing_white == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Polyester - Dyeing White"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Polyester - Dyeing White"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Polyester - Dyeing White",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })

#     if work_order.custom_polyester_re_dyeing_colour == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Polyester - Re Dyeing  Colour"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Polyester - Re Dyeing  Colour"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Polyester - Re Dyeing  Colour",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })
            
#     if work_order.custom_polyester_re_dyeing_white == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Polyester - Re Dyeing  Colour"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Polyester - Re Dyeing White"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Polyester - Re Dyeing White",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })
            
#     if work_order.custom_polyester_re_washing == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Polyester - Re Washing"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Polyester - Re Washing"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Polyester - Re Washing",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })

#     if work_order.custom_polyester_washing == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Polyester - Washing"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Polyester - Washing"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Polyester - Washing",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })

#     if work_order.custom_stitching_overlock == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Stitching (Overlock)"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Stitching (Overlock)"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Stitching (Overlock)",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })
            

#     if work_order.custom_tubular_stitching_overlock == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Tubular Stitching (Overlock)"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Tubular Stitching (Overlock)"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Tubular Stitching (Overlock)",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })
            
#     if work_order.custom_collar_padding == 1:

#         local_rate = frappe.get_value("Operation Rate", {"name": "Collar Padding"}, "rate")

#         if local_rate is not None:
#             # Remove existing "Loading Greige" rows from the table
#             work_order.custom_work_order_operations = [
#                 row for row in work_order.custom_work_order_operations
#                 if row.operation_name != "Collar Padding"
#             ]

#             # Append the new operation
#             work_order.append("custom_work_order_operations", {
#                 "operation_name": "Collar Padding",
#                 "qty": work_order.qty,
#                 "rate": local_rate,
#                 "amount": work_order.qty * local_rate,
#             })                                                                                                                                                

#     # Calculate the total contract operation cost
#     total_cost = sum(row.amount for row in work_order.custom_work_order_operations if row.amount)

#     total_cost_exclude_stitch_and_padding = sum(
#         row.amount for row in work_order.custom_work_order_operations 
#         if row.amount and row.operation not in ["Stitching (Overlock)", "Tubular Stitching (Overlock)", "Collar Padding"]
#     )


#     stitch_cost = sum(
#         row.amount for row in work_order.custom_work_order_operations 
#         if row.amount and row.operation in ["Stitching (Overlock)", "Tubular Stitching (Overlock)"]
#     )

#     padding_cost = sum(
#         row.amount for row in work_order.custom_work_order_operations 
#         if row.amount and row.operation in ["Collar Padding"]
#     )


#     # Store the total in the custom field
#     work_order.custom_total_contract_operation_cost = total_cost

#     work_order.custom_stitch_operation_cost = stitch_cost

#     work_order.custom_padding_operation_cost = padding_cost

#     work_order.custom_total_contract_operation_cost_exclude_stitch_and_pad = total_cost_exclude_stitch_and_padding

#     # Save and commit changes
#     work_order.save(ignore_permissions=True)
#     frappe.db.commit()

#     frappe.msgprint(f"Operating Cost Table updated. Total Contract Operation Cost: {total_cost}")
   
#     return

# @frappe.whitelist()
# def set_operation_cost_in_work_order(docname):
#     # Fetch the Work Order document
#     work_order = frappe.get_doc('Work Order', docname)

#     operations = {
#         "custom_include_loading_greige": "Loading Greige",
#         "custom_loading_and_unloading_greige_lot": "Loading and Unloading Greige Lot",
#         "custom_loading_and_unloading_finished_lot": "Loading and Unloading Finished Lot",
#         "custom_loading_and_unloading_wet_lot": "Loading and Unloading Wet Lot",
#         "custom_sample_dyeing": "Sample - Dyeing",
#         "custom_cotton_dyeing_colour": "Cotton - Dyeing Colour",
#         "custom_cotton_washing": "Cotton - Washing",
#         "custom_cotton_white": "Cotton - White",
#         "custom_poly_cotton_double_dyeing": "Poly Cotton - Double Dyeing",
#         "custom_polyester_double_dyeing": "Polyester - Double Dyeing",
#         "custom_polyester_dyeing_colour": "Polyester - Dyeing Colour",
#         "custom_polyester_dyeing_white": "Polyester - Dyeing White",
#         "custom_polyester_re_dyeing_colour": "Polyester - Re Dyeing Colour",
#         "custom_polyester_re_dyeing_white": "Polyester - Re Dyeing White",
#         "custom_polyester_re_washing": "Polyester - Re Washing",
#         "custom_polyester_washing": "Polyester - Washing",
#         "custom_stitching_overlock": "Stitching (Overlock)",
#         "custom_tubular_stitching_overlock": "Tubular Stitching (Overlock)",
#         "custom_collar_padding": "Collar Padding"
#     }

#     # Clear all rows from the child table before inserting new ones
#     work_order.set("custom_work_order_operations", [])

#     # Process each operation and insert rows
#     for field, operation_name in operations.items():
#         if getattr(work_order, field, 0) == 1:
#             local_rate = frappe.get_value("Operation Rate", {"name": operation_name}, "rate")
#             if local_rate is not None:
#                 work_order.append("custom_work_order_operations", {
#                     "operation_name": operation_name,
#                     "qty": work_order.qty,
#                     "rate": local_rate,
#                     "amount": work_order.qty * local_rate,
#                 })

#     # Calculate total costs
#     total_cost = sum(row.amount for row in work_order.custom_work_order_operations if row.amount)

#     total_cost_exclude_stitch_and_padding = sum(
#         row.amount for row in work_order.custom_work_order_operations
#         if row.amount and row.operation_name not in ["Stitching (Overlock)", "Tubular Stitching (Overlock)", "Collar Padding"]
#     )

#     stitch_cost = sum(
#         row.amount for row in work_order.custom_work_order_operations
#         if row.amount and row.operation_name in ["Stitching (Overlock)", "Tubular Stitching (Overlock)"]
#     )

#     padding_cost = sum(
#         row.amount for row in work_order.custom_work_order_operations
#         if row.amount and row.operation_name == "Collar Padding"
#     )

#     # Update total cost fields in the Work Order
#     work_order.custom_total_contract_operation_cost = total_cost
#     work_order.custom_total_contract_operation_cost_exclude_stitch_and_pad = total_cost_exclude_stitch_and_padding
#     work_order.custom_stitch_operation_cost = stitch_cost
#     work_order.custom_padding_operation_cost = padding_cost

#     # Save the updated Work Order
#     work_order.save()

#     return {
#         "message": "Operation costs updated successfully",
#         "total_cost": total_cost,
#         "stitch_cost": stitch_cost,
#         "padding_cost": padding_cost,
#         "total_cost_excluding_stitch_and_padding": total_cost_exclude_stitch_and_padding
#     }




@frappe.whitelist()
def set_operation_cost_in_sales_invoice(docname):
    print("set_operation_cost_in_sales_invoice")
    sales_invoice = frappe.get_doc('Sales Invoice', docname)
    operations = {
        "custom_loading_and_unloading_greige_lot": "Loading and Unloading Greige Lot",
        "custom_loading_and_unloading_finished_lot": "Loading and Unloading Finished Lot",
        "custom_loading_and_unloading_wet_lot": "Loading and Unloading Wet Lot"
    }

    # Clear all rows from the child table before inserting new ones
    sales_invoice.set("custom_loading_and_unloading_operations", [])

    # Process each operation and insert rows
    for field, operation_name in operations.items():
        if getattr(sales_invoice, field, 0) == 1:
            local_rate = frappe.get_value("Operation Rate", {"name": operation_name}, "rate")
            if local_rate is not None:
                # qty = (
                #     stock_entry.custom_trims_weight
                #     if operation_name == "Collar Padding"
                #     else stock_entry.custom_fabric_and_trims_weight
                # )
                sales_invoice.append("custom_loading_and_unloading_operations", {
                    "operation_name": operation_name,
                    "qty": sales_invoice.custom_total_weight,
                    "rate": local_rate,
                    "amount": sales_invoice.custom_total_weight * local_rate,
                })

    # Calculate total costs
    total_cost = sum(row.amount for row in sales_invoice.custom_loading_and_unloading_operations if row.amount)

    

    # Update total cost fields in the Stock Entry
    sales_invoice.custom_total_contract_operation_cost = total_cost
    

    # Save the updated Work Order
    sales_invoice.save()

    return {
        "message": "Operation costs updated successfully",
        "total_cost": total_cost
    }


@frappe.whitelist()
def set_operation_cost_in_stock_entry(docname):
    print("set_operation_cost_in_stock_entry")
    stock_entry = frappe.get_doc('Stock Entry', docname)
    operations = {
        "custom_loading_and_unloading_greige_lot": "Loading and Unloading Greige Lot",
        "custom_loading_and_unloading_finished_lot": "Loading and Unloading Finished Lot",
        "custom_loading_and_unloading_wet_lot": "Loading and Unloading Wet Lot"
    }

    # Clear all rows from the child table before inserting new ones
    stock_entry.set("custom_loading_and_unloading_operations", [])

    # Process each operation and insert rows
    for field, operation_name in operations.items():
        if getattr(stock_entry, field, 0) == 1:
            local_rate = frappe.get_value("Operation Rate", {"name": operation_name}, "rate")
            if local_rate is not None:
                # qty = (
                #     stock_entry.custom_trims_weight
                #     if operation_name == "Collar Padding"
                #     else stock_entry.custom_fabric_and_trims_weight
                # )
                stock_entry.append("custom_loading_and_unloading_operations", {
                    "operation_name": operation_name,
                    "qty": stock_entry.custom_total_weight,
                    "rate": local_rate,
                    "amount": stock_entry.custom_total_weight * local_rate,
                })

    # Calculate total costs
    total_cost = sum(row.amount for row in stock_entry.custom_loading_and_unloading_operations if row.amount)

    

    # Update total cost fields in the Stock Entry
    stock_entry.custom_total_contract_operation_cost = total_cost
    

    # Save the updated Work Order
    stock_entry.save()

    return {
        "message": "Operation costs updated successfully",
        "total_cost": total_cost
    }

@frappe.whitelist()
def set_operation_cost_in_purchase_receipt(docname):
    print("set_operation_cost_in_purchase_receipt")
    purchase_receipt = frappe.get_doc('Purchase Receipt', docname)
    operations = {
        "custom_loading_and_unloading_greige_lot": "Loading and Unloading Greige Lot",
        "custom_loading_and_unloading_finished_lot": "Loading and Unloading Finished Lot",
        "custom_loading_and_unloading_wet_lot": "Loading and Unloading Wet Lot"
    }

    # Clear all rows from the child table before inserting new ones
    purchase_receipt.set("custom_loading_and_unloading_operations", [])

    # Process each operation and insert rows
    for field, operation_name in operations.items():
        if getattr(purchase_receipt, field, 0) == 1:
            local_rate = frappe.get_value("Operation Rate", {"name": operation_name}, "rate")
            if local_rate is not None:
                # qty = (
                #     stock_entry.custom_trims_weight
                #     if operation_name == "Collar Padding"
                #     else stock_entry.custom_fabric_and_trims_weight
                # )
                purchase_receipt.append("custom_loading_and_unloading_operations", {
                    "operation_name": operation_name,
                    "qty": purchase_receipt.custom_total_weight,
                    "rate": local_rate,
                    "amount": purchase_receipt.custom_total_weight * local_rate,
                })

    # Calculate total costs
    total_cost = sum(row.amount for row in purchase_receipt.custom_loading_and_unloading_operations if row.amount)

    

    # Update total cost fields in the Stock Entry
    purchase_receipt.custom_total_contract_operation_cost = total_cost
    

    # Save the updated Work Order
    purchase_receipt.save()

    return {
        "message": "Operation costs updated successfully",
        "total_cost": total_cost
    }    




@frappe.whitelist()
def set_operation_cost_in_work_order(docname):
    # Fetch the Work Order document
    work_order = frappe.get_doc('Work Order', docname)

    operations = {
        "custom_include_loading_greige": "Loading Greige",
        "custom_loading_and_unloading_greige_lot": "Loading and Unloading Greige Lot",
        "custom_loading_and_unloading_finished_lot": "Loading and Unloading Finished Lot",
        "custom_loading_and_unloading_wet_lot": "Loading and Unloading Wet Lot",
        "custom_sample_dyeing": "Sample - Dyeing",
        "custom_sample_double_dyeing": "Sample Double Dyeing",
        "custom_sample_washing": "Sample Washing",
        "custom_cotton_dyeing_colour": "Cotton - Dyeing Colour",
        "custom_cotton_washing": "Cotton - Washing",
        "custom_cotton_white": "Cotton - White",
        "custom_poly_cotton_double_dyeing": "Poly Cotton - Double Dyeing",
        "custom_polyester_double_dyeing": "Polyester - Double Dyeing",
        "custom_polyester_dyeing_colour": "Polyester - Dyeing Colour",
        "custom_polyester_dyeing_white": "Polyester - Dyeing White",
        "custom_polyester_re_dyeing_colour": "Polyester - Re Dyeing Colour",
        "custom_polyester_re_dyeing_white": "Polyester - Re Dyeing White",
        "custom_polyester_re_washing": "Polyester - Re Washing",
        "custom_polyester_washing": "Polyester - Washing",
        "custom_stitching_overlock": "Stitching (Overlock)",
        "custom_tubular_stitching_overlock": "Tubular Stitching (Overlock)",
        "custom_collar_padding": "Collar Padding"
    }

    # Clear all rows from the child table before inserting new ones
    work_order.set("custom_work_order_operations", [])

    # Process each operation and insert rows
    for field, operation_name in operations.items():
        if getattr(work_order, field, 0) == 1:
            local_rate = frappe.get_value("Operation Rate", {"name": operation_name}, "rate")
            if local_rate is not None:
                # qty = (
                #     work_order.custom_trims_weight
                #     if operation_name == "Collar Padding"
                #     else work_order.custom_fabric_and_trims_weight
                # )
                if operation_name == "Collar Padding":
                    qty = work_order.custom_trims_weight
                elif operation_name == "Stitching (Overlock)" or operation_name == "Tubular Stitching (Overlock)":
                    qty = work_order.custom_stitching_weight
                else:
                    qty = work_order.custom_fabric_and_trims_weight      
                work_order.append("custom_work_order_operations", {
                    "operation_name": operation_name,
                    "qty": qty,
                    "rate": local_rate,
                    "amount": qty * local_rate,
                })

    # Calculate total costs
    total_cost = sum(row.amount for row in work_order.custom_work_order_operations if row.amount)

    total_cost_exclude_stitch_and_padding = sum(
        row.amount for row in work_order.custom_work_order_operations
        if row.amount and row.operation_name not in ["Stitching (Overlock)", "Tubular Stitching (Overlock)", "Collar Padding"]
    )

    stitch_cost = sum(
        row.amount for row in work_order.custom_work_order_operations
        if row.amount and row.operation_name in ["Stitching (Overlock)", "Tubular Stitching (Overlock)"]
    )

    padding_cost = sum(
        row.amount for row in work_order.custom_work_order_operations
        if row.amount and row.operation_name == "Collar Padding"
    )

    # Update total cost fields in the Work Order
    work_order.custom_total_contract_operation_cost = total_cost
    work_order.custom_total_contract_operation_cost_exclude_stitch_and_pad = total_cost_exclude_stitch_and_padding
    work_order.custom_stitch_operation_cost = stitch_cost
    work_order.custom_padding_operation_cost = padding_cost

    # Save the updated Work Order
    work_order.save()

    return {
        "message": "Operation costs updated successfully",
        "total_cost": total_cost,
        "stitch_cost": stitch_cost,
        "padding_cost": padding_cost,
        "total_cost_excluding_stitch_and_padding": total_cost_exclude_stitch_and_padding
    }





@frappe.whitelist()
def get_total_of_work_order_payments(custom_work_order_payments):
    
    # Fetch the Work Order Payment document
    work_order_payment = frappe.get_doc("Work Order Payments", custom_work_order_payments)
    # payment_entry_doc = frappe.get_doc("Payment Entry", docname)
    # payment_entry_doc.paid_amount = work_order_payment.grand_total
    # payment_entry_doc.save(ignore_permissions=True)
    # frappe.db.commit()
    return work_order_payment.grand_total


    



# @frappe.whitelist()
# def get_unpaid_work_order(docname, from_date, to_date, contractor, stitching_contractor, padding_contractor, contractor_category):
#     print("\n\ncontractor\n\n",contractor)
#     print("\n\nstitching_contractor\n\n",stitching_contractor)
#     print("\n\npadding_contractor\n\n",padding_contractor)

#     if contractor:
#         unpaid_work_orders = frappe.get_all(
#             "Work Order",
#             filters={
#                 "custom_payment_status": ["!=", "Paid"],
#                 "creation": ["between", [from_date, to_date]],
#                 "custom_contractor": ["=", contractor]
#             },
#             fields=["name", "custom_total_contract_operation_cost", "custom_total_contract_operation_cost_exclude_stitch_and_pad", "custom_stitch_operation_cost", "custom_padding_operation_cost"]
#         )

#         if not unpaid_work_orders:
#             frappe.msgprint("No unpaid Work Orders found in the given date range.")
#             return

#         # Fetch the Work Order Payment document
#         work_order_payment = frappe.get_doc("Work Order Payments", docname)

#         # Clear existing rows from work_order_payment_item table
#         work_order_payment.set("work_order_payment_item", [])  

#         total_amount = 0  # Initialize total amount


#         for wo in unpaid_work_orders:
#             amount = wo.custom_total_contract_operation_cost_exclude_stitch_and_pad or 0
#             total_amount += amount

#             # Append new rows to the work_order_payment_item table
#             work_order_payment.append("work_order_payment_item", {
#                 "work_order": wo.name,
#                 "amount": amount
#             })

#         work_order_payment.contractor = contractor       

#         # Store the total in the grand_total field
#         work_order_payment.grand_total = total_amount

#         work_order_payment.net_total = total_amount - total_amount*(work_order_payment.deduct_percentage/100)

#         print("\n\n\nwork_order_payment.net_total\n\n\n",work_order_payment.net_total)

#         # Save and commit changes
#         work_order_payment.save(ignore_permissions=True)
#         frappe.db.commit()

#         frappe.msgprint(f"Replaced existing Work Orders and added {len(unpaid_work_orders)} new Work Orders to Work Order Payment {docname}. Grand Total: {total_amount}")

# if stitching_contractor:
#         unpaid_work_orders = frappe.get_all(
#             "Work Order",
#             filters={
#                 "custom_payment_status": ["!=", "Paid"],
#                 "creation": ["between", [from_date, to_date]],
#                 "custom_stitching_contractor": ["=", stitching_contractor]
#             },
#             fields=["name", "custom_total_contract_operation_cost", "custom_total_contract_operation_cost_exclude_stitch_and_pad", "custom_stitch_operation_cost", "custom_padding_operation_cost"]
#         )

#         if not unpaid_work_orders:
#             frappe.msgprint("No unpaid Work Orders found in the given date range.")
#             return

#         # Fetch the Work Order Payment document
#         work_order_payment = frappe.get_doc("Work Order Payments", docname)

#         # Clear existing rows from work_order_payment_item table
#         work_order_payment.set("work_order_payment_item", [])  

#         total_amount = 0  # Initialize total amount


#         for wo in unpaid_work_orders:
#             amount = wo.custom_stitch_operation_cost or 0
#             total_amount += amount

#             # Append new rows to the work_order_payment_item table
#             work_order_payment.append("work_order_payment_item", {
#                 "work_order": wo.name,
#                 "amount": amount
#             })

#         work_order_payment.stitching_contractor = stitching_contractor       

#         # Store the total in the grand_total field
#         work_order_payment.grand_total = total_amount

#         work_order_payment.net_total = total_amount - total_amount*(work_order_payment.deduct_percentage/100)

#         print("\n\n\nwork_order_payment.net_total\n\n\n",work_order_payment.net_total)

#         # Save and commit changes
#         work_order_payment.save(ignore_permissions=True)
#         frappe.db.commit()

#         frappe.msgprint(f"Replaced existing Work Orders and added {len(unpaid_work_orders)} new Work Orders to Work Order Payment {docname}. Grand Total: {total_amount}")

# if npadding_contractor:
#         unpaid_work_orders = frappe.get_all(
#             "Work Order",
#             filters={
#                 "custom_payment_status": ["!=", "Paid"],
#                 "creation": ["between", [from_date, to_date]],
#                 "custom_padding_contractor": ["=", padding_contractor]
#             },
#             fields=["name", "custom_total_contract_operation_cost", "custom_total_contract_operation_cost_exclude_stitch_and_pad", "custom_stitch_operation_cost", "custom_padding_operation_cost"]
#         )

#         if not unpaid_work_orders:
#             frappe.msgprint("No unpaid Work Orders found in the given date range.")
#             return

#         # Fetch the Work Order Payment document
#         work_order_payment = frappe.get_doc("Work Order Payments", docname)

#         # Clear existing rows from work_order_payment_item table
#         work_order_payment.set("work_order_payment_item", [])  

#         total_amount = 0  # Initialize total amount


#         for wo in unpaid_work_orders:
#             amount = wo.custom_padding_operation_cost or 0
#             total_amount += amount

#             # Append new rows to the work_order_payment_item table
#             work_order_payment.append("work_order_payment_item", {
#                 "work_order": wo.name,
#                 "amount": amount
#             })

#         work_order_payment.padding_contractor = padding_contractor       

#         # Store the total in the grand_total field
#         work_order_payment.grand_total = total_amount

#         work_order_payment.net_total = total_amount - total_amount*(work_order_payment.deduct_percentage/100)

#         print("\n\n\nwork_order_payment.net_total\n\n\n",work_order_payment.net_total)

#         # Save and commit changes
#         work_order_payment.save(ignore_permissions=True)
#         frappe.db.commit()

#         frappe.msgprint(f"Replaced existing Work Orders and added {len(unpaid_work_orders)} new Work Orders to Work Order Payment {docname}. Grand Total: {total_amount}")


@frappe.whitelist()
def get_unpaid_work_order(docname, from_date, to_date, contractor=None, stitching_contractor=None, padding_contractor=None, contractor_category=None):
    print("\n\ncontractor\n\n", contractor)
    print("\n\nstitching_contractor\n\n", stitching_contractor)
    print("\n\npadding_contractor\n\n", padding_contractor)

    def process_work_orders(contractor_field, amount_field, contractor_value, contractor_type):
        if contractor_value:
            unpaid_work_orders = frappe.get_all(
                "Work Order",
                filters={
                    "custom_payment_status": ["!=", "Paid"],
                    "modified": ["between", [from_date, to_date]],
                    contractor_field: ["=", contractor_value]
                },
                fields=["name", "custom_total_contract_operation_cost", "custom_total_contract_operation_cost_exclude_stitch_and_pad", "custom_stitch_operation_cost", "custom_padding_operation_cost"]
            )

            if not unpaid_work_orders:
                frappe.msgprint(f"No unpaid Work Orders found for {contractor_type} in the given date range.")
                return

            # Fetch the Work Order Payment document
            work_order_payment = frappe.get_doc("Work Order Payments", docname)

            # Clear existing rows from work_order_payment_item table
            work_order_payment.set("work_order_payment_item", [])

            total_amount = sum(getattr(wo, amount_field, 0) or 0 for wo in unpaid_work_orders)

            # Append new rows to the work_order_payment_item table
            for wo in unpaid_work_orders:
                amount = getattr(wo, amount_field, 0) or 0
                work_order_payment.append("work_order_payment_item", {
                    "work_order": wo.name,
                    "amount": amount
                })

                work_order_payment.work_order_payment_item.sort(key=lambda item: item.work_order)


            setattr(work_order_payment, contractor_type, contractor_value)

            # Store the total in the grand_total field
            work_order_payment.grand_total = total_amount
            work_order_payment.net_total = total_amount - total_amount * (work_order_payment.deduct_percentage / 100)

            print("\n\n\nwork_order_payment.net_total\n\n\n", work_order_payment.net_total)

            # Save and commit changes
            work_order_payment.save(ignore_permissions=True)
            frappe.db.commit()

            frappe.msgprint(f"Replaced existing Work Orders and added {len(unpaid_work_orders)} new Work Orders to Work Order Payment {docname}. Grand Total: {total_amount}")

    # Process for general contractor
    process_work_orders("custom_contractor", "custom_total_contract_operation_cost_exclude_stitch_and_pad", contractor, "contractor")

    # Process for stitching contractor
    process_work_orders("custom_stitching_contractor", "custom_stitch_operation_cost", stitching_contractor, "stitching_contractor")

    # Process for padding contractor
    process_work_orders("custom_padding_contractor", "custom_padding_operation_cost", padding_contractor, "padding_contractor")



@frappe.whitelist()
def get_unpaid_stock_entry(docname, from_date, to_date, contractor=None):
    print("\n\ncontractor\n\n", contractor)
    

    def process_stock_entry(contractor_field, amount_field, contractor_value, contractor_type):
        if contractor_value:
            unpaid_stock_entry = frappe.get_all(
                "Stock Entry",
                filters={
                    "custom_payment_status": ["!=", "Paid"],
                    "modified": ["between", [from_date, to_date]],
                    contractor_field: ["=", contractor_value]
                },
                fields=["name", "custom_total_contract_operation_cost"]
            )

            if not unpaid_stock_entry:
                frappe.msgprint(f"No unpaid Stock Entry found for {contractor_type} in the given date range.")
                return

            # Fetch the Work Order Payment document
            loading_and_unloading_payment = frappe.get_doc("Loading and Unloading Payments", docname)

            # Clear existing rows from work_order_payment_item table
            loading_and_unloading_payment.set("stock_entry_payment_item", [])

            total_amount = sum(getattr(se, amount_field, 0) or 0 for se in unpaid_stock_entry)

            # Append new rows to the work_order_payment_item table
            for se in unpaid_stock_entry:
                amount = getattr(se, amount_field, 0) or 0
                loading_and_unloading_payment.append("stock_entry_payment_item", {
                    "stock_entry": se.name,
                    "amount": amount
                })

            setattr(loading_and_unloading_payment, contractor_type, contractor_value)

            # Store the total in the grand_total field
            loading_and_unloading_payment.grand_total_for_stock_entry = total_amount
            loading_and_unloading_payment.net_total_for_stock_entry = total_amount - total_amount * (loading_and_unloading_payment.deduct_percentage / 100)

            print("\n\n\nstock_entry_payment.net_total\n\n\n", loading_and_unloading_payment.net_total_for_stock_entry)

            # Save and commit changes
            loading_and_unloading_payment.save(ignore_permissions=True)
            frappe.db.commit()

            frappe.msgprint(f"Replaced existing Stock Entry and added {len(unpaid_stock_entry)} new Loading and Unloading to Loading and Unloading Payment {docname}. Grand Total: {total_amount}")

    # Process for general contractor
    process_stock_entry("custom_contractor", "custom_total_contract_operation_cost", contractor, "contractor")



@frappe.whitelist()
def get_unpaid_purchase_receipt(docname, from_date, to_date, contractor=None):
    print("\n\ncontractor\n\n", contractor)
    

    def process_purchase_receipt(contractor_field, amount_field, contractor_value, contractor_type):
        if contractor_value:
            unpaid_purchase_receipt = frappe.get_all(
                "Purchase Receipt",
                filters={
                    "custom_payment_status": ["!=", "Paid"],
                    "modified": ["between", [from_date, to_date]],
                    contractor_field: ["=", contractor_value]
                },
                fields=["name", "custom_total_contract_operation_cost"]
            )

            if not unpaid_purchase_receipt:
                frappe.msgprint(f"No unpaid Purchase Receipt found for {contractor_type} in the given date range.")
                return

            # Fetch the Work Order Payment document
            loading_and_unloading_payment = frappe.get_doc("Loading and Unloading Payments", docname)

            # Clear existing rows from work_order_payment_item table
            loading_and_unloading_payment.set("purchase_receipt_payment_item", [])

            total_amount = sum(flt(getattr(pr, amount_field, 0)) for pr in unpaid_purchase_receipt)


            # Append new rows to the work_order_payment_item table
            for se in unpaid_purchase_receipt:
                amount = getattr(se, amount_field, 0) or 0
                loading_and_unloading_payment.append("purchase_receipt_payment_item", {
                    "purchase_receipt": se.name,
                    "amount": amount
                })

            setattr(loading_and_unloading_payment, contractor_type, contractor_value)

            # Store the total in the grand_total field
            loading_and_unloading_payment.grand_total_for_purchase_receipt = total_amount
            loading_and_unloading_payment.net_total_for_purchase_receipt = total_amount - total_amount * (loading_and_unloading_payment.deduct_percentage / 100)

            print("\n\n\nstock_entry_payment.net_total\n\n\n", loading_and_unloading_payment.net_total_for_purchase_receipt)

            # Save and commit changes
            loading_and_unloading_payment.save(ignore_permissions=True)
            frappe.db.commit()

            frappe.msgprint(f"Replaced existing Stock Entry and added {len(unpaid_purchase_receipt)} new Loading and Unloading to Loading and Unloading Payment {docname}. Grand Total: {total_amount}")

    # Process for general contractor
    process_purchase_receipt("custom_contractor", "custom_total_contract_operation_cost", contractor, "contractor")



@frappe.whitelist()
def get_unpaid_sales_invoice(docname, from_date, to_date, contractor=None):
    print("\n\ncontractor\n\n", contractor)
    

    def process_sales_invoice(contractor_field, amount_field, contractor_value, contractor_type):
        if contractor_value:
            unpaid_sales_invoice = frappe.get_all(
                "Sales Invoice",
                filters={
                    "custom_payment_status": ["!=", "Paid"],
                    "modified": ["between", [from_date, to_date]],
                    contractor_field: ["=", contractor_value]
                },
                fields=["name", "custom_total_contract_operation_cost"]
            )

            if not unpaid_sales_invoice:
                frappe.msgprint(f"No unpaid Sales Invoice found for {contractor_type} in the given date range.")
                return

            # Fetch the Work Order Payment document
            loading_and_unloading_payment = frappe.get_doc("Loading and Unloading Payments", docname)

            # Clear existing rows from work_order_payment_item table
            loading_and_unloading_payment.set("sales_invoice_payment_item", [])

            total_amount = sum(flt(getattr(pr, amount_field, 0)) for pr in unpaid_sales_invoice)


            # Append new rows to the work_order_payment_item table
            for se in unpaid_sales_invoice:
                amount = getattr(se, amount_field, 0) or 0
                loading_and_unloading_payment.append("sales_invoice_payment_item", {
                    "sales_invoice": se.name,
                    "amount": amount
                })

            setattr(loading_and_unloading_payment, contractor_type, contractor_value)

            # Store the total in the grand_total field
            loading_and_unloading_payment.grand_total_for_sales_invoice = total_amount
            loading_and_unloading_payment.net_total_for_sales_invoice = total_amount - total_amount * (loading_and_unloading_payment.deduct_percentage / 100)

            print("\n\n\nsales_invoice_payment.net_total\n\n\n", loading_and_unloading_payment.net_total_for_sales_invoice)

            # Save and commit changes
            loading_and_unloading_payment.save(ignore_permissions=True)
            frappe.db.commit()

            frappe.msgprint(f"Replaced existing Sales Invoice and added {len(unpaid_sales_invoice)} new Loading and Unloading to Loading and Unloading Payment {docname}. Grand Total: {total_amount}")

    # Process for general contractor
    process_sales_invoice("custom_contractor", "custom_total_contract_operation_cost", contractor, "contractor")

    


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


@frappe.whitelist()
def set_paid_status_to_work_orders(docname,custom_work_order_payments):
    print("\n\n\nset_paid_status_to_work_orders\n\n\n")

    # Fetch all work order names from "Work Order Payment Item" child table
    paid_work_orders = frappe.get_all(
        "Work Order Payment Item",
        filters={"parent": custom_work_order_payments},  # Filter by the given Work Order Payment document
        fields=["work_order"]
    )

    # Extract work order names into a list
    work_order_names = [wo["work_order"] for wo in paid_work_orders]

    print("\n\n\nwork_order_names\n\n\n",work_order_names)

    if work_order_names:
        # Update custom_payment_status to "Paid" for all fetched Work Orders
        frappe.db.set_value(
            "Work Order",
            {"name": ["in", work_order_names]},
            "custom_payment_status",
            "Paid"
        )

        # Commit the changes to the database
        frappe.db.commit()
        print(f"Updated {len(work_order_names)} Work Orders to 'Paid' status.")
    else:
        print("No Work Orders found in Work Order Payment Item.")

    return work_order_names  # Return updated work order names for reference




def every_five_minutes():
    print("\n\n\nevery_1_minutes\n\n\n")



@frappe.whitelist()
def create_jv_for_wo(docname):
    print("\n\ncreate_jv_for_wo\n\n")
    work_order_payment = frappe.get_doc("Work Order Payments", docname)
    print("\n\nwork_order_payment\n\n",work_order_payment.net_total)
    print("\n\nwork_order_payment\n\n",work_order_payment.grand_total)
    work_order_payment_bonus = work_order_payment.grand_total - work_order_payment.net_total
    print("\n\nwork_order_payment_bonus\n\n",work_order_payment_bonus)
    if work_order_payment.contractor:
        contractor = work_order_payment.contractor
        contractors = work_order_payment.contractor + ','+ work_order_payment.contractor + ' (Reserved)'
    if work_order_payment.stitching_contractor:
        contractor = work_order_payment.stitching_contractor
        contractors = work_order_payment.stitching_contractor + ','+ work_order_payment.stitching_contractor + ' (Reserved)'
    if work_order_payment.padding_contractor:
        contractor = work_order_payment.padding_contractor
        contractors = work_order_payment.padding_contractor + ','+ work_order_payment.padding_contractor + ' (Reserved)'
        
    # contractors = work_order_payment.contractor + ','+ work_order_payment.contractor + ' (Reserved)'
    # print("\n\n\ncontractors\n\n\n",contractors)
    doc=frappe.new_doc("Journal Entry")
    doc.workflow_state="Draft"
    doc.docstatus=0
    doc.voucher_type="Journal Entry"
    doc.ineligibility_reason="As per rules 42 & 43 of CGST Rules"
    doc.naming_series = "JV/24/.#"
    doc.company="Pranera Services and Solutions Pvt. Ltd.,"
    doc.posting_date = datetime.today().strftime("%Y-%m-%d")  # Assigns current date in "YYYY-MM-DD" format
    doc.apply_tds=0
    doc.write_off_based_on="Accounts Receivable"
    doc.write_off_amount=0.0
    doc.letter_head="CUSTOM__PSS JV_LOGO"
    doc.is_opening="No"
    doc.doctype="Journal Entry"
    doc.custom_work_order_payments = docname
    doc.append("accounts", {
        "docstatus": 0,
        "idx": 1,
        "account": "Loading Unloading Charges - PSS",
        "account_type": "",
        "party_type": "",
        "party": "",
        "cost_center": "Pranera Dyeing - PSS",
        "account_currency": "INR",
        "exchange_rate": 1.0,
        "debit_in_account_currency": 0.0,
        "credit": 0.0,
        "credit_in_account_currency": work_order_payment.grand_total,
        "debit": work_order_payment.grand_total,
        "is_advance": "No",
        "against_account": contractors,
        "parentfield": "accounts",
        "parenttype": "Journal Entry",
        "doctype": "Journal Entry Account"
    })

    doc.append("accounts", {
        "docstatus": 0,
        "idx": 2,
        "account": "Creditors - PSS",
        "account_type": "Payable",
        "party_type": "Supplier",
        "party": contractor + ' (Reserved)',
        "cost_center": "Pranera Dyeing - PSS",
        "account_currency": "INR",
        "exchange_rate": 1.0,
        "debit_in_account_currency": work_order_payment_bonus,
        "credit": work_order_payment_bonus,
        "credit_in_account_currency": 0.0,
        "debit": 0.0,
        "is_advance": "No",
        "against_account": "Loading Unloading Charges - PSS",
        "parentfield": "accounts",
        "parenttype": "Journal Entry",
        "doctype": "Journal Entry Account"
    })

    doc.append("accounts", {
        "docstatus": 0,
        "idx": 3,
        "account": "Creditors - PSS",
        "account_type": "Payable",
        "party_type": "Supplier",
        "party": contractor,
        "cost_center": "Pranera Dyeing - PSS",
        "account_currency": "INR",
        "exchange_rate": 1.0,
        "debit_in_account_currency": work_order_payment.net_total,
        "credit": work_order_payment.net_total,
        "credit_in_account_currency": 0.0,
        "debit": 0.0,
        "is_advance": "No",
        "against_account": "Loading Unloading Charges - PSS",
        "parentfield": "accounts",
        "parenttype": "Journal Entry",
        "doctype": "Journal Entry Account"
    })
    doc.save(ignore_permissions=True)
    frappe.msgprint("JV Created")





# {
#     "data": {
#         "docstatus": 0,
#         "idx": 0,
#         "workflow_state": "Draft",
#         "is_system_generated": 0,
#         "title": "Payroll Payable Account - PSS",
#         "voucher_type": "Journal Entry",
#         "ineligibility_reason": "As per rules 42 & 43 of CGST Rules",
#         "naming_series": "JV/24/.#",
#         "company": "Pranera Services and Solutions Pvt. Ltd.,",
#         "company_gstin": "",
#         "posting_date": "2025-02-10",
#         "apply_tds": 0,
#         "total_debit": 100.0,
#         "total_credit": 100.0,
#         "difference": 0.0,
#         "multi_currency": 0,
#         "total_amount": 0.0,
#         "total_amount_in_words": "INR Zero only.",
#         "acc_payye": "Yes",
#         "write_off_based_on": "Accounts Receivable",
#         "write_off_amount": 0.0,
#         "letter_head": "CUSTOM__PSS JV_LOGO",
#         "is_opening": "No",
#         "doctype": "Journal Entry",
#         "accounts": [
#             {
#                 "docstatus": 0,
#                 "idx": 1,
#                 "account": "Payroll Payable Account - PSS",
#                 "account_type": "",
#                 "party_type": "",
#                 "party": "",
#                 "cost_center": "HO - PSS",
#                 "account_currency": "INR",
#                 "exchange_rate": 1.0,
#                 "debit_in_account_currency": 0.0,
#                 "debit": 0.0,
#                 "credit_in_account_currency": 100.0,
#                 "credit": 100.0,
#                 "is_advance": "No",
#                 "against_account": "Loading Unloading Charges - PSS",
#                 "parentfield": "accounts",
#                 "parenttype": "Journal Entry",
#                 "doctype": "Journal Entry Account"
#             },
#             {
#                 "docstatus": 0,
#                 "idx": 2,
#                 "account": "Loading Unloading Charges - PSS",
#                 "account_type": "",
#                 "party_type": "",
#                 "party": "",
#                 "cost_center": "HO - PSS",
#                 "account_currency": "INR",
#                 "exchange_rate": 1.0,
#                 "debit_in_account_currency": 100.0,
#                 "debit": 100.0,
#                 "credit_in_account_currency": 0.0,
#                 "credit": 0.0,
#                 "is_advance": "No",
#                 "against_account": "Payroll Payable Account - PSS",
#                 "parentfield": "accounts",
#                 "parenttype": "Journal Entry",
#                 "doctype": "Journal Entry Account"
#             }
#         ]
#     }
# }







    





    
             
              
