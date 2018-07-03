# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class HRSettings(Document):
	def validate(self):
		from erpnext.setup.doctype.naming_series.naming_series import set_by_naming_series
		set_by_naming_series("Employee", "employee_number",
			self.get("emp_created_by")=="Naming Series", hide_name_field=True)

		self.check_duplicates()

	def check_duplicates(self):
                if flt(self.max_days_incountry) < 0:
                        frappe.throw(_("DSA Ceiling for In-Country travel cannot be a negative value."), title="Invalid Data")

                if flt(self.max_days_outcountry) < 0:
                        frappe.throw(_("DSA Ceiling for Out-Country travel cannot be a negative value."), title="Invalid Data")

                # In-Country DSA ceiling
                dup = {}
                for i in self.get("incountry"):
                        key = str(i.travel_type)
                        if dup.has_key(key):
                                frappe.throw(_("Row#{0} : Duplicate record found for Travel Type <b>{1}</b> under In-Country table.").format(i.idx, i.travel_type),title="Duplicate Values")
                        else:
                                dup.update({key: 1})

                # Out-Country DSA ceiling
                dup = {}
                for i in self.get("outcountry"):                        
                        key = str(i.travel_type)
                        if dup.has_key(key):
                                frappe.throw(_("Row#{0} : Duplicate record found for Travel Type <b>{1}</b> under Out-Country table.").format(i.idx, i.travel_type),title="Duplicate Values")
                        else:
                                dup.update({key: 1})
