"""
textiles_and_garments/api/verify_rolls.py

Backend for the Roll App's "Verify Rolls" page (pranera_roll frontend,
/roll-app/verify-rolls).

Flow
----
1. The user scans (or picks) the 2D barcode of a submitted
   "Stock Entry - Material Transfer" that was created from a
   Roll Wise Pick List (Stock Entry.custom_roll_wise_pick_list).
   -> get_transfer_for_verification()

2. The page lists every roll on that pick list with its weight. Each roll
   starts "Not Verified" and turns "Verified" when its roll label is
   scanned. This happens client-side only — nothing is written yet.

3. Once every roll is verified the user is asked whether to make a
   "Stock Entry - Material Transfer". If yes, they choose a bin for each
   roll. The chosen bin is that roll's Target Warehouse. The Source
   Warehouse is the Target Warehouse the roll arrived in on the scanned
   Stock Entry.
   -> create_verified_transfer()

"Bins" are ordinary leaf (non-group) Warehouses. There's no separate bin
doctype on this site.

Bookkeeping on the new Stock Entry
----------------------------------
custom_verified_from_stock_entry  the scanned source entry
custom_verified_rolls             Verified Roll Item rows (roll -> bin)

Doc events registered in hooks.py:
  validate   -> validate_verified_transfer   (one put-away per source entry)
  on_submit  -> on_verified_transfer_submit  (Roll.warehouse = bin)
  on_cancel  -> on_verified_transfer_cancel  (Roll.warehouse = source back)
Each one returns immediately for any Stock Entry that isn't a verified
put-away, so normal Stock Entries aren't affected.
"""
import json
from urllib.parse import unquote

import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate, nowtime


# ── Helpers ─────────────────────────────────────────────────────────────────

def _resolve_stock_entry_name(scanned):
	"""Turn whatever the 2D barcode / search field gave us into a Stock
	Entry name. Accepts:
	  * the bare name                       MT/26/23243
	  * a desk URL                          https://erp.pranera.in/app/stock-entry/MT%2F26%2F23243
	  * a print / printview URL             .../printview?doctype=Stock%20Entry&name=MT%2F26%2F23243
	  * "Stock Entry:<name>" or "...#<name>" style payloads
	"""
	text = (scanned or "").strip()
	if not text:
		frappe.throw(_("Scan or select a Stock Entry"))

	candidates = [text, unquote(text)]

	decoded = unquote(text)
	if "/stock-entry/" in decoded:
		candidates.append(decoded.split("/stock-entry/", 1)[1].split("?")[0].split("#")[0].strip("/"))
	if "name=" in decoded:
		candidates.append(decoded.split("name=", 1)[1].split("&")[0])
	if ":" in decoded and not decoded.lower().startswith("http"):
		candidates.append(decoded.split(":", 1)[1].strip())
	if "#" in decoded:
		candidates.append(decoded.split("#")[-1].strip())

	for c in candidates:
		if c and frappe.db.exists("Stock Entry", c):
			return c

	frappe.throw(_("Stock Entry not found for scanned value: {0}").format(frappe.bold(text)))


def _pick_list_for(se):
	name = se.get("custom_roll_wise_pick_list")
	if name and frappe.db.exists("Roll Wise Pick List", name):
		return name
	return frappe.db.get_value(
		"Roll Wise Pick List", {"stock_entry": se.name, "docstatus": 1}, "name"
	)


def _source_map(se):
	"""(item_code, batch) -> where that material landed on the scanned entry
	(its t_warehouse). That landing spot is the new Source Warehouse."""
	m = {}
	for row in se.items:
		if row.t_warehouse:
			m.setdefault((row.item_code, row.batch_no or None), row.t_warehouse)
	return m


def _existing_put_away(source_se, exclude=None):
	filters = {"custom_verified_from_stock_entry": source_se, "docstatus": ["<", 2]}
	if exclude:
		filters["name"] = ["!=", exclude]
	return frappe.db.get_value("Stock Entry", filters, ["name", "docstatus"], as_dict=True)


def _get_warehouse_address(warehouse):
	if not warehouse:
		return None
	return frappe.db.get_value(
		"Dynamic Link",
		{"link_doctype": "Warehouse", "link_name": warehouse, "parenttype": "Address"},
		"parent",
	)


def _load_transfer(stock_entry_name):
	se = frappe.get_doc("Stock Entry", stock_entry_name)
	se.check_permission("read")

	if se.purpose != "Material Transfer":
		frappe.throw(_("{0} is a {1} entry — only Material Transfer entries can be verified").format(
			frappe.bold(se.name), se.purpose))
	if se.docstatus == 0:
		frappe.throw(_("{0} is still a draft — submit it before verifying its rolls").format(frappe.bold(se.name)))
	if se.docstatus == 2:
		frappe.throw(_("{0} is cancelled").format(frappe.bold(se.name)))

	pick_list = _pick_list_for(se)
	if not pick_list:
		frappe.throw(_("{0} wasn't created from a Roll Wise Pick List — there are no rolls to verify").format(
			frappe.bold(se.name)))

	pl = frappe.get_doc("Roll Wise Pick List", pick_list)
	src_map = _source_map(se)
	fallback_src = se.to_warehouse or next((r.t_warehouse for r in se.items if r.t_warehouse), None)

	pick_rows = [r for r in (pl.get("roll_wise_pick_item") or []) if r.roll_no]
	roll_meta = {}
	if pick_rows:
		for r in frappe.get_all(
			"Roll",
			filters={"name": ["in", [p.roll_no for p in pick_rows]]},
			fields=["name", "item_name", "commercial_name", "color", "width"],
		):
			roll_meta[r.name] = r

	rolls, seen = [], set()
	for p in pick_rows:
		if p.roll_no in seen:
			continue
		seen.add(p.roll_no)
		meta = roll_meta.get(p.roll_no) or {}
		rolls.append({
			"roll_no": p.roll_no,
			"item_code": p.item_code,
			"item_name": meta.get("item_name"),
			"commercial_name": meta.get("commercial_name"),
			"color": meta.get("color"),
			"batch": p.batch,
			"qty": flt(p.qty),
			"uom": p.uom,
			"roll_weight": flt(p.roll_weight) or flt(p.qty),
			"source_warehouse": src_map.get((p.item_code, p.batch or None)) or fallback_src,
		})

	return se, pl, rolls


# ── Endpoints ───────────────────────────────────────────────────────────────

@frappe.whitelist()
def search_material_transfers(txt=None, limit=20):
	"""Submitted Material Transfers made from a Roll Wise Pick List that
	haven't been put away yet. Newest first."""
	se = frappe.qb.DocType("Stock Entry")
	put_away = frappe.qb.DocType("Stock Entry").as_("pa")

	sub = (
		frappe.qb.from_(put_away)
		.select(put_away.custom_verified_from_stock_entry)
		.where(put_away.docstatus < 2)
		.where(put_away.custom_verified_from_stock_entry.isnotnull())
	)
	q = (
		frappe.qb.from_(se)
		.select(se.name, se.posting_date, se.to_warehouse, se.custom_roll_wise_pick_list)
		.where(se.docstatus == 1)
		.where(se.purpose == "Material Transfer")
		.where(se.custom_roll_wise_pick_list.isnotnull())
		.where(se.custom_roll_wise_pick_list != "")
		.where(se.name.notin(sub))
		.orderby(se.creation, order=frappe.qb.desc)
		.limit(min(cint(limit) or 20, 50))
	)
	if txt:
		like = f"%{txt}%"
		q = q.where(
			(se.name.like(like))
			| (se.custom_roll_wise_pick_list.like(like))
			| (se.to_warehouse.like(like))
		)
	return q.run(as_dict=True)


@frappe.whitelist()
def get_transfer_for_verification(stock_entry):
	"""stock_entry may be the raw scanned barcode text — see
	_resolve_stock_entry_name for what's accepted."""
	name = _resolve_stock_entry_name(stock_entry)
	se, pl, rolls = _load_transfer(name)

	if not rolls:
		frappe.throw(_(
			"Pick list {0} on {1} is a batch transfer — it has no individual rolls to verify"
		).format(frappe.bold(pl.name), frappe.bold(se.name)))

	existing = _existing_put_away(se.name)
	return {
		"stock_entry": se.name,
		"posting_date": str(se.posting_date) if se.posting_date else None,
		"company": se.company,
		"pick_list": pl.name,
		"source_warehouses": sorted({r["source_warehouse"] for r in rolls if r["source_warehouse"]}),
		"rolls": rolls,
		"total_rolls": len(rolls),
		"total_weight": round(sum(r["roll_weight"] for r in rolls), 3),
		"already_put_away": existing.name if existing else None,
		"already_put_away_status": (
			None if not existing else ("Submitted" if existing.docstatus == 1 else "Draft")
		),
	}


@frappe.whitelist()
def search_bins(txt=None, near_warehouse=None, company=None, limit=30):
	"""Leaf (non-group), enabled Warehouses usable as a bin.

	With no search text, lists the warehouses that share near_warehouse's
	parent (i.e. the bins sitting alongside where the rolls are now), so
	the common case needs no typing. Typing searches every bin in the
	company."""
	limit = min(cint(limit) or 30, 100)
	filters = {"is_group": 0, "disabled": 0}
	if company:
		filters["company"] = company

	if not txt and near_warehouse:
		parent = frappe.db.get_value("Warehouse", near_warehouse, "parent_warehouse")
		if parent:
			rows = frappe.get_all(
				"Warehouse",
				filters={**filters, "parent_warehouse": parent, "name": ["!=", near_warehouse]},
				fields=["name", "warehouse_name", "parent_warehouse"],
				order_by="name asc",
				limit_page_length=limit,
			)
			if rows:
				return rows

	or_filters = None
	if txt:
		or_filters = {
			"name": ["like", f"%{txt}%"],
			"warehouse_name": ["like", f"%{txt}%"],
			"parent_warehouse": ["like", f"%{txt}%"],
		}
	return frappe.get_all(
		"Warehouse",
		filters=filters,
		or_filters=or_filters,
		fields=["name", "warehouse_name", "parent_warehouse"],
		order_by="name asc",
		limit_page_length=limit,
	)


@frappe.whitelist(methods=["POST"])
def create_verified_transfer(stock_entry, rolls, posting_date=None, submit=1):
	"""Create the put-away Material Transfer.

	rolls: JSON list of {"roll_no": ..., "bin": ...} — must cover EVERY roll
	on the scanned entry's pick list, exactly once (the page only offers
	this step after all rolls are verified; this re-checks server-side).
	Source warehouse per roll is never taken from the client — it's always
	re-derived from the scanned Stock Entry.
	"""
	frappe.has_permission("Stock Entry", "create", throw=True)

	if isinstance(rolls, str):
		rolls = json.loads(rolls)
	if not isinstance(rolls, list) or not rolls:
		frappe.throw(_("No rolls sent"))

	name = _resolve_stock_entry_name(stock_entry)

	# Serialize concurrent put-aways of the same source entry (two devices
	# tapping "Yes" at once) — the second waits here, then sees the first.
	frappe.db.sql("SELECT name FROM `tabStock Entry` WHERE name = %s FOR UPDATE", name)

	existing = _existing_put_away(name)
	if existing:
		frappe.throw(_("Rolls of {0} were already put away in {1}").format(
			frappe.bold(name), frappe.bold(existing.name)))

	se_src, pl, expected = _load_transfer(name)
	expected_by_roll = {r["roll_no"]: r for r in expected}

	sent = {}
	for r in rolls:
		roll_no = (r.get("roll_no") or "").strip()
		bin_wh = (r.get("bin") or "").strip()
		if not roll_no:
			continue
		if roll_no in sent:
			frappe.throw(_("Roll {0} was sent twice").format(roll_no))
		if roll_no not in expected_by_roll:
			frappe.throw(_("Roll {0} is not on pick list {1}").format(roll_no, pl.name))
		if not bin_wh:
			frappe.throw(_("Select a bin for roll {0}").format(roll_no))
		sent[roll_no] = bin_wh

	missing = [r for r in expected_by_roll if r not in sent]
	if missing:
		frappe.throw(_("Not all rolls were verified — missing: {0}").format(", ".join(missing)))

	# Validate every bin once
	for bin_wh in set(sent.values()):
		wh = frappe.db.get_value("Warehouse", bin_wh, ["is_group", "disabled", "company"], as_dict=True)
		if not wh:
			frappe.throw(_("Bin {0} does not exist").format(frappe.bold(bin_wh)))
		if wh.is_group:
			frappe.throw(_("{0} is a group warehouse — pick a bin inside it").format(frappe.bold(bin_wh)))
		if wh.disabled:
			frappe.throw(_("Bin {0} is disabled").format(frappe.bold(bin_wh)))
		if wh.company and wh.company != se_src.company:
			frappe.throw(_("Bin {0} belongs to {1}, not {2}").format(
				frappe.bold(bin_wh), wh.company, se_src.company))

	# Group into Stock Entry rows by (item, batch, source, bin)
	grouped = {}
	for roll_no, bin_wh in sent.items():
		r = expected_by_roll[roll_no]
		if not r["source_warehouse"]:
			frappe.throw(_("Could not work out the source warehouse for roll {0}").format(roll_no))
		if r["source_warehouse"] == bin_wh:
			frappe.throw(_("Roll {0} is already in {1} — choose a different bin").format(
				roll_no, frappe.bold(bin_wh)))
		key = (r["item_code"], r["batch"], r["source_warehouse"], bin_wh)
		g = grouped.setdefault(key, {"qty": 0.0, "uom": r["uom"], "rolls": 0})
		g["qty"] += flt(r["qty"])
		g["rolls"] += 1

	sources = {k[2] for k in grouped}
	bins = {k[3] for k in grouped}

	se = frappe.new_doc("Stock Entry")
	if se_src.get("naming_series"):
		se.naming_series = se_src.naming_series
	se.stock_entry_type = "Material Transfer"
	se.purpose = "Material Transfer"
	se.company = se_src.company
	# posting_time must be set explicitly — the auto-built Serial and Batch
	# Bundles (use_serial_batch_fields=1) combine posting_date + posting_time
	# before Stock Entry.validate() would have defaulted it.
	se.set_posting_time = 1
	se.posting_date = posting_date or nowdate()
	se.posting_time = nowtime()
	if se_src.get("project"):
		se.project = se_src.project
	if len(sources) == 1:
		se.from_warehouse = next(iter(sources))
		se.source_warehouse_address = _get_warehouse_address(se.from_warehouse)
	if len(bins) == 1:
		se.to_warehouse = next(iter(bins))
		se.target_warehouse_address = _get_warehouse_address(se.to_warehouse)
	se.remarks = _("Roll put-away after verification of {0} (pick list {1})").format(se_src.name, pl.name)

	se.custom_verified_from_stock_entry = se_src.name

	for (item_code, batch, src, bin_wh), g in grouped.items():
		se.append("items", {
			"item_code": item_code,
			"s_warehouse": src,
			"t_warehouse": bin_wh,
			"qty": g["qty"],
			"transfer_qty": g["qty"],
			"uom": g["uom"],
			"stock_uom": g["uom"],
			"conversion_factor": 1,
			"batch_no": batch,
			"use_serial_batch_fields": 1 if batch else 0,
			"allow_zero_valuation_rate": 0,
		})

	for roll_no, bin_wh in sent.items():
		r = expected_by_roll[roll_no]
		se.append("custom_verified_rolls", {
			"roll_no": roll_no,
			"item_code": r["item_code"],
			"batch": r["batch"],
			"qty": r["qty"],
			"uom": r["uom"],
			"roll_weight": r["roll_weight"],
			"source_warehouse": r["source_warehouse"],
			"bin": bin_wh,
		})

	se.insert()
	if cint(submit):
		se.submit()

	return {
		"stock_entry": se.name,
		"submitted": bool(cint(submit)),
		"rolls": len(sent),
		"rows": len(se.items),
	}


# ── Doc events (registered in hooks.py) ─────────────────────────────────────

def validate_verified_transfer(doc, method=None):
	"""One live put-away per source entry. Also covers Duplicate/Amend from
	desk (no_copy clears the link on Duplicate; an Amend keeps it and is
	allowed because the original is cancelled by then)."""
	src = doc.get("custom_verified_from_stock_entry")
	if not src:
		return
	existing = _existing_put_away(src, exclude=doc.name)
	if existing:
		frappe.throw(_("Rolls of {0} were already put away in {1}").format(
			frappe.bold(src), frappe.bold(existing.name)))


def on_verified_transfer_submit(doc, method=None):
	if not doc.get("custom_verified_from_stock_entry"):
		return
	for row in doc.get("custom_verified_rolls") or []:
		if row.roll_no and row.bin and frappe.db.exists("Roll", row.roll_no):
			frappe.db.set_value("Roll", row.roll_no, "warehouse", row.bin, update_modified=False)


def on_verified_transfer_cancel(doc, method=None):
	if not doc.get("custom_verified_from_stock_entry"):
		return
	for row in doc.get("custom_verified_rolls") or []:
		if row.roll_no and row.source_warehouse and frappe.db.exists("Roll", row.roll_no):
			frappe.db.set_value("Roll", row.roll_no, "warehouse", row.source_warehouse, update_modified=False)
