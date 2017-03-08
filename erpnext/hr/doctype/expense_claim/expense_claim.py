# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SSK		                   10/08/2016         Account Posting is modified
1.0		  SSK		                   12/08/2016         Sanctioned Amount should be after advance deduction.
1.0               SSK                              07/09/2016         Validations for Expense Claim Date added
1.0               SSK                              09/09/2016         Voucher construction is modified
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import get_fullname, flt
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name
from frappe import msgprint
from frappe.utils import cint, flt, nowdate
from frappe.utils import money_in_words

class InvalidExpenseApproverError(frappe.ValidationError): pass

class ExpenseClaim(Document):
	def get_feed(self):
		return _("{0}: From {0} for {1}").format(self.approval_status,
			self.employee_name, self.total_claimed_amount)

	def validate(self):
		self.validate_sanctioned_amount()
		self.validate_expense_approver()
		self.calculate_total_amount()
		set_employee_name(self)
		self.set_expense_account()
		self.validate_dates()
		if self.task and not self.project:
			self.project = frappe.db.get_value("Task", self.task, "project")

	def on_submit(self):
		if self.approval_status=="Draft":
			frappe.throw(_("""Approval Status must be 'Approved' or 'Rejected'"""))


		#if self.approval_status=="Approved":
                #        make_bank_entry(self.name)
                        
		self.update_task_and_project()

	def on_cancel(self):
		self.update_task_and_project()

	def update_task_and_project(self):
		if self.task:
			self.update_task()
		elif self.project:
			frappe.get_doc("Project", self.project).update_project()

        # Ver 1.0 Begins, added by SSK on 07/09/2016
        def validate_dates(self):
                max_date = ""
                
                for row in self.get('expenses'):
                        if max_date:
                                pass
                        else:
                                max_date = row.to_date

                        if row.to_date > max_date:
                                max_date = row.to_date

                if self.workflow_state != 'Travel Request Draft' and self.expense_date == "":
                        frappe.throw(_("Expense Claim Date should be a valid date."))
                elif self.expense_date and self.expense_date < self.posting_date:
                        frappe.throw(_("Expense Claim Date cannot be before travel request date."))
                elif self.expense_date and self.expense_date < max_date:
                        frappe.throw(_("Expense Claim Date should be on or after {0}".format(max_date)))

	def calculate_total_amount(self):
		self.total_claimed_amount = 0
		self.total_sanctioned_amount = 0
		# Ver 1.0 Begins added by SSK on 12/08/2016, total_advance_amount is introducted
		self.total_advance_amount = 0
		
		for d in self.get('expenses'):
			self.total_claimed_amount += flt(flt(d.claim_amount) if d.claim_amount else 0.00)
			self.total_sanctioned_amount += flt(flt(d.sanctioned_amount) if d.sanctioned_amount  else 0.00)
			# Ver 1.0 Begins added by SSK on 12/08/2016, total_advance_amount is introducted
			self.total_advance_amount += flt(flt(d.advance_total_amount) if d.advance_total_amount else 0.00)
			
                # Ver 1.0 Begins added by SSK on 12/08/2016, total_advance_amount is introducted
		self.total_sanctioned_amount -=  flt(self.total_advance_amount)

	def validate_expense_approver(self):
		if self.exp_approver and "Expense Approver" not in frappe.get_roles(self.exp_approver):
			frappe.throw(_("{0} ({1}) must have role 'Expense Approver'")\
				.format(get_fullname(self.exp_approver), self.exp_approver), InvalidExpenseApproverError)

	def update_task(self):
		task = frappe.get_doc("Task", self.task)
		task.update_total_expense_claim()
		task.save()

	def validate_sanctioned_amount(self):
		for d in self.get('expenses'):
			if flt(d.sanctioned_amount) > flt(d.claim_amount):
				frappe.throw(_("Sanctioned Amount cannot be greater than Claim Amount in Row {0}.").format(d.idx))

	def set_expense_account(self):
		for expense in self.expenses:
			if not expense.default_account:
				expense.default_account = get_expense_claim_account(expense.expense_type, self.company)["account"]
		
@frappe.whitelist()
def get_expense_approver(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("employee"):
		frappe.throw(_("Please select Employee Record first."))

	approver = frappe.get_value("Employee", filters.get("employee"), "reports_to")
	approver_id = frappe.get_value("Employee", approver, "user_id")
	
	lists = frappe.db.sql("""
		select u.name, concat(u.first_name, ' ', u.last_name)
		from tabUser u where
		u.enabled = 1 and u.name = %s
	""", approver_id)

	if lists:
		return lists
	else:
		frappe.throw("Set \'Reports To \' field for employee " + str(filters.get("employee")))
		#and u.enabled = 1 and u.name like %s
	#""", ("%" + txt + "%"))

@frappe.whitelist()
def get_expense_approver_mod(employee):
	return frappe.db.sql("""
		select u.name, concat(u.first_name, ' ', u.last_name)
		from tabUser u, tabUserRole r, tabEmployee e1, tabEmployee e2
		where u.name = r.parent and r.role = 'Expense Approver' 
		and u.enabled  = 1
		and e1.employee = '%s'
		and e1.reports_to = e2.employee
		and u.name = e2.user_id
	""" % (employee))


@frappe.whitelist()
def make_bank_entry(docname):
	from erpnext.accounts.doctype.journal_entry.journal_entry import get_default_bank_cash_account

	expense_claim = frappe.get_doc("Expense Claim", docname)
	default_bank_cash_account = get_default_bank_cash_account(expense_claim.company, "Bank")

        # Ver 1.0 by SSK on 10/08/2016, fetching cost_center for the employee
        #msgprint(expense_claim.employee)
        cost_center = frappe.db.sql("""
                        select t2.cost_center
                        from `tabEmployee` t1, `tabDivision` t2
                        where t2.name = t1.division
                        and t2.dpt_name = t1.department
                        and t2.branch = t1.branch
                        and t1.name = '%s'
                """ % (expense_claim.employee))

        # Ver 1.0 Ends, by SSK on 10/08/2016

	je = frappe.new_doc("Journal Entry")
	je.title = 'Travel Claims - '+str(expense_claim.employee)+' '+str(expense_claim.employee_name)
	je.voucher_type = 'Bank Entry'
	je.naming_series = 'Bank Payment Voucher'
	je.company = expense_claim.company
	je.remark = 'Payment against Expense Claim: ' + docname;
        #je.posting_date = nowdate()
	je.posting_date = expense_claim.expense_date
        je.total_amount_in_words =  money_in_words(expense_claim.total_sanctioned_amount)

        # Ver 1.0 Begins, added by SSK on 09/09/2016
        # Following code is commented and the equivalet is passed
        '''
	for expense in expense_claim.expenses:
		je.append("accounts", {
			"account": expense.default_account,
			"debit_in_account_currency": expense.sanctioned_amount,
			"reference_type": "Expense Claim",
			"reference_name": expense_claim.name,
                        "party_type": "Employee",
                        "party": expense_claim.employee,
                        "cost_center": cost_center[0][0],
                        "party_check": 0
		})
        '''

        default_accounts = frappe.db.sql("""
                                select default_account, sum(ifnull(sanctioned_amount,0)) sanctioned_amount,
                                sum(ifnull(advance_total_amount,0)) advance_amount
                                from `tabExpense Claim Detail`
                                where parent = '%s'
                                group by default_account
                                """ % (expense_claim.name), as_dict=True)

        for da in default_accounts:
                if flt(da.sanctioned_amount if da.sanctioned_amount else 0.00) > 0.00:
                        je.append("accounts", {
                                "account": da.default_account,
                                "debit_in_account_currency": da.sanctioned_amount,
                                "reference_type": "Expense Claim",
                                "reference_name": expense_claim.name,
                                "cost_center": cost_center[0][0],
                                "party_check": 0
                        })
                
        # Ver 1.0 Ends

        if flt(expense_claim.total_advance_amount if expense_claim.total_advance_amount else 0.00) > 0.00:
                je.append("accounts", {
                        "account": "Advance to Employee-Travel - SMCL",
                        "credit_in_account_currency": flt(expense_claim.total_advance_amount),
                        "reference_type": "Expense Claim",
                        "reference_name": expense_claim.name,
                        "party_type": "Employee",
                        "party": expense_claim.employee,
                        "cost_center": cost_center[0][0],
                        "party_check": 0
                })

        if flt(expense_claim.total_sanctioned_amount if expense_claim.total_sanctioned_amount else 0.00) > 0.00:
                je.append("accounts", {
                        "account": "Sundry Creditors - Employee - SMCL",
                        "debit_in_account_currency": expense_claim.total_sanctioned_amount,
                        "reference_type": "Expense Claim",
                        "reference_name": expense_claim.name,
                        "party_type": "Employee",
                        "party": expense_claim.employee,
                        "cost_center": cost_center[0][0],
                        "party_check": 0
                })

                je.append("accounts", {
                        "account": "Sundry Creditors - Employee - SMCL",
                        "credit_in_account_currency": expense_claim.total_sanctioned_amount,
                        "reference_type": "Expense Claim",
                        "reference_name": expense_claim.name,
                        "party_type": "Employee",
                        "party": expense_claim.employee,
                        "cost_center": cost_center[0][0],
                        "party_check": 0
                })
                
                je.append("accounts", {
                        "account": default_bank_cash_account.account,
                        "credit_in_account_currency": expense_claim.total_sanctioned_amount,
                        "reference_type": "Expense Claim",
                        "reference_name": expense_claim.name,
                        "balance": default_bank_cash_account.balance,
                        "account_currency": default_bank_cash_account.account_currency,
                        "account_type": default_bank_cash_account.account_type,
                        "cost_center": "Corporate Head Office - SMCL"
                })

                je.insert()
                
        msgprint(_("Posting to Accounts Successful..."))
	#return je.as_dict()

@frappe.whitelist()
def get_expense_claim_account(expense_claim_type, company):
	account = frappe.db.get_value("Expense Claim Account",
		{"parent": expense_claim_type, "company": company}, "default_account")
	
	if not account:
		frappe.throw(_("Please set default account in Expense Claim Type {0}")
			.format(expense_claim_type))
	
	return {
		"account": account
	}
