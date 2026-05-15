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
    address = get_organization_address(organization)
    address_name = address.get("name") if address else None

    # ── 1. Resolve Customer ───────────────────────────────────────────────────
    #
    # Priority:
    #   1. custom_customer field on Deal (user selected — most reliable)
    #   2. Organization field exact match in ERPNext Customer
    #   3. Auto-create new Customer from Organization name
    #
    customer_name = deal.get("custom_customer") or None

    if customer_name:
        frappe.logger().info(f"[CRM] Using custom_customer field: {customer_name}")
    else:
        org = deal.organization or organization
        if not org:
            frappe.throw(
                "No Customer or Organization set on this Deal. "
                "Please set at least the Organization field."
            )

        # Exact match — DB collation utf8mb4_unicode_ci is case insensitive
        customer_name = frappe.db.get_value(
            "Customer", {"customer_name": org}, "name"
        )
        frappe.logger().info(f"[CRM] Exact match for '{org}': {customer_name}")

        if not customer_name:
            # Auto-create Customer from Organization name
            new_customer               = frappe.new_doc("Customer")
            new_customer.customer_name = org
            new_customer.customer_type = "Company"
            new_customer.territory     = "All Territories"
            new_customer.insert(ignore_permissions=True)
            frappe.db.commit()
            customer_name = new_customer.name
            frappe.logger().info(f"[CRM] Auto-created Customer: {customer_name}")

        # Save resolved customer back to the Deal's custom_customer field
        # so next time it's used directly without lookup
        frappe.db.set_value("CRM Deal", crm_deal, "custom_customer", customer_name)
        frappe.db.commit()
        frappe.logger().info(
            f"[CRM] Saved customer '{customer_name}' to Deal custom_customer field"
        )

    # ── 2. Contact from CRM Deal ───────────────────────────────────────────────
    # Get primary contact. If not linked to this customer yet, add the link.
    contact = get_primary_contact(crm_deal)
    frappe.logger().info(f"[CRM] Primary contact for deal {crm_deal}: {contact}")

    if contact:
        already_linked = frappe.db.get_value("Dynamic Link", {
            "parenttype":   "Contact",
            "parent":       contact,
            "link_doctype": "Customer",
            "link_name":    customer_name
        }, "name")

        if not already_linked:
            contact_doc = frappe.get_doc("Contact", contact)
            contact_doc.append("links", {
                "link_doctype": "Customer",
                "link_name":    customer_name
            })
            contact_doc.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.logger().info(
                f"[CRM] Linked contact {contact} to customer {customer_name}"
            )
        else:
            frappe.logger().info(
                f"[CRM] Contact {contact} already linked to {customer_name}"
            )

    # ── 3. Build Quotation ────────────────────────────────────────────────────
    quotation                  = frappe.new_doc("Quotation")
    quotation.quotation_to     = "Customer"
    quotation.party_name       = customer_name
    quotation.crm_deal         = crm_deal
    quotation.company          = erpnext_crm_settings.erpnext_company
    quotation.contact_person   = contact
    quotation.customer_address = address_name

    # ── 4. Map CRM Deal products -> Quotation items ───────────────────────────
    quotation.items = []
    for product in deal.products:
        quotation.append("items", {
            "item_code": product.custom_item_code,
            "item_name": product.product_name or product.custom_item_code,
            "qty":       product.qty or 1,
            "rate":      product.rate or 0,
            "uom":       "Nos",
        })

    # ERPNext requires at least one item row
    if not deal.products:
        quotation.append("items", {})

    # ── 5. Save ───────────────────────────────────────────────────────────────
    quotation.flags.ignore_mandatory = True
    quotation.flags.ignore_links     = True
    quotation.flags.ignore_validate  = True

    try:
        quotation.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info(f"[CRM] Quotation saved: {quotation.name}")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "create_quotation_from_deal Failed")
        frappe.throw(frappe.get_traceback())

    return f"/app/quotation/{quotation.name}"