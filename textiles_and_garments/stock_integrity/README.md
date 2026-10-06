# Stock ledger integrity

Prevents, detects and repairs the stock ledger problems that put 223 rows (−Rs 2.73 lakh)
in red on the Stock_balance_checking report, cleaned up by hand on 3 Oct 2026
(SR/00021 – SR/00033, ST/26/19895).

It works alongside `stock_valuation_guard.py`, which blocks absurd *valuations*
(BM/25/90012). This module covers ledger *consistency*.

## Root causes found, and what now handles each

| What went wrong (example) | Layer | Module |
|---|---|---|
| A posted entry never reached the running balance (MF/25/10763, +24.84 kg, 14 months) | Block at submit: each new ledger line must continue the balance before it, and the Bin must equal the last line | `guard.on_submit` (chain) |
| A transfer posted its outgoing half only (BM/25/89360, arrival line cancelled) | Block at submit: every Stock Entry row needs a ledger line per warehouse | `guard.on_submit` (missing_leg) |
| A batch issued from a warehouse that never received it (JOB11723 at NAP_E1/GF/A04) | Block at submit: no batch may go below zero in its warehouse | `guard.on_submit` (negative_batch) |
| Reposts failing silently (16 Failed, oldest Aug 2024; YRFPP090's Rs 5,044.50) | Hourly e-mail per new failure, with the error | `monitor.check_failed_reposts` |
| 0.001 kg crumbs left behind carrying value (≈180 dust rows) | Outgoing row takes the whole batch if ≤ 5 g would be left | `guard.snap_remainders` |
| Non-batch Stock Reconciliation lines stored with actual_qty = 0, so SUM-based reports disagree with the stock (LILA, MARS_POLO) | actual_qty filled with the real change on submit, and again after reposts | `guard.fill_sr_actual_qty`, `monitor.refill_after_reposts` |
| Clean-up adjustments undone by a repost (SR/00024, 12 minutes after commit) | Reposts starting at or before a protected line are refused; protected vouchers cannot be cancelled | `protect.guard_repost`, `protect.guard_cancel` |
| Stock received at rate 0 (MR/25/00909: Rs 50 lakh of chemicals into Pranera Marketing at no value) | Material Receipt of a stock item without a rate alerts (or blocks) unless "Allow Zero Valuation Rate" is ticked | `guard.check_zero_rate_receipt` |
| Problems only noticed when someone ran the report | Nightly e-mail of every red or out-of-sync item/warehouse | `monitor.nightly_scan` |
| Repairs needed console pasting | One dry-run-first command | `repair.run` |

Not fixed in code: the old pre-migration batches mixed with batch-wise valuation in the same
warehouse (groups B/C). That is an ERPNext valuation design issue; the nightly scan reports
any new rows it produces and `repair.run` fixes them.

## Configuration (`site_config.json`, no deploy needed)

```json
"stock_integrity_enabled": 1,
"stock_integrity_missing_leg": "block",
"stock_integrity_chain": "block",
"stock_integrity_negative_batch": "block",
"stock_integrity_zero_rate_receipt": "alert",
"stock_integrity_fill_sr_actual_qty": 1,
"stock_integrity_snap_remainder": 0.005,
"stock_integrity_protect": 1,
"stock_integrity_alert_to": ["aravindsprint@gmail.com"]
```

Modes are `block` (submit rolled back with a message), `alert` (e-mail + Error Log only) or `off`.
`negative_batch` drops to `alert` automatically when Stock Settings allows negative stock.

### Suggested rollout

1. Deploy with the three checks in `alert` mode for a week and watch the Error Log / e-mails.
2. Switch each to `block` once it has stayed quiet on normal work.

```bash
bench --site pranera.erpnext.com set-config stock_integrity_chain alert
bench --site pranera.erpnext.com set-config stock_integrity_missing_leg alert
bench --site pranera.erpnext.com set-config stock_integrity_negative_batch alert
```

## Operations

Nightly scan on demand (no e-mail):
```bash
bench --site pranera.erpnext.com execute textiles_and_garments.stock_integrity.monitor.nightly_scan --kwargs "{'send': 0}"
```

Repair red rows, dry run then apply:
```bash
bench --site pranera.erpnext.com execute textiles_and_garments.stock_integrity.repair.run
bench --site pranera.erpnext.com execute textiles_and_garments.stock_integrity.repair.run --kwargs "{'apply': 1}"
```
Options: `dust=1` also takes rows between Rs −1 and 0; `exclude=[[item, warehouse]]`;
`only=[[item, warehouse]]`; `frag=0.05`. Rows that hold real stock are valued at their
stored rate if positive, otherwise the 12-month median incoming rate; check those lines in
the dry run. Committed reconciliations are protected automatically.

Protected vouchers:
```python
from textiles_and_garments.stock_integrity.protect import get_protected, protect, unprotect
```
A deliberate, supervised repost through a protected line:
`frappe.flags.allow_protected_repost = True` in the console session, or set
`stock_integrity_protect` to 0 temporarily.

## Tests

```bash
python -m pytest tests/test_stock_integrity_pure.py
```
Covers the decision logic (chain continuity, snapping, repost/protection comparison,
row classification, chunking, medians). The Frappe-side checks need a site; test them on
staging by submitting a Stock Entry with the modes set to `alert` and checking the Error Log.
