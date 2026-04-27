import frappe


@frappe.whitelist()
def get_conversations(limit=100, offset=0):
    """Get latest message per unique contact for conversation list with pagination"""
    limit = int(limit)
    offset = int(offset)
    
    messages = frappe.db.sql("""
        SELECT 
            w1.name, w1.type, w1.status, w1.`to`, w1.`from`,
            COALESCE(
                (SELECT profile_name FROM `tabWhatsApp Message` 
                 WHERE reference_name = w1.reference_name 
                 AND profile_name IS NOT NULL AND profile_name != ''
                 ORDER BY creation ASC LIMIT 1),
                w1.profile_name
            ) as profile_name,
            w1.message, w1.message_type, w1.content_type, w1.attach,
            w1.template, w1.template_parameters, w1.whatsapp_account,
            w1.reference_doctype, w1.reference_name, w1.creation, w1.modified,
            (SELECT COUNT(*) FROM `tabWhatsApp Message` w2 
             WHERE w2.reference_name = w1.reference_name 
             AND w2.type = 'Incoming'
             AND w2.status NOT IN ('read', 'marked as read')) as unread_count
        FROM `tabWhatsApp Message` w1
        INNER JOIN (
            SELECT reference_name, MAX(modified) as max_modified
            FROM `tabWhatsApp Message`
            WHERE reference_name IS NOT NULL AND reference_name != ''
            GROUP BY reference_name
        ) latest ON w1.reference_name = latest.reference_name 
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
        "data": messages, "total": total,
        "limit": limit, "offset": offset,
        "has_more": (offset + limit) < total
    }


@frappe.whitelist()
def get_session_id():
    """Return current user's session id for socket authentication."""
    return frappe.session.sid
