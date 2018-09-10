# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.maintenance.report.maintenance_report import get_pol_consumed_till, get_pol_till

class HSDAdjustment(Document):
	def validate(self):
		self.check_mandatory_fields()

	def check_mandatory_fields(self):
		for a in self.items:
			e_no, hsd_type, branch = frappe.db.get_value("Equipment", a.equipment, ["equipment_number", "hsd_type", "branch"])
			if branch != self.branch:
				frappe.throw("Equipment <b>"+str(a.equipment)+"</b> doesn't belong to " + str(self.branch))
			a.equipment_number = e_no
			a.hsd_type = hsd_type
			if not hsd_type:
				frappe.throw("HSD Type for Equipment is Mandatory on row "+ str(a.idx) +". Please set it in the Equipment Master")
			else:
				item_name = frappe.db.get_value("Item", a.hsd_type, "item_name")
				a.hsd_name = item_name
			if a.balance < 0:
				frappe.throw("Balance Quantity cannot be less than 0")

	def on_submit(self):
		self.make_pol_entry()

	def make_pol_entry(self):	
		for a in self.items:
			received = get_pol_till("Receive", a.equipment, self.date, a.hsd_type)
                        consumed = get_pol_consumed_till(a.equipment, self.date)
                        actual_receive = flt(a.balance) + flt(consumed)
                        qty = flt(actual_receive) - flt(received)
	
			con = frappe.new_doc("POL Entry")
			con.flags.ignore_permissions = 1	
			con.equipment = a.equipment
			con.pol_type = a.hsd_type
			con.branch = self.branch
			con.date = self.date
			con.posting_time = self.posting_time
			con.qty = qty
			con.reference_type = "HSD Adjustment"
			con.reference_name = self.name
			con.is_opening = 1
			con.own_cost_center = 1
			con.type = "Receive"
			con.submit()

	def on_cancel(self):
		self.cancel_pol_entry()

	def cancel_pol_entry(self):
		frappe.db.sql("delete from `tabPOL Entry` where reference_name = %s", self.name)

	def get_equipments(self):
		if not self.branch:
			frappe.throw("Select the Branch first")
		query = "select name as equipment, equipment_number, hsd_type from tabEquipment where is_disabled = 0 and branch = \'" + str(self.branch) + "\'"
		entries = frappe.db.sql(query, as_dict=True)
		self.set('items', [])

		for d in entries:
			d.balance = 0
			row = self.append('items', {})
			row.update(d)


