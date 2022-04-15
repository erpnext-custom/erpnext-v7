# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Delinkassetandjournal(Document):
	def on_submit(self):
		# je_no = []
		for a in frappe.db.sql("""select parent from `tabJournal Entry Account` where reference_name = '{0}'""".format(self.asset), as_dict=True):
			je_no = a.parent
			# doc = frappe.get_doc("Journal Entry", je_no)
			# doc.cancel()
		# frappe.throw(je_no)
    
		frappe.db.sql ("update `tabJournal Entry Account` set reference_name = null where reference_name = '{0}'".format(self.asset))
			
		frappe.db.sql ("update `tabAsset Issue Details` set reference_code  = null where reference_code = '{0}'".format(self.asset))
		frappe.db.sql ("update `tabDepreciation Schedule` set journal_entry =null where parent = '{0}'".format(self.asset))
		frappe.db.sql ("update `tabGL Entry` set against_voucher = null where against_voucher = '{0}'".format(self.asset))
		doc = frappe.get_doc("Journal Entry", je_no)
		doc.cancel()
		


