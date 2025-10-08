# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

# import frappe
# from frappe import _
# from frappe.utils import add_to_date, cint, flt, get_datetime, get_table_name, getdate
# from frappe.utils.deprecations import deprecated
# from pypika import functions as fn

# from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter


# SLE_COUNT_LIMIT = 100_000


# def execute(filters=None):
# 	if not filters:
# 		filters = {}

# 	sle_count = frappe.db.estimate_count("Stock Ledger Entry")

# 	if (
# 		sle_count > SLE_COUNT_LIMIT
# 		and not filters.get("item_code")
# 		and not filters.get("warehouse")
# 		and not filters.get("warehouse_type")
# 	):
# 		frappe.throw(
# 			_("Please select either the Item or Warehouse or Warehouse Type filter to generate the report.")
# 		)

# 	if filters.from_date > filters.to_date:
# 		frappe.throw(_("From Date must be before To Date"))

# 	float_precision = cint(frappe.db.get_default("float_precision")) or 3

# 	columns = get_columns(filters)
# 	item_map = get_item_details(filters)
# 	iwb_map = get_item_warehouse_batch_map(filters, float_precision)

# 	# Get valid batches with batch_qty > 0 and disabled = 0 along with additional fields
# 	valid_batches = get_valid_batches_with_details()

# 	data = []
# 	for item in sorted(iwb_map):
# 		if not filters.get("item") or filters.get("item") == item:
# 			for wh in sorted(iwb_map[item]):
# 				for batch in sorted(iwb_map[item][wh]):
# 					# Filter out batches that don't meet the criteria
# 					if batch not in valid_batches:
# 						continue
						
# 					qty_dict = iwb_map[item][wh][batch]
					
# 					# Filter: Only include records where balance quantity is greater than 0
# 					if not (qty_dict.bal_qty > 0):
# 						continue
					
# 					# Get item type and parent batch information
# 					custom_item_type = item_map[item].get("custom_item_type", "")
# 					parent_batch = valid_batches.get(batch, {}).get("custom_parent_batch", "")
# 					batch_status = valid_batches.get(batch, {}).get("batch_status", "")
					
# 					# Get collar and cuff quantities for fabric items
# 					collar_qty = 0.0
# 					cuff_qty = 0.0
# 					qc_ok_qty = 0.0
# 					grade2_qty = 0.0
					
# 					if custom_item_type == "Fabric" and parent_batch:
# 						# Find all batches with the same parent batch
# 						related_batches = get_related_batches_by_parent(parent_batch, valid_batches)
						
# 						for related_batch, related_data in related_batches.items():
# 							related_item = get_item_from_batch(related_batch)
# 							if related_item and related_item in item_map:
# 								related_item_type = item_map[related_item].get("custom_item_type", "")
# 								related_batch_status = related_data.get("batch_status", "")
								
# 								# Get quantity for this related batch
# 								related_qty = get_batch_quantity(related_batch, wh, iwb_map, item_map)
								
# 								if related_item_type == "Collar":
# 									collar_qty += related_qty
# 								elif related_item_type == "Cuff":
# 									cuff_qty += related_qty
								
# 								# Track QC status quantities
# 								if related_batch_status == "QC Ok":
# 									qc_ok_qty += related_qty
# 								elif related_batch_status == "Grade 2":
# 									grade2_qty += related_qty
					
# 					# For non-fabric items or items without parent batch, use current batch status
# 					if custom_item_type != "Fabric" or not parent_batch:
# 						if batch_status == "QC OK":
# 							qc_ok_qty = qty_dict.bal_qty
# 						elif batch_status == "GRADE 2":
# 							grade2_qty = qty_dict.bal_qty
					
# 					if qty_dict.opening_qty or qty_dict.in_qty or qty_dict.out_qty or qty_dict.bal_qty:
# 						batch_details = valid_batches.get(batch, {})
# 						data.append(
# 							[
# 								item,
# 								item_map[item].get("commercial_name", ""),  # From Item
# 								item_map[item].get("color", ""),     # From Item
# 								item_map[item].get("width", 0),        # From Item
# 								item_map[item]["item_name"],
# 								wh,
# 								batch,
# 								batch_details.get("batch_status", ""),      # From Batch
# 								batch_details.get("custom_parent_batch", ""), # From Batch
# 								flt(qty_dict.bal_qty, float_precision),
# 								item_map[item]["stock_uom"],
# 								flt(qty_dict.opening_qty, float_precision),
# 								flt(qty_dict.in_qty, float_precision),
# 								flt(qty_dict.out_qty, float_precision),
# 								flt(qc_ok_qty, float_precision),  # QC Ok Qty
# 								flt(grade2_qty, float_precision), # Grade 2 Qty
# 								flt(collar_qty, float_precision), # Collar Qty
# 								flt(cuff_qty, float_precision),   # Cuff Qty
# 							]
# 						)

# 	return columns, data


# def get_related_batches_by_parent(parent_batch, valid_batches):
# 	"""Get all batches that have the same parent batch"""
# 	related_batches = {}
# 	for batch, batch_data in valid_batches.items():
# 		if batch_data.get("custom_parent_batch") == parent_batch:
# 			related_batches[batch] = batch_data
# 	return related_batches


# def get_item_from_batch(batch_no):
# 	"""Get item code from batch"""
# 	batch_item = frappe.db.get_value("Batch", batch_no, "item")
# 	return batch_item


# def get_batch_quantity(batch_no, warehouse, iwb_map, item_map):
# 	"""Get balance quantity for a batch in a warehouse"""
# 	for item in iwb_map:
# 		for wh in iwb_map[item]:
# 			if wh == warehouse and batch_no in iwb_map[item][wh]:
# 				return iwb_map[item][wh][batch_no].bal_qty
# 	return 0.0


# def get_valid_batches_with_details():
# 	"""Get batches where batch_qty > 0 and disabled = 0 with additional fields"""
# 	batch = frappe.qb.DocType("Batch")
# 	query = (
# 		frappe.qb.from_(batch)
# 		.select(
# 			batch.name,
# 			batch.item,
# 			batch.batch_status,
# 			batch.custom_parent_batch,
# 			batch.batch_status
# 		)
# 		.where((batch.batch_qty > 0))
# 	)
	
# 	valid_batches = {}
# 	for batch_data in query.run(as_dict=True):
# 		valid_batches[batch_data.name] = {
# 			"item": batch_data.item,
# 			"batch_status": batch_data.batch_status,
# 			"custom_parent_batch": batch_data.custom_parent_batch,
# 			"batch_status": batch_data.batch_status
# 		}
	
# 	return valid_batches


# def get_columns(filters):
# 	"""return columns based on filters"""

# 	columns = [
# 		_("Item") + ":Link/Item:290",
# 		_("Commercial Name") + "::210",      # New column
# 		_("color") + "::180",                # New column
# 		_("width") + "::60",            # New column
# 		_("Item Name") + "::150",
# 		_("Warehouse") + ":Link/Warehouse:100",
# 		_("Batch") + ":Link/Batch:100",
# 		_("Batch Status") + "::100",         # New column
# 		_("Parent Batch") + ":Link/Batch:100", # New column
# 		_("Balance Qty") + ":Float:90",
# 		_("UOM") + "::90",
# 		_("Opening Qty") + ":Float:90",
# 		_("In Qty") + ":Float:80",
# 		_("Out Qty") + ":Float:80",
# 		_("QC Ok Qty") + ":Float:80",    # New column
# 		_("Grade 2 Qty") + ":Float:80",  # New column
# 		_("Collar Qty") + ":Float:80",   # New column
# 		_("Cuff Qty") + ":Float:80",     # New column
# 	]

# 	return columns


# def get_stock_ledger_entries(filters):
# 	entries = get_stock_ledger_entries_for_batch_no(filters)

# 	entries += get_stock_ledger_entries_for_batch_bundle(filters)
# 	return entries


# @deprecated
# def get_stock_ledger_entries_for_batch_no(filters):
# 	if not filters.get("from_date"):
# 		frappe.throw(_("'From Date' is required"))
# 	if not filters.get("to_date"):
# 		frappe.throw(_("'To Date' is required"))

# 	posting_datetime = get_datetime(add_to_date(filters["to_date"], days=1))

# 	sle = frappe.qb.DocType("Stock Ledger Entry")
# 	query = (
# 		frappe.qb.from_(sle)
# 		.select(
# 			sle.item_code,
# 			sle.warehouse,
# 			sle.batch_no,
# 			sle.posting_date,
# 			fn.Sum(sle.actual_qty).as_("actual_qty"),
# 		)
# 		.where(
# 			(sle.docstatus < 2)
# 			& (sle.is_cancelled == 0)
# 			& (sle.batch_no != "")
# 			& (sle.posting_datetime < posting_datetime)
# 		)
# 		.groupby(sle.voucher_no, sle.batch_no, sle.item_code, sle.warehouse)
# 	)

# 	query = apply_warehouse_filter(query, sle, filters)
# 	if filters.warehouse_type and not filters.warehouse:
# 		warehouses = frappe.get_all(
# 			"Warehouse",
# 			filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
# 			pluck="name",
# 		)

# 		if warehouses:
# 			query = query.where(sle.warehouse.isin(warehouses))

# 	for field in ["item_code", "batch_no", "company"]:
# 		if filters.get(field):
# 			query = query.where(sle[field] == filters.get(field))

# 	return query.run(as_dict=True) or []


# def get_stock_ledger_entries_for_batch_bundle(filters):
# 	sle = frappe.qb.DocType("Stock Ledger Entry")
# 	batch_package = frappe.qb.DocType("Serial and Batch Entry")

# 	to_date = get_datetime(filters.to_date + " 23:59:59")

# 	query = (
# 		frappe.qb.from_(sle)
# 		.inner_join(batch_package)
# 		.on(batch_package.parent == sle.serial_and_batch_bundle)
# 		.select(
# 			sle.item_code,
# 			sle.warehouse,
# 			batch_package.batch_no,
# 			sle.posting_date,
# 			fn.Sum(batch_package.qty).as_("actual_qty"),
# 		)
# 		.where(
# 			(sle.docstatus < 2)
# 			& (sle.is_cancelled == 0)
# 			& (sle.has_batch_no == 1)
# 			& (sle.posting_datetime <= to_date)
# 		)
# 		.groupby(sle.voucher_no, batch_package.batch_no, batch_package.warehouse)
# 	)

# 	query = apply_warehouse_filter(query, sle, filters)
# 	if filters.warehouse_type and not filters.warehouse:
# 		warehouses = frappe.get_all(
# 			"Warehouse",
# 			filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
# 			pluck="name",
# 		)

# 		if warehouses:
# 			query = query.where(sle.warehouse.isin(warehouses))

# 	for field in ["item_code", "batch_no", "company"]:
# 		if filters.get(field):
# 			if field == "batch_no":
# 				query = query.where(batch_package[field] == filters.get(field))
# 			else:
# 				query = query.where(sle[field] == filters.get(field))

# 	return query.run(as_dict=True) or []


# def get_item_warehouse_batch_map(filters, float_precision):
# 	sle = get_stock_ledger_entries(filters)
# 	iwb_map = {}

# 	from_date = getdate(filters["from_date"])
# 	to_date = getdate(filters["to_date"])

# 	for d in sle:
# 		iwb_map.setdefault(d.item_code, {}).setdefault(d.warehouse, {}).setdefault(
# 			d.batch_no, frappe._dict({"opening_qty": 0.0, "in_qty": 0.0, "out_qty": 0.0, "bal_qty": 0.0})
# 		)
# 		qty_dict = iwb_map[d.item_code][d.warehouse][d.batch_no]
# 		if d.posting_date < from_date:
# 			qty_dict.opening_qty = flt(qty_dict.opening_qty, float_precision) + flt(
# 				d.actual_qty, float_precision
# 			)
# 		elif d.posting_date >= from_date and d.posting_date <= to_date:
# 			if flt(d.actual_qty) > 0:
# 				qty_dict.in_qty = flt(qty_dict.in_qty, float_precision) + flt(d.actual_qty, float_precision)
# 			else:
# 				qty_dict.out_qty = flt(qty_dict.out_qty, float_precision) + abs(
# 					flt(d.actual_qty, float_precision)
# 				)

# 		qty_dict.bal_qty = flt(qty_dict.bal_qty, float_precision) + flt(d.actual_qty, float_precision)

# 	return iwb_map


# def get_item_details(filters):
# 	"""Get item details including additional fields"""
# 	item_map = {}
# 	query = (
# 		frappe.qb.from_("Item")
# 		.select(
# 			"name", 
# 			"item_name", 
# 			"description", 
# 			"stock_uom",
# 			"commercial_name",
# 			"color",
# 			"width",
# 			"custom_item_type"  # Added custom_item_type field
# 		)
# 	)
	
# 	for d in query.run(as_dict=True):
# 		item_map[d.name] = d

# 	return item_map


# import frappe
# from frappe import _
# from frappe.utils import add_to_date, cint, flt, get_datetime, get_table_name, getdate
# from frappe.utils.deprecations import deprecated
# from pypika import functions as fn

# from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter


# SLE_COUNT_LIMIT = 100_000


# def execute(filters=None):
# 	if not filters:
# 		filters = {}

# 	sle_count = frappe.db.estimate_count("Stock Ledger Entry")

# 	if (
# 		sle_count > SLE_COUNT_LIMIT
# 		and not filters.get("item_code")
# 		and not filters.get("warehouse")
# 		and not filters.get("warehouse_type")
# 	):
# 		frappe.throw(
# 			_("Please select either the Item or Warehouse or Warehouse Type filter to generate the report.")
# 		)

# 	if filters.from_date > filters.to_date:
# 		frappe.throw(_("From Date must be before To Date"))

# 	float_precision = cint(frappe.db.get_default("float_precision")) or 3

# 	columns = get_columns(filters)
# 	item_map = get_item_details(filters)
# 	iwb_map = get_item_warehouse_batch_map(filters, float_precision)

# 	# Get all batches with details (not just valid ones for better relationship mapping)
# 	all_batches = get_all_batches_with_details()
	
# 	# Pre-calculate related quantities for better performance
# 	related_quantities_map = precalculate_related_quantities(iwb_map, all_batches, item_map)

# 	data = []
# 	for item in sorted(iwb_map):
# 		if not filters.get("item") or filters.get("item") == item:
# 			for wh in sorted(iwb_map[item]):
# 				for batch in sorted(iwb_map[item][wh]):
# 					qty_dict = iwb_map[item][wh][batch]
					
# 					# Filter: Only include records where balance quantity is greater than 0
# 					if not (qty_dict.bal_qty > 0):
# 						continue
					
# 					# Get item type and batch details
# 					custom_item_type = item_map.get(item, {}).get("custom_item_type", "")
# 					batch_details = all_batches.get(batch, {})
# 					parent_batch = batch_details.get("custom_parent_batch", "")
# 					batch_status = batch_details.get("batch_status", "")
					
# 					# Initialize quantities
# 					qc_ok_qty = 0.0
# 					grade2_qty = 0.0
# 					collar_qty = 0.0
# 					cuff_qty = 0.0
					
# 					# For fabric items with parent batch, get related quantities
# 					if custom_item_type == "Fabric" and parent_batch:
# 						related_key = f"{parent_batch}|{wh}"
# 						if related_key in related_quantities_map:
# 							related_data = related_quantities_map[related_key]
# 							collar_qty = related_data.get("collar_qty", 0.0)
# 							cuff_qty = related_data.get("cuff_qty", 0.0)
# 							qc_ok_qty = related_data.get("qc_ok_qty", 0.0)
# 							grade2_qty = related_data.get("grade2_qty", 0.0)
# 					else:
# 						# For non-fabric items or items without parent batch
# 						if batch_status == "QC OK":
# 							qc_ok_qty = qty_dict.bal_qty
# 						elif batch_status == "GRADE 2":
# 							grade2_qty = qty_dict.bal_qty
					
# 					# For collar/cuff items themselves, show their own quantities
# 					if custom_item_type == "Collar":
# 						collar_qty = qty_dict.bal_qty
# 					elif custom_item_type == "Cuff":
# 						cuff_qty = qty_dict.bal_qty
					
# 					if qty_dict.opening_qty or qty_dict.in_qty or qty_dict.out_qty or qty_dict.bal_qty:
# 						data.append(
# 							[
# 								item,
# 								item_map.get(item, {}).get("commercial_name", ""),
# 								item_map.get(item, {}).get("color", ""),
# 								item_map.get(item, {}).get("width", 0),
# 								item_map.get(item, {}).get("item_name", ""),
# 								wh,
# 								batch,
# 								batch_status,
# 								parent_batch,
# 								flt(qty_dict.bal_qty, float_precision),
# 								item_map.get(item, {}).get("stock_uom", ""),
# 								flt(qty_dict.opening_qty, float_precision),
# 								flt(qty_dict.in_qty, float_precision),
# 								flt(qty_dict.out_qty, float_precision),
# 								flt(qc_ok_qty, float_precision),
# 								flt(grade2_qty, float_precision),
# 								flt(collar_qty, float_precision),
# 								flt(cuff_qty, float_precision),
# 							]
# 						)

# 	return columns, data


# def precalculate_related_quantities(iwb_map, all_batches, item_map):
# 	"""Pre-calculate related quantities for better performance"""
# 	related_quantities_map = {}
	
# 	# First, build a map of parent batch to all child batches
# 	parent_child_map = {}
# 	for batch, batch_data in all_batches.items():
# 		parent_batch = batch_data.get("custom_parent_batch")
# 		if parent_batch:
# 			if parent_batch not in parent_child_map:
# 				parent_child_map[parent_batch] = []
# 			parent_child_map[parent_batch].append(batch)
	
# 	# Now calculate quantities for each parent batch in each warehouse
# 	for parent_batch, child_batches in parent_child_map.items():
# 		for child_batch in child_batches:
# 			child_item = all_batches.get(child_batch, {}).get("item")
# 			child_item_type = item_map.get(child_item, {}).get("custom_item_type", "")
# 			child_batch_status = all_batches.get(child_batch, {}).get("batch_status", "")
			
# 			# Find all warehouses where this child batch has stock
# 			for item in iwb_map:
# 				for wh in iwb_map[item]:
# 					if child_batch in iwb_map[item][wh]:
# 						qty_dict = iwb_map[item][wh][child_batch]
# 						if qty_dict.bal_qty > 0:
# 							related_key = f"{parent_batch}|{wh}"
# 							if related_key not in related_quantities_map:
# 								related_quantities_map[related_key] = {
# 									"collar_qty": 0.0,
# 									"cuff_qty": 0.0,
# 									"qc_ok_qty": 0.0,
# 									"grade2_qty": 0.0
# 								}
							
# 							# Add to collar/cuff quantities
# 							if child_item_type == "Collar":
# 								related_quantities_map[related_key]["collar_qty"] += qty_dict.bal_qty
# 							elif child_item_type == "Cuff":
# 								related_quantities_map[related_key]["cuff_qty"] += qty_dict.bal_qty
							
# 							# Add to QC status quantities
# 							if child_batch_status == "QC OK":
# 								related_quantities_map[related_key]["qc_ok_qty"] += qty_dict.bal_qty
# 							elif child_batch_status == "GRADE 2":
# 								related_quantities_map[related_key]["grade2_qty"] += qty_dict.bal_qty
	
# 	return related_quantities_map


# def get_all_batches_with_details():
# 	"""Get all batches with details (not filtering by batch_qty > 0)"""
# 	batch = frappe.qb.DocType("Batch")
# 	query = (
# 		frappe.qb.from_(batch)
# 		.select(
# 			batch.name,
# 			batch.item,
# 			batch.batch_status,
# 			batch.custom_parent_batch,
# 			batch.batch_status,
# 			batch.batch_qty
# 		)
# 	)
	
# 	all_batches = {}
# 	for batch_data in query.run(as_dict=True):
# 		all_batches[batch_data.name] = {
# 			"item": batch_data.item,
# 			"batch_status": batch_data.batch_status,
# 			"custom_parent_batch": batch_data.custom_parent_batch,
# 			"batch_status": batch_data.batch_status,
# 			"batch_qty": batch_data.batch_qty
# 		}
	
# 	return all_batches


# def get_columns(filters):
# 	"""return columns based on filters"""

# 	columns = [
# 		_("Item") + ":Link/Item:290",
# 		_("Commercial Name") + "::210",
# 		_("color") + "::180",
# 		_("width") + "::60",
# 		_("Item Name") + "::150",
# 		_("Warehouse") + ":Link/Warehouse:100",
# 		_("Batch") + ":Link/Batch:100",
# 		_("Batch Status") + "::100",
# 		_("Parent Batch") + ":Link/Batch:100",
# 		_("Balance Qty") + ":Float:90",
# 		_("UOM") + "::90",
# 		_("QC Ok Qty") + ":Float:80",
# 		_("Grade 2 Qty") + ":Float:80",
# 		_("Collar Qty") + ":Float:80",
# 		_("Cuff Qty") + ":Float:80",
# 	]

# 	return columns


# def get_stock_ledger_entries(filters):
# 	entries = get_stock_ledger_entries_for_batch_no(filters)

# 	entries += get_stock_ledger_entries_for_batch_bundle(filters)
# 	return entries


# @deprecated
# def get_stock_ledger_entries_for_batch_no(filters):
# 	if not filters.get("from_date"):
# 		frappe.throw(_("'From Date' is required"))
# 	if not filters.get("to_date"):
# 		frappe.throw(_("'To Date' is required"))

# 	posting_datetime = get_datetime(add_to_date(filters["to_date"], days=1))

# 	sle = frappe.qb.DocType("Stock Ledger Entry")
# 	query = (
# 		frappe.qb.from_(sle)
# 		.select(
# 			sle.item_code,
# 			sle.warehouse,
# 			sle.batch_no,
# 			sle.posting_date,
# 			fn.Sum(sle.actual_qty).as_("actual_qty"),
# 		)
# 		.where(
# 			(sle.docstatus < 2)
# 			& (sle.is_cancelled == 0)
# 			& (sle.batch_no != "")
# 			& (sle.posting_datetime < posting_datetime)
# 		)
# 		.groupby(sle.voucher_no, sle.batch_no, sle.item_code, sle.warehouse)
# 	)

# 	query = apply_warehouse_filter(query, sle, filters)
# 	if filters.warehouse_type and not filters.warehouse:
# 		warehouses = frappe.get_all(
# 			"Warehouse",
# 			filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
# 			pluck="name",
# 		)

# 		if warehouses:
# 			query = query.where(sle.warehouse.isin(warehouses))

# 	for field in ["item_code", "batch_no", "company"]:
# 		if filters.get(field):
# 			query = query.where(sle[field] == filters.get(field))

# 	return query.run(as_dict=True) or []


# def get_stock_ledger_entries_for_batch_bundle(filters):
# 	sle = frappe.qb.DocType("Stock Ledger Entry")
# 	batch_package = frappe.qb.DocType("Serial and Batch Entry")

# 	to_date = get_datetime(filters.to_date + " 23:59:59")

# 	query = (
# 		frappe.qb.from_(sle)
# 		.inner_join(batch_package)
# 		.on(batch_package.parent == sle.serial_and_batch_bundle)
# 		.select(
# 			sle.item_code,
# 			sle.warehouse,
# 			batch_package.batch_no,
# 			sle.posting_date,
# 			fn.Sum(batch_package.qty).as_("actual_qty"),
# 		)
# 		.where(
# 			(sle.docstatus < 2)
# 			& (sle.is_cancelled == 0)
# 			& (sle.has_batch_no == 1)
# 			& (sle.posting_datetime <= to_date)
# 		)
# 		.groupby(sle.voucher_no, batch_package.batch_no, batch_package.warehouse)
# 	)

# 	query = apply_warehouse_filter(query, sle, filters)
# 	if filters.warehouse_type and not filters.warehouse:
# 		warehouses = frappe.get_all(
# 			"Warehouse",
# 			filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
# 			pluck="name",
# 		)

# 		if warehouses:
# 			query = query.where(sle.warehouse.isin(warehouses))

# 	for field in ["item_code", "batch_no", "company"]:
# 		if filters.get(field):
# 			if field == "batch_no":
# 				query = query.where(batch_package[field] == filters.get(field))
# 			else:
# 				query = query.where(sle[field] == filters.get(field))

# 	return query.run(as_dict=True) or []


# def get_item_warehouse_batch_map(filters, float_precision):
# 	sle = get_stock_ledger_entries(filters)
# 	iwb_map = {}

# 	from_date = getdate(filters["from_date"])
# 	to_date = getdate(filters["to_date"])

# 	for d in sle:
# 		iwb_map.setdefault(d.item_code, {}).setdefault(d.warehouse, {}).setdefault(
# 			d.batch_no, frappe._dict({"opening_qty": 0.0, "in_qty": 0.0, "out_qty": 0.0, "bal_qty": 0.0})
# 		)
# 		qty_dict = iwb_map[d.item_code][d.warehouse][d.batch_no]
# 		if d.posting_date < from_date:
# 			qty_dict.opening_qty = flt(qty_dict.opening_qty, float_precision) + flt(
# 				d.actual_qty, float_precision
# 			)
# 		elif d.posting_date >= from_date and d.posting_date <= to_date:
# 			if flt(d.actual_qty) > 0:
# 				qty_dict.in_qty = flt(qty_dict.in_qty, float_precision) + flt(d.actual_qty, float_precision)
# 			else:
# 				qty_dict.out_qty = flt(qty_dict.out_qty, float_precision) + abs(
# 					flt(d.actual_qty, float_precision)
# 				)

# 		qty_dict.bal_qty = flt(qty_dict.bal_qty, float_precision) + flt(d.actual_qty, float_precision)

# 	return iwb_map


# def get_item_details(filters):
# 	"""Get item details including additional fields"""
# 	item_map = {}
# 	query = (
# 		frappe.qb.from_("Item")
# 		.select(
# 			"name", 
# 			"item_name", 
# 			"description", 
# 			"stock_uom",
# 			"commercial_name",
# 			"color",
# 			"width",
# 			"custom_item_type"
# 		)
# 	)
	
# 	for d in query.run(as_dict=True):
# 		item_map[d.name] = d

# 	return item_map


# import frappe
# from frappe import _
# from frappe.utils import add_to_date, cint, flt, get_datetime, get_table_name, getdate
# from frappe.utils.deprecations import deprecated
# from pypika import functions as fn

# from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter


# SLE_COUNT_LIMIT = 100_000


# def execute(filters=None):
# 	if not filters:
# 		filters = {}

# 	sle_count = frappe.db.estimate_count("Stock Ledger Entry")

# 	if (
# 		sle_count > SLE_COUNT_LIMIT
# 		and not filters.get("item_code")
# 		and not filters.get("warehouse")
# 		and not filters.get("warehouse_type")
# 	):
# 		frappe.throw(
# 			_("Please select either the Item or Warehouse or Warehouse Type filter to generate the report.")
# 		)

# 	if filters.from_date > filters.to_date:
# 		frappe.throw(_("From Date must be before To Date"))

# 	float_precision = cint(frappe.db.get_default("float_precision")) or 3

# 	columns = get_columns(filters)
# 	item_map = get_item_details(filters)
# 	iwb_map = get_item_warehouse_batch_map(filters, float_precision)

# 	# Get all batches with details (not just valid ones for better relationship mapping)
# 	all_batches = get_all_batches_with_details()
	
# 	# Pre-calculate related quantities for better performance
# 	related_quantities_map = precalculate_related_quantities(iwb_map, all_batches, item_map)

# 	data = []
# 	for item in sorted(iwb_map):
# 		if not filters.get("item") or filters.get("item") == item:
# 			for wh in sorted(iwb_map[item]):
# 				for batch in sorted(iwb_map[item][wh]):
# 					qty_dict = iwb_map[item][wh][batch]
					
# 					# Filter: Only include records where balance quantity is greater than 0
# 					if not (qty_dict.bal_qty > 0):
# 						continue
					
# 					# Get item details
# 					item_details = item_map.get(item, {})
# 					custom_item_type = item_details.get("custom_item_type", "")
# 					commercial_name = item_details.get("commercial_name", "")
# 					color = item_details.get("color", "")
					
# 					# Apply filters for commercial_name, color, and custom_item_type
# 					if filters.get("commercial_name") and commercial_name != filters.get("commercial_name"):
# 						continue
					
# 					if filters.get("color") and color != filters.get("color"):
# 						continue
						
# 					if filters.get("custom_item_type") and custom_item_type != filters.get("custom_item_type"):
# 						continue
					
# 					batch_details = all_batches.get(batch, {})
# 					parent_batch = batch_details.get("custom_parent_batch", "")
# 					batch_status = batch_details.get("batch_status", "")
					
# 					# Apply batch_status filter
# 					if filters.get("batch_status") and batch_status != filters.get("batch_status"):
# 						continue
					
# 					# Initialize quantities
# 					qc_ok_qty = 0.0
# 					grade2_qty = 0.0
# 					collar_qty = 0.0
# 					cuff_qty = 0.0
					
# 					# For fabric items with parent batch, get related quantities
# 					if custom_item_type == "Fabric" and parent_batch:
# 						related_key = f"{parent_batch}|{wh}"
# 						if related_key in related_quantities_map:
# 							related_data = related_quantities_map[related_key]
# 							collar_qty = related_data.get("collar_qty", 0.0)
# 							cuff_qty = related_data.get("cuff_qty", 0.0)
# 							qc_ok_qty = related_data.get("qc_ok_qty", 0.0)
# 							grade2_qty = related_data.get("grade2_qty", 0.0)
# 					else:
# 						# For non-fabric items or items without parent batch
# 						if batch_status == "QC OK":
# 							qc_ok_qty = qty_dict.bal_qty
# 						elif batch_status == "GRADE 2":
# 							grade2_qty = qty_dict.bal_qty
					
# 					# For collar/cuff items themselves, show their own quantities
# 					if custom_item_type == "Collar":
# 						collar_qty = qty_dict.bal_qty
# 					elif custom_item_type == "Cuff":
# 						cuff_qty = qty_dict.bal_qty
					
# 					if qty_dict.opening_qty or qty_dict.in_qty or qty_dict.out_qty or qty_dict.bal_qty:
# 						data.append(
# 							[
# 								item,
# 								commercial_name,
# 								color,
# 								item_details.get("width", 0),
# 								item_details.get("item_name", ""),
# 								wh,
# 								batch,
# 								batch_status,
# 								parent_batch,
# 								flt(qty_dict.bal_qty, float_precision),
# 								item_details.get("stock_uom", ""),
# 								flt(qty_dict.opening_qty, float_precision),
# 								flt(qty_dict.in_qty, float_precision),
# 								flt(qty_dict.out_qty, float_precision),
# 								flt(qc_ok_qty, float_precision),
# 								flt(grade2_qty, float_precision),
# 								flt(collar_qty, float_precision),
# 								flt(cuff_qty, float_precision),
# 							]
# 						)

# 	return columns, data


# def precalculate_related_quantities(iwb_map, all_batches, item_map):
# 	"""Pre-calculate related quantities for better performance"""
# 	related_quantities_map = {}
	
# 	# First, build a map of parent batch to all child batches
# 	parent_child_map = {}
# 	for batch, batch_data in all_batches.items():
# 		parent_batch = batch_data.get("custom_parent_batch")
# 		if parent_batch:
# 			if parent_batch not in parent_child_map:
# 				parent_child_map[parent_batch] = []
# 			parent_child_map[parent_batch].append(batch)
	
# 	# Now calculate quantities for each parent batch in each warehouse
# 	for parent_batch, child_batches in parent_child_map.items():
# 		for child_batch in child_batches:
# 			child_item = all_batches.get(child_batch, {}).get("item")
# 			child_item_type = item_map.get(child_item, {}).get("custom_item_type", "")
# 			child_batch_status = all_batches.get(child_batch, {}).get("batch_status", "")
			
# 			# Find all warehouses where this child batch has stock
# 			for item in iwb_map:
# 				for wh in iwb_map[item]:
# 					if child_batch in iwb_map[item][wh]:
# 						qty_dict = iwb_map[item][wh][child_batch]
# 						if qty_dict.bal_qty > 0:
# 							related_key = f"{parent_batch}|{wh}"
# 							if related_key not in related_quantities_map:
# 								related_quantities_map[related_key] = {
# 									"collar_qty": 0.0,
# 									"cuff_qty": 0.0,
# 									"qc_ok_qty": 0.0,
# 									"grade2_qty": 0.0
# 								}
							
# 							# Add to collar/cuff quantities
# 							if child_item_type == "Collar":
# 								related_quantities_map[related_key]["collar_qty"] += qty_dict.bal_qty
# 							elif child_item_type == "Cuff":
# 								related_quantities_map[related_key]["cuff_qty"] += qty_dict.bal_qty
							
# 							# Add to QC status quantities
# 							if child_batch_status == "QC OK":
# 								related_quantities_map[related_key]["qc_ok_qty"] += qty_dict.bal_qty
# 							elif child_batch_status == "GRADE 2":
# 								related_quantities_map[related_key]["grade2_qty"] += qty_dict.bal_qty
	
# 	return related_quantities_map


# def get_all_batches_with_details():
# 	"""Get all batches with details (not filtering by batch_qty > 0)"""
# 	batch = frappe.qb.DocType("Batch")
# 	query = (
# 		frappe.qb.from_(batch)
# 		.select(
# 			batch.name,
# 			batch.item,
# 			batch.batch_status,
# 			batch.custom_parent_batch,
# 			batch.batch_status,
# 			batch.batch_qty
# 		)
# 	)
	
# 	all_batches = {}
# 	for batch_data in query.run(as_dict=True):
# 		all_batches[batch_data.name] = {
# 			"item": batch_data.item,
# 			"batch_status": batch_data.batch_status,
# 			"custom_parent_batch": batch_data.custom_parent_batch,
# 			"batch_status": batch_data.batch_status,
# 			"batch_qty": batch_data.batch_qty
# 		}
	
# 	return all_batches


# def get_columns(filters):
# 	"""return columns based on filters"""

# 	columns = [
# 		_("Item") + ":Link/Item:290",
# 		_("Commercial Name") + "::210",
# 		_("color") + "::180",
# 		_("width") + "::60",
# 		_("Item Name") + "::150",
# 		_("Warehouse") + ":Link/Warehouse:100",
# 		_("Batch") + ":Link/Batch:100",
# 		_("Batch Status") + "::100",
# 		_("Parent Batch") + ":Link/Batch:100",
# 		_("Balance Qty") + ":Float:90",
# 		_("UOM") + "::90",
# 		_("QC Ok Qty") + ":Float:80",
# 		_("Grade 2 Qty") + ":Float:80",
# 		_("Collar Qty") + ":Float:80",
# 		_("Cuff Qty") + ":Float:80",
# 	]

# 	return columns


# def get_stock_ledger_entries(filters):
# 	entries = get_stock_ledger_entries_for_batch_no(filters)

# 	entries += get_stock_ledger_entries_for_batch_bundle(filters)
# 	return entries


# @deprecated
# def get_stock_ledger_entries_for_batch_no(filters):
# 	if not filters.get("from_date"):
# 		frappe.throw(_("'From Date' is required"))
# 	if not filters.get("to_date"):
# 		frappe.throw(_("'To Date' is required"))

# 	posting_datetime = get_datetime(add_to_date(filters["to_date"], days=1))

# 	sle = frappe.qb.DocType("Stock Ledger Entry")
# 	query = (
# 		frappe.qb.from_(sle)
# 		.select(
# 			sle.item_code,
# 			sle.warehouse,
# 			sle.batch_no,
# 			sle.posting_date,
# 			fn.Sum(sle.actual_qty).as_("actual_qty"),
# 		)
# 		.where(
# 			(sle.docstatus < 2)
# 			& (sle.is_cancelled == 0)
# 			& (sle.batch_no != "")
# 			& (sle.posting_datetime < posting_datetime)
# 		)
# 		.groupby(sle.voucher_no, sle.batch_no, sle.item_code, sle.warehouse)
# 	)

# 	query = apply_warehouse_filter(query, sle, filters)
# 	if filters.warehouse_type and not filters.warehouse:
# 		warehouses = frappe.get_all(
# 			"Warehouse",
# 			filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
# 			pluck="name",
# 		)

# 		if warehouses:
# 			query = query.where(sle.warehouse.isin(warehouses))

# 	for field in ["item_code", "batch_no", "company"]:
# 		if filters.get(field):
# 			query = query.where(sle[field] == filters.get(field))

# 	return query.run(as_dict=True) or []


# def get_stock_ledger_entries_for_batch_bundle(filters):
# 	sle = frappe.qb.DocType("Stock Ledger Entry")
# 	batch_package = frappe.qb.DocType("Serial and Batch Entry")

# 	to_date = get_datetime(filters.to_date + " 23:59:59")

# 	query = (
# 		frappe.qb.from_(sle)
# 		.inner_join(batch_package)
# 		.on(batch_package.parent == sle.serial_and_batch_bundle)
# 		.select(
# 			sle.item_code,
# 			sle.warehouse,
# 			batch_package.batch_no,
# 			sle.posting_date,
# 			fn.Sum(batch_package.qty).as_("actual_qty"),
# 		)
# 		.where(
# 			(sle.docstatus < 2)
# 			& (sle.is_cancelled == 0)
# 			& (sle.has_batch_no == 1)
# 			& (sle.posting_datetime <= to_date)
# 		)
# 		.groupby(sle.voucher_no, batch_package.batch_no, batch_package.warehouse)
# 	)

# 	query = apply_warehouse_filter(query, sle, filters)
# 	if filters.warehouse_type and not filters.warehouse:
# 		warehouses = frappe.get_all(
# 			"Warehouse",
# 			filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
# 			pluck="name",
# 		)

# 		if warehouses:
# 			query = query.where(sle.warehouse.isin(warehouses))

# 	for field in ["item_code", "batch_no", "company"]:
# 		if filters.get(field):
# 			if field == "batch_no":
# 				query = query.where(batch_package[field] == filters.get(field))
# 			else:
# 				query = query.where(sle[field] == filters.get(field))

# 	return query.run(as_dict=True) or []


# def get_item_warehouse_batch_map(filters, float_precision):
# 	sle = get_stock_ledger_entries(filters)
# 	iwb_map = {}

# 	from_date = getdate(filters["from_date"])
# 	to_date = getdate(filters["to_date"])

# 	for d in sle:
# 		iwb_map.setdefault(d.item_code, {}).setdefault(d.warehouse, {}).setdefault(
# 			d.batch_no, frappe._dict({"opening_qty": 0.0, "in_qty": 0.0, "out_qty": 0.0, "bal_qty": 0.0})
# 		)
# 		qty_dict = iwb_map[d.item_code][d.warehouse][d.batch_no]
# 		if d.posting_date < from_date:
# 			qty_dict.opening_qty = flt(qty_dict.opening_qty, float_precision) + flt(
# 				d.actual_qty, float_precision
# 			)
# 		elif d.posting_date >= from_date and d.posting_date <= to_date:
# 			if flt(d.actual_qty) > 0:
# 				qty_dict.in_qty = flt(qty_dict.in_qty, float_precision) + flt(d.actual_qty, float_precision)
# 			else:
# 				qty_dict.out_qty = flt(qty_dict.out_qty, float_precision) + abs(
# 					flt(d.actual_qty, float_precision)
# 				)

# 		qty_dict.bal_qty = flt(qty_dict.bal_qty, float_precision) + flt(d.actual_qty, float_precision)

# 	return iwb_map


# def get_item_details(filters):
# 	"""Get item details including additional fields with filtering"""
# 	item_map = {}
	
# 	item = frappe.qb.DocType("Item")
# 	query = (
# 		frappe.qb.from_(item)
# 		.select(
# 			item.name, 
# 			item.item_name, 
# 			item.description, 
# 			item.stock_uom,
# 			item.commercial_name,
# 			item.color,
# 			item.width,
# 			item.custom_item_type
# 		)
# 		.where(item.has_batch_no == 1)
# 	)
	
# 	# Apply filters for commercial_name, color, and custom_item_type
# 	if filters.get("commercial_name"):
# 		query = query.where(item.commercial_name == filters.get("commercial_name"))
	
# 	if filters.get("color"):
# 		query = query.where(item.color == filters.get("color"))
		
# 	if filters.get("custom_item_type"):
# 		query = query.where(item.custom_item_type == filters.get("custom_item_type"))
	
# 	for d in query.run(as_dict=True):
# 		item_map[d.name] = d

# 	return item_map


# import frappe
# from frappe import _
# from frappe.utils import add_to_date, cint, flt, get_datetime, get_table_name, getdate
# from frappe.utils.deprecations import deprecated
# from pypika import functions as fn

# from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter


# SLE_COUNT_LIMIT = 100_000


# def execute(filters=None):
# 	if not filters:
# 		filters = {}

# 	sle_count = frappe.db.estimate_count("Stock Ledger Entry")

# 	if (
# 		sle_count > SLE_COUNT_LIMIT
# 		and not filters.get("item_code")
# 		and not filters.get("warehouse")
# 		and not filters.get("warehouse_type")
# 	):
# 		frappe.throw(
# 			_("Please select either the Item or Warehouse or Warehouse Type filter to generate the report.")
# 		)

# 	if filters.from_date > filters.to_date:
# 		frappe.throw(_("From Date must be before To Date"))

# 	float_precision = cint(frappe.db.get_default("float_precision")) or 3

# 	columns = get_columns(filters)
# 	item_map = get_item_details(filters)
# 	iwb_map = get_item_warehouse_batch_map(filters, float_precision)

# 	all_batches = get_all_batches_with_details()
# 	warehouse_map = get_warehouse_details()

# 	# Precalculate collar/cuff totals
# 	related_quantities_map = precalculate_related_quantities(iwb_map, all_batches, item_map, warehouse_map)

# 	# Intermediate grouping for Fabric items
# 	grouped_data = {}

# 	for item in iwb_map:
# 		item_details = item_map.get(item, {})
# 		custom_item_type = item_details.get("custom_item_type", "")
# 		if custom_item_type != "Fabric":
# 			continue  # Skip all non-fabric items

# 		for wh in iwb_map[item]:
# 			warehouse_details = warehouse_map.get(wh, {})
# 			custom_parentwarehouse = warehouse_details.get("custom_parentwarehouse", "")

# 			for batch in iwb_map[item][wh]:
# 				qty_dict = iwb_map[item][wh][batch]
# 				if not (qty_dict.bal_qty > 0):
# 					continue

# 				batch_details = all_batches.get(batch, {})
# 				parent_batch = batch_details.get("custom_parent_batch", "")
# 				batch_status = batch_details.get("batch_status", "")

# 				# Filtering by user filters
# 				if filters.get("batch_status") and batch_status != filters.get("batch_status"):
# 					continue

# 				commercial_name = item_details.get("commercial_name", "")
# 				color = item_details.get("color", "")
# 				width = item_details.get("width", 0)
# 				item_name = item_details.get("item_name", "")
# 				uom = item_details.get("stock_uom", "")

# 				# Aggregate key for grouping
# 				group_key = f"{parent_batch}|{custom_parentwarehouse}"

# 				if group_key not in grouped_data:
# 					grouped_data[group_key] = {
# 						"item": item,
# 						"commercial_name": commercial_name,
# 						"color": color,
# 						"width": width,
# 						"item_name": item_name,
# 						"custom_item_type": custom_item_type,
# 						"warehouse": wh,
# 						"parent_warehouse": custom_parentwarehouse,
# 						"parent_batch": parent_batch,
# 						"bal_qty": 0.0,
# 						"qc_ok_qty": 0.0,
# 						"grade2_qty": 0.0,
# 						"collar_qty": 0.0,
# 						"cuff_qty": 0.0,
# 						"uom": uom,
# 					}

# 				# Add up balance qty for all fabric batches
# 				grouped_data[group_key]["bal_qty"] += flt(qty_dict.bal_qty, float_precision)

# 				# QC category split
# 				if batch_status == "QC OK":
# 					grouped_data[group_key]["qc_ok_qty"] += flt(qty_dict.bal_qty, float_precision)
# 				elif batch_status == "GRADE 2":
# 					grouped_data[group_key]["grade2_qty"] += flt(qty_dict.bal_qty, float_precision)

# 				# Add related collar/cuff quantities (if exist)
# 				if group_key in related_quantities_map:
# 					related = related_quantities_map[group_key]
# 					grouped_data[group_key]["collar_qty"] += flt(related.get("collar_qty", 0.0), float_precision)
# 					grouped_data[group_key]["cuff_qty"] += flt(related.get("cuff_qty", 0.0), float_precision)

# 	data = []
# 	for key, row in grouped_data.items():
# 		data.append([
# 			row["item"],
# 			row["commercial_name"],
# 			row["color"],
# 			row["width"],
# 			row["item_name"],
# 			row["custom_item_type"],
# 			row["warehouse"],
# 			row["parent_warehouse"],
# 			"",  # No individual batch column since grouped
# 			"",  # Batch status omitted
# 			row["parent_batch"],
# 			flt(row["bal_qty"], float_precision),
# 			row["uom"],
# 			flt(row["qc_ok_qty"], float_precision),
# 			flt(row["grade2_qty"], float_precision),
# 			flt(row["collar_qty"], float_precision),
# 			flt(row["cuff_qty"], float_precision),
# 		])

# 	return columns, data



# def precalculate_related_quantities(iwb_map, all_batches, item_map, warehouse_map):
# 	"""Pre-calculate related quantities for better performance"""
# 	related_quantities_map = {}
	
# 	frappe.logger().debug("=== Starting precalculate_related_quantities ===")
	
# 	# First, build a comprehensive map of all collar and cuff items by parent batch and parent warehouse
# 	for item in iwb_map:
# 		for wh in iwb_map[item]:
# 			for batch in iwb_map[item][wh]:
# 				qty_dict = iwb_map[item][wh][batch]
# 				if qty_dict.bal_qty <= 0:
# 					continue
					
# 				batch_details = all_batches.get(batch, {})
# 				parent_batch = batch_details.get("custom_parent_batch", "")
# 				item_details = item_map.get(item, {})
# 				custom_item_type = item_details.get("custom_item_type", "")
# 				warehouse_details = warehouse_map.get(wh, {})
# 				parent_warehouse = warehouse_details.get("custom_parentwarehouse", "")
				
# 				# Debug logging for collar and cuff items
# 				if custom_item_type in ["Collar", "Cuff"]:
# 					frappe.logger().debug(f"Collar/Cuff Item: {item}, Batch: {batch}, Parent Batch: '{parent_batch}', Parent Warehouse: '{parent_warehouse}', Qty: {qty_dict.bal_qty}")
				
# 				# Only process collar and cuff items that have a parent batch
# 				if custom_item_type in ["Collar", "Cuff"] and parent_batch:
# 					# Clean the values to remove any trailing spaces
# 					parent_batch = parent_batch.strip()
					
# 					# For each collar/cuff item, we need to find all warehouses with the same parent warehouse
# 					# and aggregate quantities by parent_batch + parent_warehouse
# 					if parent_warehouse:
# 						related_key = f"{parent_batch}|{parent_warehouse}"
						
# 						if related_key not in related_quantities_map:
# 							related_quantities_map[related_key] = {
# 								"collar_qty": 0.0,
# 								"cuff_qty": 0.0,
# 								"qc_ok_qty": 0.0,
# 								"grade2_qty": 0.0
# 							}
						
# 						# Add to collar/cuff quantities
# 						if custom_item_type == "Collar":
# 							related_quantities_map[related_key]["collar_qty"] += qty_dict.bal_qty
# 							frappe.logger().debug(f"Added to collar: {qty_dict.bal_qty} for key: {related_key}")
# 						elif custom_item_type == "Cuff":
# 							related_quantities_map[related_key]["cuff_qty"] += qty_dict.bal_qty
# 							frappe.logger().debug(f"Added to cuff: {qty_dict.bal_qty} for key: {related_key}")
						
# 						# Add to QC status quantities based on batch status
# 						batch_status = batch_details.get("batch_status", "")
# 						if batch_status == "QC OK":
# 							related_quantities_map[related_key]["qc_ok_qty"] += qty_dict.bal_qty
# 						elif batch_status == "GRADE 2":
# 							related_quantities_map[related_key]["grade2_qty"] += qty_dict.bal_qty
# 					else:
# 						# Handle collar/cuff items without parent warehouse
# 						frappe.logger().debug(f"Collar/Cuff item without parent warehouse: {item}, Warehouse: {wh}")
	
# 	# Debug: Print the final related quantities map
# 	frappe.logger().debug("=== Final Related Quantities Map ===")
# 	for key, value in related_quantities_map.items():
# 		frappe.logger().debug(f"Key: '{key}' -> {value}")
# 	frappe.logger().debug("=== End Related Quantities Map ===")
	
# 	return related_quantities_map


# def get_all_batches_with_details():
# 	"""Get all batches with details (not filtering by batch_qty > 0)"""
# 	batch = frappe.qb.DocType("Batch")
# 	query = (
# 		frappe.qb.from_(batch)
# 		.select(
# 			batch.name,
# 			batch.item,
# 			batch.batch_status,
# 			batch.custom_parent_batch,
# 			batch.batch_qty
# 		)
# 	)
	
# 	all_batches = {}
# 	for batch_data in query.run(as_dict=True):
# 		all_batches[batch_data.name] = {
# 			"item": batch_data.item,
# 			"batch_status": batch_data.batch_status,
# 			"custom_parent_batch": batch_data.custom_parent_batch,
# 			"batch_qty": batch_data.batch_qty
# 		}
	
# 	return all_batches


# def get_warehouse_details():
# 	"""Get warehouse details including custom_parentwarehouse"""
# 	warehouse = frappe.qb.DocType("Warehouse")
# 	query = (
# 		frappe.qb.from_(warehouse)
# 		.select(
# 			warehouse.name,
# 			warehouse.custom_parentwarehouse
# 		)
# 	)
	
# 	warehouse_map = {}
# 	for wh_data in query.run(as_dict=True):
# 		warehouse_map[wh_data.name] = {
# 			"custom_parentwarehouse": wh_data.custom_parentwarehouse
# 		}
	
# 	return warehouse_map


# def get_columns(filters):
# 	"""return columns based on filters"""

# 	columns = [
# 		_("Item") + ":Link/Item:290",
# 		_("Commercial Name") + "::210",
# 		_("color") + "::180",
# 		_("width") + "::60",
# 		_("Item Name") + "::150",
# 		_("Item Type") + "::120",  # Added custom_item_type column
# 		_("Warehouse") + ":Link/Warehouse:100",
# 		_("Parent Warehouse") + "::120",  # Added custom_parentwarehouse column
# 		_("Batch") + ":Link/Batch:100",
# 		_("Batch Status") + "::100",
# 		_("Parent Batch") + ":Link/Batch:100",
# 		_("Balance Qty") + ":Float:90",
# 		_("UOM") + "::90",
# 		_("QC Ok Qty") + ":Float:80",
# 		_("Grade 2 Qty") + ":Float:80",
# 		_("Collar Qty") + ":Float:80",
# 		_("Cuff Qty") + ":Float:80",
# 	]

# 	return columns

# def get_stock_ledger_entries(filters):
# 	entries = get_stock_ledger_entries_for_batch_no(filters)

# 	entries += get_stock_ledger_entries_for_batch_bundle(filters)
# 	return entries


# @deprecated
# def get_stock_ledger_entries_for_batch_no(filters):
# 	if not filters.get("from_date"):
# 		frappe.throw(_("'From Date' is required"))
# 	if not filters.get("to_date"):
# 		frappe.throw(_("'To Date' is required"))

# 	posting_datetime = get_datetime(add_to_date(filters["to_date"], days=1))

# 	sle = frappe.qb.DocType("Stock Ledger Entry")
# 	query = (
# 		frappe.qb.from_(sle)
# 		.select(
# 			sle.item_code,
# 			sle.warehouse,
# 			sle.batch_no,
# 			sle.posting_date,
# 			fn.Sum(sle.actual_qty).as_("actual_qty"),
# 		)
# 		.where(
# 			(sle.docstatus < 2)
# 			& (sle.is_cancelled == 0)
# 			& (sle.batch_no != "")
# 			& (sle.posting_datetime < posting_datetime)
# 		)
# 		.groupby(sle.voucher_no, sle.batch_no, sle.item_code, sle.warehouse)
# 	)

# 	query = apply_warehouse_filter(query, sle, filters)
# 	if filters.warehouse_type and not filters.warehouse:
# 		warehouses = frappe.get_all(
# 			"Warehouse",
# 			filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
# 			pluck="name",
# 		)

# 		if warehouses:
# 			query = query.where(sle.warehouse.isin(warehouses))

# 	for field in ["item_code", "batch_no", "company"]:
# 		if filters.get(field):
# 			query = query.where(sle[field] == filters.get(field))

# 	return query.run(as_dict=True) or []


# def get_stock_ledger_entries_for_batch_bundle(filters):
# 	sle = frappe.qb.DocType("Stock Ledger Entry")
# 	batch_package = frappe.qb.DocType("Serial and Batch Entry")

# 	to_date = get_datetime(filters.to_date + " 23:59:59")

# 	query = (
# 		frappe.qb.from_(sle)
# 		.inner_join(batch_package)
# 		.on(batch_package.parent == sle.serial_and_batch_bundle)
# 		.select(
# 			sle.item_code,
# 			sle.warehouse,
# 			batch_package.batch_no,
# 			sle.posting_date,
# 			fn.Sum(batch_package.qty).as_("actual_qty"),
# 		)
# 		.where(
# 			(sle.docstatus < 2)
# 			& (sle.is_cancelled == 0)
# 			& (sle.has_batch_no == 1)
# 			& (sle.posting_datetime <= to_date)
# 		)
# 		.groupby(sle.voucher_no, batch_package.batch_no, batch_package.warehouse)
# 	)

# 	query = apply_warehouse_filter(query, sle, filters)
# 	if filters.warehouse_type and not filters.warehouse:
# 		warehouses = frappe.get_all(
# 			"Warehouse",
# 			filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
# 			pluck="name",
# 		)

# 		if warehouses:
# 			query = query.where(sle.warehouse.isin(warehouses))

# 	for field in ["item_code", "batch_no", "company"]:
# 		if filters.get(field):
# 			if field == "batch_no":
# 				query = query.where(batch_package[field] == filters.get(field))
# 			else:
# 				query = query.where(sle[field] == filters.get(field))

# 	return query.run(as_dict=True) or []


# def get_item_warehouse_batch_map(filters, float_precision):
# 	sle = get_stock_ledger_entries(filters)
# 	iwb_map = {}

# 	from_date = getdate(filters["from_date"])
# 	to_date = getdate(filters["to_date"])

# 	for d in sle:
# 		iwb_map.setdefault(d.item_code, {}).setdefault(d.warehouse, {}).setdefault(
# 			d.batch_no, frappe._dict({"opening_qty": 0.0, "in_qty": 0.0, "out_qty": 0.0, "bal_qty": 0.0})
# 		)
# 		qty_dict = iwb_map[d.item_code][d.warehouse][d.batch_no]
# 		if d.posting_date < from_date:
# 			qty_dict.opening_qty = flt(qty_dict.opening_qty, float_precision) + flt(
# 				d.actual_qty, float_precision
# 			)
# 		elif d.posting_date >= from_date and d.posting_date <= to_date:
# 			if flt(d.actual_qty) > 0:
# 				qty_dict.in_qty = flt(qty_dict.in_qty, float_precision) + flt(d.actual_qty, float_precision)
# 			else:
# 				qty_dict.out_qty = flt(qty_dict.out_qty, float_precision) + abs(
# 					flt(d.actual_qty, float_precision)
# 				)

# 		qty_dict.bal_qty = flt(qty_dict.bal_qty, float_precision) + flt(d.actual_qty, float_precision)

# 	return iwb_map


# def get_item_details(filters):
# 	"""Get item details including additional fields with filtering"""
# 	item_map = {}
	
# 	item = frappe.qb.DocType("Item")
# 	query = (
# 		frappe.qb.from_(item)
# 		.select(
# 			item.name, 
# 			item.item_name, 
# 			item.description, 
# 			item.stock_uom,
# 			item.commercial_name,
# 			item.color,
# 			item.width,
# 			item.custom_item_type  # Added custom_item_type field
# 		)
# 		.where(item.has_batch_no == 1)
# 	)
	
# 	# Apply filters for commercial_name, color, and custom_item_type
# 	if filters.get("commercial_name"):
# 		query = query.where(item.commercial_name == filters.get("commercial_name"))
	
# 	if filters.get("color"):
# 		query = query.where(item.color == filters.get("color"))
		
# 	if filters.get("custom_item_type"):
# 		query = query.where(item.custom_item_type == filters.get("custom_item_type"))
	
# 	for d in query.run(as_dict=True):
# 		item_map[d.name] = d

# 	return item_map


# import frappe
# from frappe import _
# from frappe.utils import add_to_date, cint, flt, get_datetime, get_table_name, getdate
# from frappe.utils.deprecations import deprecated
# from pypika import functions as fn
# from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter

# SLE_COUNT_LIMIT = 100_000

# def execute(filters=None):
# 	if not filters:
# 		filters = {}

# 	sle_count = frappe.db.estimate_count("Stock Ledger Entry")

# 	if (
# 		sle_count > SLE_COUNT_LIMIT
# 		and not filters.get("item_code")
# 		and not filters.get("warehouse")
# 		and not filters.get("warehouse_type")
# 	):
# 		frappe.throw(
# 			_("Please select either the Item or Warehouse or Warehouse Type filter to generate the report.")
# 		)

# 	if filters.from_date > filters.to_date:
# 		frappe.throw(_("From Date must be before To Date"))

# 	float_precision = cint(frappe.db.get_default("float_precision")) or 3

# 	columns = get_columns(filters)
# 	item_map = get_item_details(filters)
# 	iwb_map = get_item_warehouse_batch_map(filters, float_precision)

# 	all_batches = get_all_batches_with_details()
# 	warehouse_map = get_warehouse_details()
# 	related_quantities_map = precalculate_related_quantities(iwb_map, all_batches, item_map, warehouse_map)

# 	grouped_data = {}

# 	# --- Main Fabric grouping logic ---
# 	for item in iwb_map:
# 		item_details = item_map.get(item, {})
# 		custom_item_type = item_details.get("custom_item_type", "")
# 		if custom_item_type != "Fabric":
# 			continue  # only Fabric rows

# 		for wh in iwb_map[item]:
# 			warehouse_details = warehouse_map.get(wh, {})
# 			custom_parentwarehouse = warehouse_details.get("custom_parentwarehouse", "")

# 			for batch in iwb_map[item][wh]:
# 				qty_dict = iwb_map[item][wh][batch]
# 				if not (qty_dict.bal_qty > 0):
# 					continue

# 				batch_details = all_batches.get(batch, {})
# 				parent_batch = batch_details.get("custom_parent_batch", "")
# 				batch_status = batch_details.get("batch_status", "")

# 				# Filter by batch status if provided
# 				if filters.get("batch_status") and batch_status != filters.get("batch_status"):
# 					continue

# 				commercial_name = item_details.get("commercial_name", "")
# 				color = item_details.get("color", "")
# 				width = item_details.get("width", 0)
# 				item_name = item_details.get("item_name", "")
# 				uom = item_details.get("stock_uom", "")

# 				# Group key = Item + Warehouse + Parent Warehouse + Parent Batch
# 				group_key = f"{item}|{wh}|{custom_parentwarehouse}|{parent_batch}"

# 				if group_key not in grouped_data:
# 					grouped_data[group_key] = {
# 						"item": item,
# 						"commercial_name": commercial_name,
# 						"color": color,
# 						"width": width,
# 						"item_name": item_name,
# 						"custom_item_type": custom_item_type,
# 						"warehouse": wh,
# 						"parent_warehouse": custom_parentwarehouse,
# 						"parent_batch": parent_batch,
# 						"bal_qty": 0.0,
# 						"qc_ok_qty": 0.0,
# 						"grade2_qty": 0.0,
# 						"collar_qty": 0.0,
# 						"cuff_qty": 0.0,
# 						"uom": uom,
# 					}

# 				# Aggregate quantities
# 				grouped_data[group_key]["bal_qty"] += flt(qty_dict.bal_qty, float_precision)
# 				if batch_status == "QC OK":
# 					grouped_data[group_key]["qc_ok_qty"] += flt(qty_dict.bal_qty, float_precision)
# 				elif batch_status == "GRADE 2":
# 					grouped_data[group_key]["grade2_qty"] += flt(qty_dict.bal_qty, float_precision)

# 				# Add related collar/cuff quantities
# 				related_key = f"{parent_batch}|{custom_parentwarehouse}"
# 				if related_key in related_quantities_map:
# 					related = related_quantities_map[related_key]
# 					grouped_data[group_key]["collar_qty"] += flt(related.get("collar_qty", 0.0), float_precision)
# 					grouped_data[group_key]["cuff_qty"] += flt(related.get("cuff_qty", 0.0), float_precision)

# 	# --- Build final data list ---
# 	data = []
# 	total_bal = total_qc = total_g2 = total_collar = total_cuff = 0.0

# 	for key, row in grouped_data.items():
# 		data.append([
# 			row["item"],
# 			row["commercial_name"],
# 			row["color"],
# 			row["width"],
# 			row["item_name"],
# 			row["custom_item_type"],
# 			row["warehouse"],
# 			row["parent_warehouse"],
# 			"",  # Batch
# 			"",  # Batch status
# 			row["parent_batch"],
# 			flt(row["bal_qty"], float_precision),
# 			row["uom"],
# 			flt(row["qc_ok_qty"], float_precision),
# 			flt(row["grade2_qty"], float_precision),
# 			flt(row["collar_qty"], float_precision),
# 			flt(row["cuff_qty"], float_precision),
# 		])

# 		total_bal += row["bal_qty"]
# 		total_qc += row["qc_ok_qty"]
# 		total_g2 += row["grade2_qty"]
# 		total_collar += row["collar_qty"]
# 		total_cuff += row["cuff_qty"]

# 	# --- Add total row at the bottom ---
# 	# data.append([
# 	# 	"<b>Total</b>", "", "", "", "", "", "", "", "", "", "",
# 	# 	flt(total_bal, float_precision), "", 
# 	# 	flt(total_qc, float_precision),
# 	# 	flt(total_g2, float_precision),
# 	# 	flt(total_collar, float_precision),
# 	# 	flt(total_cuff, float_precision),
# 	# ])

# 	return columns, data


# # --- Helper: Precalculate collar/cuff relationships ---
# def precalculate_related_quantities(iwb_map, all_batches, item_map, warehouse_map):
# 	related_quantities_map = {}

# 	for item in iwb_map:
# 		for wh in iwb_map[item]:
# 			for batch in iwb_map[item][wh]:
# 				qty_dict = iwb_map[item][wh][batch]
# 				if qty_dict.bal_qty <= 0:
# 					continue

# 				batch_details = all_batches.get(batch, {})
# 				parent_batch = batch_details.get("custom_parent_batch", "")
# 				item_details = item_map.get(item, {})
# 				custom_item_type = item_details.get("custom_item_type", "")
# 				warehouse_details = warehouse_map.get(wh, {})
# 				parent_warehouse = warehouse_details.get("custom_parentwarehouse", "")

# 				if custom_item_type in ["Collar", "Cuff"] and parent_batch and parent_warehouse:
# 					key = f"{parent_batch}|{parent_warehouse}"
# 					if key not in related_quantities_map:
# 						related_quantities_map[key] = {
# 							"collar_qty": 0.0,
# 							"cuff_qty": 0.0
# 						}

# 					if custom_item_type == "Collar":
# 						related_quantities_map[key]["collar_qty"] += qty_dict.bal_qty
# 					elif custom_item_type == "Cuff":
# 						related_quantities_map[key]["cuff_qty"] += qty_dict.bal_qty

# 	return related_quantities_map


# # --- Helper: Batch details ---
# def get_all_batches_with_details():
# 	batch = frappe.qb.DocType("Batch")
# 	query = (
# 		frappe.qb.from_(batch)
# 		.select(
# 			batch.name,
# 			batch.item,
# 			batch.batch_status,
# 			batch.custom_parent_batch,
# 			batch.batch_qty
# 		)
# 	)
# 	all_batches = {}
# 	for b in query.run(as_dict=True):
# 		all_batches[b.name] = {
# 			"item": b.item,
# 			"batch_status": b.batch_status,
# 			"custom_parent_batch": b.custom_parent_batch,
# 			"batch_qty": b.batch_qty
# 		}
# 	return all_batches


# # --- Helper: Warehouse details ---
# def get_warehouse_details():
# 	warehouse = frappe.qb.DocType("Warehouse")
# 	query = (
# 		frappe.qb.from_(warehouse)
# 		.select(
# 			warehouse.name,
# 			warehouse.custom_parentwarehouse
# 		)
# 	)
# 	warehouse_map = {}
# 	for w in query.run(as_dict=True):
# 		warehouse_map[w.name] = {
# 			"custom_parentwarehouse": w.custom_parentwarehouse
# 		}
# 	return warehouse_map


# # --- Report columns ---
# def get_columns(filters):
# 	return [
# 		_("Item") + ":Link/Item:200",
# 		_("Commercial Name") + "::160",
# 		_("Color") + "::120",
# 		_("Width") + "::60",
# 		_("Item Name") + "::150",
# 		_("Item Type") + "::100",
# 		_("Warehouse") + ":Link/Warehouse:120",
# 		_("Parent Warehouse") + "::120",
# 		_("Batch") + ":Link/Batch:100",
# 		_("Batch Status") + "::100",
# 		_("Parent Batch") + ":Link/Batch:120",
# 		_("Balance Qty") + ":Float:100",
# 		_("UOM") + "::80",
# 		_("QC Ok Qty") + ":Float:100",
# 		_("Grade 2 Qty") + ":Float:100",
# 		_("Collar Qty") + ":Float:100",
# 		_("Cuff Qty") + ":Float:100",
# 	]


# # --- Ledger & item helpers ---
# def get_stock_ledger_entries(filters):
# 	entries = get_stock_ledger_entries_for_batch_no(filters)
# 	entries += get_stock_ledger_entries_for_batch_bundle(filters)
# 	return entries


# @deprecated
# def get_stock_ledger_entries_for_batch_no(filters):
# 	if not filters.get("from_date"):
# 		frappe.throw(_("'From Date' is required"))
# 	if not filters.get("to_date"):
# 		frappe.throw(_("'To Date' is required"))

# 	posting_datetime = get_datetime(add_to_date(filters["to_date"], days=1))
# 	sle = frappe.qb.DocType("Stock Ledger Entry")

# 	query = (
# 		frappe.qb.from_(sle)
# 		.select(
# 			sle.item_code,
# 			sle.warehouse,
# 			sle.batch_no,
# 			sle.posting_date,
# 			fn.Sum(sle.actual_qty).as_("actual_qty"),
# 		)
# 		.where(
# 			(sle.docstatus < 2)
# 			& (sle.is_cancelled == 0)
# 			& (sle.batch_no != "")
# 			& (sle.posting_datetime < posting_datetime)
# 		)
# 		.groupby(sle.voucher_no, sle.batch_no, sle.item_code, sle.warehouse)
# 	)

# 	query = apply_warehouse_filter(query, sle, filters)
# 	return query.run(as_dict=True) or []


# def get_stock_ledger_entries_for_batch_bundle(filters):
# 	sle = frappe.qb.DocType("Stock Ledger Entry")
# 	batch_package = frappe.qb.DocType("Serial and Batch Entry")
# 	to_date = get_datetime(filters.to_date + " 23:59:59")

# 	query = (
# 		frappe.qb.from_(sle)
# 		.inner_join(batch_package)
# 		.on(batch_package.parent == sle.serial_and_batch_bundle)
# 		.select(
# 			sle.item_code,
# 			sle.warehouse,
# 			batch_package.batch_no,
# 			sle.posting_date,
# 			fn.Sum(batch_package.qty).as_("actual_qty"),
# 		)
# 		.where(
# 			(sle.docstatus < 2)
# 			& (sle.is_cancelled == 0)
# 			& (sle.has_batch_no == 1)
# 			& (sle.posting_datetime <= to_date)
# 		)
# 		.groupby(sle.voucher_no, batch_package.batch_no, batch_package.warehouse)
# 	)

# 	query = apply_warehouse_filter(query, sle, filters)
# 	return query.run(as_dict=True) or []


# def get_item_warehouse_batch_map(filters, float_precision):
# 	sle = get_stock_ledger_entries(filters)
# 	iwb_map = {}

# 	from_date = getdate(filters["from_date"])
# 	to_date = getdate(filters["to_date"])

# 	for d in sle:
# 		iwb_map.setdefault(d.item_code, {}).setdefault(d.warehouse, {}).setdefault(
# 			d.batch_no, frappe._dict({"opening_qty": 0.0, "in_qty": 0.0, "out_qty": 0.0, "bal_qty": 0.0})
# 		)
# 		qty_dict = iwb_map[d.item_code][d.warehouse][d.batch_no]
# 		if d.posting_date < from_date:
# 			qty_dict.opening_qty += flt(d.actual_qty, float_precision)
# 		elif from_date <= d.posting_date <= to_date:
# 			if flt(d.actual_qty) > 0:
# 				qty_dict.in_qty += flt(d.actual_qty, float_precision)
# 			else:
# 				qty_dict.out_qty += abs(flt(d.actual_qty, float_precision))
# 		qty_dict.bal_qty += flt(d.actual_qty, float_precision)

# 	return iwb_map


# def get_item_details(filters):
# 	item_map = {}
# 	item = frappe.qb.DocType("Item")
# 	query = (
# 		frappe.qb.from_(item)
# 		.select(
# 			item.name,
# 			item.item_name,
# 			item.description,
# 			item.stock_uom,
# 			item.commercial_name,
# 			item.color,
# 			item.width,
# 			item.custom_item_type
# 		)
# 		.where(item.has_batch_no == 1)
# 	)

# 	if filters.get("commercial_name"):
# 		query = query.where(item.commercial_name == filters.get("commercial_name"))
# 	if filters.get("color"):
# 		query = query.where(item.color == filters.get("color"))
# 	if filters.get("custom_item_type"):
# 		query = query.where(item.custom_item_type == filters.get("custom_item_type"))

# 	for d in query.run(as_dict=True):
# 		item_map[d.name] = d
# 	return item_map

import frappe
from frappe import _
from frappe.utils import add_to_date, cint, flt, get_datetime, getdate
from frappe.utils.deprecations import deprecated
from pypika import functions as fn
from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter

SLE_COUNT_LIMIT = 100_000

def execute(filters=None):
	if not filters:
		filters = {}

	sle_count = frappe.db.estimate_count("Stock Ledger Entry")

	if (
		sle_count > SLE_COUNT_LIMIT
		and not filters.get("item_code")
		and not filters.get("warehouse")
		and not filters.get("warehouse_type")
	):
		frappe.throw(
			_("Please select either the Item or Warehouse or Warehouse Type filter to generate the report.")
		)

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

	float_precision = cint(frappe.db.get_default("float_precision")) or 3

	columns = get_columns(filters)
	item_map = get_item_details(filters)
	iwb_map = get_item_warehouse_batch_map(filters, float_precision)

	all_batches = get_all_batches_with_details()
	warehouse_map = get_warehouse_details()
	related_quantities_map = precalculate_related_quantities(iwb_map, all_batches, item_map, warehouse_map)

	grouped_data = {}

	# --- Main Fabric grouping logic ---
	for item in iwb_map:
		item_details = item_map.get(item, {})
		custom_item_type = item_details.get("custom_item_type", "")
		if custom_item_type != "Fabric":
			continue  # only Fabric rows

		for wh in iwb_map[item]:
			warehouse_details = warehouse_map.get(wh, {})
			custom_parentwarehouse = warehouse_details.get("custom_parentwarehouse", "")

			for batch in iwb_map[item][wh]:
				qty_dict = iwb_map[item][wh][batch]
				if not (qty_dict.bal_qty > 0):
					continue

				batch_details = all_batches.get(batch, {})
				parent_batch = batch_details.get("custom_parent_batch", "")
				batch_status = batch_details.get("batch_status", "")

				# Filter by batch status if provided
				if filters.get("batch_status") and batch_status != filters.get("batch_status"):
					continue

				commercial_name = item_details.get("commercial_name", "")
				color = item_details.get("color", "")
				width = item_details.get("width", 0)
				item_name = item_details.get("item_name", "")
				uom = item_details.get("stock_uom", "")

				# Group key = Item + Warehouse + Parent Warehouse + Parent Batch
				group_key = f"{item}|{wh}|{custom_parentwarehouse}|{parent_batch}"

				if group_key not in grouped_data:
					grouped_data[group_key] = {
						"item": item,
						"commercial_name": commercial_name,
						"color": color,
						"width": width,
						"item_name": item_name,
						"custom_item_type": custom_item_type,
						"warehouse": wh,
						"parent_warehouse": custom_parentwarehouse,
						"parent_batch": parent_batch,
						"bal_qty": 0.0,
						"qc_ok_qty": 0.0,
						"grade2_qty": 0.0,
						"collar_qty": 0.0,
						"cuff_qty": 0.0,
						"uom": uom,
					}

				# Aggregate quantities
				grouped_data[group_key]["bal_qty"] += flt(qty_dict.bal_qty, float_precision)
				if batch_status == "QC OK":
					grouped_data[group_key]["qc_ok_qty"] += flt(qty_dict.bal_qty, float_precision)
				elif batch_status == "GRADE 2":
					grouped_data[group_key]["grade2_qty"] += flt(qty_dict.bal_qty, float_precision)

				# Add related collar/cuff quantities
				related_key = f"{parent_batch}|{custom_parentwarehouse}"
				if related_key in related_quantities_map:
					related = related_quantities_map[related_key]
					grouped_data[group_key]["collar_qty"] += flt(related.get("collar_qty", 0.0), float_precision)
					grouped_data[group_key]["cuff_qty"] += flt(related.get("cuff_qty", 0.0), float_precision)

	# --- Build final data list ---
	data = []
	total_bal = total_qc = total_g2 = total_collar = total_cuff = 0.0

	for key, row in grouped_data.items():
		data.append([
			row["item"],
			row["commercial_name"],
			row["color"],
			row["width"],
			row["item_name"],
			row["custom_item_type"],
			row["warehouse"],
			row["parent_warehouse"],
			row["parent_batch"],
			flt(row["bal_qty"], float_precision),
			row["uom"],
			flt(row["qc_ok_qty"], float_precision),
			flt(row["grade2_qty"], float_precision),
			flt(row["collar_qty"], float_precision),
			flt(row["cuff_qty"], float_precision),
		])

		total_bal += row["bal_qty"]
		total_qc += row["qc_ok_qty"]
		total_g2 += row["grade2_qty"]
		total_collar += row["collar_qty"]
		total_cuff += row["cuff_qty"]

	return columns, data


# --- Helper: Precalculate collar/cuff relationships ---
def precalculate_related_quantities(iwb_map, all_batches, item_map, warehouse_map):
	related_quantities_map = {}

	for item in iwb_map:
		for wh in iwb_map[item]:
			for batch in iwb_map[item][wh]:
				qty_dict = iwb_map[item][wh][batch]
				if qty_dict.bal_qty <= 0:
					continue

				batch_details = all_batches.get(batch, {})
				parent_batch = batch_details.get("custom_parent_batch", "")
				item_details = item_map.get(item, {})
				custom_item_type = item_details.get("custom_item_type", "")
				warehouse_details = warehouse_map.get(wh, {})
				parent_warehouse = warehouse_details.get("custom_parentwarehouse", "")

				if custom_item_type in ["Collar", "Cuff"] and parent_batch and parent_warehouse:
					key = f"{parent_batch}|{parent_warehouse}"
					if key not in related_quantities_map:
						related_quantities_map[key] = {
							"collar_qty": 0.0,
							"cuff_qty": 0.0
						}

					if custom_item_type == "Collar":
						related_quantities_map[key]["collar_qty"] += qty_dict.bal_qty
					elif custom_item_type == "Cuff":
						related_quantities_map[key]["cuff_qty"] += qty_dict.bal_qty

	return related_quantities_map


# --- Helper: Batch details ---
def get_all_batches_with_details():
	batch = frappe.qb.DocType("Batch")
	query = (
		frappe.qb.from_(batch)
		.select(
			batch.name,
			batch.item,
			batch.batch_status,
			batch.custom_parent_batch,
			batch.batch_qty
		)
	)
	all_batches = {}
	for b in query.run(as_dict=True):
		all_batches[b.name] = {
			"item": b.item,
			"batch_status": b.batch_status,
			"custom_parent_batch": b.custom_parent_batch,
			"batch_qty": b.batch_qty
		}
	return all_batches


# --- Helper: Warehouse details ---
def get_warehouse_details():
	warehouse = frappe.qb.DocType("Warehouse")
	query = (
		frappe.qb.from_(warehouse)
		.select(
			warehouse.name,
			warehouse.custom_parentwarehouse
		)
	)
	warehouse_map = {}
	for w in query.run(as_dict=True):
		warehouse_map[w.name] = {
			"custom_parentwarehouse": w.custom_parentwarehouse
		}
	return warehouse_map


# --- Report columns ---
def get_columns(filters):
	return [
		_("Item") + ":Link/Item:200",
		_("Commercial Name") + "::160",
		_("Color") + "::120",
		_("Width") + "::60",
		_("Item Name") + "::150",
		_("Item Type") + "::100",
		_("Warehouse") + ":Link/Warehouse:120",
		_("Parent Warehouse") + "::120",
		# _("Batch") + ":Link/Batch:100",       # Hidden
		# _("Batch Status") + "::100",          # Hidden
		_("Parent Batch") + ":Link/Batch:120",
		_("Balance Qty") + ":Float:100",
		_("UOM") + "::80",
		_("QC Ok Qty") + ":Float:100",
		_("Grade 2 Qty") + ":Float:100",
		_("Collar Qty") + ":Float:100",
		_("Cuff Qty") + ":Float:100",
	]


# --- Ledger & item helpers ---
def get_stock_ledger_entries(filters):
	entries = get_stock_ledger_entries_for_batch_no(filters)
	entries += get_stock_ledger_entries_for_batch_bundle(filters)
	return entries


@deprecated
def get_stock_ledger_entries_for_batch_no(filters):
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))
	if not filters.get("to_date"):
		frappe.throw(_("'To Date' is required"))

	posting_datetime = get_datetime(add_to_date(filters["to_date"], days=1))
	sle = frappe.qb.DocType("Stock Ledger Entry")

	query = (
		frappe.qb.from_(sle)
		.select(
			sle.item_code,
			sle.warehouse,
			sle.batch_no,
			sle.posting_date,
			fn.Sum(sle.actual_qty).as_("actual_qty"),
		)
		.where(
			(sle.docstatus < 2)
			& (sle.is_cancelled == 0)
			& (sle.batch_no != "")
			& (sle.posting_datetime < posting_datetime)
		)
		.groupby(sle.voucher_no, sle.batch_no, sle.item_code, sle.warehouse)
	)

	query = apply_warehouse_filter(query, sle, filters)
	return query.run(as_dict=True) or []


def get_stock_ledger_entries_for_batch_bundle(filters):
	sle = frappe.qb.DocType("Stock Ledger Entry")
	batch_package = frappe.qb.DocType("Serial and Batch Entry")
	to_date = get_datetime(filters.to_date + " 23:59:59")

	query = (
		frappe.qb.from_(sle)
		.inner_join(batch_package)
		.on(batch_package.parent == sle.serial_and_batch_bundle)
		.select(
			sle.item_code,
			sle.warehouse,
			batch_package.batch_no,
			sle.posting_date,
			fn.Sum(batch_package.qty).as_("actual_qty"),
		)
		.where(
			(sle.docstatus < 2)
			& (sle.is_cancelled == 0)
			& (sle.has_batch_no == 1)
			& (sle.posting_datetime <= to_date)
		)
		.groupby(sle.voucher_no, batch_package.batch_no, batch_package.warehouse)
	)

	query = apply_warehouse_filter(query, sle, filters)
	return query.run(as_dict=True) or []


def get_item_warehouse_batch_map(filters, float_precision):
	sle = get_stock_ledger_entries(filters)
	iwb_map = {}

	from_date = getdate(filters["from_date"])
	to_date = getdate(filters["to_date"])

	for d in sle:
		iwb_map.setdefault(d.item_code, {}).setdefault(d.warehouse, {}).setdefault(
			d.batch_no, frappe._dict({"opening_qty": 0.0, "in_qty": 0.0, "out_qty": 0.0, "bal_qty": 0.0})
		)
		qty_dict = iwb_map[d.item_code][d.warehouse][d.batch_no]
		if d.posting_date < from_date:
			qty_dict.opening_qty += flt(d.actual_qty, float_precision)
		elif from_date <= d.posting_date <= to_date:
			if flt(d.actual_qty) > 0:
				qty_dict.in_qty += flt(d.actual_qty, float_precision)
			else:
				qty_dict.out_qty += abs(flt(d.actual_qty, float_precision))
		qty_dict.bal_qty += flt(d.actual_qty, float_precision)

	return iwb_map


def get_item_details(filters):
	item_map = {}
	item = frappe.qb.DocType("Item")
	query = (
		frappe.qb.from_(item)
		.select(
			item.name,
			item.item_name,
			item.description,
			item.stock_uom,
			item.commercial_name,
			item.color,
			item.width,
			item.custom_item_type
		)
		.where(item.has_batch_no == 1)
	)

	if filters.get("commercial_name"):
		query = query.where(item.commercial_name == filters.get("commercial_name"))
	if filters.get("color"):
		query = query.where(item.color == filters.get("color"))
	if filters.get("custom_item_type"):
		query = query.where(item.custom_item_type == filters.get("custom_item_type"))

	for d in query.run(as_dict=True):
		item_map[d.name] = d
	return item_map

