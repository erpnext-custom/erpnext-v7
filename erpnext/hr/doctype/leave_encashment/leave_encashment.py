# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
	comma_or, get_fullname, nowdate, money_in_words
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from erpnext.custom_autoname import get_auto_name
from datetime import *
from erpnext.hr.doctype.salary_structure.salary_structure import get_salary_tax
from erpnext.accounts.doctype.journal_entry.journal_entry import get_default_bank_cash_account
#from dateutil.relativedelta import *

class OverlapError(frappe.ValidationError): pass
class InsufficientError(frappe.ValidationError): pass

class LeaveEncashment(Document):
        def autoname(self):
                today = datetime.today()
                #self.name = make_autoname(get_auto_name(self) + "/.#####")
                monthyear = str(today.year)
                if len(str(today.month)) < 2:
                        monthyear += "0"+str(today.month)

                self.name = make_autoname(self.employee+"/LE/"+monthyear+"/.#####")
        
        def validate(self):
                self.validate_leave_application()
                self.validate_balances()
                
        def on_submit(self):
		self.post_accounts_entry()

	def before_cancel(self):
		self.check_gl_entry()
	
	def get_leave_credits(self):
                pass
	
	def check_gl_entry(self):
		if self.encash_journal:
			docstat = frappe.db.get_value("Journal Entry", self.encash_journal, "docstatus")
			if docstat == 1:
				frappe.throw("You cannot cancel this document without cancelling the journal entry")


        def validate_leave_application(self):
                from_date, to_date = self.get_current_year_dates()
                ref_docs = ''
                
                encashed_list = frappe.db.sql("""
                        select name from `tabLeave Encashment`
                        where employee = %s and leave_type = %s and docstatus = 1
                        and application_date between %s and %s
                        """,(self.employee, self.leave_type, from_date, to_date), as_dict=1)

                for row in encashed_list:
                        ref_docs += '<br /><a style="color: green" href="#Form/Leave Encashment/{0}">{0}</a>'.format(row.name)
               
                if ref_docs:
                        ref_docs = "<br /><br />Reference: {0}".format(ref_docs)
                        #frappe.throw(_("Employee has already encashed for the current year.{0}").format(ref_docs), OverlapError)
                        frappe.throw(_("Employee has already encashed for the current year.{0}").format(ref_docs))

        def validate_balances(self):
                msg = ''
                #le = get_le_settings(["encashment_days","encashment_min","encashment_lapse"])
                le = get_le_settings()
               
                if flt(self.balance_before if self.balance_before else 0) < flt(le.encashment_min if le.encashment_min else 0):
                        msg = "Minimum leave balance {0} required to encash.".format(le.encashment_min)
                elif flt(self.balance_after if self.balance_after else 0.00) < 0.00:
                        msg = "Insufficient Leave Balance"

                if msg:
                      #frappe.throw(_("{0}").format(msg), InsufficientError)
                      frappe.throw(_("{0}").format(msg))  

        def get_current_year_dates(self):
                from_date = date(date.today().year,1,1).strftime('%Y-%m-%d')
                to_date = date(date.today().year,12,31).strftime('%Y-%m-%d')
                return from_date, to_date

        def get_salary_structure(self):
                salary_struc_list = frappe.db.sql("""
                        select name from `tabSalary Structure`
                        where employee = %s
                        and is_active = 'Yes'
                        and now() between ifnull(from_date,'0000-00-00') and ifnull(to_date,'2050-12-31')
                        order by ifnull(from_date,'0000-00-00') desc limit 1
                """,(self.employee))

                if salary_struc_list:
                        return salary_struc_list[0][0]
                else:
                        frappe.throw(_("No Active Salary Structure found for the employee."))
                        
                return salary_struc_list[0][0]
        
        def post_accounts_entry(self):
                employee = frappe.get_doc("Employee", self.employee)
                default_bank_cash_account = get_default_bank_cash_account(employee.company, "Bank")
                sal_struc_name = self.get_salary_structure()
                #le = get_le_settings(["expense_account", "tax_account"])
                le = get_le_settings()
                if sal_struc_name:
                        sal_struc= frappe.get_doc("Salary Structure",sal_struc_name)
                        for d in sal_struc.earnings:
                                if d.salary_component == 'Basic Pay':
                                        basic_pay = flt(d.amount)
                else:
                        frappe.throw(_("No Active salary structure found."))
                        
                if basic_pay:
                        salary_tax = get_salary_tax(basic_pay)

                salary_tax = flt(salary_tax) if salary_tax else 0.00                
                
                je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = 'Leave Encashment - '+str(employee.employee_name)
                je.voucher_type = 'Bank Entry'
                je.naming_series = 'Bank Payment Voucher'
                je.company = employee.company
                je.remark = 'Payment against Leave Encashment: ' + self.name;
                je.posting_date = self.application_date
                je.total_amount_in_words =  money_in_words(flt(basic_pay)-flt(salary_tax))

                je.append("accounts", {
                        "account": le.expense_account,
                        "debit_in_account_currency": flt(basic_pay),
                        "reference_type": "Leave Encashment",
                        "reference_name": self.name,
                        #"party_type": "Employee",
                        #"party": self.employee,
                        "cost_center": self.cost_center,
                        "party_check": 0
                })

                je.append("accounts", {
                        "account": le.tax_account,
                        "credit_in_account_currency": flt(salary_tax),
                        "reference_type": "Leave Encashment",
                        "reference_name": self.name,
                        #"party_type": "Employee",
                        #"party": self.employee,
                        "cost_center": self.cost_center,
                        "party_check": 0
                })

                je.append("accounts", {
                        "account": "Sundry Creditors - Employee - SMCL",
                        "debit_in_account_currency": flt(basic_pay),
                        "reference_type": "Leave Encashment",
                        "reference_name": self.name,
                        "party_type": "Employee",
                        "party": self.employee,
                        "cost_center": self.cost_center,
                        "party_check": 0
                })

                je.append("accounts", {
                        "account": "Sundry Creditors - Employee - SMCL",
                        "credit_in_account_currency": flt(basic_pay),
                        "reference_type": "Leave Encashment",
                        "reference_name": self.name,
                        "party_type": "Employee",
                        "party": self.employee,
                        "cost_center": self.cost_center,
                        "party_check": 0
                })

                je.append("accounts", {
                        "account": default_bank_cash_account.account,
                        "credit_in_account_currency": (flt(basic_pay)-flt(salary_tax)),
                        "reference_type": "Leave Encashment",
                        "reference_name": self.name,
                        "balance": default_bank_cash_account.balance,
                        "account_currency": default_bank_cash_account.account_currency,
                        "account_type": default_bank_cash_account.account_type,
                        "cost_center": self.cost_center
                })
                je.insert()

		self.db_set("encash_journal", je.name)
		self.db_set("encashment_amount", flt(basic_pay))
		self.db_set("tax_amount", flt(salary_tax))
                
@frappe.whitelist()
def get_employee_cost_center(division):
        #cost_center = frappe.db.get_value("Division", division, "cost_center")
        division = frappe.get_doc("Division", division)
        return division.cost_center

@frappe.whitelist()                        
def get_le_settings(*arg, **kwargs):
        le = frappe.db.get_value("Leave Encashment Settings", filters = None, \
                        fieldname = ["encashment_days","encashment_min","encashment_lapse","expense_account","tax_account"], as_dict = True)
        
        return le
