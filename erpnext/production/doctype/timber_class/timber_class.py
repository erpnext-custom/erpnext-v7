# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils.data import nowdate, add_years, add_days, date_diff

class TimberClass(Document):
	def before_save(self):
		for i, item in enumerate(sorted(self.items, key=lambda item: item.from_date), start=1):
			item.idx = i

	def validate(self):
		self.set_dates()

        def set_dates(self):
                to_date = self.items[len(self.items) - 1].to_date
                for a in reversed(self.items):
                        a.to_date = to_date
                        to_date = add_days(a.from_date, -1)



