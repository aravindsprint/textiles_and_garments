import frappe

@frappe.whitelist()
def create_quotation_from_deal(crm_deal: str, organization: str | None = None):
    from crm.fcrm.doctype.erpnext_crm_settings.erpnext_crm_settings import (
        _get_enabled_settings,
        get_primary_contact,
        get_organization_address,
    )

    deal = frappe.get_doc("CRM Deal", crm_deal)
    erpnext_crm_settings = _get_enabled_settings()
    contact = get_primary_contact(crm_deal)
    address = get_organization_address(organization)
    address_name = address.get("name") if address else None

    quotation = frappe.new_doc("Quotation")
    quotation.quotation_to = "CRM Deal"
    quotation.party_name = crm_deal
    quotation.crm_deal = crm_deal
    quotation.company = erpnext_crm_settings.erpnext_company
    quotation.contact_person = contact
    quotation.customer_address = address_name

    # Clear default blank row
    quotation.items = []

    # Map CRM Deal products → Quotation items
    for product in deal.products:
        quotation.append("items", {
            "item_code": product.custom_item_code,
            "item_name": product.product_name or product.custom_item_code,
            "qty": product.qty or 1,
            "rate": product.rate or 0,
            "uom": "Nos",
        })

    # ERPNext requires at least one item row
    if not deal.products:
        quotation.append("items", {})

    quotation.flags.ignore_mandatory = True
    quotation.flags.ignore_validate = True
    quotation.flags.ignore_links = True

    try:
        quotation.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info(f"Quotation saved: {quotation.name}")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "create_quotation_from_deal Failed")
        frappe.throw(frappe.get_traceback())

    return f"/app/quotation/{quotation.name}"