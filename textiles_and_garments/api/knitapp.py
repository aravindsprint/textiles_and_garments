@frappe.whitelist()
def get_rolls_for_job_card(job_card):
    """
    Returns all rolls linked to a Job Card via Roll Packing List.
    Looks up the job card's work order + batch to find relevant rolls.
    """
    jc = frappe.get_doc("Job Card", job_card)
    work_order = jc.work_order

    if not work_order:
        return {"success": False, "data": [], "message": "No work order linked"}

    # Get Roll Packing List entries for this work order
    # Adjust the doctype/field names to match your custom app
    rolls = frappe.db.sql("""
        SELECT 
            rpl.roll_no,
            rpl.batch_no,
            rpl.item_code,
            rpl.qty,
            rpl.warehouse
        FROM `tabRoll Packing List` rpl
        WHERE rpl.work_order = %(work_order)s
          AND rpl.docstatus = 1
          AND rpl.roll_no IS NOT NULL
          AND rpl.roll_no != ''
        ORDER BY rpl.batch_no, rpl.roll_no
    """, {"work_order": work_order}, as_dict=True)

    # Optionally also filter by job card's lot_no / batch if your Job Card has it
    # Uncomment if your Job Card doc has a batch_no or lot_no field:
    # if jc.get("lot_no"):
    #     rolls = [r for r in rolls if r.batch_no == jc.lot_no]

    return {
        "success": True,
        "data": rolls,
        "job_card": job_card,
        "work_order": work_order,
        "total_rolls": len(rolls)
    }