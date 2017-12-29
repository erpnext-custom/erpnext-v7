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
		self.update_user_permissions()

        def update_user_permissions(self):
                prev_branch  = self.get_db_value("branch")
                prev_company = self.get_db_value("company")
                prev_user_id = self.get_db_value("user_id")

                if prev_user_id:
                        frappe.permissions.remove_user_permission("Muster Roll Employee", self.name, prev_user_id)
                        frappe.permissions.remove_user_permission("Company", prev_company, prev_user_id)
                        frappe.permissions.remove_user_permission("Branch", prev_branch, prev_user_id)

                if self.user_id:
                        frappe.permissions.add_user_permission("Muster Roll Employee", self.name, self.user_id)
                        frappe.permissions.add_user_permission("Company", self.company, self.user_id)
                        frappe.permissions.add_user_permission("Branch", self.branch, self.user_id)
                
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
                if getdate(self.joining_date) != getdate(self.get_db_value("joining_date")):
                        for wh in self.internal_work_history:
                                if getdate(self.get_db_value("joining_date")) == getdate(wh.from_date):
                                        wh.from_date = self.joining_date

                if self.status == 'Left' and self.separation_date:
                        for wh in self.internal_work_history:
                                if not wh.to_date:
                                        wh.to_date = self.separation_date
                                elif self.get_db_value("separation_date"):
                                        if getdate(self.get_db_value("separation_date")) == getdate(wh.to_date):
                                                wh.to_date = self.separation_date
                                                
                if self.branch != self.get_db_value("branch") or self.cost_center != self.get_db_value("cost_center"):

                        for wh in self.internal_work_history:
                                if not wh.to_date:
                                        wh.to_date = wh.from_date if getdate(today()) < getdate(wh.from_date) else today()

                        if not self.internal_work_history:
                                self.append("internal_work_history",{
                                                                "branch": self.branch,
                                                                "cost_center": self.cost_center,
                                                                "from_date": self.joining_date,
                                                                "owner": frappe.session.user,
                                                                "creation": nowdate(),
                                                                "modified_by": frappe.session.user,
                                                                "modified": nowdate()
                                                })
                        else:
                                self.append("internal_work_history",{
                                                                "branch": self.branch,
                                                                "cost_center": self.cost_center,
                                                                "from_date": today(),
                                                                "owner": frappe.session.user,
                                                                "creation": nowdate(),
                                                                "modified_by": frappe.session.user,
                                                                "modified": nowdate()
                                                })
                                
