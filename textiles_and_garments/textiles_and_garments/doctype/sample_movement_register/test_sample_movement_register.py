# Copyright (c) 2026, Aravind and contributors
import frappe
from frappe.tests.utils import FrappeTestCase


class TestSampleMovementRegister(FrappeTestCase):
	def _doc(self, rows):
		doc = frappe.new_doc("Sample Movement Register")
		for r in rows:
			doc.append("items", r)
		return doc

	def test_return_progress(self):
		doc = self._doc([{"item_description": "A", "quantity": 2, "unit": "Pcs"}])
		doc.set_return_progress()
		self.assertEqual(doc.return_progress, "Not Returned")

		doc.items[0].returned_qty = 1
		doc.set_return_progress()
		self.assertEqual(doc.return_progress, "Partially Returned")

		doc.items[0].returned_qty = 2
		doc.set_return_progress()
		self.assertEqual(doc.return_progress, "Fully Returned")

		doc.items[0].returned_qty = 1
		doc.items[0].written_off = 1
		doc.set_return_progress()
		self.assertEqual(doc.return_progress, "Resolved with Write-off")

	def test_whole_number_units(self):
		doc = self._doc([{"item_description": "A", "quantity": 1.5, "unit": "Pcs"}])
		self.assertRaises(frappe.ValidationError, doc.validate_items)

	def test_returned_cannot_exceed(self):
		doc = self._doc([{"item_description": "A", "quantity": 1, "returned_qty": 2, "unit": "Mtrs"}])
		self.assertRaises(frappe.ValidationError, doc.validate_items)
