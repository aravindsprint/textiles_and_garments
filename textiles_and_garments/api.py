# -*- coding: utf-8 -*-
# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, today, nowdate, cint
import json

# ==================== SECURITY HELPER FUNCTIONS ====================

def check_role_permission(roles):
    """Check if user has any of the required roles"""
    user_roles = frappe.get_roles(frappe.session.user)
    return any(role in user_roles for role in roles)

def can_access_pick_orders():
    """Check if user can access pick order APIs"""
    allowed_roles = [
        'System Manager',
        'Stock Manager', 
        'Stock User',
        'Manufacturing Manager',
        'Manufacturing User'
    ]
    return check_role_permission(allowed_roles)

def filter_pick_orders_by_user(filters):
    """Apply user-based filtering for pick orders"""
    user = frappe.session.user
    
    # System Manager and Stock Manager can see all
    if check_role_permission(['System Manager', 'Stock Manager', 'Manufacturing Manager']):
        return filters
    
    # Stock User - filter by warehouse permissions or assigned_to
    if 'Stock User' in frappe.get_roles(user):
        # Get user's warehouse permissions
        user_warehouses = frappe.get_all(
            'User Permission',
            filters={
                'user': user,
                'allow': 'Warehouse'
            },
            pluck='for_value'
        )
        
        if user_warehouses:
            # User can see pick orders for their warehouses or assigned to them
            filters['source_warehouse'] = ['in', user_warehouses]
        else:
            # If no warehouse permissions, only see assigned pick orders
            filters['assigned_to'] = user
    
    return filters

# ==================== PICK ORDER LIST & DETAILS ====================

@frappe.whitelist()
def get_pick_orders(status=None, assigned_to=None):
    """
    Get pick orders for mobile app with security filtering
    
    Args:
        status: Optional status filter (Pending, In Progress, Completed)
        assigned_to: Optional user filter
        
    Returns:
        dict: {success: bool, data: list, count: int}
    """
    try:
        # Security check
        if not can_access_pick_orders():
            frappe.throw(_("You don't have permission to access Pick Orders"), frappe.PermissionError)
        
        # Base filters
        filters = {
            'docstatus': 1  # Only submitted documents
        }
        
        # Apply optional filters
        if status:
            filters['status'] = status
        if assigned_to:
            filters['assigned_to'] = assigned_to
        
        # Apply user-based filtering
        filters = filter_pick_orders_by_user(filters)
        
        # Fetch pick orders
        pick_orders = frappe.get_all(
            'Roll Wise Pick Order',
            filters=filters,
            fields=[
                'name', 'posting_date', 'pick_type', 'document_name',
                'project', 'status', 'source_warehouse', 'target_warehouse',
                'batch', 'total_qty', 'total_rolls', 'assigned_to', 'creation'
            ],
            order_by='creation desc',
            limit=100
        )
        
        return {
            "success": True,
            "data": pick_orders,
            "count": len(pick_orders)
        }
    
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"Error fetching pick orders: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e),
            "data": [],
            "count": 0
        }

@frappe.whitelist()
def get_pick_order_details(pick_order_name):
    """
    Get detailed pick order information for mobile app
    
    Args:
        pick_order_name: Name of the pick order document
        
    Returns:
        dict: {success: bool, data: dict}
    """
    try:
        # Get document with permission check
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Check read permission
        if not doc.has_permission("read"):
            frappe.throw(_("You don't have permission to view this Pick Order"), frappe.PermissionError)
        
        return {
            "success": True,
            "data": {
                "name": doc.name,
                "posting_date": doc.posting_date,
                "pick_type": doc.pick_type,
                "document_type": doc.document_type,
                "document_name": doc.document_name,
                "project": doc.project,
                "production_item": doc.production_item if hasattr(doc, 'production_item') else None,
                "source_warehouse": doc.source_warehouse,
                "target_warehouse": doc.target_warehouse,
                "batch": doc.batch,
                "status": doc.status,
                "total_qty": doc.total_qty,
                "total_rolls": doc.total_rolls,
                "assigned_to": doc.assigned_to,
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
    
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"Error fetching pick order details: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }

# ==================== ROLL OPERATIONS ====================

@frappe.whitelist()
def get_rolls_by_filters(filters):
    """
    Get rolls filtered by warehouse, batch, item, etc.
    
    Args:
        filters: JSON string of filters {warehouse, batch, item_code, etc.}
        
    Returns:
        dict: {success: bool, data: list}
    """
    try:
        # Parse filters
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        # Fetch rolls
        rolls = frappe.get_all(
            'Roll',
            filters=filters,
            fields=['name', 'item_code', 'batch', 'roll_weight', 'stock_uom', 'warehouse'],
            limit=100
        )
        
        return {
            "success": True,
            "data": rolls,
            "count": len(rolls)
        }
    
    except Exception as e:
        frappe.log_error(f"Error fetching rolls: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e),
            "data": []
        }

@frappe.whitelist()
def validate_roll_for_pick_order(pick_order_name, roll_no):
    """
    Validate if a roll can be added to pick order
    
    Args:
        pick_order_name: Pick order name
        roll_no: Roll number to validate
        
    Returns:
        dict: {success: bool, message: str, data: dict}
    """
    try:
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Check permission
        if not doc.has_permission("write"):
            frappe.throw(_("You don't have permission to modify this Pick Order"), frappe.PermissionError)
        
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
        
        return {
            "success": True,
            "message": "Roll can be added",
            "data": {
                "roll_no": roll_doc.name,
                "item_code": roll_doc.item_code,
                "batch": roll_doc.batch,
                "qty": roll_doc.roll_weight,
                "uom": roll_doc.stock_uom
            }
        }
    
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"Error validating roll: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }

@frappe.whitelist()
def add_roll_to_pick_order(pick_order_name, roll_no):
    """
    Add roll to pick order from mobile app (barcode scanning)
    
    Args:
        pick_order_name: Pick order name
        roll_no: Roll number to add
        
    Returns:
        dict: {success: bool, message: str, data: dict}
    """
    try:
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Check permission
        if not doc.has_permission("write"):
            frappe.throw(_("You don't have permission to modify this Pick Order"), frappe.PermissionError)
        
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
    
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"Error adding roll: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }

@frappe.whitelist()
def update_pick_order_rolls(pick_order_name, rolls):
    """
    Update all rolls in pick order (bulk update from mobile)
    
    Args:
        pick_order_name: Pick order name
        rolls: JSON string array of roll data
        
    Returns:
        dict: {success: bool, message: str}
    """
    try:
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Check permission
        if not doc.has_permission("write"):
            frappe.throw(_("You don't have permission to modify this Pick Order"), frappe.PermissionError)
        
        # Parse rolls
        if isinstance(rolls, str):
            rolls = json.loads(rolls)
        
        # Clear existing rolls
        doc.roll_wise_pick_item = []
        
        # Add new rolls
        for roll_data in rolls:
            doc.append("roll_wise_pick_item", roll_data)
        
        doc.save()
        
        return {
            "success": True,
            "message": f"Updated {len(rolls)} rolls"
        }
    
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"Error updating rolls: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }

# ==================== STATUS MANAGEMENT ====================

@frappe.whitelist()
def update_pick_order_status(pick_order_name, status):
    """
    Update pick order status from mobile app
    
    Args:
        pick_order_name: Pick order name
        status: New status (Pending, In Progress, Completed, Cancelled)
        
    Returns:
        dict: {success: bool, message: str}
    """
    try:
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Check permission
        if not doc.has_permission("write"):
            frappe.throw(_("You don't have permission to modify this Pick Order"), frappe.PermissionError)
        
        # Validate status
        valid_statuses = ["Draft", "Pending", "In Progress", "Completed", "Cancelled"]
        if status not in valid_statuses:
            frappe.throw(f"Invalid status: {status}")
        
        # Use db_set to update submitted document
        doc.db_set('status', status)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Status updated to {status}"
        }
    
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"Error updating status: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }

@frappe.whitelist()
def start_picking(pick_order_name):
    """
    Start picking - update status to In Progress
    
    Args:
        pick_order_name: Pick order name
        
    Returns:
        dict: {success: bool, message: str}
    """
    return update_pick_order_status(pick_order_name, "In Progress")

# ==================== STOCK ENTRY CREATION ====================

@frappe.whitelist()
def create_stock_entry_from_pick_order(pick_order_name, submit=False):
    """
    Create Stock Entry from Pick Order
    
    Args:
        pick_order_name: Pick order name
        submit: Boolean to auto-submit the stock entry
        
    Returns:
        dict: {success: bool, stock_entry: str, message: str}
    """
    try:
        pick_order = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Check permission
        if not pick_order.has_permission("submit"):
            frappe.throw(_("You don't have permission to create Stock Entry"), frappe.PermissionError)
        
        # Determine stock entry purpose
        purpose_map = {
            "From Work Order": "Manufacture",
            "To Work Order": "Material Transfer for Manufacture",
            "From Subcontracting Order": "Material Receipt",
            "To Subcontracting Order": "Send to Subcontractor",
            "From Purchase Order": "Material Receipt",
            "Manual Roll Pick": "Material Transfer",
            "From Batch": "Material Transfer"
        }
        
        purpose = purpose_map.get(pick_order.pick_type, "Material Transfer")
        
        # Create Stock Entry
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = purpose
        stock_entry.posting_date = pick_order.posting_date or today()
        stock_entry.from_warehouse = pick_order.source_warehouse
        stock_entry.to_warehouse = pick_order.target_warehouse
        stock_entry.custom_roll_pick_order = pick_order.name
        
        # Add items from rolls
        for roll in pick_order.roll_wise_pick_item:
            stock_entry.append("items", {
                "item_code": roll.item_code,
                "s_warehouse": roll.warehouse,
                "t_warehouse": pick_order.target_warehouse,
                "qty": roll.qty,
                "uom": roll.uom,
                "batch_no": roll.batch,
                "custom_roll_no": roll.roll_no
            })
        
        # Add items from batches
        for batch in pick_order.batch_wise_pick_item:
            stock_entry.append("items", {
                "item_code": batch.item_code,
                "s_warehouse": batch.warehouse,
                "t_warehouse": pick_order.target_warehouse,
                "qty": batch.qty,
                "uom": batch.uom,
                "batch_no": batch.batch
            })
        
        stock_entry.insert()
        
        # Auto-submit if requested
        if submit and cint(submit):
            stock_entry.submit()
        
        return {
            "success": True,
            "stock_entry": stock_entry.name,
            "message": f"Stock Entry {stock_entry.name} created successfully"
        }
    
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"Error creating stock entry: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }

@frappe.whitelist()
def complete_pick_order(pick_order_name, rolls=None):
    """
    Complete pick order by creating and submitting stock entry
    
    Args:
        pick_order_name: Pick order name
        rolls: Optional JSON string of roll updates
        
    Returns:
        dict: {success: bool, stock_entry: str, message: str}
    """
    try:
        # Update rolls if provided
        if rolls:
            update_result = update_pick_order_rolls(pick_order_name, rolls)
            if not update_result.get("success"):
                return update_result
        
        # Create and submit stock entry
        result = create_stock_entry_from_pick_order(pick_order_name, submit=True)
        
        if result.get("success"):
            # Update status to Completed
            update_pick_order_status(pick_order_name, "Completed")
        
        return result
    
    except Exception as e:
        frappe.log_error(f"Error completing pick order: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }

# ==================== UTILITY FUNCTIONS ====================

@frappe.whitelist()
def get_pick_order_summary(pick_order_name):
    """
    Get summary statistics for a pick order
    
    Args:
        pick_order_name: Pick order name
        
    Returns:
        dict: {success: bool, summary: dict}
    """
    try:
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Check permission
        if not doc.has_permission("read"):
            frappe.throw(_("You don't have permission to view this Pick Order"), frappe.PermissionError)
        
        summary = {
            "total_rolls": len(doc.roll_wise_pick_item),
            "total_batches": len(doc.batch_wise_pick_item),
            "total_qty": doc.total_qty,
            "required_items_count": len(doc.required_items),
            "fully_picked_items": sum(1 for item in doc.required_items if item.remaining_qty == 0),
            "over_picked_items": sum(1 for item in doc.required_items if item.remaining_qty < 0),
            "status": doc.status
        }
        
        return {
            "success": True,
            "summary": summary
        }
    
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"Error getting summary: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }

@frappe.whitelist()
def cancel_pick_order(pick_order_name, reason=None):
    """
    Cancel a pick order
    
    Args:
        pick_order_name: Pick order name
        reason: Optional cancellation reason
        
    Returns:
        dict: {success: bool, message: str}
    """
    try:
        doc = frappe.get_doc("Roll Wise Pick Order", pick_order_name)
        
        # Check permission
        if not doc.has_permission("cancel"):
            frappe.throw(_("You don't have permission to cancel this Pick Order"), frappe.PermissionError)
        
        # Cancel the document
        doc.cancel()
        
        # Add cancellation reason if provided
        if reason:
            doc.add_comment("Comment", f"Cancellation Reason: {reason}")
        
        return {
            "success": True,
            "message": "Pick Order cancelled successfully"
        }
    
    except frappe.PermissionError:
        raise
    except Exception as e:
        frappe.log_error(f"Error cancelling pick order: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e)
        }

@frappe.whitelist()
def get_available_batches(warehouse=None, item_code=None, project=None):
    """
    Get available batches for selection
    
    Args:
        warehouse: Optional warehouse filter
        item_code: Optional item filter
        project: Optional project filter
        
    Returns:
        dict: {success: bool, data: list}
    """
    try:
        filters = {}
        
        if warehouse:
            filters['warehouse'] = warehouse
        if item_code:
            filters['item'] = item_code
        if project:
            filters['custom_project'] = project
        
        batches = frappe.get_all(
            'Batch',
            filters=filters,
            fields=['name', 'item', 'batch_qty', 'expiry_date'],
            limit=100
        )
        
        return {
            "success": True,
            "data": batches,
            "count": len(batches)
        }
    
    except Exception as e:
        frappe.log_error(f"Error fetching batches: {str(e)}", "API Error")
        return {
            "success": False,
            "message": str(e),
            "data": []
        }


@frappe.whitelist()
def get_conversations(limit=100, offset=0):
    """Get latest message per unique contact for conversation list with pagination"""
    limit = int(limit)
    offset = int(offset)
    
    messages = frappe.db.sql("""
        SELECT 
            w1.name,
            w1.type,
            w1.status,
            w1.`to`,
            w1.`from`,
            COALESCE(
                (SELECT profile_name FROM `tabWhatsApp Message` 
                 WHERE reference_name = w1.reference_name 
                 AND profile_name IS NOT NULL 
                 AND profile_name != ''
                 ORDER BY creation ASC
                 LIMIT 1),
                w1.profile_name
            ) as profile_name,
            w1.message,
            w1.message_type,
            w1.content_type,
            w1.attach,
            w1.template,
            w1.template_parameters,
            w1.whatsapp_account,
            w1.reference_doctype,
            w1.reference_name,
            w1.creation,
            w1.modified,
            (
                SELECT COUNT(*) 
                FROM `tabWhatsApp Message` w2 
                WHERE w2.reference_name = w1.reference_name 
                AND w2.type = 'Incoming'
                AND w2.status NOT IN ('read', 'marked as read')
            ) as unread_count
        FROM `tabWhatsApp Message` w1
        INNER JOIN (
            SELECT reference_name, MAX(modified) as max_modified
            FROM `tabWhatsApp Message`
            WHERE reference_name IS NOT NULL AND reference_name != ''
            GROUP BY reference_name
        ) latest 
        ON w1.reference_name = latest.reference_name 
        AND w1.modified = latest.max_modified
        ORDER BY w1.modified DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """, {"limit": limit, "offset": offset}, as_dict=True)
    
    total = frappe.db.sql("""
        SELECT COUNT(DISTINCT reference_name) as total
        FROM `tabWhatsApp Message`
        WHERE reference_name IS NOT NULL AND reference_name != ''
    """, as_dict=True)[0].total
    
    return {
        "data": messages,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }