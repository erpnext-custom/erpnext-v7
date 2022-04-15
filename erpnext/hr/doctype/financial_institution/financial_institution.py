# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class FinancialInstitution(Document):
	def onload(self):
		self.load_branches()

	def validate(self):
		self.validate_mandatory()
		self.sync_branches()
		self.items = []

	def validate_mandatory(self):
		if not self.bank_name:
			frappe.throw(_("Bank Name is mandatory"))

	def get_branches(self):
		return frappe.get_all("Financial Institution Branch", "*", {"financial_institution": self.name}, order_by="branch_name")

	def load_branches(self):
		self.items = []
		for branch in self.get_branches():
			self.append("items",{
				"branch_name": branch.branch_name,
				"financial_system_code": branch.financial_system_code,
				"financial_institution_branch": branch.name
			})

	def sync_branches(self):
		for item in self.items:
			if item.financial_institution_branch:
				branch = frappe.get_doc("Financial Institution Branch", item.financial_institution_branch)
			else:
				branch = frappe.new_doc("Financial Institution Branch")

			branch.update({
				"financial_institution": self.name,
				"branch_name": str(item.branch_name).strip(),
				"financial_system_code": str(item.financial_system_code).strip()
			})
			branch.save(ignore_permissions=True)
