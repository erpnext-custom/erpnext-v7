# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint
from calendar import monthrange
from erpnext.hr.hr_custom_functions import get_officiating_employee
from erpnext.hr.doctype.approver_settings.approver_settings import get_final_approver

class ProcessMRPayment(Document):
	def validate(self):
		self.validate_workflow()
                # Setting `monthyear`
		month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(self.month) + 1
		month = str(month) if cint(month) > 9 else str("0" + str(month))
                self.monthyear = str(self.fiscal_year)+str(month)
                total_days = monthrange(cint(self.fiscal_year), cint(month))[1]
                
		if self.items:
			total_ot = total_wage = total_health = salary = 0
			
			for a in self.items:
                                self.duplicate_entry_check(a.employee, a.employee_type, a.idx)
                                a.fiscal_year   = self.fiscal_year
                                a.month         = self.month
                                if not a.lumpsum:
				        a.total_ot_amount = flt(a.hourly_rate) * flt(a.number_of_hours)
				        a.total_wage = flt(a.daily_rate) * flt(a.number_of_days)
                                else:
                                        a.total_wage = a.lumpsum
                                        a.total_ot_amount = 0
				
				if a.employee_type == "DES Employee":
                                        salary = frappe.db.get_value("DES Employee", a.employee, "salary")
                                        if flt(a.total_wage) > flt(salary):
                                                a.total_wage = flt(salary)

                                        if flt(total_days) == flt(a.number_of_days):
                                                a.total_wage = flt(salary)
                                        
				a.total_amount = flt(a.total_ot_amount) + flt(a.total_wage)
				total_ot += flt(a.total_ot_amount)
				total_wage += flt(a.total_wage)
				if a.employee_type == "DES Employee":
					a.health = flt(a.total_wage) * 0.01
					a.wage_payable = flt(a.total_wage) - flt(a.health)
					total_health += flt(a.health)
				
			total = total_ot + total_wage
			self.wages_amount = total_wage
			self.ot_amount = total_ot
			self.total_overall_amount = total
			if a.employee_type == "DES Employee":
				self.total_health_amount = total_health
                #frappe.msgprint("Reached here")

	def validate_workflow(self):
		# Verified By Supervisor
		# Forwarding by Unit Managers
		if self.workflow_state == "Verified By Supervisor":
			unit_manager, unit_manager_name = frappe.db.get_value("Unit", self.unit, ["employee", "employee_name"])
			if not unit_manager:
				frappe.throw("Please assgin Unit Manager for {0} unit".format(self.unit))
				
			unit_manager_userid = frappe.db.get_value("Employee", unit_manager, "user_id")
			officiating = get_officiating_employee(unit_manager)
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
				if frappe.session.user != officiating[0]:
					frappe.throw("Only Officiating Unit Manager {} will be able to forward the Payment".format(officiating[1]))
			else:
				if frappe.session.user != unit_manager_userid:				
					frappe.throw("Only Unit Manager {0} ({1}) is allowed to forward MR Payment".format(unit_manager, unit_manager_name))
		# BY Respective GM
		elif self.workflow_state == "Waiting Approval":
			final_approver = frappe.db.get_value("Employee", {"user_id": get_final_approver(self.branch)}, ["user_id","employee_name","designation","name"])
			officiating = get_officiating_employee(final_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
				if frappe.session.user != officiating[0]:
					frappe.throw("Only Officiating GM {} will be able to forward the Payment".format(officiating[1]))
			else:
				if frappe.session.user != final_approver[0]:				
					frappe.throw("Only GM {0} ({1}) is allowed to forward MR Payment".format(final_approver[1], final_approver[0]))

		elif self.workflow_state == "Approved":
			approver = frappe.db.get_value("Employee", {"designation":"Chief Executive Officer", "status": 'Active'}, ["user_id","employee_name","designation","name"])
			officiating = get_officiating_employee(approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
				if frappe.session.user != officiating[0]:
					frappe.throw("Only Officiating CEO {} will be able to forward the Payment".format(officiating[1]))
			else:
				if frappe.session.user != approver[0]:				
					frappe.throw("Only CEO, {0} ({1}) is allowed to forward MR Payment".format(approver[1], approver[0]))
			
	def on_submit(self):
		self.post_journal_entry()

	def before_cancel(self):
		cl_status = frappe.db.get_value("Journal Entry", self.payment_jv, "docstatus")
		if cl_status and cl_status != 2:
			frappe.throw("You need to cancel the journal entry related to this payment first!")
		
		self.db_set('payment_jv', "")

        def update_details(self):
                if self.project:
                        self.branch = frappe.db.get_value("Project", self.project, "branch")
                        self.cost_center = frappe.db.get_value("Project", self.project, "cost_center")
                elif self.branch:
                        self.cost_center = frappe.db.get_value("Branch", self.branch, "cost_center")
                else:
                        pass
        
        def duplicate_entry_check(self, employee, employee_type, idx):
                pl = frappe.db.sql("""
                                select
                                        i.name,
                                        i.parent,
                                        i.docstatus,
                                        i.person_name,
                                        i.employee
                                from `tabMR Payment Item` i, `tabProcess MR Payment` m
                                where i.employee = '{0}'
                                and i.employee_type = '{1}'
                                and i.fiscal_year = '{2}'
                                and i.month = '{3}'
                                and m.docstatus in (0,1)
                                and i.parent != '{4}'
				and i.parent = m.name
				and m.cost_center = '{5}'
                        """.format(employee, employee_type, self.fiscal_year, self.month, self.name, self.cost_center), as_dict=1)

                for l in pl:
                        msg = 'Payment already processed for `{2}({3})`<br>RowId#{1}: Reference# <a href="#Form/Process MR Payment/{0}">{0}</a>'.format(l.parent, idx, l.person_name, l.employee)
                        frappe.throw(_("{0}").format(msg), title="Duplicate Record Found")                        
                
	#Populate Budget Accounts with Expense and Fixed Asset Accounts
	def load_employee(self):
		if self.employee_type == "DES Employee":
			query = "select 'DES Employee' as employee_type, name as employee, person_name, id_card, rate_per_day as daily_rate, rate_per_hour as hourly_rate from `tabDES Employee` where status = 'Active'"
		elif self.employee_type == "Muster Roll Employee":
                        #Added by cheten on 06-10-2020
                        #if not is_lumpsum:
			query = "select 'Muster Roll Employee' as employee_type, name as employee, person_name, id_card, rate_per_day as daily_rate, rate_per_hour as hourly_rate from `tabMuster Roll Employee` where status = 'Active'"
                        #else:
                                #query = "select 'Muster Roll Employee' as employee_type, name as employee, person_name, id_card, lumpsum from `tabMuster Roll Employee` where status = 'Active'"
		else:
			frappe.throw("Select employee record first!")
	
		if not self.branch:
			frappe.throw("Select branch first!")

		query += " and branch = \'" + str(self.branch) + "\'"
                if self.unit:
                        query += " and unit = \'" + str(self.unit) + "\'"        	
			
		entries = frappe.db.sql(query, as_dict=True)
		if not entries:
			frappe.msgprint("No Attendance and Overtime Record Found")

		self.set('items', [])

		for d in entries:
			row = self.append('items', {})
			row.update(d)

        # Ver 3.0 Begins, by SHIV on 2018/11/05
        # Following code commented by SHIV on 2018/11/05
        """
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
		elif self.employee_type == "DES Employee":
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
		total_amount = flt(self.total_overall_amount)

                '''
		if self.total_health_amount and self.employee_type == "DES Employee":
			total_amount -= flt(self.total_health_amount)
                '''
                
                total_amount = flt(self.wages_amount,2) + flt(self.ot_amount,2) - flt(self.total_health_amount,2)
                
		je.append("accounts", {
				"account": expense_bank_account,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(total_amount,2),
				"credit": flt(total_amount,2),
			})
		if self.ot_amount:	
			je.append("accounts", {
					"account": ot_account,
					"reference_type": "Process MR Payment",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(self.ot_amount,2),
					"debit": flt(self.ot_amount,2),
				})

		if self.wages_amount:
			if self.total_health_amount and self.employee_type == "DES Employee":
				health_account = frappe.db.get_value("Salary Component", "Health Contribution", "gl_head")
				if not health_account:
					frappe.throw("No GL Account for Health Contribution")
				je.append("accounts", {
						"account": health_account,
						"reference_type": "Process MR Payment",
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"credit_in_account_currency": flt(self.total_health_amount,2),
						"credit": flt(self.total_health_amount,2),
					})

			je.append("accounts", {
					"account": wage_account,
					"reference_type": "Process MR Payment",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(self.wages_amount,2),
					"debit": flt(self.wages_amount,2),
				})

		je.insert()
		self.db_set("payment_jv", je.name)
		
		if self.total_health_amount and self.employee_type == "DES Employee":
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
					"debit_in_account_currency": flt(self.total_health_amount,2),
					"debit": flt(self.total_health_amount,2),
				})

			hjv.append("accounts", {
					"account": expense_bank_account,
					"cost_center": self.cost_center,
					"credit_in_account_currency": flt(self.total_health_amount,2),
					"credit": flt(self.total_health_amount,2),
				})
			hjv.insert()
	"""

        # Following code added by SHIV on 2018/11/05
	def post_journal_entry(self):
                expense_bank_account = None
                wage_account = None
                ot_account = None
                health_account = None
                
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
		elif self.employee_type == "DES Employee":
			ot_account = frappe.db.get_single_value("Projects Accounts Settings", "gep_overtime_account")
			if not ot_account:
				frappe.throw("Setup GEP Overtime Account in Projects Accounts Settings")
			wage_account = frappe.db.get_single_value("Projects Accounts Settings", "gep_wages_account")
			if not wage_account:
				frappe.throw("Setup GEP Wages Account in Projects Accounts Settings")
		else:
			frappe.throw("Invalid Employee Type")

                if self.total_health_amount:
                        health_account = frappe.db.get_value("Salary Component", "Health Contribution", "gl_head")
			if not health_account:
				frappe.throw("No GL Account for Health Contribution")

                li = frappe.db.sql("""
                        select business_activity,
                                sum(ifnull(total_wage,0)) as total_wage,
                                sum(ifnull(total_ot_amount,0)) as total_ot,
                                sum(ifnull(health,0)) as total_health
                        from `tabMR Payment Item`
                        where parent = '{0}'
                        group by business_activity
                        order by business_activity
                """.format(self.name), as_dict = True)

                # Posting payables
                if flt(self.wages_amount,2) + flt(self.ot_amount,2) - flt(self.total_health_amount,2):
                        je = frappe.new_doc("Journal Entry")
                        je.flags.ignore_permissions = 1 
                        je.title = "Payment for " + self.employee_type  + " (" + self.branch + ")"
                        je.voucher_type = 'Bank Entry'
                        je.naming_series = 'Bank Payment Voucher'
                        je.remark = 'Payment against : ' + self.name;
                        je.posting_date = self.posting_date
                        je.branch = self.branch
                        
                        for i in li:
                                total_amount = flt(i.total_wage,2) + flt(i.total_ot,2) - flt(i.total_health,2) 
                                if i.total_wage:
                                        je.append("accounts", {
                                                "account": wage_account,
                                                "reference_type": "Process MR Payment",
                                                "reference_name": self.name,
                                                "cost_center": self.cost_center,
                                                "debit_in_account_currency": flt(i.total_wage,2),
                                                "debit": flt(i.total_wage,2),
                                                "business_activity": i.business_activity
                                        })

                                if i.total_ot:
                                        je.append("accounts", {
                                                "account": ot_account,
                                                "reference_type": "Process MR Payment",
                                                "reference_name": self.name,
                                                "cost_center": self.cost_center,
                                                "debit_in_account_currency": flt(i.total_ot,2),
                                                "debit": flt(i.total_ot,2),
                                                "business_activity": i.business_activity
                                        })

                                if i.total_health:
                                        je.append("accounts", {
                                                "account": health_account,
                                                "reference_type": "Process MR Payment",
                                                "reference_name": self.name,
                                                "cost_center": self.cost_center,
                                                "credit_in_account_currency": flt(i.total_health,2),
                                                "credit": flt(i.total_health,2),
                                                "business_activity": i.business_activity
                                        })
                                        
                                je.append("accounts", {
                                        "account": expense_bank_account,
                                        "cost_center": self.cost_center,
                                        "credit_in_account_currency": flt(total_amount,2),
                                        "credit": flt(total_amount,2),
                                        "business_activity": i.business_activity
                                })

                        je.insert()
                        self.db_set("payment_jv", je.name)

                # Posting health contribution remittance
                if self.total_health_amount:
                        hjv = frappe.new_doc("Journal Entry")
			hjv.flags.ignore_permissions = 1 
			hjv.title = "Health Contribution for " + self.employee_type  + " (" + self.branch + ")"
			hjv.voucher_type = 'Bank Entry'
			hjv.naming_series = 'Bank Payment Voucher'
			hjv.remark = 'HC Payment against : ' + self.name;
			hjv.posting_date = self.posting_date
			hjv.branch = self.branch
			
                        for i in li:
                                if i.total_health:
                                        hjv.append("accounts", {
                                                "account": health_account,
                                                "reference_type": "Process MR Payment",
                                                "reference_name": self.name,
                                                "cost_center": self.cost_center,
                                                "debit_in_account_currency": flt(i.total_health,2),
                                                "debit": flt(i.total_health,2),
                                                "business_activity": i.business_activity
                                        })

                                        hjv.append("accounts", {
                                                "account": expense_bank_account,
                                                "cost_center": self.cost_center,
                                                "credit_in_account_currency": flt(i.total_health,2),
                                                "credit": flt(i.total_health,2),
                                                "business_activity": i.business_activity
                                        })
                        hjv.insert()

@frappe.whitelist()
def get_records(employee_type, fiscal_year, fiscal_month, from_date, to_date, cost_center, branch, dn, unit):
        month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(fiscal_month) + 1
        month = str(month) if cint(month) > 9 else str("0" + str(month))

        total_days = monthrange(cint(fiscal_year), cint(month))[1]
        from_date = str(fiscal_year) + '-' + str(month) + '-' + str('01')
        to_date   = str(fiscal_year) + '-' + str(month) + '-' + str(total_days)

        data = []
        li = frappe.db.sql("""
                                select employee,
                                        sum(number_of_days) as number_of_days,
                                        sum(number_of_hours) as number_of_hours,
                                        {4} as noof_days_in_month
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
                                        group by employee, b.date
                                        UNION ALL
                                        select
                                                number as employee,
                                                0 as number_of_days,
                                                max(c.number_of_hours) as number_of_hours
                                        from `tabOvertime Entry` c
                                        where c.employee_type = '{0}'
                                        and c.date between '{1}' and '{2}'
                                        and c.cost_center = '{3}'
                                        and c.docstatus = 1
                                        group by number, c.date
                                ) as abc
                                group by employee
                        """.format(employee_type, from_date, to_date, cost_center, total_days), as_dict=True)
        frappe.msgprint(str(li))

        for i in li:
                if not i.is_lumpsum:
                        rest = frappe.db.sql("""
                                select
                                        '{0}' as type,
                                        name,
                                        person_name,
                                        id_card,
                                        business_activity,
                                        rate_per_day,
                                        rate_per_hour,
                                        is_lumpsum,
                                        lumpsum,
                                        salary
                                from `tab{0}` as e
                                where name = '{1}'
                                and unit = '{6}'
                                and not exists(
                                        select 1
                                        from `tabMR Payment Item` i, `tabProcess MR Payment` m
                                        where i.employee = e.name
                                        and i.employee_type = '{0}'
                                        and i.fiscal_year = '{2}'
                                        and i.month = '{3}'
                                        and m.docstatus in (0,1)
                                        and i.parent != '{4}'
                                        and m.name = i.parent
                                        and m.cost_center = '{5}'
                                )
                        """.format(employee_type, i.employee, fiscal_year, fiscal_month, dn, cost_center, unit), as_dict=True)

                if rest:
                        rest[0].update(i)
                        data.append(rest[0])
                        # frappe.msgprint(str(data))


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
	elif employee_type == "DES Employee":
		data = frappe.db.sql("""
                                select
                                        'DES Employee' as type,
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
                                from `tabDES Employee` a
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
