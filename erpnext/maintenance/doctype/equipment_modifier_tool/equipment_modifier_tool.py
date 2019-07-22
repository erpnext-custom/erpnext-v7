# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class EquipmentModifierTool(Document):
	def validate(self):
		self.check_double_entry()
		self.check_mandiatory()

	def check_mandiatory(self):
		if not self.posting_date: self.posting_date = now_datetime()
		if not self.get("items"):
			frappe.throw("Equipment List Cannot Be Empty")
		'''if self.current_equipment_type == self.new_equipment_type:
			frappe.throw(" New Equipment Type Cannot be like Current Equipment Type")
		if self.current_equipment_model == self.new_equipment_model:
			frappe.throw(" New Equipment Model Cannot be Like Current Equipment model")'''
		if not self.current_equipment_type or not self.new_equipment_type:
			frappe.msgprint(" Equipment Type Is Mandiatory")
		if not 	self.current_equipment_model or not self.new_equipment_model:
			frappe.msgprint(" Equipment Model Is Mandiatory")

	def on_submit(self):
		self.update_equipment_master()	

	def on_cancel(self):
        	self.delete_entries()
	
	def check_double_entry(self):
                found = []
                for eq in self.get("items"):
                        if eq.equipment in found:
                                frappe.throw("Equipment <b> '{0}' </b> Already Added In The List".format(eq.equipment))
                        found.append(eq.equipment)

	def update_equipment_master(self):
                for eq in self.get("items"):
                        eq_obj = frappe.get_doc("Equipment", eq.equipment)
			if eq_obj.model_items and  frappe.db.exists("Equipment Model History", {"parent": eq.equipment, \
				"equipment_model": self.new_equipment_model, "equipment_type": self.new_equipment_type, \
				"modified_date": self.posting_date}):
				frappe.throw("The Same Record already maintained in Equipment Master <b> '{0}' </b> ".format(eq.equipment))
			else: 
				eq_obj.flags.ignore_permissions = 1,
				eq_obj.db_set("equipment_type", self.new_equipment_type),
                        	eq_obj.db_set("equipment_model", self.new_equipment_model),
				eq_obj.append("model_items",{
								"equipment_model": self.new_equipment_model,
								"equipment_type": self.new_equipment_type,
								"modified_date": self.posting_date,
								"ref_doc": self.name
					})
				eq_obj.save()	

	def delete_entries(self):
                frappe.db.sql("delete from `tabEquipment Model History` where ref_doc = %s", self.name)

	def get_equipment(self):
		if not self.current_equipment_model and not self.current_equipment_type:
			frappe.throw("Current Equipment Model and Type Is Not Selected")
		else:
			query = "select name as equipment, equipment_number, equipment_model, equipment_category, equipment_type from tabEquipment \
					where is_disabled != 1 and equipment_type = '{0}' \
				and equipment_model = '{1}'".format(self.current_equipment_type, self.current_equipment_model)
			if self.branch:
				query += " and branch = '{0}'".format(self.branch)
			entries = frappe.db.sql(query, as_dict=True, debug =1)
			if not entries:
				frappe.throw("No equipment found")
			self.set('items', [])

			for d in entries:
				row = self.append('items', {})
				row.update(d)
			

