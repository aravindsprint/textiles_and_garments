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
    errors = []

    print(f"[sync_customers_to_crm_organizations] Starting sync for {total} customers...")

    for i, cust in enumerate(customers, start=1):
        cust_name = cust["name"]
        try:
            if cust_name in existing_orgs:
                org = frappe.get_doc("CRM Organization", cust_name)

                if org.custom_customer == cust_name:
                    skipped_already_linked += 1
                    continue

                org.custom_customer = cust_name

                if cust.get("customer_group") and not org.custom_customer_group:
                    org.custom_customer_group = cust["customer_group"]

                if cust.get("territory") and not org.territory:
                    org.territory = cust["territory"]

                org.save(ignore_permissions=True)
                linked += 1
            else:
                org = frappe.new_doc("CRM Organization")
                org.organization_name = cust.get("customer_name") or cust_name
                org.custom_customer = cust_name
                org.custom_customer_group = cust.get("customer_group")
                org.territory = cust.get("territory")
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
    print(f"  Errors                    : {len(errors)}")

    if errors:
        print("  First 20 errors:")
        for err in errors[:20]:
            print(f"    - {err}")
