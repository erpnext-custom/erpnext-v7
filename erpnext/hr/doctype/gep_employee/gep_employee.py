# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, cint, validate_email_add, today, add_years, date_diff, nowdate

class GEPEmployee(Document):
	def validate(self):
		#self.check_status()
		self.calculate_rates()
		self.populate_work_history()

	def calculate_rates(self):
		if not self.rate_per_day:
			self.rate_per_day = flt(self.salary) / 30
		if not self.rate_per_hour:
			self.rate_per_hour = (flt(self.salary) * 1.5) / (30 * 8)

	def check_status(self):
		if self.status == "Left":
			self.cost_center = ''
			self.branch = ''

	# Following method introducted by SHIV on 04/10/2017
        def populate_work_history(self):
                if self.branch != self.get_db_value("branch") or self.cost_center != self.get_db_value("cost_center"):

                        for wh in self.internal_work_history:
                                if not wh.to_date:
                                        wh.to_date = wh.from_date if getdate(today()) < getdate(wh.from_date) else today()
                        
                        self.append("internal_work_history",{
                                                        "branch": self.branch,
                                                        "cost_center": self.cost_center,
                                                        "from_date": today(),
                                                        "owner": frappe.session.user,
                                                        "creation": nowdate(),
                                                        "modified_by": frappe.session.user,
                                                        "modified": nowdate()
                                        })


def update_work_history():
        print "Updating from console..."

        count = 0
        
        wh_list = frappe.db.sql("""
                        select
                                name,
                                person_name,
                                date_of_joining,
                                branch
                        from `tabGEP Employee` as gep
                        where not exists(select 1
                                         from `tabEmployee Internal Work History` as wh
                                         where wh.parent = gep.name
                                         and   wh.parenttype = 'GEP Employee')
                        """, as_dict=1)

        for rec in wh_list:
                wh = frappe.get_doc("GEP Employee", rec.name)

                wh.append("internal_work_history", {
                        "branch": rec.branch,
                        "from_date": rec.date_of_joining
                })

                count += 1
                wh.save()

        print count, "Row(s) Inserted."
