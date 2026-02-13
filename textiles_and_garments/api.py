# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, today, nowdate
import json

# ==================== PICK ORDER LIST & DETAILS ====================

@frappe.whitelist()
def get_pick_orders(status=None, assigned_to=None):
    """
    Get pick orders for mobile app
    
    Args:
        status: Filter by status (Pending, In Progress, Completed, etc.)
        assigned_to: Filter by assigned user
    
    Returns:
        dict: Success status and list of pick orders
    """
    try:
        filters = {
            "docstatus": 1
        }
        
        # Add status filter
        if status and status != "all":
            filters["status"] = status
        else:
            # Default: show only Pending and In Progress
            filters["status"] = ["in", ["Pending", "In Progress"]]
        
        # Add assigned_to filter
        if assigned_to:
            filters["assigned_to"] = assigned_to
        
        # Get pick orders
        pick_orders = frappe.get_all(
            "Roll Wise Pick Order",
            filters=filters,
            fields=[
                "name", "posting_date", "status", "pick_type", 
                "document_type", "document_name", "project", 
                "source_warehouse", "target_warehouse", "batch", 
                "total_qty", "total_rolls", "assigned_to",
                "company", "remarks", "creation", "modified"
            ],
            order_by="posting_date desc, modified desc",
            limit=100
        )
        
        return {
            "success": True,
            "message": pick_orders,
            "count": len(pick_orders)
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_pick_orders: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def get_pick_order_details(pick_order_name):
    """
    Get complete pick order details including required items and picked rolls
    
    Args:
        pick_order_name: Name of the Roll Wise Pick Order document
    
    Returns:
        dict: Complete pick order data
    """
    try:
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Check permissions
        if not doc.has_permission("read"):
            frappe.throw(_("You don't have permission to view this pick order"))
        
        return {
            "success": True,
            "data": {
                "name": doc.name,
                "posting_date": doc.posting_date,
                "status": doc.status,
                "pick_type": doc.pick_type,
                "document_type": doc.document_type,
                "document_name": doc.document_name,
                "project": doc.project,
                "source_warehouse": doc.source_warehouse,
                "target_warehouse": doc.target_warehouse,
                "batch": doc.batch,
                "total_qty": doc.total_qty,
                "total_rolls": doc.total_rolls,
                "assigned_to": doc.assigned_to,
                "company": doc.company,
                "remarks": doc.remarks,
                "from_work_order": doc.from_work_order,
                "from_subcontracting_order": doc.from_subcontracting_order,
                "required_items": [
                    {
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "stock_uom": item.stock_uom,
                        "required_qty": flt(item.required_qty, 2),
                        "transferred_qty": flt(item.transferred_qty or 0, 2),
                        "supplied_qty": flt(item.supplied_qty or 0, 2),
                        "picked_qty": flt(item.picked_qty or 0, 2),
                        "remaining_qty": flt(item.remaining_qty or 0, 2)
                    }
                    for item in doc.required_items
                ],
                "rolls": [
                    {
                        "roll_no": roll.roll_no,
                        "item_code": roll.item_code,
                        "warehouse": roll.warehouse,
                        "batch": roll.batch,
                        "qty": flt(roll.qty, 2),
                        "uom": roll.uom
                    }
                    for roll in doc.roll_wise_pick_item
                ],
                "batches": [
                    {
                        "batch": batch.batch,
                        "item_code": batch.item_code,
                        "warehouse": batch.warehouse,
                        "qty": flt(batch.qty, 2),
                        "uom": batch.uom
                    }
                    for batch in doc.batch_wise_pick_item
                ]
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_pick_order_details: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }


# ==================== ROLL MANAGEMENT ====================

@frappe.whitelist()
def get_rolls_by_filters(filters):
    """
    Get rolls filtered by warehouse, batch, item, etc.
    
    Args:
        filters: JSON string or dict with filter conditions
    
    Returns:
        dict: List of matching rolls
    """
    try:
        # Parse filters if string
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        # Build query filters
        roll_filters = {}
        
        if filters.get("warehouse"):
            roll_filters["warehouse"] = filters["warehouse"]
        
        if filters.get("batch"):
            roll_filters["batch"] = filters["batch"]
        
        if filters.get("item_code"):
            roll_filters["item_code"] = filters["item_code"]
        
        # Get rolls
        rolls = frappe.get_all(
            "Roll",
            filters=roll_filters,
            fields=[
                "name", "roll_no", "item_code", "warehouse", 
                "batch", "roll_weight", "stock_uom", "status"
            ],
            order_by="creation desc",
            limit=500
        )
        
        return {
            "success": True,
            "message": rolls,
            "count": len(rolls)
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_rolls_by_filters: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def validate_roll_for_pick_order(pick_order_name, roll_no):
    """
    Validate if a roll can be added to pick order
    
    Args:
        pick_order_name: Name of the pick order
        roll_no: Roll number to validate
    
    Returns:
        dict: Validation result with roll details
    """
    try:
        # Get pick order
        pick_order = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Get roll details
        roll = frappe.get_doc("Roll", roll_no)
        
        # Validations
        errors = []
        
        # Check warehouse
        if pick_order.source_warehouse and roll.warehouse != pick_order.source_warehouse:
            errors.append(f"Roll is in {roll.warehouse}, expected {pick_order.source_warehouse}")
        
        # Check batch if specified
        if pick_order.batch and roll.batch != pick_order.batch:
            errors.append(f"Roll batch {roll.batch} doesn't match {pick_order.batch}")
        
        # Check if already added
        for existing_roll in pick_order.roll_wise_pick_item:
            if existing_roll.roll_no == roll_no:
                errors.append("Roll already added to this pick order")
                break
        
        # Check roll status
        if hasattr(roll, 'status') and roll.status not in ['Active', 'Available', '']:
            errors.append(f"Roll status is {roll.status}")
        
        if errors:
            return {
                "success": False,
                "message": "\n".join(errors),
                "roll_data": None
            }
        
        return {
            "success": True,
            "message": "Roll is valid",
            "roll_data": {
                "roll_no": roll.name,
                "item_code": roll.item_code,
                "warehouse": roll.warehouse,
                "batch": roll.batch,
                "qty": roll.roll_weight,
                "uom": roll.stock_uom
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in validate_roll_for_pick_order: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e),
            "roll_data": None
        }


@frappe.whitelist()
def add_roll_to_pick_order(pick_order_name, roll_no):
    """
    Add a roll to pick order after validation
    
    Args:
        pick_order_name: Name of the pick order
        roll_no: Roll number to add
    
    Returns:
        dict: Success status and updated pick order data
    """
    try:
        # Validate roll first
        validation = validate_roll_for_pick_order(pick_order_name, roll_no)
        
        if not validation["success"]:
            return validation
        
        # Get pick order
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Add roll
        roll_data = validation["roll_data"]
        doc.append("roll_wise_pick_item", {
            "roll_no": roll_data["roll_no"],
            "item_code": roll_data["item_code"],
            "warehouse": roll_data["warehouse"],
            "batch": roll_data["batch"],
            "qty": roll_data["qty"],
            "uom": roll_data["uom"]
        })
        
        doc.save()
        
        return {
            "success": True,
            "message": f"Roll {roll_no} added successfully",
            "data": {
                "total_qty": doc.total_qty,
                "total_rolls": doc.total_rolls
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in add_roll_to_pick_order: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def update_pick_order_rolls(pick_order_name, rolls):
    """
    Update all rolls in pick order (replace existing)
    
    Args:
        pick_order_name: Name of the pick order
        rolls: JSON string or list of roll data
    
    Returns:
        dict: Success status
    """
    try:
        # Parse rolls if string
        if isinstance(rolls, str):
            rolls = json.loads(rolls)
        
        # Get pick order
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Clear existing rolls
        doc.roll_wise_pick_item = []
        
        # Add new rolls
        for roll in rolls:
            doc.append("roll_wise_pick_item", {
                "roll_no": roll.get("roll_no"),
                "item_code": roll.get("item_code"),
                "warehouse": roll.get("warehouse"),
                "batch": roll.get("batch"),
                "qty": flt(roll.get("qty")),
                "uom": roll.get("uom")
            })
        
        doc.save()
        
        return {
            "success": True,
            "message": "Rolls updated successfully",
            "data": {
                "total_qty": doc.total_qty,
                "total_rolls": doc.total_rolls
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in update_pick_order_rolls: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }


# ==================== STATUS MANAGEMENT ====================

@frappe.whitelist()
def update_pick_order_status(pick_order_name, status):
    """
    Update pick order status
    
    Args:
        pick_order_name: Name of the pick order
        status: New status (Pending, In Progress, Completed, Cancelled)
    
    Returns:
        dict: Success status
    """
    try:
        # Validate status
        valid_statuses = ["Draft", "Pending", "In Progress", "Completed", "Cancelled"]
        if status not in valid_statuses:
            frappe.throw(f"Invalid status: {status}. Must be one of {', '.join(valid_statuses)}")
        
        # Get and update document
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Check permissions
        if not doc.has_permission("write"):
            frappe.throw(_("You don't have permission to update this pick order"))
        
        old_status = doc.status
        doc.status = status
        doc.save()
        
        return {
            "success": True,
            "message": f"Status updated from {old_status} to {status}",
            "old_status": old_status,
            "new_status": status
        }
        
    except Exception as e:
        frappe.log_error(f"Error in update_pick_order_status: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def start_picking(pick_order_name):
    """
    Start picking - update status to In Progress
    
    Args:
        pick_order_name: Name of the pick order
    
    Returns:
        dict: Success status
    """
    return update_pick_order_status(pick_order_name, "In Progress")


# ==================== STOCK ENTRY CREATION ====================

@frappe.whitelist()
def create_stock_entry_from_pick_order(pick_order_name, submit=False):
    """
    Create Stock Entry from Pick Order without completing it
    
    Args:
        pick_order_name: Name of the pick order
        submit: Whether to submit the stock entry (default: False)
    
    Returns:
        dict: Success status and stock entry name
    """
    try:
        # Get pick order
        pick_order = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Validate pick order has items
        if not pick_order.roll_wise_pick_item and not pick_order.batch_wise_pick_item:
            return {
                "success": False,
                "message": "No rolls or batches selected in pick order"
            }
        
        # Determine stock entry type based on pick type
        stock_entry_type = get_stock_entry_type(pick_order.pick_type)
        
        # Create Stock Entry
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = stock_entry_type
        stock_entry.posting_date = pick_order.posting_date or today()
        stock_entry.company = pick_order.company
        
        # Set custom field reference (if it exists)
        if hasattr(stock_entry, 'custom_roll_pick_order'):
            stock_entry.custom_roll_pick_order = pick_order.name
        
        # Set work order reference if applicable
        if pick_order.pick_type in ["To Work Order", "From Work Order"] and pick_order.document_name:
            stock_entry.work_order = pick_order.document_name
        
        # Set purchase order reference if applicable
        if pick_order.pick_type == "From Purchase Order" and pick_order.document_name:
            stock_entry.purchase_order = pick_order.document_name
        
        # Set subcontracting order reference if applicable
        if pick_order.pick_type in ["To Subcontracting Order", "From Subcontracting Order"]:
            if hasattr(stock_entry, 'subcontracting_order'):
                stock_entry.subcontracting_order = pick_order.document_name
        
        # Add items from roll_wise_pick_item
        for roll in pick_order.roll_wise_pick_item:
            stock_entry.append("items", {
                "item_code": roll.item_code,
                "qty": flt(roll.qty),
                "uom": roll.uom,
                "s_warehouse": pick_order.source_warehouse,
                "t_warehouse": pick_order.target_warehouse,
                "batch_no": roll.batch,
                "custom_roll_no": roll.roll_no if hasattr(stock_entry.items[0], 'custom_roll_no') else None
            })
        
        # Add items from batch_wise_pick_item
        for batch in pick_order.batch_wise_pick_item:
            stock_entry.append("items", {
                "item_code": batch.item_code,
                "qty": flt(batch.qty),
                "uom": batch.uom,
                "s_warehouse": pick_order.source_warehouse,
                "t_warehouse": pick_order.target_warehouse,
                "batch_no": batch.batch
            })
        
        # Set from/to warehouse at header level
        stock_entry.from_warehouse = pick_order.source_warehouse
        stock_entry.to_warehouse = pick_order.target_warehouse
        
        # Add remarks
        stock_entry.remarks = f"Created from Roll Wise Pick Order: {pick_order.name}"
        if pick_order.remarks:
            stock_entry.remarks += f"\n{pick_order.remarks}"
        
        # Insert stock entry
        stock_entry.insert()
        
        # Submit if requested
        if submit:
            stock_entry.submit()
        
        return {
            "success": True,
            "message": f"Stock Entry {'submitted' if submit else 'created'} successfully",
            "stock_entry": stock_entry.name,
            "submitted": submit
        }
        
    except Exception as e:
        frappe.log_error(f"Error creating stock entry: {str(e)}", "API Error")
        frappe.db.rollback()
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def complete_pick_order(pick_order_name, rolls=None):
    """
    Complete pick order by creating and submitting stock entry
    
    Args:
        pick_order_name: Name of the pick order
        rolls: Optional - update rolls before completing
    
    Returns:
        dict: Success status and stock entry name
    """
    try:
        # Update rolls if provided
        if rolls:
            update_result = update_pick_order_rolls(pick_order_name, rolls)
            if not update_result.get("success"):
                return update_result
        
        # Get pick order
        pick_order = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Validate has items
        if not pick_order.roll_wise_pick_item and not pick_order.batch_wise_pick_item:
            return {
                "success": False,
                "message": "Cannot complete pick order without any rolls or batches"
            }
        
        # Create and submit stock entry
        result = create_stock_entry_from_pick_order(pick_order_name, submit=True)
        
        if result.get("success"):
            # Update pick order status to Completed
            pick_order.status = "Completed"
            pick_order.save()
            
            result["message"] = "Pick order completed successfully"
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Error completing pick order: {str(e)}", "API Error")
        frappe.db.rollback()
        return {
            "success": False,
            "message": str(e)
        }


# ==================== UTILITY FUNCTIONS ====================

def get_stock_entry_type(pick_type):
    """
    Get appropriate stock entry type based on pick type
    
    Args:
        pick_type: Pick type from Roll Wise Pick Order
    
    Returns:
        str: Stock Entry Type
    """
    stock_entry_type_map = {
        "From Work Order": "Manufacture",
        "To Work Order": "Material Transfer for Manufacture",
        "From Purchase Order": "Material Receipt",
        "To Subcontracting Order": "Send to Subcontractor",
        "From Subcontracting Order": "Material Receipt",
        "From Stock Entry": "Material Transfer",
        "From Batch": "Material Transfer",
        "Manual Roll Pick": "Material Transfer"
    }
    
    return stock_entry_type_map.get(pick_type, "Material Transfer")


@frappe.whitelist()
def get_pick_order_summary(pick_order_name):
    """
    Get summary statistics for a pick order
    
    Args:
        pick_order_name: Name of the pick order
    
    Returns:
        dict: Summary statistics
    """
    try:
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Calculate statistics
        total_required = sum([flt(item.required_qty) for item in doc.required_items])
        total_picked = sum([flt(item.picked_qty) for item in doc.required_items])
        total_remaining = sum([flt(item.remaining_qty) for item in doc.required_items])
        
        completion_percentage = 0
        if total_required > 0:
            completion_percentage = (total_picked / total_required) * 100
        
        return {
            "success": True,
            "data": {
                "pick_order": pick_order_name,
                "status": doc.status,
                "total_rolls": doc.total_rolls or 0,
                "total_weight": doc.total_qty or 0,
                "total_required": total_required,
                "total_picked": total_picked,
                "total_remaining": total_remaining,
                "completion_percentage": round(completion_percentage, 2),
                "items_count": len(doc.required_items),
                "fully_picked_items": len([i for i in doc.required_items if flt(i.remaining_qty) <= 0])
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_pick_order_summary: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def cancel_pick_order(pick_order_name, reason=None):
    """
    Cancel a pick order
    
    Args:
        pick_order_name: Name of the pick order
        reason: Cancellation reason
    
    Returns:
        dict: Success status
    """
    try:
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Check if already completed
        if doc.status == "Completed":
            return {
                "success": False,
                "message": "Cannot cancel a completed pick order"
            }
        
        # Check permissions
        if not doc.has_permission("cancel"):
            frappe.throw(_("You don't have permission to cancel this pick order"))
        
        # Update status
        doc.status = "Cancelled"
        if reason:
            doc.remarks = f"{doc.remarks or ''}\nCancellation Reason: {reason}".strip()
        doc.save()
        
        return {
            "success": True,
            "message": "Pick order cancelled successfully"
        }
        
    except Exception as e:
        frappe.log_error(f"Error cancelling pick order: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }


# ==================== BATCH OPERATIONS ====================

@frappe.whitelist()
def get_available_batches(warehouse=None, item_code=None, project=None):
    """
    Get available batches for selection
    
    Args:
        warehouse: Filter by warehouse
        item_code: Filter by item code
        project: Filter by project
    
    Returns:
        dict: List of available batches
    """
    try:
        filters = {}
        
        if warehouse:
            filters["warehouse"] = warehouse
        
        if item_code:
            filters["item"] = item_code
        
        if project and frappe.db.has_column("Batch", "custom_project"):
            filters["custom_project"] = project
        
        batches = frappe.get_all(
            "Batch",
            filters=filters,
            fields=["name", "batch_id", "item", "batch_qty"],
            order_by="creation desc",
            limit=100
        )
        
        return {
            "success": True,
            "data": batches,
            "count": len(batches)
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_available_batches: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }
