# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

from collections import defaultdict
import frappe
from frappe import _
from frappe.utils import flt, today

# Initialize logger
batch_logger = frappe.logger("batch_sourcing", allow_site=True, file_count=5)
batch_logger.setLevel(frappe.log_level or "INFO")

def execute(filters=None):
    """Main report execution function"""
    batch_logger.info("Report execution started")
    columns, data = [], []
    
    try:
        data = get_data(filters)
        columns = get_columns(filters)
        batch_logger.info(f"Report generated with {len(data)} rows")
    except Exception as e:
        batch_logger.error(f"Error in execute: {str(e)}", exc_info=True)
        frappe.throw(_("Error generating report. Please check logs for details."))
    
    return columns, data

def get_columns(filters):
    """Define report columns"""
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
    batch_logger.debug("Columns definition prepared")
    return columns

def get_data(filters):
    """Get report data"""
    batch_logger.debug(f"Processing with filters: {filters}")
    
    if not filters.get("batch_no"):
        batch_logger.error("No batch number provided in filters")
        frappe.throw(_("Please select a Batch Number"))
    
    batch_no = filters.get("batch_no")
    batch_logger.info(f"Starting batch trace for: {batch_no}")
    
    try:
        sources = get_batch_source(batch_no)
    except Exception as e:
        batch_logger.error(f"Error tracing batch {batch_no}: {str(e)}", exc_info=True)
        raise
    
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
    
    batch_logger.info(f"Completed trace for {batch_no}. Found {len(sources)} sources")
    return data

def get_batch_source(batch_no):
    """Trace the origin of a batch and return source documents with QI info"""
    batches = []
    processed_batches = set()
    
    def _trace_batch(batch):
        if batch in processed_batches:
            batch_logger.debug(f"Skipping already processed batch: {batch}")
            return
            
        processed_batches.add(batch)
        batch_logger.info(f"Processing batch: {batch}")
        
        try:
            batch_doc = frappe.get_doc("Batch", batch)
            source_docs = get_source_documents(batch)
            batch_logger.info(f"Found {len(source_docs)} source documents for {batch}")
            
            if not source_docs:
                batch_logger.info(f"No source docs found - treating as source batch: {batch}")
                qi_doc = get_quality_inspection(batch)
                batch_data = {
                    "batch": batch,
                    "doctype": "Purchase Receipt",
                    "docname": None,
                    "qi_doc": qi_doc.name if qi_doc else None,
                    "link": get_link(qi_doc) if qi_doc else None
                }
                batches.append(batch_data)
                batch_logger.debug(f"Added source batch: {batch_data}")
                return
                
            for source in source_docs:
                batch_logger.debug(f"Processing source: {source.doctype} {source.name}")
                
                if source.doctype in ["Purchase Receipt", "Stock Entry"]:
                    if source.doctype == "Stock Entry" and source.purpose not in [
                        "Material Receipt", "Material Transfer", 
                        "Material Transfer for Manufacture", 
                        "Send to Subcontractor", "Material Issue"
                    ]:
                        batch_logger.info(f"Tracing raw materials from {source.name}")
                        raw_material_batches = get_raw_material_batches(source.name)
                        batch_logger.info(f"Found raw material batches: {raw_material_batches}")
                        
                        for rm_batch in raw_material_batches:
                            batch_logger.debug(f"Tracing raw material: {rm_batch}")
                            _trace_batch(rm_batch)
                    else:
                        qi_doc = get_quality_inspection(batch, source.doctype, source.name)
                        batch_data = {
                            "batch": batch,
                            "doctype": source.doctype,
                            "docname": source.name,
                            "qi_doc": qi_doc.name if qi_doc else None,
                            "link": get_link(qi_doc) if qi_doc else None
                        }
                        batches.append(batch_data)
                        batch_logger.debug(f"Added batch data: {batch_data}")
                        
                elif source.doctype == "Subcontracting Receipt":
                    batch_logger.info(f"Processing subcontract: {source.name}")
                    supplied_batches = get_supplied_raw_material_batches(source.name)
                    batch_logger.info(f"Found supplied batches: {supplied_batches}")
                    
                    for s_batch in supplied_batches:
                        batch_logger.debug(f"Tracing supplied batch: {s_batch}")
                        _trace_batch(s_batch)
                        
        except Exception as e:
            batch_logger.error(f"Error tracing batch {batch}: {str(e)}", exc_info=True)
            raise
    
    _trace_batch(batch_no)
    batch_logger.info(f"Completed tracing. Total batches: {len(batches)}")
    return batches

def get_source_documents(batch_no):
    """Get documents where this batch was created"""
    batch_logger.debug(f"Getting source docs for batch: {batch_no}")
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
    
    batch_logger.debug(f"Found {len(source_docs)} source documents")
    return source_docs

def get_raw_material_batches(stock_entry_name):
    """Get raw material batches used in manufacture/repack"""
    batch_logger.debug(f"Getting raw materials from: {stock_entry_name}")
    batches = []
    se_doc = frappe.get_doc("Stock Entry", stock_entry_name)
    
    for item in se_doc.items:
        if not item.t_warehouse and item.batch_no:
            batches.append(item.batch_no)
    
    batch_logger.debug(f"Found raw material batches: {batches}")
    return batches

def get_supplied_raw_material_batches(subcontract_receipt_name):
    """Get batches of raw materials supplied for subcontracting"""
    batch_logger.debug(f"Getting supplied batches from: {subcontract_receipt_name}")
    batches = []
    scr_doc = frappe.get_doc("Subcontracting Receipt", subcontract_receipt_name)
    
    for item in scr_doc.supplied_items:
        if item.batch_no:
            batches.append(item.batch_no)
    
    batch_logger.debug(f"Found supplied batches: {batches}")
    return batches

def get_quality_inspection(batch_no, doctype=None, docname=None):
    """Get Quality Inspection linked to batch or document"""
    batch_logger.debug(f"Getting QI for {batch_no}, {doctype}, {docname}")
    
    # First try direct batch link
    qi_list = frappe.get_all("Quality Inspection", 
        filters={"batch_no": batch_no},
        fields=["name"]
    )
    if qi_list:
        batch_logger.debug(f"Found direct QI link: {qi_list[0].name}")
        return frappe.get_doc("Quality Inspection", qi_list[0].name)
    
    # Check document items if provided
    if doctype and docname:
        if doctype == "Purchase Receipt":
            pr_items = frappe.get_all("Purchase Receipt Item",
                filters={"parent": docname, "batch_no": batch_no},
                fields=["quality_inspection"]
            )
            for item in pr_items:
                if item.quality_inspection:
                    batch_logger.debug(f"Found QI in PR item: {item.quality_inspection}")
                    return frappe.get_doc("Quality Inspection", item.quality_inspection)
                    
        elif doctype == "Stock Entry":
            se_doc = frappe.get_doc("Stock Entry", docname)
            for item in se_doc.items:
                if item.batch_no == batch_no and item.quality_inspection:
                    batch_logger.debug(f"Found QI in SE item: {item.quality_inspection}")
                    return frappe.get_doc("Quality Inspection", item.quality_inspection)
                    
        elif doctype == "Subcontracting Receipt":
            scr_doc = frappe.get_doc("Subcontracting Receipt", docname)
            for item in scr_doc.items:
                if item.batch_no == batch_no and item.quality_inspection:
                    batch_logger.debug(f"Found QI in SCR item: {item.quality_inspection}")
                    return frappe.get_doc("Quality Inspection", item.quality_inspection)
    
    batch_logger.debug("No QI found")
    return None

def get_link(qi_doc):
    """Get link to view QI document"""
    if not qi_doc:
        return None
    return f"<a href='/app/quality-inspection/{qi_doc.name}' target='_blank'>View QI</a>"