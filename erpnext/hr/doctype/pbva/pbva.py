# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, date_diff, cint
from erpnext.hr.doctype.salary_structure.salary_structure import get_salary_tax

class PBVA(Document):
	def validate(self):
		self.calculate_values()

	def on_submit(self):
		cc_amount = {}
		for a in self.items:
			cc = frappe.db.get_value("Employee", a.employee, "cost_center")
			if cc_amount.has_key(cc):
				cc_amount[cc] = cc_amount[cc] + a.amount
			else:
				cc_amount[cc] = a.amount;
		
		self.post_journal_entry(cc_amount)

        def calculate_values(self):
                if self.items:
			tot = tax = net = 0
			for a in self.items:
				a.tax_amount = get_salary_tax(flt(a.amount))
				a.balance_amount = flt(a.amount) - flt(a.tax_amount)
				tot += flt(a.amount)
				tax += flt(a.tax_amount)
				net += flt(a.balance_amount)
			self.total_amount = flt(tot)
			self.tax_amount   = flt(tax)
			self.net_amount   = flt(net)
		else:
			frappe.throw("Cannot save without employee details")
        
	def post_journal_entry(self, cc_amount):
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "PBVA (" + self.name + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = 'PBVA payment against : ' + self.name;
		je.posting_date = self.posting_date

		for key in cc_amount.keys():
			je.append("accounts", {
					"account": "Performance Based Variable Pay - SMCL",
					"reference_type": "PBVA",
					"reference_name": self.name,
					"cost_center": key,
					"debit_in_account_currency": flt(cc_amount[key]),
					"debit": flt(cc_amount[key]),
				})
		
		je.append("accounts", {
				"account": "Bank of Bhutan Ltd - 100891887 - SMCL",
				"reference_type": "PBVA",
				"reference_name": self.name,
				"cost_center": "Corporate Head Office - SMCL",
				"credit_in_account_currency": flt(self.total_amount) - flt(self.tax_amount),
				"credit": flt(self.total_amount) - flt(self.tax_amount),
			})
		
		je.append("accounts", {
				"account": "Salary Tax - SMCL",
				"reference_type": "PBVA",
				"reference_name": self.name,
				"cost_center": "Corporate Head Office - SMCL",
				"credit_in_account_currency": flt(self.tax_amount),
				"credit": flt(self.tax_amount),
			})

		je.insert()

		self.db_set("journal_entry", je.name)

	#@frappe.whitelist()
	def get_pbva_details(self):
                if not self.fiscal_year:
			frappe.throw("Fiscal Year is Mandatory")

		#start, end = frappe.db.get_value("Fiscal Year", self.fiscal_year, ["year_start_date", "year_end_date"])
                start = str(self.fiscal_year)+'-01-01'
		end   = str(self.fiscal_year)+'-12-31'
                cond  = ""
                
                if self.branch:
                        cond += "and branch = \'" + str(self.branch) + "\'";
		
		query = """
                                select
                                        e.name as employee,
                                        e.employee_name,
                                        e.employee_group,
                                        e.employment_type,
                                        e.branch,
                                        e.date_of_joining,
                                        e.relieving_date,
                                        e.reason_for_resignation as leaving_type,
					e.salary_mode,
					e.bank_name,
					e.bank_ac_no,
                                        datediff(least(ifnull(e.relieving_date,'9999-12-31'),'{2}'),
                                                        greatest(e.date_of_joining,'{1}'))+1 days_worked,
                                        (
                                                select
                                                        sd.amount
                                                from
                                                        `tabSalary Detail` sd,
                                                        `tabSalary Slip` sl,
                                                        `tabSalary Structure` ss
                                                where sd.parent = sl.name
                                                and sl.employee = e.name
                                                and sl.salary_structure = ss.name
                                                and sd.salary_component = 'Basic Pay'
                                                and sl.docstatus = 1
                                                and ifnull(ss.eligible_for_pbva,0) = 1
                                                and sl.fiscal_year <= {0}
						and (sd.salary_component = 'Basic Pay'
                                                        or exists(select 1 from `tabSalary Component` sc
                                                                        where sc.name = sd.salary_component
                                                                        and sc.is_pf_deductible = 1
                                                                        and sc.type = 'Earning')
                                                )
                                                order by sl.month desc limit 1
                                        ) as basic_pay,
                                        0 as percent
                                from tabEmployee e
                                where (
                                        ('{3}' = 'Active' and e.date_of_joining <= '{2}' and ifnull(e.relieving_date,'9999-12-31') > '{2}')
                                        or
                                        ('{3}' = 'Left' and ifnull(e.relieving_date,'9999-12-31') between '{1}' and '{2}')
                                        or
                                        ('{3}' = 'All' and e.date_of_joining <= '{2}' and ifnull(e.relieving_date,'9999-12-31') >= '{1}')
                                        )
                                {5}
                                and not exists(
                                                select 1
                                                from `tabPBVA Details` bd, `tabPBVA` b
                                                where b.fiscal_year = '{0}'
                                                and b.name <> '{4}'
                                                and bd.parent = b.name
                                                and bd.employee = e.employee
                                                and b.docstatus in (0,1))
                                order by e.branch
                        """.format(self.fiscal_year, start, end, self.employee_status, self.name, cond)
		
		entries = frappe.db.sql(query, as_dict=True)
		self.set('items', [])

		start = getdate(start)
		end = getdate(end)

		for d in entries:
                        tax = 0.0
                        
                        if flt(d.basic_pay) > 0:
                                d.percent        = flt(self.above) if d.employee_group in ("Chief Executive Officer", "Executive") else flt(self.below)
                                d.months         = flt(self.noof_months)
                                d.amount         = flt(d.basic_pay)*flt(d.months)*(flt(d.percent)/100)
                                d.tax_amount     = get_salary_tax(d.amount)
                                d.balance_amount = flt(d.amount)-flt(d.tax_amount)
                                row              = self.append('items', {})
                                row.update(d)

	def on_cancel(self):
		jv = frappe.db.sql("select name, docstatus from `tabJournal Entry` where name = %s and docstatus = 1", self.journal_entry)
		if jv:
			frappe.throw("Can not cancel PBVA without canceling the corresponding journal entry " + str(self.journal_entry))
		else:
			self.db_set("journal_entry", "")


@frappe.whitelist()
def get_pbva_details_x(branch=None):
	query = """
                select
                        b.employee,
                        b.employee_name,
                        b.branch,
                        a.amount
                from
                        `tabSalary Detail` a,
                        `tabSalary Structure` b
                where a.parent = b.name
                and a.salary_component = 'Basic Pay'
                and b.is_active = 'Yes'
                and b.eligible_for_pbva = 1
                """
	
	if branch:
		query += " and b.branch = \'" + str(branch) + "\'";
	query += " order by b.branch"
	return frappe.db.sql(query, as_dict=True)

@frappe.whitelist()
def get_pbva_percent(employee):
	group = frappe.db.get_value("Employee", employee, "employee_group")
	if group in ("Chief Executive Officer", "Executive"):
		return "above"
	else:
		return "below"
