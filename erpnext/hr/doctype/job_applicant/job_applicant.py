# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from frappe import _
from frappe.utils import comma_and, validate_email_add

from frappe.utils import today
from datetime import timedelta, date
from frappe.utils import rounded, flt, cint, now, nowdate, getdate, get_datetime,now_datetime
sender_field = "email_id"

class DuplicationError(frappe.ValidationError): pass

class JobApplicant(Document):
	def onload(self):
		offer_letter = frappe.get_all("Offer Letter", filters={"job_applicant": self.name})
		if offer_letter:
			self.get("__onload").offer_letter = offer_letter[0].name

	def autoname(self):
		keys = filter(None, (self.applicant_name, self.email_id))
		if not keys:
			frappe.throw(_("Name or Email is mandatory"), frappe.NameError)
		self.name = " - ".join(keys)

	def validate(self):
		self.check_email_id_is_unique()
		validate_email_add(self.email_id, True)

		if not self.applicant_name and self.email_id:
			guess = self.email_id.split('@')[0]
			self.applicant_name = ' '.join([p.capitalize() for p in guess.split('.')])

		dep_sch = frappe.db.sql(""" select name, journal_entry, parent, schedule_date from `tabDepreciation Schedule` where parent = 'ASSET171100002' order by idx desc limit 1""", as_dict = 1)
		frappe.msgprint("this {0} {1}".format(getdate(dep_sch[0].schedule_date), today()))

	def check_email_id_is_unique(self):
		if self.email_id:
			names = frappe.db.sql_list("""select name from `tabJob Applicant`
				where email_id=%s and name!=%s""", (self.email_id, self.name))

			if names:
				frappe.throw(_("Email id must be unique, already exists for {0}").format(comma_and(names)), frappe.DuplicateEntryError)

