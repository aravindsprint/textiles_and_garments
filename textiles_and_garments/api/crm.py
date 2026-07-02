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
def set_lead_geolocation(docname, geolocation):
    """
    Directly sets geolocation on CRM Lead bypassing timestamp/version check.
    Called from the frontend after GPS capture.
    """
    frappe.db.set_value(
        "CRM Lead",
        docname,
        "custom_geolocation",
        geolocation,
        update_modified=False  # Don't update modified timestamp — avoids re-triggering
    )
    frappe.db.commit()
    return True

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


@frappe.whitelist()
def get_sales_order_for_deal(crm_deal):
    """Return the latest Sales Order linked to this CRM Deal, or None."""
    so_name = frappe.db.get_value(
        "Sales Order",
        {"custom_crm_deal": crm_deal, "docstatus": ["<", 2]},
        "name",
        order_by="creation desc"
    )
    if so_name:
        return {"sales_order_name": so_name}
    return None


@frappe.whitelist()
def create_sales_order_from_deal(crm_deal, organization):
    from crm.fcrm.doctype.erpnext_crm_settings.erpnext_crm_settings import _get_enabled_settings

    deal = frappe.get_doc("CRM Deal", crm_deal)
    customer = deal.custom_customer
    if not customer:
        frappe.throw("No customer linked to this Deal. Please create the customer first.")

    customer_doc = frappe.get_doc("Customer", customer)
    erpnext_crm_settings = _get_enabled_settings()

    so = frappe.new_doc("Sales Order")
    so.customer = customer
    so.company = erpnext_crm_settings.erpnext_company
    so.custom_crm_deal = crm_deal
    so.delivery_date = frappe.utils.add_days(frappe.utils.today(), 7)

    # Mandatory custom fields on this instance
    so.payment_terms = "Standard"
    so.delivery_terms = "Ex MILL"
    so.delivery_to = customer

    # Sales team — pull from Customer's own sales team allocation
    if customer_doc.sales_team:
        for row in customer_doc.sales_team:
            so.append("sales_team", {
                "sales_person": row.sales_person,
                "allocated_percentage": row.allocated_percentage
            })

    # Customer billing address (needed for GST fields below)
    customer_address = frappe.db.get_value(
        "Dynamic Link",
        {"link_doctype": "Customer", "link_name": customer, "parenttype": "Address"},
        "parent"
    )
    if customer_address:
        so.customer_address = customer_address
        addr = frappe.get_doc("Address", customer_address)
        so.billing_address_gstin = addr.gstin
        if addr.gst_state_number:
            so.place_of_supply = f"{addr.gst_state_number}-{addr.state}"

    so.gst_category = customer_doc.gst_category or "Unregistered"

    # Company GST address (adjust to your actual default branch/GSTIN)
    so.company_address = "Pranera Tirupur"
    so.company_gstin = "33AAECP8397C1ZA"

    quotation_name = frappe.db.get_value(
        "Quotation",
        {"crm_deal": crm_deal, "docstatus": ["<", 2]},
        "name",
        order_by="creation desc"
    )

    if quotation_name:
        quotation = frappe.get_doc("Quotation", quotation_name)
        so.selling_price_list = quotation.selling_price_list
        for item in quotation.items:
            so.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "qty": item.qty,
                "rate": item.rate,
                "uom": item.uom,
                "delivery_date": so.delivery_date,
            })
    else:
        for product in deal.products:
            item_doc = frappe.get_cached_doc("Item", product.custom_item_code)
            so.append("items", {
                "item_code": product.custom_item_code,
                "item_name": product.product_name or product.custom_item_code,
                "qty": product.qty or 1,
                "rate": product.rate or 0,
                "uom": item_doc.stock_uom,   # pull real UOM, don't hardcode
                "delivery_date": so.delivery_date,
            })

    if not so.items:
        frappe.throw(
            "No items found to create this Sales Order. "
            "Please add products to the Deal or create a Quotation first."
        )

    so.set_missing_values()
    so.flags.ignore_mandatory = False
    so.insert(ignore_permissions=True)

    return f"/app/sales-order/{frappe.utils.cstr(so.name)}"