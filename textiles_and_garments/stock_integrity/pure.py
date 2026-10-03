"""
Frappe-free decision helpers for stock_integrity.

Everything here is plain Python so it can be unit-tested without a site
(see tests/test_stock_integrity_pure.py at the repo root).
"""

QTY_TOL = 0.001  # stock UOM; matches the ROUND(..., 3) used by the checking report
VALUE_TOL = 0.01


def median(values):
    """Median of a list of numbers, or None for an empty list."""
    s = sorted(v for v in values if v is not None)
    n = len(s)
    if not n:
        return None
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def chain_ok(prev_qty_after, actual_qty, qty_after, tol=QTY_TOL):
    """True when a ledger line continues the running balance of the line before it."""
    return abs((prev_qty_after or 0) + (actual_qty or 0) - (qty_after or 0)) <= tol


def snap_remainder(available, taking, snap):
    """
    Quantity to add to an outgoing row so it takes the whole batch.

    Returns the leftover when 0 < leftover <= snap (a weighing/rounding crumb
    that would otherwise sit in the warehouse as a 0.001 kg fragment carrying
    value), else 0.
    """
    if not snap or snap <= 0:
        return 0
    rem = round((available or 0) - (taking or 0), 6)
    return rem if 0 < rem <= snap + 1e-9 else 0


def repost_hits_protected(repost_start, protected_at):
    """
    A repost recalculates every ledger line at or after its start.
    It would rewrite a protected line when it starts at or before that line.
    Both arguments must be comparable (datetimes or ISO strings).
    """
    return repost_start <= protected_at


def classify_row(has_batch, live_pos_qty, has_live, has_empty_batch, bin_qty, frag):
    """
    Decide how the repair tool treats one item/warehouse.

      K  keep stock: restate live batches at a rate        (batch item, qty > frag)
      Z  fragment:   live batches written off to 0        (batch item, 0 < qty <= frag)
      C  clear:      one empty batch reconciled to 0      (batch item, no live batch)
      U  non-batch:  posted as target+1, then set to target
      S  skip:       only negative batches, nothing ERPNext can reconcile
    """
    if not has_batch:
        return "U"
    if live_pos_qty > frag:
        return "K"
    if has_live:
        return "Z"
    if has_empty_batch:
        return "C"
    return "S"


def chunk_groups(groups, size):
    """
    Pack row-groups into chunks of at most `size` rows without splitting a group.
    A single group larger than `size` becomes its own chunk.
    ERPNext queues Stock Reconciliations with more than 100 rows in the background,
    which would break same-transaction adjustment, so callers keep size <= 90.
    """
    chunks, cur = [], []
    for g in groups:
        if cur and len(cur) + len(g) > size:
            chunks.append(cur)
            cur = []
        cur = cur + list(g)
    if cur:
        chunks.append(cur)
    return chunks


def is_red(sum_qty, sum_value, qty_tol=QTY_TOL, value_floor=-1.0):
    """Row the checking report would show in red: value <= -1 or qty < -0.001."""
    return round(sum_value or 0, 2) <= value_floor or round(sum_qty or 0, 3) < -qty_tol


def out_of_sync(sum_qty, sum_value, bin_qty, bin_value, qty_tol=QTY_TOL, value_tol=1.0):
    """Ledger total and stored (Bin) balance disagree."""
    return abs((sum_qty or 0) - (bin_qty or 0)) > qty_tol or abs((sum_value or 0) - (bin_value or 0)) > value_tol
