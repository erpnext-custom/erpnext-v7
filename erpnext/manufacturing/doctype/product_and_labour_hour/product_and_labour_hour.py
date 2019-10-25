# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, date_diff, nowdate

class ProductandLabourHour(Document):
	def validate(self):
		pass

	def on_submit(self):
		self.create_cost_sheet()

	def on_cancel(self):
		pass

	def create_cost_sheet(self):
		today = getdate(nowdate())
		cs = frappe.new_doc("Cost Sheet")
		cs.item = self.item_code
		cs.item_name = self.item_name
		cs.product_code = self.product_code
		cs.posting_date = today
		cs.product_and_labour_hour = self.name
		cs.insert()
		
		labour_cost = curving_cost = painting_cost = 0.00
		csd_obj = frappe.get_doc("Cost Sheet", {"product_and_labour_hour":self.name})
		
		csd_obj.flags.ignore_permissions = 1
		# Labour Cost
		csd_obj.append("items",{
					"particular": "Labour Cost",
					"hours": self.labour_hour,
					"rate": self.labour_rate,
					"amount": flt(self.labour_hour) * flt(self.labour_rate),
				})
		labour_cost = flt(self.labour_hour) * flt(self.labour_rate)

		# Curving Cost
		csd_obj.append("items",{
					"particular": "Curving Cost",
					"hours": self.sq_ft,
					"rate": self.curving,
					"amount": flt(self.sq_ft) * flt(self.curving),
				})
		curving_cost = flt(self.sq_ft) * flt(self.curving)

		# Painting Cost
		csd_obj.append("items",{
					"particular": "Painting Cost",
					"rate": self.painting,
					"amount": flt(self.painting),
				})
		painting_cost = flt(self.painting)

		prime_cost = flt(labour_cost) + flt(curving_cost) + flt(painting_cost)

		# MANUFACTURING OVERHEAD Cost
		labour_cost_percent = frappe.db.get_single_value("Manufacturing Settings", "labour_cost")
		csd_obj.append("items",{
					"particular": "Manufacturing Overhead",
					"percent": flt(labour_cost_percent),
					"amount": (flt(labour_cost_percent) / 100) * (flt(labour_cost)),
				})
		manufacturing_cost = flt(prime_cost) + ((flt(labour_cost_percent) / 100) * (flt(labour_cost)))

		# ADMINISTRATION & OTHER OVERHEAD
		manufacturing_cost_percent = frappe.db.get_single_value("Manufacturing Settings", "manufacturing_cost")

		csd_obj.append("items",{
					"particular": "Administration and Other Overhead",
					"percent": flt(manufacturing_cost_percent),
					"amount": (flt(manufacturing_cost_percent) / 100) * (flt(manufacturing_cost)),
				})
		production_cost = flt(manufacturing_cost) + ((flt(manufacturing_cost_percent) / 100) * (flt(manufacturing_cost)))

		csd_obj.prime_cost = flt(prime_cost)
		csd_obj.manufacturing_cost = flt(manufacturing_cost)
		csd_obj.production_cost = flt(production_cost)

		csd_obj.save()
		csd_obj.submit()
