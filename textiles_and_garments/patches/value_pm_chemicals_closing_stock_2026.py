"""
Value Pranera Marketing's closing stock of two SCIESSENT chemicals on 31-03-2026.

Why: PSS bought them on PO25TIRUPUR17125-1 ($17.65 / $8.80 per kg), received them on
PREC25/6183 and sold them to Pranera Marketing on PHGB25/00051 (20 Aug 2025). Pranera
Marketing booked the stock with Material Receipt MR/25/00909 (4 Aug 2025) at rate 0, so
820 kg NOBO and 4,038 kg COMFORTEC sat in PM/SWARNAPURI/WH01 at Rs 0 / Rs 42,500 on 31-03-2026.

What: one Stock Reconciliation dated 31-03-2026 23:59 that keeps the quantities and sets the
landed rates (Rs 1,773.93 and Rs 884.45 per kg). Closing value Rs 50,26,031.70. ERPNext then
queues reposts that revalue the later sales invoices; nothing is manufactured from this
stock, so the repost stays inside these two items. Pranera Marketing has perpetual inventory
off, so no GL entry is posted.

Safe to run anywhere:
  - skipped when a submitted reconciliation already sets these rates on 31-03-2026
    (production: SR/00035, done by hand on 4 Oct 2026),
  - skipped when the company, warehouse, items or batches do not exist (other sites),
  - skipped, with an Error Log entry, when the quantities on 31-03-2026 are not the ones below.
"""

import frappe
from frappe.utils import flt

COMPANY = "Pranera Marketing"
WAREHOUSE = "PM/SWARNAPURI/WH01 - PM"
POSTING_DATE, POSTING_TIME = "2026-03-31", "23:59:00"
ROWS = [  # item, batch, qty on 31-03-2026, landed rate per kg
    ("CHEM00347/NOBO", "CHEM00347/NOBO/4082025", 820, 1773.93),
    ("CHEM00348/COMFORTEC", "CHEM00348/COMFORTEC/4082025", 3988, 884.45),
    ("CHEM00348/COMFORTEC", "PO25PM00502-1", 50, 884.45),
]
REMARKS = ("Closing stock 31-03-2026 at landed cost of SCIESSENT PO25TIRUPUR17125-1 ($17.65 / $8.80 per kg). "
           "Stock reached PM via Material Receipt MR/25/00909 (4 Aug 2025) at rate 0; PSS sale PHGB25/00051 "
           "(20 Aug 2025). [patch value_pm_chemicals_closing_stock_2026]")


def _already_done():
    return frappe.db.sql(
        """SELECT sr.name FROM `tabStock Reconciliation` sr
           JOIN `tabStock Reconciliation Item` i ON i.parent = sr.name
           WHERE sr.docstatus = 1 AND sr.company = %s AND sr.posting_date = %s
             AND i.item_code = %s AND i.warehouse = %s AND ABS(i.valuation_rate - %s) < 0.01
           LIMIT 1""",
        (COMPANY, POSTING_DATE, ROWS[0][0], WAREHOUSE, ROWS[0][3]),
    )


def _batch_qty_on(item, batch):
    q = frappe.db.sql(
        """SELECT SUM(e.qty) FROM `tabStock Ledger Entry` s
           JOIN `tabSerial and Batch Entry` e ON e.parent = s.serial_and_batch_bundle
           WHERE s.item_code=%s AND s.warehouse=%s AND s.is_cancelled=0 AND e.batch_no=%s
             AND s.posting_date <= %s""",
        (item, WAREHOUSE, batch, POSTING_DATE),
    )[0][0]
    return flt(q, 3)


def execute():
    if not frappe.db.exists("Company", COMPANY) or not frappe.db.exists("Warehouse", WAREHOUSE):
        return
    for item, batch, _qty, _rate in ROWS:
        if not frappe.db.exists("Item", item) or not frappe.db.exists("Batch", batch):
            return

    done = _already_done()
    if done:
        print("value_pm_chemicals_closing_stock_2026: already done by", done[0][0])
        return

    mismatch = []
    for item, batch, qty, _rate in ROWS:
        have = _batch_qty_on(item, batch)
        if abs(have - qty) > 0.001:
            mismatch.append("{0} / {1}: expected {2}, found {3}".format(item, batch, qty, have))
    if mismatch:
        frappe.log_error(title="Patch value_pm_chemicals_closing_stock_2026 skipped",
                         message="Quantities on 31-03-2026 differ:\n" + "\n".join(mismatch))
        return

    sr = frappe.get_doc({
        "doctype": "Stock Reconciliation",
        "company": COMPANY,
        "purpose": "Stock Reconciliation",
        "posting_date": POSTING_DATE,
        "posting_time": POSTING_TIME,
        "set_posting_time": 1,
        "remarks": REMARKS,
        "items": [
            {"item_code": item, "warehouse": WAREHOUSE, "use_serial_batch_fields": 1, "batch_no": batch,
             "qty": qty, "valuation_rate": rate}
            for item, batch, qty, rate in ROWS
        ],
    })
    sr.insert(ignore_permissions=True)
    sr.submit()
    print("value_pm_chemicals_closing_stock_2026: created", sr.name, "- reposts queued for the later sales invoices")
