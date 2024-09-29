# Copyright (c) 2024, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import flt
from erpnext.setup.utils import get_exchange_rate
from bs4 import BeautifulSoup
import urllib.parse
from frappe_whatsapp.utils import run_server_script_for_doc_event
from datetime import datetime


class DyeReceipe(Document):
    def before_save(self):
        if self.is_default == 1:
            # Fetch all other documents with the same item but is_default == 1
            other_dye_recipes = frappe.get_all("Dye Receipe", 
                                               filters={"item": self.item, "is_default": 1, "name": ["!=", self.name]})
            for recipe in other_dye_recipes:
                # Update is_default to 0 for each document found
                other_doc = frappe.get_doc("Dye Receipe", recipe.name)
                other_doc.is_default = 0
                other_doc.save()
            
            print("\n\n\n\nis_default == 1 and other documents updated\n\n\n\n\n")

