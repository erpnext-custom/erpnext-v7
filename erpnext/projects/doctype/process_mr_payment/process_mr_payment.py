# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint
from calendar import monthrange

class ProcessMRPayment(Document):
	def validate(self):
                # Setting `monthyear`
		month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(self.month) + 1
		month = str(month) if cint(month) > 9 else str("0" + str(month))
                self.monthyear = str(self.fiscal_year)+str(month)
                
		if self.items:
			total_ot = total_wage = total_health = salary = 0
			
			for a in self.items:
                                self.duplicate_entry_check(a.employee, a.employee_type, a.idx)
                                a.fiscal_year   = self.fiscal_year
                                a.month         = self.month
                                
				a.total_ot_amount = flt(a.hourly_rate) * flt(a.number_of_hours)
				a.total_wage = flt(a.daily_rate) * flt(a.number_of_days)
				
				if a.employee_type == "GEP Employee":
                                        salary = frappe.db.get_value("GEP Employee", a.employee, "salary")
                                        if flt(a.total_wage) > flt(salary):
                                                a.total_wage = flt(salary)
                                        
				a.total_amount = flt(a.total_ot_amount) + flt(a.total_wage)
				total_ot += flt(a.total_ot_amount)
				total_wage += flt(a.total_wage)
				if a.employee_type == "GEP Employee":
					a.health = flt(a.total_wage) * 0.01
					a.wage_payable = flt(a.total_wage) - flt(a.health)
					total_health += flt(a.health)
				
			total = total_ot + total_wage
			self.wages_amount = total_wage
			self.ot_amount = total_ot
			self.total_overall_amount = total
			if a.employee_type == "GEP Employee":
				self.total_health_amount = total_health
			

	def on_submit(self):
		self.post_journal_entry()

	def before_cancel(self):
		cl_status = frappe.db.get_value("Journal Entry", self.payment_jv, "docstatus")
		if cl_status and cl_status != 2:
			frappe.throw("You need to cancel the journal entry related to this payment first!")
		
		self.db_set('payment_jv', "")

        def duplicate_entry_check(self, employee, employee_type, idx):
                pl = frappe.db.sql("""
                                select
                                        name,
                                        parent,
                                        docstatus,
                                        person_name,
                                        employee
                                from `tabMR Payment Item`
                                where employee = '{0}'
                                and employee_type = '{1}'
                                and fiscal_year = '{2}'
                                and month = '{3}'
                                and docstatus in (0,1)
                                and parent != '{4}'
                        """.format(employee, employee_type, self.fiscal_year, self.month, self.name), as_dict=1)

                for l in pl:
                        msg = 'Payment already processed for `{2}({3})`<br>RowId#{1}: Reference# <a href="#Form/Process MR Payment/{0}">{0}</a>'.format(l.parent, idx, l.person_name, l.employee)
                        frappe.throw(_("{0}").format(msg), title="Duplicate Record Found")                        
                
	#Populate Budget Accounts with Expense and Fixed Asset Accounts
	def load_employee(self):
		if self.employee_type == "GEP Employee":
			query = "select 'GEP Employee' as employee_type, name as employee, person_name, id_card, rate_per_day as daily_rate, rate_per_hour as hourly_rate from `tabGEP Employee` where status = 'Active'"
		elif self.employee_type == "Muster Roll Employee":
			query = "select 'Muster Roll Employee' as employee_type, name as employee, person_name, id_card, rate_per_day as daily_rate, rate_per_hour as hourly_rate from `tabMuster Roll Employee` where status = 'Active'"
		else:
			frappe.throw("Select employee record first!")
	
		if not self.branch:
			frappe.throw("Set Branch before loading employee data")
		else:
			query += " and branch = \'" + str(self.branch) + "\'"	
			
		entries = frappe.db.sql(query, as_dict=True)
		if not entries:
			frappe.msgprint("No Attendance and Overtime Record Found")

		self.set('items', [])

		for d in entries:
			row = self.append('items', {})
			row.update(d)

	def post_journal_entry(self):
                '''
		expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		if not expense_bank_account:
			frappe.throw("Setup Default Expense Bank Account for your Branch")
		'''

                expense_bank_account  = frappe.db.get_single_value("HR Accounts Settings", "salary_payable_account")
                if not expense_bank_account:
			frappe.throw("Setup Default Salary Payable Account in `HR Accounts Settings`")
			
		if self.employee_type == "Muster Roll Employee":
			ot_account = frappe.db.get_single_value("Projects Accounts Settings", "mr_overtime_account")
			if not ot_account:
				frappe.throw("Setup MR Overtime Account in Projects Accounts Settings")
			wage_account = frappe.db.get_single_value("Projects Accounts Settings", "mr_wages_account")
			if not wage_account:
				frappe.throw("Setup MR Wages Account in Projects Accounts Settings")
		elif self.employee_type == "GEP Employee":
			ot_account = frappe.db.get_single_value("Projects Accounts Settings", "gep_overtime_account")
			if not ot_account:
				frappe.throw("Setup GEP Overtime Account in Projects Accounts Settings")
			wage_account = frappe.db.get_single_value("Projects Accounts Settings", "gep_wages_account")
			if not wage_account:
				frappe.throw("Setup GEP Wages Account in Projects Accounts Settings")
		else:
			frappe.throw("Invalid Employee Type")

		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Payment for " + self.employee_type  + " (" + self.branch + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = 'Payment against : ' + self.name;
		je.posting_date = self.posting_date
		je.branch = self.branch
		total_amount = self.total_overall_amount

		if self.total_health_amount and self.employee_type == "GEP Employee":
			total_amount -= flt(self.total_health_amount)

		je.append("accounts", {
				"account": expense_bank_account,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(total_amount),
				"credit": flt(total_amount),
			})
	
		if self.ot_amount:	
			je.append("accounts", {
					"account": ot_account,
					"reference_type": "Process MR Payment",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(self.ot_amount),
					"debit": flt(self.ot_amount),
				})

		if self.wages_amount:
			if self.total_health_amount and self.employee_type == "GEP Employee":
				health_account = frappe.db.get_value("Salary Component", "Health Contribution", "gl_head")
				if not health_account:
					frappe.throw("No GL Account for Health Contribution")
				je.append("accounts", {
						"account": health_account,
						"reference_type": "Process MR Payment",
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"credit_in_account_currency": flt(self.total_health_amount),
						"credit": flt(self.total_health_amount),
					})

			je.append("accounts", {
					"account": wage_account,
					"reference_type": "Process MR Payment",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(self.wages_amount),
					"debit": flt(self.wages_amount),
				})

		je.insert()
		self.db_set("payment_jv", je.name)

		
		if self.total_health_amount and self.employee_type == "GEP Employee":
			health_account = frappe.db.get_value("Salary Component", "Health Contribution", "gl_head")
			if not health_account:
				frappe.throw("No GL Account for Health Contribution")
			hjv = frappe.new_doc("Journal Entry")
			hjv.flags.ignore_permissions = 1 
			hjv.title = "Health Contribution for " + self.employee_type  + " (" + self.branch + ")"
			hjv.voucher_type = 'Bank Entry'
			hjv.naming_series = 'Bank Payment Voucher'
			hjv.remark = 'HC Payment against : ' + self.name;
			hjv.posting_date = self.posting_date
			hjv.branch = self.branch

			hjv.append("accounts", {
					"account": health_account,
					"reference_type": "Process MR Payment",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(self.total_health_amount),
					"debit": flt(self.total_health_amount),
				})

			hjv.append("accounts", {
					"account": expense_bank_account,
					"cost_center": self.cost_center,
					"credit_in_account_currency": flt(self.total_health_amount),
					"credit": flt(self.total_health_amount),
				})
			hjv.insert()
			

@frappe.whitelist()
def get_records(employee_type, fiscal_year, fiscal_month, from_date, to_date, cost_center, branch, dn):
        month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(fiscal_month) + 1
        month = str(month) if cint(month) > 9 else str("0" + str(month))

        total_days = monthrange(cint(fiscal_year), cint(month))[1]
        from_date = str(fiscal_year) + '-' + str(month) + '-' + str('01')
        to_date   = str(fiscal_year) + '-' + str(month) + '-' + str(total_days)

        data = []

        li = frappe.db.sql("""
                                select employee,
                                        sum(number_of_days) as number_of_days,
                                        sum(number_of_hours) as number_of_hours
                                from (
                                        select
                                                employee,
                                                1 as number_of_days,
                                                0 as number_of_hours
                                        from `tabAttendance Others` b
                                        where b.employee_type = '{0}'
                                        and b.date between '{1}' and '{2}'
                                        and b.cost_center = '{3}'
                                        and b.status = 'Present'
                                        and b.docstatus = 1
                                        UNION ALL
                                        select
                                                number as employee,
                                                0 as number_of_days,
                                                c.number_of_hours as number_of_hours
                                        from `tabOvertime Entry` c
                                        where c.employee_type = '{0}'
                                        and c.date between '{1}' and '{2}'
                                        and c.cost_center = '{3}'
                                        and c.docstatus = 1
                                ) as abc
                                group by employee
                        """.format(employee_type, from_date, to_date, cost_center), as_dict=True)

        for i in li:
                rest = frappe.db.sql("""
                                select
                                        '{0}' as type,
                                        name,
                                        person_name,
                                        id_card,
                                        rate_per_day,
                                        rate_per_hour,
                                        salary
                                from `tab{0}` as e
                                where name = '{1}'
                                and not exists(
                                        select 1
                                        from `tabMR Payment Item` i, `tabProcess MR Payment` m
                                        where i.employee = e.name
                                        and i.employee_type = '{0}'
                                        and i.fiscal_year = '{2}'
                                        and i.month = '{3}'
                                        and i.docstatus in (0,1)
                                        and i.parent != '{4}'
                                        and m.name = i.parent
                                        and m.cost_center = '{5}'
                                )
                        """.format(employee_type, i.employee, fiscal_year, fiscal_month, dn, cost_center), as_dict=True)

                if rest:
                        rest[0].update(i)
                        data.append(rest[0])
        '''
        # 2nd Try
        data = frappe.db.sql("""
                        select distinct
                                iw.parenttype,
                                e.name,
                                e.person_name,
                                iw.branch,
                                iw.cost_center,
                                e.id_card,
                                e.rate_per_day,
                                e.rate_per_hour,
                                e.salary
                        from `tab{0}` as e, `tabEmployee Internal Work History` as iw
                        where iw.parent = e.name
                        and iw.cost_center = '{1}'
                        and not exists(
                                        select 1
                                        from `tabMR Payment Item` i
                                        where i.employee = iw.parent
                                        and i.employee_type = iw.parenttype
                                        and i.fiscal_year = '{2}'
                                        and i.month = '{3}'
                                        and i.docstatus in (0,1)
                                        and i.parent != '{4}'
                        )
                """.format(employee_type, cost_center, fiscal_year, fiscal_month, dn), as_dict=True)

        for e in data:
                nod = frappe.db.sql("""
                                select count(*) as number_of_days
                                from `tabAttendance Others` b
                                where b.employee = '{0}'
                                and b.employee_type = '{1}'
                                and b.date between '{2}' and '{3}'
                                and b.cost_center = '{4}'
                                and b.branch = '{5}'
                                and b.status = 'Present'
                                and b.docstatus = 1
                                """.format(e.name, e.parenttype, from_date, to_date, e.cost_center, e.branch))

                noh = frappe.db.sql("""
                                select sum(c.number_of_hours) as number_of_hours
                                from `tabOvertime Entry` c
                                where c.number = '{0}'
                                and c.employee_type = '{1}'
                                and c.date between '{2}' and '{3}'
                                and c.cost_center = '{4}'
                                and c.branch = '{5}'
                                and c.docstatus = 1
                                """.format(e.name, e.parenttype, from_date, to_date, e.cost_center, e.branch))
                
                e.setdefault('number_of_days', nod if nod else 0.0)
                e.setdefault('number_of_hours', noh if noh else 0.0)

        frappe.msgprint(_("{0}").format(data))
        '''
        
        '''
        # 1st Try
	if employee_type == "Muster Roll Employee":
		data = frappe.db.sql("""
                                select
                                        'Muster Roll Employee' as type,
                                        a.name,
                                        a.person_name,
                                        a.id_card,
                                        a.rate_per_day,
                                        a.rate_per_hour,
                                        (
                                                select sum(1)
                                                from `tabAttendance Others` b
                                                where b.employee = a.name
                                                and b.employee_type = '{0}'
                                                and b.date between %s and %s
                                                and b.cost_center = %s
                                                and b.branch = %s
                                                and b.status = 'Present'
                                                and b.docstatus = 1
                                                and not exists(
                                                                select 1
                                                                from `tabMR Payment Item` i
                                                                where i.employee = b.employee
                                                                and i.employee_type = '{0}'
                                                                and i.fiscal_year = '{1}'
                                                                and i.month = '{2}'
                                                                and i.docstatus in (0,1)
                                                                and i.parent != '{3}'
                                                )
                                        ) as number_of_days,
                                        (
                                                select sum(c.number_of_hours)
                                                from `tabOvertime Entry` c
                                                where c.number = a.name
                                                and c.date between %s and %s
                                                and c.cost_center = %s
                                                and c.branch = %s
                                                and c.docstatus = 1
                                                and not exists(
                                                                select 1
                                                                from `tabMR Payment Item` i
                                                                where i.employee = c.number
                                                                and i.employee_type = '{0}'
                                                                and i.fiscal_year = '{1}'
                                                                and i.month = '{2}'
                                                                and i.docstatus in (0,1)
                                                                and i.parent != '{3}'
                                                )
                                        ) as number_of_hours
                                        from `tabMuster Roll Employee` a
                                        where a.cost_center = %s
                                        order by a.person_name
                                        """.format(employee_type, fiscal_year, fiscal_month, dn), (str(from_date), str(to_date), str(cost_center), str(branch), str(from_date), str(to_date), str(cost_center), str(branch), str(cost_center)), as_dict=True)
	elif employee_type == "GEP Employee":
		data = frappe.db.sql("""
                                select
                                        'GEP Employee' as type,
                                        a.name,
                                        a.person_name,
                                        a.id_card,
                                        a.rate_per_day,
                                        a.rate_per_hour,
                                        (
                                                select sum(1)
                                                from `tabAttendance Others` b
                                                where b.employee = a.name
                                                and b.date between %s and %s
                                                and b.cost_center = %s
                                                and b.branch = %s
                                                and b.status = 'Present'
                                                and b.docstatus = 1
                                                and not exists(
                                                                select 1
                                                                from `tabMR Payment Item` i
                                                                where i.employee = b.employee
                                                                and i.employee_type = '{0}'
                                                                and i.fiscal_year = '{1}'
                                                                and i.month = '{2}'
                                                                and i.docstatus in (0,1)
                                                                and i.parent != '{3}'
                                                )
                                        )  as number_of_days,
                                        (
                                                select sum(c.number_of_hours)
                                                from `tabOvertime Entry` c
                                                where c.number = a.name
                                                and c.date between %s and %s
                                                and c.cost_center = %s
                                                and c.branch = %s
                                                and c.docstatus = 1
                                                and not exists(
                                                                select 1
                                                                from `tabMR Payment Item` i
                                                                where i.employee = c.number
                                                                and i.employee_type = '{0}'
                                                                and i.fiscal_year = '{1}'
                                                                and i.month = '{2}'
                                                                and i.docstatus in (0,1)
                                                                and i.parent != '{3}'
                                                )
                                        ) as number_of_hours,
                                        a.salary
                                from `tabGEP Employee` a
                                where a.cost_center = %s
                                order by a.person_name
                                """.format(employee_type, fiscal_year, fiscal_month, dn), (str(from_date), str(to_date), str(cost_center), str(branch), str(from_date), str(to_date), str(cost_center), str(branch), str(cost_center)), as_dict=True)
                                
	else:
		frappe.throw("Invalid Employee Type")
        '''
        
	if data:
		return data
	else:
		frappe.throw(_("No data found!"),title="No Data Found!")
