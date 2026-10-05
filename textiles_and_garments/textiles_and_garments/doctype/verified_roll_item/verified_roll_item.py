# Copyright (c) 2026, Pranera Services & Solutions and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class VerifiedRollItem(Document):
	"""One row per roll verified on the Roll App's "Verify Rolls" page —
	child table of Stock Entry (custom field custom_verified_rolls).
	Records which bin each roll was put away into, so cancelling the
	put-away Stock Entry can send each roll's warehouse back to where it
	came from (see textiles_and_garments.api.verify_rolls)."""

	pass
