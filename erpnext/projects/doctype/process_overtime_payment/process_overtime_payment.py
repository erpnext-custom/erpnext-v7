# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.custom_utils import check_budget_available, get_branch_cc
from frappe.utils import flt, nowdate, getdate
from frappe.model.document import Document
from erpnext.hr.hr_custom_functions import get_month_details
from erpnext.custom_utils import prepare_gl, check_future_date

class ProcessOvertimePayment(Document):
	def validate(self):
		if not self.fiscal_year or not self.month:
			frappe.throw("Fiscal Year/ Month is Required")
	
		if not self.cost_center:
			frappe.throw("Cost Center is not Selected")
	
		if not self.branch:
			frappe.throw(" Branch is Mandiatory")

		self.check_duplicate_entries()

	def check_duplicate_entries(self):
                not_found = []
                found = []
                for a in self.items:
                        if a.employee not in  found:
                                not_found.append(a.employee)
                        else:
                                found.append(a.employee)
                		frappe.throw("Double Entry is not allowed for {0}".format(found))

	def on_submit(self):
		self.post_general_ledger()
		#self.update_ot()

	def on_cancel(self):
		if self.clearance_date:
                        frappe.throw("Already done bank reconciliation.")

		frappe.db.sql(""" update `tabOvertime Application` set payment_jv = '' where payment_jv = '{0}'""".format(self.name))
		frappe.db.sql(""" delete from `tabGL Entry` where voucher_type = '{0}' and voucher_no = '{1}'""".format(self.doctype, self.name))
	def get_ot_details(self):
		m = get_month_details(self.fiscal_year, self.month)
                from_date = m['month_start_date']
                to_date = m['month_end_date']
		query = """select employee, employee_name, rate as hourly_rate, sum(total_hours) as total_hours, 
			sum(total_amount) as total_ot_amount
			from `tabOvertime Application` where docstatus = 1 and workflow_state = 'Approved' 
			and ifnull(payment_jv, '') = '' and posting_date between '{0}' and '{1}' and  
			cost_center in (select cost_center from `tabCost Center` where parent = '{2}' )  group by employee
		""".format(from_date, to_date, self.cost_center)
		
		entries = frappe.db.sql(query, as_dict=True, debug = 1)
                if not entries:
                        frappe.msgprint("OT Payment is already processed or there is no Approved OT to process")

                self.set('items', [])

                for d in entries:
                        doc = frappe.get_doc("Employee", d.employee)
			row = self.append('items', {})
                        row.bank_name = doc.bank_name
			row.bank_account = doc.bank_ac_no
			row.designation = doc.designation
			row.grade = doc.employee_subgroup	
			row.update(d)

		total = 0.0
                for a in self.get('items'):
                        total += a.total_ot_amount
                self.total_amount = total

	
	def post_general_ledger(self):
		gl_entries = []
		ot_account = frappe.db.get_single_value("HR Accounts Settings", "overtime_account")
                expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
                if not self.cost_center:
                        frappe.throw("Cost Center Is Required")
                if not expense_bank_account:
                        frappe.throw("Setup Default Expense Bank Account for your Branch")
                if not ot_account:
                        frappe.throw("Setup Default Overtime Account in HR Account Setting")

		
		m = get_month_details(self.fiscal_year, self.month)
                from_date = m['month_start_date']
                to_date = m['month_end_date']
		query = """
                        select cost_center, sum(total_amount) as total_ot_amount 
                        from `tabOvertime Application` where docstatus = 1 and workflow_state = 'Approved'
                        and posting_date between '{0}' and '{1}' and 
			cost_center in (select cost_center from `tabCost Center` where parent = '{2}')  
			group by cost_center
                """.format(from_date, to_date, self.cost_center)
                for d in frappe.db.sql(query, as_dict = True):
			check_budget_available(d.cost_center, ot_account, self.posting_date, d.total_ot_amount, throw_error=True)
			gl_entries.append(
				prepare_gl(self, {"account": expense_bank_account,
					 "credit": flt(d.total_ot_amount),
					 "credit_in_account_currency": flt(d.total_ot_amount),
					 "voucher_no": self.name,
                                         "voucher_type": self.doctype,
					 "cost_center": d.cost_center,
					 "company": self.company
					})
			)

			gl_entries.append(
				prepare_gl(self, {"account": ot_account,
						"debit": flt(d.total_ot_amount),
						"debit_in_account_currency": flt(d.toatl_ot_amount),
						"voucher_no": self.name,
                                         	"voucher_type": self.doctype,
                                         	"cost_center": d.cost_center,
                                         	"company": self.company
						})
				)

			from erpnext.accounts.general_ledger import make_gl_entries
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False)
		self.update_ot()


	def update_ot(self):
                m = get_month_details(self.fiscal_year, self.month)
                from_date = m['month_start_date']
                to_date = m['month_end_date']
                query = """
                        select name 
                        from `tabOvertime Application` where docstatus = 1 and workflow_state = 'Approved'
                        and ifnull(payment_jv, '') = '' and posting_date between '{0}' and '{1}' and 
                        cost_center in (select cost_center from `tabCost Center` where parent = '{2}')  
                """.format(from_date, to_date, self.cost_center)
                for d in frappe.db.sql(query, as_dict = True):
                        doc = frappe.get_doc("Overtime Application", d.name)
                        doc.db_set("payment_jv", self.name)	
