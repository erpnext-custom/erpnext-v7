# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, cint, validate_email_add, today, add_years, date_diff, nowdate

class MusterRollEmployee(Document):
	def validate(self):
		self.calculate_rates()
		#self.check_status()
		self.populate_work_history()

	def calculate_rates(self):
		if not self.rate_per_hour:
			self.rate_per_hour = (flt(self.rate_per_day) * 1.5) / 8

	def check_status(self):
		if self.status == "Left":
			self.cost_center = ''
			self.branch = ''
			self.project = ''

        # Following method introducted by SHIV on 04/10/2017
        def populate_work_history(self):
                if self.branch != self.get_db_value("branch"):

                        for wh in self.internal_work_history:
                                if not wh.to_date:
                                        wh.to_date = wh.from_date if getdate(today()) < getdate(wh.from_date) else today()
                        
                        self.append("internal_work_history",{
                                                        "branch": self.branch,
                                                        "from_date": today(),
                                                        "owner": frappe.session.user,
                                                        "creation": nowdate(),
                                                        "modified_by": frappe.session.user,
                                                        "modified": nowdate()
                                        })
