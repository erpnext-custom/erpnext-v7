# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from datetime import date
from erpnext.custom_workflow import validate_workflow_states

class EmployeeBenefits(Document):
	def validate(self):
		validate_workflow_states(self)
		self.validate_gratuity()

	def on_submit(self):
		if self.purpose == "Separation":
			self.update_employee()
		self.post_journal()
	
	def validate_gratuity(self):
		self.total_amount = 0
		for a in self.items:
			self.total_amount = self.total_amount + a.amount 
			if a.benefit_type=="Gratuity":
				date_of_joining = frappe.db.get_value("Employee", self.employee, "date_of_joining")
				employee_group = frappe.db.get_value("Employee", self.employee, "employee_group")
				today_date = date.today()
				years_in_service = abs(((today_date - date_of_joining).days)/364)
				if years_in_service < 5 and employee_group != "ESP":
					frappe.throw("Should have minimum of 5 years in service for Gratuity. Only <b>{0}</b> year/s in Services as of now ".format(years_in_service))
				elif employee_group == "ESP" and years_in_service < 1:
					frappe.throw("ESP Employee should have minimum of 1 years in service for Gratuity. Only <b>{0}</b> year/s in Services as of now ".format(years_in_service))
					
			elif a.benefit_type == "Carriage Charges":
				emp_grade = frappe.db.get_value("Employee", self.employee, "employee_subgroup")
				maximum_charges = frappe.db.get_value("Employee Grade", emp_grade, "carriage_ceiling")
				if a.amount > maximum_charges:
					frappe.throw("Carriage charges <b>{0}</b> is exceeding the ceiling of {1}".format(a.amount, maximum_charges))	
	
	def post_journal(self):
		emp = frappe.get_doc("Employee", self.employee)
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions=1
		je.branch = emp.branch
		je.posting_date = self.posting_date
		je.title = str(self.purpose) + " Benefit (" + str(self.employee_name) + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = str(self.purpose) + ' Benefit payments for ' + str(self.employee_name) + "("+str(self.employee)+")";

		total_amount = 0
		for a in self.items:
			je.append("accounts", {
					"account": a.gl_account,
					"party_type": "Employee",
					"party": self.employee,
					"reference_type": "Employee Benefits",
					"reference_name": self.name,
					"cost_center": emp.cost_center,
					"debit_in_account_currency": flt(a.amount),
					"debit": flt(a.amount),
					"business_activity": emp.business_activity,
				})
			total_amount = flt(total_amount) + flt(a.amount)
		je.append("accounts", {
				"account": frappe.db.get_value("Branch", emp.branch, "expense_bank_account"),
				"cost_center": emp.cost_center,
				"credit_in_account_currency": flt(total_amount),
				"credit": flt(total_amount),
				"business_activity": emp.business_activity,
			})
		je.insert()
		self.db_set("journal", je.name)

	def update_employee(self):
		emp = frappe.get_doc("Employee", self.employee)
                emp.flags.ignore_permissions = 1
                for a in self.items:
                        emp.append("separation_benefits", {
                                        "s_b_type": a.benefit_type,
                                        "s_b_currency": a.amount,
                                        "s_remarks": self.description,
                                        "ref_doc": self.name
                                })
                if self.purpose == "Separation":
                        emp.relieving_date = self.separation_date
                        emp.reason_for_resignation = self.reason_for_resignation
                        emp.status = "Left"

                '''for a in self.items:
                        doc = frappe.new_doc("Separation Benefits")
                        doc.parent = self.employee
                        doc.parentfield = "separation_benefits"
                        doc.parenttype = "Employee"
                        doc.s_b_type = a.benefit_type
                        doc.s_b_currency = a.amount
                        doc.save()'''
                emp.save()

	def on_cancel(self):
		self.check_journal()

	def check_journal(self):
		docstatus = frappe.db.get_value("Journal Entry", self.journal, "docstatus")
		if docstatus and docstatus != 2:
			frappe.throw("Cancel Journal Entry {0} before cancelling this document".format(frappe.get_desk_link("Journal Entry", self.journal)))


@frappe.whitelist()
def get_basic_salary(employee):
	query = "select amount from `tabSalary Structure` s, `tabSalary Detail` d where s.name = d.parent and s.employee=\'" + str(employee) + "\' and d.salary_component='Basic Pay' and is_active='Yes'"
        data = frappe.db.sql(query, as_dict=True)
        if not data:
                frappe.throw("Basic Salary has not been assigned")
        return data[0].amount
