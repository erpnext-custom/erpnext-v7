# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AssignSupervisor(Document):
	def validate(self):
		self.check_duplicate()

	def on_submit(self):
		self.assign_approver(None)

	def on_cancel(self):
		self.assign_approver(cancel = "cancel")

        def assign_approver(self, cancel):
		approver = self.approver
		approver_name = self.approver_name
		if cancel:
			approver = None
                	approver_name = None

                if self.items:
                        for a in self.items:
                                doc  = frappe.get_doc("Employee", a.employee)
                                doc.flags.ignore_permissions = True
                                doc.reports_to =  approver
				doc.reports_to_name = approver_name
				doc.save()

	def check_duplicate(self):
		found = []
		for a in self.get("items"):
			if a.employee not in found:
				found.append(a.employee)
			else:
				frappe.throw("Employee <b> '{0}' </b> already added in the list".format(a.employee)) 

        def get_branch_employees(self):
                emp = frappe.db.sql(""" select name as employee, employee_name, designation from `tabEmployee` where status = 'Active' 
                        and branch = '{0}' and reports_to != '{1}' and employee != '{1}'""".format(self.branch, self.approver), as_dict = True)

                if emp:
                        self.set('items', [])
                        for d in emp:
                                already = False

                                for a in self.items:
                                        if a.employee == d.name:
                                                already = True
                                if not already:
                                        row = self.append('items', {})
                                        row.update(d)
                else:
                        frappe.msgprint("Supervisor '{0}' already assigned/No Employee Found with Selected branch <b>{1} </b>, Check Employee Master ".format(self.approver, self.branch))

