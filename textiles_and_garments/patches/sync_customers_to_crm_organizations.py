"""
Patch: sync_customers_to_crm_organizations

One-time migration: link every ERPNext Customer to a Frappe CRM Organization,
creating new Organization records where no match exists.

Place this file at:
    textiles_and_garments/textiles_and_garments/patches/sync_customers_to_crm_organizations.py

Register in:
    textiles_and_garments/textiles_and_garments/patches.txt
    (add the line:textiles_and_garments.patches.sync_customers_to_crm_organizations)

Then run:
    bench --site pranera.erpnext.com migrate
"""

import frappe


def _ensure_territory(territory_name):
    """
    CRM Organization.territory is a Link field — but its `options` points to
    "CRM Territory", NOT the standard ERPNext "Territory" doctype (confirmed
    via DocField: fieldname=territory, label="Territory", options="CRM
    Territory"). The field's label is "Territory", which is why Frappe's own
    error message ("Could not find Territory: X") looks like it's about the
    standard Territory doctype — it isn't; that's just the field's display
    label leaking into the error text. The standard Territory doctype
    genuinely does have all these values already; "CRM Territory" is a
    separate, nearly-empty table (4 rows) that was never populated. Auto-
    create the missing leaf CRM Territory record instead of failing the
    whole customer record. parent_crm_territory isn't a required field on
    this doctype, so these can land as flat top-level leaves; they can be
    reorganized under proper parents later if needed.
    Returns None (instead of raising) if creation itself fails for some
    other reason, so the caller can fall back to leaving territory unset
    rather than losing the whole customer/organization record over it.
    """
    if not territory_name:
        return None
    if frappe.db.exists("CRM Territory", territory_name):
        return territory_name

    try:
        doc = frappe.new_doc("CRM Territory")
        doc.territory_name = territory_name
        doc.is_group = 0
        doc.insert(ignore_permissions=True)
        return doc.name
    except Exception as e:
        frappe.log_error(
            f"Could not auto-create CRM Territory '{territory_name}': {e}",
            "sync_customers_to_crm_organizations",
        )
        frappe.db.rollback()
        return None


def execute():
    if "crm" not in frappe.get_installed_apps():
        # CRM app not installed on this site, nothing to do
        return

    if not frappe.db.exists("DocType", "CRM Organization"):
        return

    customers = frappe.get_all(
        "Customer",
        fields=["name", "customer_name", "customer_group", "territory"],
    )

    existing_orgs = set(frappe.get_all("CRM Organization", pluck="name"))

    total = len(customers)
    created = 0
    linked = 0
    skipped_already_linked = 0
    territories_created = 0
    errors = []

    print(f"[sync_customers_to_crm_organizations] Starting sync for {total} customers...")

    for i, cust in enumerate(customers, start=1):
        cust_name = cust["name"]
        try:
            territory = cust.get("territory")
            if territory and not frappe.db.exists("CRM Territory", territory):
                resolved = _ensure_territory(territory)
                if resolved:
                    territories_created += 1
                    territory = resolved
                else:
                    # Couldn't create it — proceed without a territory rather
                    # than losing the whole customer/organization record.
                    territory = None

            if cust_name in existing_orgs:
                org = frappe.get_doc("CRM Organization", cust_name)

                if org.custom_customer == cust_name:
                    skipped_already_linked += 1
                    continue

                org.custom_customer = cust_name

                if cust.get("customer_group") and not org.custom_customer_group:
                    org.custom_customer_group = cust["customer_group"]

                if territory and not org.territory:
                    org.territory = territory

                org.save(ignore_permissions=True)
                linked += 1
            else:
                org = frappe.new_doc("CRM Organization")
                org.organization_name = cust.get("customer_name") or cust_name
                org.custom_customer = cust_name
                org.custom_customer_group = cust.get("customer_group")
                org.territory = territory
                org.insert(ignore_permissions=True)
                created += 1

        except Exception as e:
            errors.append(f"{cust_name}: {e}")
            frappe.db.rollback()
            continue

        if i % 200 == 0:
            frappe.db.commit()
            print(f"  ...processed {i}/{total} (created={created}, linked={linked})")

    frappe.db.commit()

    print("[sync_customers_to_crm_organizations] Sync complete")
    print(f"  Total customers processed : {total}")
    print(f"  New CRM Organizations     : {created}")
    print(f"  Existing orgs linked      : {linked}")
    print(f"  Already linked (skipped)  : {skipped_already_linked}")
    print(f"  Territories auto-created  : {territories_created}")
    print(f"  Errors                    : {len(errors)}")

    if errors:
        print("  First 20 errors:")
        for err in errors[:20]:
            print(f"    - {err}")
