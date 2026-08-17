# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RollWisePickOrder(Document):
    def validate(self):
        """Validate document before saving"""
        self.set_document_type()
        self.fetch_required_items()
        self.update_required_items_picked_qty()
        self.calculate_totals()
    
    def set_document_type(self):
        """Set document_type based on pick_type"""
        doc_type_map = {
            "From Work Order": "Work Order",
            "To Work Order": "Work Order",
            "From Purchase Order": "Purchase Order",
            "To Subcontracting Order": "Subcontracting Order",
            "From Subcontracting Order": "Subcontracting Order",
            "From Stock Entry": "Stock Entry"
        }
        
        if self.pick_type in doc_type_map:
            self.document_type = doc_type_map[self.pick_type]
    
    def fetch_required_items(self):
        """Fetch required items from source document"""
        if not self.document_name or not self.document_type:
            return
        
        # Only fetch if required_items is empty (to avoid overwriting)
        if self.required_items:
            return
        
        try:
            source_doc = frappe.get_doc(self.document_type, self.document_name)
            
            # Clear existing required items
            self.required_items = []
            
            if self.document_type == "Work Order":
                self.project = source_doc.project
                
                if self.pick_type == "To Work Order":
                    # Fetch required items (Raw Materials)
                    for item in source_doc.required_items:
                        self.append("required_items", {
                            "item_code": item.item_code,
                            "item_name": item.item_name,
                            "stock_uom": item.stock_uom,
                            "required_qty": item.required_qty,
                            "transferred_qty": item.transferred_qty or 0,
                            "remaining_qty": (item.required_qty or 0) - (item.transferred_qty or 0)
                        })
                    
                    # Set target warehouse (WIP warehouse)
                    if source_doc.wip_warehouse:
                        self.target_warehouse = source_doc.wip_warehouse
                
                elif self.pick_type == "From Work Order":
                    # Set source warehouse (FG warehouse)
                    if source_doc.fg_warehouse:
                        self.source_warehouse = source_doc.fg_warehouse
            
            elif self.document_type == "Purchase Order":
                if hasattr(source_doc, 'project'):
                    self.project = source_doc.project
                
                # Fetch items from Purchase Order
                for item in source_doc.items:
                    self.append("required_items", {
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "stock_uom": item.stock_uom,
                        "required_qty": item.qty,
                        "remaining_qty": item.qty
                    })
            
            elif self.document_type == "Subcontracting Order":
                if hasattr(source_doc, 'items') and source_doc.items:
                    self.project = source_doc.items[0].project
                
                if self.pick_type == "To Subcontracting Order":
                    # Fetch supplied items
                    for item in source_doc.supplied_items:
                        self.append("required_items", {
                            "item_code": item.rm_item_code,
                            "item_name": item.item_name,
                            "stock_uom": item.stock_uom,
                            "required_qty": item.required_qty,
                            "supplied_qty": item.supplied_qty or 0,
                            "remaining_qty": (item.required_qty or 0) - (item.supplied_qty or 0)
                        })
                    
                    # Set target warehouse (supplier warehouse)
                    if source_doc.supplier_warehouse:
                        self.target_warehouse = source_doc.supplier_warehouse
                
                elif self.pick_type == "From Subcontracting Order":
                    # Fetch main items
                    for item in source_doc.items:
                        self.append("required_items", {
                            "item_code": item.item_code,
                            "item_name": item.item_name,
                            "stock_uom": item.stock_uom,
                            "required_qty": item.qty,
                            "remaining_qty": item.qty
                        })
            
            elif self.document_type == "Stock Entry":
                # Fetch items from Stock Entry
                for item in source_doc.items:
                    self.append("required_items", {
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "stock_uom": item.stock_uom,
                        "required_qty": item.qty,
                        "remaining_qty": item.qty
                    })
        
        except Exception as e:
            frappe.throw(f"Error fetching document details: {str(e)}")
    
    def update_required_items_picked_qty(self):
        """Update picked_qty and remaining_qty in required_items"""
        
        # Create dict to sum picked quantities by item_code
        picked_map = {}
        
        # Sum from roll_wise_pick_item
        for roll in self.roll_wise_pick_item:
            if roll.item_code:
                picked_map[roll.item_code] = picked_map.get(roll.item_code, 0) + (roll.qty or 0)
        
        # Sum from batch_wise_pick_item
        for batch in self.batch_wise_pick_item:
            if batch.item_code:
                picked_map[batch.item_code] = picked_map.get(batch.item_code, 0) + (batch.qty or 0)
        
        # Update each required item
        for item in self.required_items:
            item.picked_qty = picked_map.get(item.item_code, 0)
            
            # Calculate remaining based on pick_type
            if self.pick_type in ["To Work Order"]:
                # For Work Orders: remaining = required - transferred - picked
                item.remaining_qty = (item.required_qty or 0) - (item.transferred_qty or 0) - (item.picked_qty or 0)
            
            elif self.pick_type in ["To Subcontracting Order"]:
                # For Subcontracting: remaining = required - supplied - picked
                item.remaining_qty = (item.required_qty or 0) - (item.supplied_qty or 0) - (item.picked_qty or 0)
            
            else:
                # For others: remaining = required - picked
                item.remaining_qty = (item.required_qty or 0) - (item.picked_qty or 0)
    
    def calculate_totals(self):
        """Calculate total quantity and total rolls"""
        total_qty = 0
        total_rolls = 0
        
        # Calculate from roll_wise_pick_item
        for roll in self.roll_wise_pick_item:
            total_qty += roll.qty or 0
            total_rolls += 1
        
        # Add batch_wise_pick_item
        for batch in self.batch_wise_pick_item:
            total_qty += batch.qty or 0
            total_rolls += 1
        
        self.total_qty = total_qty
        self.total_rolls = total_rolls
    
    def before_submit(self):
        """Validate before submission"""
        # Check if any rolls/batches are selected
        if not self.roll_wise_pick_item and not self.batch_wise_pick_item:
            frappe.throw("Please add at least one roll or batch before submitting")
        
        # Validate that all required items have been picked (optional validation)
        # for item in self.required_items:
        #     if item.remaining_qty > 0:
        #         frappe.msgprint(f"Warning: {item.item_code} still has {item.remaining_qty} {item.stock_uom} remaining", 
        #                       alert=True)
    
    def on_submit(self):
        """On submit, update status to Pending"""
        self.db_set('status', 'Pending')
    
    def on_cancel(self):
        """On cancel, update status to Cancelled"""
        self.db_set('status', 'Cancelled')


# API Methods for Ionic App Integration
@frappe.whitelist()
def get_pick_order_details(pick_order_name):
    """Get pick order details for mobile app"""
    try:
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        return {
            "success": True,
            "data": {
                "name": doc.name,
                "posting_date": doc.posting_date,
                "pick_type": doc.pick_type,
                "document_name": doc.document_name,
                "project": doc.project,
                "source_warehouse": doc.source_warehouse,
                "target_warehouse": doc.target_warehouse,
                "batch": doc.batch,
                "status": doc.status,
                "required_items": [
                    {
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "stock_uom": item.stock_uom,
                        "required_qty": item.required_qty,
                        "picked_qty": item.picked_qty,
                        "remaining_qty": item.remaining_qty
                    }
                    for item in doc.required_items
                ],
                "rolls": [
                    {
                        "roll_no": roll.roll_no,
                        "item_code": roll.item_code,
                        "warehouse": roll.warehouse,
                        "batch": roll.batch,
                        "qty": roll.qty,
                        "uom": roll.uom
                    }
                    for roll in doc.roll_wise_pick_item
                ],
                "batches": [
                    {
                        "batch": batch.batch,
                        "item_code": batch.item_code,
                        "warehouse": batch.warehouse,
                        "qty": batch.qty,
                        "uom": batch.uom
                    }
                    for batch in doc.batch_wise_pick_item
                ]
            }
        }
    except Exception as e:
        frappe.log_error(f"Error fetching pick order: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def update_pick_order_status(pick_order_name, status):
    """Update pick order status from mobile app"""
    try:
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Validate status transition
        valid_statuses = ["Draft", "Pending", "In Progress", "Completed", "Cancelled"]
        if status not in valid_statuses:
            frappe.throw(f"Invalid status: {status}")
        
        doc.status = status
        doc.save()
        
        return {
            "success": True,
            "message": f"Status updated to {status}"
        }
    except Exception as e:
        frappe.log_error(f"Error updating status: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def add_roll_to_pick_order(pick_order_name, roll_no):
    """Add roll to pick order from mobile app (barcode scanning)"""
    try:
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Check if already added
        for roll in doc.roll_wise_pick_item:
            if roll.roll_no == roll_no:
                return {
                    "success": False,
                    "message": "Roll already added to this pick order"
                }
        
        # Fetch roll details
        roll_doc = frappe.get_doc("Roll", roll_no)
        
        # Validate warehouse
        if doc.source_warehouse and roll_doc.warehouse != doc.source_warehouse:
            return {
                "success": False,
                "message": f"Roll is in {roll_doc.warehouse}, expected {doc.source_warehouse}"
            }
        
        # Validate batch if specified
        if doc.batch and roll_doc.batch != doc.batch:
            return {
                "success": False,
                "message": f"Roll batch {roll_doc.batch} doesn't match selected batch {doc.batch}"
            }
        
        # Add roll
        doc.append("roll_wise_pick_item", {
            "roll_no": roll_doc.name,
            "item_code": roll_doc.item_code,
            "warehouse": roll_doc.warehouse,
            "batch": roll_doc.batch,
            "qty": roll_doc.roll_weight,
            "uom": roll_doc.stock_uom
        })
        
        doc.save()
        
        return {
            "success": True,
            "message": "Roll added successfully",
            "data": {
                "roll_no": roll_doc.name,
                "item_code": roll_doc.item_code,
                "qty": roll_doc.roll_weight
            }
        }
    except Exception as e:
        frappe.log_error(f"Error adding roll: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }