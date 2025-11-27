import frappe
from frappe import _

@frappe.whitelist()
def item_query_with_stock(doctype, txt, searchfield, start, page_len, filters):
    """Custom item query to show stock balance in dropdown"""
    
    warehouse = filters.get('warehouse', '')
    company = filters.get('company')
    
    # Build the base query
    query = """
        SELECT item.name, item.item_name, item.item_group, item.description, item.stock_uom
        FROM `tabItem` as item
        WHERE (item.name like %(txt)s or item.item_name like %(txt)s) 
        AND item.is_sales_item = 1 
        AND item.disabled = 0
    """
    
    params = {
        'txt': '%' + txt + '%',
        'start': start,
        'page_len': page_len
    }
    
    query += " ORDER BY item.name LIMIT %(start)s, %(page_len)s"
    
    items = frappe.db.sql(query, params, as_dict=True)
    
    result = []
    for item in items:
        # Get stock for each item
        stock_filters = {'item_code': item.name}
        if warehouse:
            stock_filters['warehouse'] = warehouse
            
        stock_qty = frappe.db.get_value('Bin', stock_filters, 'sum(actual_qty)') or 0
        
        # Proper format for link query: [value, description]
        description = f"{item.item_name} - {item.item_group} (Stock: {stock_qty} {item.stock_uom})"
        
        # The FIRST element must be the item code (value), SECOND is description
        result.append([item.name, description])
    
    return result






@frappe.whitelist()
def get_item_history(item_code, company):
    """Get purchase and sales history for an item"""
    
    purchase_history = frappe.db.sql("""
        SELECT 
            poi.parent as purchase_order,
            po.supplier,
            poi.qty,
            poi.rate,
            poi.amount,
            po.transaction_date as date,
            poi.uom
        FROM `tabPurchase Order Item` poi
        LEFT JOIN `tabPurchase Order` po ON po.name = poi.parent
        WHERE poi.item_code = %s 
            AND poi.docstatus = 1
            AND po.company = %s
        ORDER BY po.transaction_date DESC
        LIMIT 50
    """, (item_code, company), as_dict=1)
    
    sales_history = frappe.db.sql("""
        SELECT 
            sii.parent as sales_invoice,
            si.customer,
            sii.qty,
            sii.rate,
            sii.amount,
            si.posting_date as date,
            sii.uom
        FROM `tabSales Invoice Item` sii
        LEFT JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE sii.item_code = %s 
            AND sii.docstatus = 1
            AND si.company = %s
        ORDER BY si.posting_date DESC
        LIMIT 50
    """, (item_code, company), as_dict=1)
    
    return {
        'purchase_history': purchase_history,
        'sales_history': sales_history
    }








