"""
Repair red stock ledger rows as of today, without touching history.

This is the procedure used by hand on 3 Oct 2026 (SR/00021 - SR/00033), packaged so it
never needs console pasting again. For every item/warehouse whose ledger total is red
(value <= -1 or qty < -0.001), excluding pairs you pass in `exclude`:

  K  batch item holding stock > frag   live batches reconciled at a rate: the stored
                                       rate if the stored value is positive, else the
                                       12-month median incoming rate (all-time median,
                                       then Item.valuation_rate as fallbacks)
  Z  batch item holding <= frag        live batches written off to 0
  C  batch item, no live batch         the empty batch with the largest leftover value
                                       reconciled to 0
  U  non-batch item                    posted as target+1 so ERPNext always writes a line,
                                       then line and stored balance set to the target
  S  only negative batches left        skipped; ERPNext cannot reconcile a negative batch

Each reconciliation (<= 90 rows, so ERPNext does not push it to a background job) is
submitted, its own automatic reposts are marked Skipped, and its last ledger line per
item/warehouse is adjusted so that ledger total == stored balance == target. Disabled
items/warehouses are enabled only inside the transaction. Commits only if every row
checks out; otherwise everything is rolled back. Committed vouchers are added to the
protected list (stock_integrity.protect).

Usage (dry run first, always):
    bench --site pranera.erpnext.com execute textiles_and_garments.stock_integrity.repair.run
    bench --site pranera.erpnext.com execute textiles_and_garments.stock_integrity.repair.run --kwargs "{'apply': 1}"
Options: frag (default 0.05), dust=1 (also rows between Rs -1 and 0),
         exclude=[[item, warehouse], ...], only=[[item, warehouse], ...]
"""

import frappe
from frappe.utils import add_to_date, cint, flt, now_datetime, nowdate

from textiles_and_garments.stock_integrity.common import batch_balances, ledger_state
from textiles_and_garments.stock_integrity.protect import protect
from textiles_and_garments.stock_integrity.pure import chunk_groups, classify_row, median

CHUNK = 90
NOTE = ("Ledger lines of this reconciliation were adjusted by textiles_and_garments.stock_integrity.repair "
        "so the stock ledger total matches the stored balance. Its automatic reposts were marked Skipped on "
        "purpose. Do NOT cancel it or repost these items from an earlier date.")


def _rate(item_code, stored_value, qty):
    if stored_value > 0 and qty > 0:
        return round(stored_value / qty, 6)
    base = """SELECT incoming_rate FROM `tabStock Ledger Entry` WHERE item_code=%s AND is_cancelled=0
              AND actual_qty>0 AND incoming_rate>0 AND voucher_type!='Stock Reconciliation'"""
    r = median([x[0] for x in frappe.db.sql(base + " AND posting_date >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)", item_code)])
    if not r:
        r = median([x[0] for x in frappe.db.sql(base, item_code)])
    if not r:
        r = flt(frappe.db.get_value("Item", item_code, "valuation_rate"))
    return round(r or 0, 4)


def _red_pairs(company, dust=0):
    having = ("ROUND(SUM(stock_value_difference), 2) < 0 OR ROUND(SUM(actual_qty), 3) < 0" if dust else
              "ROUND(SUM(stock_value_difference), 2) <= -1 OR ROUND(SUM(actual_qty), 3) < -0.001")
    return frappe.db.sql(
        f"""SELECT item_code, warehouse FROM `tabStock Ledger Entry` WHERE is_cancelled=0 AND company=%s
            GROUP BY item_code, warehouse HAVING {having}""",
        company,
    )


def plan_rows(pairs, frag):
    plan, groups, skipped = {}, {"N": [], "C": [], "U": []}, []
    for item, wh in pairs:
        sq, sv, bq, bv = ledger_state(item, wh)
        has_batch = cint(frappe.db.get_value("Item", item, "has_batch_no"))
        live, empty, pos_q = [], [], 0.0
        if has_batch:
            for x in batch_balances(item, wh):
                if x.q > 0.0005:
                    live.append(x)
                    pos_q += x.q
                elif abs(x.q) <= 0.0005:
                    empty.append(x)
        pos_q = round(pos_q, 3)
        kind = classify_row(has_batch, pos_q, bool(live), bool(empty), bq, frag)
        if kind == "U" and bq > frag:
            tq = round(bq, 6)
        elif kind == "K":
            tq = pos_q
        else:
            tq = 0
        rate = _rate(item, bv, tq) if tq else 0
        if tq and not rate:
            skipped.append((item, wh, "no rate found"))
            continue
        if kind == "S":
            skipped.append((item, wh, "only negative batches"))
            continue
        tv = round(tq * rate, 2)
        rows = []
        if kind in ("K", "Z"):
            for x in live:
                rows.append({"item_code": item, "warehouse": wh, "use_serial_batch_fields": 1, "batch_no": x.b,
                             "qty": x.q if kind == "K" else 0, "valuation_rate": rate})
            groups["N"].append(rows)
        elif kind == "C":
            big = max(empty, key=lambda x: abs(x.v))
            rows.append({"item_code": item, "warehouse": wh, "use_serial_batch_fields": 1, "batch_no": big.b,
                         "qty": 0, "valuation_rate": 0})
            groups["C"].append(rows)
        else:
            rows.append({"item_code": item, "warehouse": wh, "qty": tq + 1, "valuation_rate": rate,
                         "allow_zero_valuation_rate": 1})
            groups["U"].append(rows)
        plan[(item, wh)] = frappe._dict(kind=kind, tq=tq, tv=tv, rate=rate, before=(sq, sv, bq, bv))
    return plan, groups, skipped


def _submit_sr(company, rows, remark, bypass_no_change):
    d = frappe.get_doc({"doctype": "Stock Reconciliation", "company": company, "purpose": "Stock Reconciliation",
                        "posting_date": nowdate(), "items": rows, "remarks": remark})
    d.flags.ignore_stock_integrity = True
    d.flags.ignore_stock_guard = True
    if bypass_no_change:
        d.remove_items_with_no_change = lambda: None
    d.insert()
    original = d.update_stock_ledger
    d.update_stock_ledger = lambda allow_negative_stock=False: original(allow_negative_stock=True)
    d.submit()
    return d


def _align(names, item, wh, p):
    sles = frappe.db.sql(
        """SELECT name, qty_after_transaction FROM `tabStock Ledger Entry`
           WHERE voucher_no IN %s AND item_code=%s AND warehouse=%s AND is_cancelled=0 ORDER BY creation""",
        (tuple(names), item, wh), as_dict=True)
    if not sles:
        return False, "no ledger line"
    last = sles[-1]
    if p.kind in ("K", "Z"):
        for s in sles:
            frappe.db.set_value("Stock Ledger Entry", s.name,
                                {"stock_value": round(flt(s.qty_after_transaction) * p.rate, 2), "valuation_rate": p.rate},
                                update_modified=False)
    frappe.db.set_value("Stock Ledger Entry", last.name,
                        {"qty_after_transaction": p.tq, "stock_value": p.tv, "valuation_rate": p.rate},
                        update_modified=False)
    bn = frappe.db.get_value("Bin", {"item_code": item, "warehouse": wh})
    if bn:
        cur = frappe.db.get_value("Bin", bn, ["actual_qty", "projected_qty"], as_dict=True)
        frappe.db.set_value("Bin", bn, {"actual_qty": p.tq,
                                        "projected_qty": flt(cur.projected_qty) + (p.tq - flt(cur.actual_qty)),
                                        "stock_value": p.tv, "valuation_rate": p.rate}, update_modified=False)
    sq, sv, _, _ = ledger_state(item, wh)
    dq, dv = round(p.tq - sq, 6), round(p.tv - sv, 2)
    if abs(dq) > 0.00001 or abs(dv) > 0.005:
        lv = frappe.db.get_value("Stock Ledger Entry", last.name, ["actual_qty", "stock_value_difference"], as_dict=True)
        frappe.db.set_value("Stock Ledger Entry", last.name,
                            {"actual_qty": flt(lv.actual_qty) + dq, "stock_value_difference": flt(lv.stock_value_difference) + dv},
                            update_modified=False)
    f = ledger_state(item, wh)
    ok = abs(f[0] - p.tq) < 0.0005 and abs(f[1] - p.tv) < 0.01 and abs(f[2] - p.tq) < 0.0005 and abs(f[3] - p.tv) < 0.01
    return ok, f


@frappe.whitelist()
def run(apply=0, frag=0.05, company=None, exclude=None, only=None, dust=0):
    frappe.only_for("System Manager")
    apply, frag = cint(apply), flt(frag)
    company = company or frappe.defaults.get_global_default("company")
    exclude = {tuple(x) for x in (frappe.parse_json(exclude) if isinstance(exclude, str) else exclude or [])}
    only = [tuple(x) for x in (frappe.parse_json(only) if isinstance(only, str) else only or [])]

    frappe.db.rollback()
    pairs = only or [tuple(x) for x in _red_pairs(company, cint(dust))]
    pairs = [p for p in pairs if p not in exclude]
    plan, groups, skipped = plan_rows(pairs, frag)

    for (item, wh), p in plan.items():
        if p.tq:
            print("%s %-36s %-34s keeps %-9s @ %-10s = Rs %s (was %s)" % (p.kind, item[:36], wh[:34], p.tq, p.rate, p.tv, p.before[:2]))
    counts = {}
    for p in plan.values():
        counts[p.kind] = counts.get(p.kind, 0) + 1
    print("plan:", counts, "| skipped:", len(skipped))
    for s in skipped:
        print("  SKIP", s)
    if not plan:
        return {"plan": 0, "skipped": skipped}

    off_wh = sorted({wh for _, wh in plan if frappe.db.get_value("Warehouse", wh, "disabled")})
    off_it = sorted({it for it, _ in plan if frappe.db.get_value("Item", it, "disabled")})
    for w in off_wh:
        frappe.db.set_value("Warehouse", w, "disabled", 0, update_modified=False)
        frappe.clear_document_cache("Warehouse", w)
    for i in off_it:
        frappe.db.set_value("Item", i, "disabled", 0, update_modified=False)
        frappe.clear_document_cache("Item", i)
    frappe.db.value_cache.clear()

    start = add_to_date(now_datetime(), seconds=-5)
    docs, bad = [], []
    frappe.flags.allow_protected_repost = True
    try:
        for gname, bypass, remark in (
            ("N", False, "Stock ledger repair: live batches restated / fragments written off."),
            ("C", True, "Stock ledger repair: leftover value cleared where no stock is held."),
            ("U", False, "Stock ledger repair (non-batch): qty posted as target+1 only so ERPNext writes a "
                         "line; line and stored balance then set to the target."),
        ):
            for chunk in chunk_groups(groups[gname], CHUNK):
                d = _submit_sr(company, chunk, remark, bypass)
                docs.append(d)
                print("SR", gname, d.name, len(chunk), "rows")
        names = [d.name for d in docs]

        skipped_rivs = 0
        for rv in frappe.db.sql(
            """SELECT name, item_code, warehouse, voucher_no FROM `tabRepost Item Valuation`
               WHERE docstatus=1 AND status='Queued' AND creation >= %s""", start, as_dict=True):
            if (rv.item_code, rv.warehouse) in plan or rv.voucher_no in names:
                frappe.db.set_value("Repost Item Valuation", rv.name, "status", "Skipped", update_modified=False)
                skipped_rivs += 1
        print("own reposts marked Skipped:", skipped_rivs)

        for (item, wh), p in plan.items():
            ok, f = _align(names, item, wh, p)
            if not ok:
                bad.append((p.kind, item, wh, f, (p.tq, p.tv)))
        print("rows ok:", len(plan) - len(bad), "of", len(plan))
        for b in bad:
            print("  !! CHECK", b)
    except Exception:
        frappe.db.rollback()
        raise
    finally:
        frappe.flags.allow_protected_repost = False
        # re-disable; if we rolled back above these writes are rolled back too, which is the same state
        for w in off_wh:
            frappe.db.set_value("Warehouse", w, "disabled", 1, update_modified=False)
            frappe.clear_document_cache("Warehouse", w)
        for i in off_it:
            frappe.db.set_value("Item", i, "disabled", 1, update_modified=False)
            frappe.clear_document_cache("Item", i)

    if apply and not bad:
        frappe.db.commit()
        for d in docs:
            d.add_comment("Comment", NOTE)
            protect("Stock Reconciliation", d.name)
        frappe.db.commit()
        print("COMMITTED", [d.name for d in docs])
        return {"committed": [d.name for d in docs], "rows": len(plan), "skipped": skipped}

    frappe.db.rollback()
    print("ROLLED BACK", "(dry run)" if not apply else "(a check failed)")
    return {"committed": [], "rows": len(plan), "bad": bad, "skipped": skipped}
