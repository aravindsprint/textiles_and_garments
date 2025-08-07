# Copyright (c) 2025, Aravind and contributors
# For license information,please see license.txt


from collections import defaultdict
import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today
import logging
import os
from frappe.utils import get_site_path



def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    columns = get_columns(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {
            "label": _("S.No"),
            "fieldname": "s_no",
            "fieldtype": "Int",
            "width": 60,
        },
        {
            "label": _("Batch"),
            "fieldname": "batch",
            "fieldtype": "Link",
            "options": "Batch",
            "width": 120,
        },
        {
            "label": _("Source Document Type"),
            "fieldname": "doctype",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Source Document"),
            "fieldname": "doc_no",
            "fieldtype": "Dynamic Link",
            "options": "doctype",
            "width": 150,
        },
        {
            "label": _("Quality Inspection"),
            "fieldname": "qi_doc_no",
            "fieldtype": "Link",
            "options": "Quality Inspection",
            "width": 150,
        },
        {
            "label": _("View QI"),
            "fieldname": "link",
            "fieldtype": "Data",
            "width": 100,
        }
    ]
    return columns

def get_data(filters):
    if not filters.get("batch_no"):
        frappe.throw(_("Please select a Batch Number"))
    
    batch_no = filters.get("batch_no")
    sources = get_batch_source(batch_no)
    
    data = []
    for idx, source in enumerate(sources, 1):
        data.append({
            "s_no": idx,
            "batch": source["batch"],
            "doctype": source["doctype"],
            "doc_no": source["docname"],
            "qi_doc_no": source["qi_doc"],
            "link": source["link"]
        })
    
    return data

def get_batch_source(batch_no):
    """
    Trace the origin of a batch and return source documents with QI info
    """
    batches = []
    processed_batches = set()
    
    def _trace_batch(batch):
        if batch in processed_batches:
            return
        processed_batches.add(batch)
        
        batch_doc = frappe.get_doc("Batch", batch)
        source_docs = get_source_documents(batch)
        
        if not source_docs:
            # Assume it's a source batch from Purchase Receipt
            qi_doc = get_quality_inspection(batch)
            batches.append({
                "batch": batch,
                "doctype": "Purchase Receipt",
                "docname": None,
                "qi_doc": qi_doc.name if qi_doc else None,
                "link": get_link(qi_doc) if qi_doc else None
            })
            return
            
        for source in source_docs:
            if source.doctype in ["Purchase Receipt", "Stock Entry"]:
                if source.doctype == "Stock Entry" and source.purpose != "Material Receipt" or source.purpose != "Material Transfer" or source.purpose != "Material Transfer for Manufacture" or source.purpose != "Send to Subcontractor" or source.purpose != "Material Issue":
                    # For manufacture/repack, trace raw material batches
                    raw_material_batches = get_raw_material_batches(source.name)
                    for rm_batch in raw_material_batches:
                        _trace_batch(rm_batch)
                else:
                    # Source batch
                    qi_doc = get_quality_inspection(batch, source.doctype, source.name)
                    batches.append({
                        "batch": batch,
                        "doctype": source.doctype,
                        "docname": source.name,
                        "qi_doc": qi_doc.name if qi_doc else None,
                        "link": get_link(qi_doc) if qi_doc else None
                    })
            elif source.doctype == "Subcontracting Receipt":
                # Trace supplied raw materials
                supplied_batches = get_supplied_raw_material_batches(source.name)
                for s_batch in supplied_batches:
                    _trace_batch(s_batch)
    
    _trace_batch(batch_no)
    return batches

def get_source_documents(batch_no):
    """
    Get documents where this batch was created
    """
    source_docs = []
    
    # Check Purchase Receipt
    pr_list = frappe.get_all("Purchase Receipt Item", 
        filters={"batch_no": batch_no},
        fields=["parent as name"],
        distinct=True
    )
    for pr in pr_list:
        pr_doc = frappe.get_doc("Purchase Receipt", pr.name)
        source_docs.append(pr_doc)
    
    # Check Stock Entry
    se_list = frappe.get_all("Stock Entry Detail", 
        filters={"batch_no": batch_no, "t_warehouse": ["!=", ""]},
        fields=["parent as name"],
        distinct=True
    )
    for se in se_list:
        se_doc = frappe.get_doc("Stock Entry", se.name)
        source_docs.append(se_doc)
    
    # Check Subcontracting Receipt
    scr_list = frappe.get_all("Subcontracting Receipt Item", 
        filters={"batch_no": batch_no},
        fields=["parent as name"],
        distinct=True
    )
    for scr in scr_list:
        scr_doc = frappe.get_doc("Subcontracting Receipt", scr.name)
        source_docs.append(scr_doc)
    
    return source_docs

def get_raw_material_batches(stock_entry_name):
    """
    Get raw material batches used in a manufacture/repack stock entry
    """
    batches = []
    se_doc = frappe.get_doc("Stock Entry", stock_entry_name)
    for item in se_doc.items:
        if not item.t_warehouse and item.batch_no:  # Raw material used
            batches.append(item.batch_no)
    return batches

def get_supplied_raw_material_batches(subcontract_receipt_name):
    """
    Get batches of raw materials supplied for subcontracting
    """
    batches = []
    scr_doc = frappe.get_doc("Subcontracting Receipt", subcontract_receipt_name)
    for item in scr_doc.supplied_items:
        if item.batch_no:
            batches.append(item.batch_no)
    return batches

def get_quality_inspection(batch_no, doctype=None, docname=None):
    """
    Get Quality Inspection linked to batch or document
    """
    qi = None
    
    # First try to get QI linked directly to batch
    qi_list = frappe.get_all("Quality Inspection", 
        filters={"batch_no": batch_no},
        fields=["name"]
    )
    if qi_list:
        return frappe.get_doc("Quality Inspection", qi_list[0].name)
    
    # If not found, try to get QI linked to source document
    if doctype and docname:
        if doctype == "Purchase Receipt":
            # Check for QI in Purchase Receipt Items
            pr_items = frappe.get_all("Purchase Receipt Item",
                filters={"parent": docname, "batch_no": batch_no},
                fields=["quality_inspection"]
            )
            for item in pr_items:
                if item.quality_inspection:
                    return frappe.get_doc("Quality Inspection", item.quality_inspection)
                    
        elif doctype == "Stock Entry":
            se_doc = frappe.get_doc("Stock Entry", docname)
            for item in se_doc.items:
                if item.batch_no == batch_no and item.quality_inspection:
                    return frappe.get_doc("Quality Inspection", item.quality_inspection)
                    
        elif doctype == "Subcontracting Receipt":
            scr_doc = frappe.get_doc("Subcontracting Receipt", docname)
            for item in scr_doc.items:
                if item.batch_no == batch_no and item.quality_inspection:
                    return frappe.get_doc("Quality Inspection", item.quality_inspection)
    
    return None

def get_link(qi_doc):
    """
    Get link to view the QI document
    """
    if not qi_doc:
        return None
    return f"<a href='/app/quality-inspection/{qi_doc.name}' target='_blank'>View QI</a>"