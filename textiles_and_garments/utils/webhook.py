import frappe


def on_whatsapp_message_insert(doc, method):
    """Triggered after any WhatsApp Message is inserted."""
    frappe.publish_realtime(
        "whatsapp_new_message",
        {
            "name": doc.name,
            "type": doc.type,
            "from": doc.get("from") or "",
            "to": doc.get("to") or "",
            "message": doc.message or "",
            "message_type": doc.message_type or "Manual",
            "content_type": doc.content_type or "text",
            "profile_name": doc.profile_name or "",
            "whatsapp_account": doc.whatsapp_account or "",
            "reference_name": doc.reference_name or "",
            "reference_doctype": doc.reference_doctype or "",
            "attach": doc.attach or "",
            "template": doc.template or "",
            "template_parameters": doc.template_parameters or "",
            "creation": str(doc.creation),
            "modified": str(doc.modified),
        },
        user="all",          # broadcast to ALL logged-in users
        after_commit=False,  # fire immediately, don't wait for DB commit
    )


def on_whatsapp_message_update(doc, method):
    """Triggered after WhatsApp Message is saved — publish status update."""
    frappe.publish_realtime(
        "whatsapp_message_status",
        {
            "name": doc.name,
            "status": doc.status or "",
            "reference_name": doc.reference_name or "",
        },
        user="all",
        after_commit=False,
    )