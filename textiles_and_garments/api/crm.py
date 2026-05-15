import frappe


@frappe.whitelist()
def get_quotation_for_deal(crm_deal: str):
    """
    Returns the latest Quotation linked to this CRM Deal.
    Used by the form script to decide whether to show
    'Create Quotation' or 'View Quotation' button.
    """
    quotation = frappe.db.get_value(
        "Quotation",
        filters={"crm_deal": crm_deal},
        fieldname=["name", "status"],
        order_by="creation desc",
        as_dict=True
    )

    if not quotation:
        return None

    return {
        "quotation_name": quotation.name,
        "quotation_url":  f"/app/quotation/{quotation.name}",
        "status":         quotation.status
    }


@frappe.whitelist()
def create_quotation_from_deal(crm_deal: str, organization: str | None = None):
    """
    Creates an ERPNext Quotation from a CRM Deal.
    - Blocks if a Quotation already exists for this Deal
    - Requires custom_customer to be set on the Deal
    - Auto-links the primary contact to the customer if not already linked
    """
    from crm.fcrm.doctype.erpnext_crm_settings.erpnext_crm_settings import (
        _get_enabled_settings,
        get_primary_contact,
        get_organization_address,
    )

    deal = frappe.get_doc("CRM Deal", crm_deal)
    erpnext_crm_settings = _get_enabled_settings()
    address = get_organization_address(organization)
    address_name = address.get("name") if address else None

    # ── 0. Block if Quotation already exists ─────────────────────────────────
    existing = frappe.db.get_value("Quotation", {"crm_deal": crm_deal}, "name")
    if existing:
        frappe.throw(
            f"A Quotation <b>{existing}</b> already exists for this Deal. "
            "Click <b>View Quotation</b> to open it."
        )

    # ── 1. Resolve Customer ───────────────────────────────────────────────────
    # custom_customer must be set — click "Create Organisation as Customer" first
    customer_name = deal.get("custom_customer") or None

    if not customer_name:
        frappe.throw(
            "Please set the <b>Customer</b> field on this Deal before creating a Quotation. "
            "Click the <b>Create Organisation as Customer</b> button first."
        )

    frappe.logger().info(f"[CRM] Using custom_customer: {customer_name}")

    # ── 2. Contact from CRM Deal ──────────────────────────────────────────────
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


@frappe.whitelist()
def create_customer_from_organisation(crm_deal: str):
    """
    Creates an ERPNext Customer from the Deal's Organisation field.
    - If customer already exists (case-insensitive match) -> reuse it
    - If not -> auto-create from Organisation name
    - Saves result to custom_customer field on the Deal
    Returns: { customer_name, customer_url, created }
    """
    deal = frappe.get_doc("CRM Deal", crm_deal)
    org  = deal.organization

    if not org:
        frappe.throw(
            "No Organization set on this Deal. "
            "Please set the Organization field first."
        )

    # Exact match — DB collation utf8mb4_unicode_ci is case-insensitive
    customer_name = frappe.db.get_value(
        "Customer", {"customer_name": org}, "name"
    )
    created = False

    if customer_name:
        frappe.logger().info(
            f"[CRM] Existing customer found for '{org}': {customer_name}"
        )
    else:
        # Auto-create Customer from Organisation name
        new_customer               = frappe.new_doc("Customer")
        new_customer.customer_name = org
        new_customer.customer_type = "Company"
        new_customer.territory     = "All Territories"
        new_customer.insert(ignore_permissions=True)
        frappe.db.commit()
        customer_name = new_customer.name
        created       = True
        frappe.logger().info(f"[CRM] Auto-created Customer: {customer_name}")

    # Save to custom_customer on the Deal
    frappe.db.set_value("CRM Deal", crm_deal, "custom_customer", customer_name)
    frappe.db.commit()
    frappe.logger().info(
        f"[CRM] Saved '{customer_name}' to custom_customer on Deal {crm_deal}"
    )

    return {
        "customer_name": customer_name,
        "customer_url":  f"/app/customer/{customer_name}",
        "created":       created
    }