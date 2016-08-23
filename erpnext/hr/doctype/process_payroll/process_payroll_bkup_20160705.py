# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt, nowdate
from frappe import _
from frappe import msgprint

from frappe.model.document import Document

class ProcessPayroll(Document):

	def get_emp_list(self):
		"""
			Returns list of active employees based on selected criteria
			and for which salary structure exists
		"""

		cond = self.get_filter_condition()
		cond += self.get_joining_releiving_condition()

		emp_list = frappe.db.sql("""
			select t1.name
			from `tabEmployee` t1, `tabSalary Structure` t2
			where t1.docstatus!=2 and t2.docstatus != 2
			and t1.name = t2.employee
		%s """% cond)

		return emp_list


	def get_filter_condition(self):
		self.check_mandatory()

		cond = ''
		for f in ['company', 'branch', 'department', 'designation']:
			if self.get(f):
				cond += " and t1." + f + " = '" + self.get(f).replace("'", "\'") + "'"

		return cond


	def get_joining_releiving_condition(self):
		m = get_month_details(self.fiscal_year, self.month)
		cond = """
			and ifnull(t1.date_of_joining, '0000-00-00') <= '%(month_end_date)s'
			and ifnull(t1.relieving_date, '2199-12-31') >= '%(month_start_date)s'
		""" % m
		return cond


	def check_mandatory(self):
		for f in ['company', 'month', 'fiscal_year']:
			if not self.get(f):
				frappe.throw(_("Please set {0}").format(f))

	def create_sal_slip(self):
		"""
			Creates salary slip for selected employees if already not created
		"""

		emp_list = self.get_emp_list()
		ss_list = []
		for emp in emp_list:
			if not frappe.db.sql("""select name from `tabSalary Slip`
					where docstatus!= 2 and employee = %s and month = %s and fiscal_year = %s and company = %s
					""", (emp[0], self.month, self.fiscal_year, self.company)):
				ss = frappe.get_doc({
					"doctype": "Salary Slip",
					"fiscal_year": self.fiscal_year,
					"employee": emp[0],
					"month": self.month,
					"email_check": self.send_email,
					"company": self.company,
				})
				ss.insert()
				ss_list.append(ss.name)

		return self.create_log(ss_list)


	def create_log(self, ss_list):
		log = "<p>" + _("No employee for the above selected criteria OR salary slip already created") + "</p>"
		if ss_list:
			log = "<b>" + _("Salary Slip Created") + "</b>\
			<br><br>%s" % '<br>'.join(self.format_as_links(ss_list))
		return log


	def get_sal_slip_list(self):
		"""
			Returns list of salary slips based on selected criteria
			which are not submitted
		"""
		cond = self.get_filter_condition()
		ss_list = frappe.db.sql("""
			select t1.name from `tabSalary Slip` t1
			where t1.docstatus = 0 and month = %s and fiscal_year = %s %s
		""" % ('%s', '%s', cond), (self.month, self.fiscal_year))
		return ss_list


	def submit_salary_slip(self):
		"""
			Submit all salary slips based on selected criteria
		"""
		ss_list = self.get_sal_slip_list()
		not_submitted_ss = []
		for ss in ss_list:
			ss_obj = frappe.get_doc("Salary Slip",ss[0])
			try:
				ss_obj.email_check = self.send_email
				ss_obj.submit()
			except Exception,e:
				not_submitted_ss.append(ss[0])
				frappe.msgprint(e)
				continue

		return self.create_submit_log(ss_list, not_submitted_ss)


	def create_submit_log(self, all_ss, not_submitted_ss):
		log = ''
		if not all_ss:
			log = "No salary slip found to submit for the above selected criteria"
		else:
			all_ss = [d[0] for d in all_ss]

		submitted_ss = self.format_as_links(list(set(all_ss) - set(not_submitted_ss)))
		if submitted_ss:
			mail_sent_msg = self.send_email and " (Mail has been sent to the employee)" or ""
			log = """
			<b>Salary Slips Submitted %s:</b>\
			<br><br> %s <br><br>
			""" % (mail_sent_msg, '<br>'.join(submitted_ss))

		if not_submitted_ss:
			log += """
				<b>Not Submitted Salary Slips: </b>\
				<br><br> %s <br><br> \
				Reason: <br>\
				May be company email id specified in employee master is not valid. <br> \
				Please mention correct email id in employee master or if you don't want to \
				send mail, uncheck 'Send Email' checkbox. <br>\
				Then try to submit Salary Slip again.
			"""% ('<br>'.join(not_submitted_ss))
		return log

	def format_as_links(self, ss_list):
		return ['<a href="#Form/Salary Slip/{0}">{0}</a>'.format(s) for s in ss_list]


	def get_total_salary(self):
		"""
			Get total salary amount from submitted salary slip based on selected criteria
		"""
		cond = self.get_filter_condition()
		tot = frappe.db.sql("""
			select sum(rounded_total) from `tabSalary Slip` t1
			where t1.docstatus = 1 and month = %s and fiscal_year = %s %s
		""" % ('%s', '%s', cond), (self.month, self.fiscal_year))

		return flt(tot[0][0])

        #
        # Ver20160705.1 added by SSK, account rules
        #
        def get_account_rules(self):
                from frappe.utils import money_in_words

                items = []
                items.extend(frappe.db.sql("""select ss.branch,ss.department,ss.division,d.cost_center,
                        sum(rounded_total) as total_amt
                         from `tabSalary Slip` ss, `tabDivision` d
                        where d.name = ss.division
                          and d.dpt_name = ss.department
                          and d.branch = ss.branch
                          and ss.month = %s
                          and ss.fiscal_year = %s
                          and ss.docstatus = 1
                        group by ss.branch,ss.department,ss.division,d.cost_center
                """ % (self.month, self.fiscal_year),as_dict=1))

                #
                # GL Mapping
                #
                accounts = []
                tot_deductions = 0
                tot_earnings = 0
                for item in items:
                        deductions = []
                        earnings = []

                        #
                        # Deductions
                        #
                        query = """select (case
                                                when sd.d_type = 'BNB Loan' then 'Financial Institution Loan - SMCL'
                                                when sd.d_type = 'BOB Loan' then 'Financial Institution Loan - SMCL'
                                                when sd.d_type = 'DPNB Loan' then 'Financial Institution Loan - SMCL'
                                                when sd.d_type = 'NPPF Loan' then 'Financial Institution Loan - SMCL'
                                                when sd.d_type = 'Other Loan' then 'Financial Institution Loan - SMCL'
                                                when sd.d_type = 'Health Contribution' then 'Health Contribution - SMCL'
                                                when sd.d_type = 'Salary Tax' then 'Salary Tax - SMCL'
                                                when sd.d_type = 'PF' then 'Provident Fund - SMCL'
                                                when sd.d_type = 'Group Insurance Scheme' then 'Group Insurance Scheme - SMCL'
                                                when sd.d_type = 'Salary Advance Deductions' then 'Salary Advance Recovery - SMCL'
                                           end) as account,
                                sum(d_modified_amount) as credit_in_account_currency,
                                'Bank of Bhutan Ltd - SMCL' as against_account,
                                '%s' as cost_center
                                from `tabSalary Slip Deduction` sd, `tabSalary Slip` ss
                               where ss.name = sd.parent
                                 and sd.d_modified_amount > 0
                                 and ss.month = '%s'
                                 and ss.fiscal_year = %s
                                 and ss.docstatus = 1
                                 and ss.branch = '%s'
                                 and ss.department = '%s'
                                 and ss.division = '%s'
                               group by (case
                                                when sd.d_type = 'BNB Loan' then 'Financial Institution Loan - SMCL'
                                                when sd.d_type = 'BOB Loan' then 'Financial Institution Loan - SMCL'
                                                when sd.d_type = 'DPNB Loan' then 'Financial Institution Loan - SMCL'
                                                when sd.d_type = 'NPPF Loan' then 'Financial Institution Loan - SMCL'
                                                when sd.d_type = 'Other Loan' then 'Financial Institution Loan - SMCL'
                                                when sd.d_type = 'Health Contribution' then 'Health Contribution - SMCL'
                                                when sd.d_type = 'Salary Tax' then 'Salary Tax - SMCL'
                                                when sd.d_type = 'PF' then 'Provident Fund - SMCL'
                                                when sd.d_type = 'Group Insurance Scheme' then 'Group Insurance Scheme - SMCL'
                                                when sd.d_type = 'Salary Advance Deductions' then 'Salary Advance Recovery - SMCL'
                                           end)
                                """ % (item['cost_center'],self.month, self.fiscal_year, item['branch'], item['department'], item['division'])
                        deductions.extend(frappe.db.sql(query, as_dict=1))                        
                        accounts.extend(deductions)

                        # Total Deductions
                        for deduction in deductions:
                                tot_deductions += deduction['credit_in_account_currency']

                        #
                        # Earnings
                        #
                        query = """select 'Salary Payable - SMCL' as account,
                                sum(e_modified_amount) as debit_in_account_currency,
                                'Bank of Bhutan Ltd - SMCL' as against_account,
                                '%s' as cost_center
                                from `tabSalary Slip Earning` se, `tabSalary Slip` ss
                               where ss.name = se.parent
                                 and se.e_modified_amount > 0
                                 and ss.month = '%s'
                                 and ss.fiscal_year = %s
                                 and ss.docstatus = 1
                                 and ss.branch = '%s'
                                 and ss.department = '%s'
                                 and ss.division = '%s'
                                """ % (item['cost_center'],self.month, self.fiscal_year, item['branch'], item['department'], item['division'])
                        earnings.extend(frappe.db.sql(query, as_dict=1))
                        accounts.extend(earnings)

                        # Total Earnings
                        for earning in earnings:
                                tot_earnings += earning['debit_in_account_currency']


                msgprint(_("Total Earnings: {0}").format(tot_earnings))
                msgprint(_("Total Deductions: {0}").format(tot_deductions))
                msgprint(_("Difference is :{0}").format(tot_earnings-tot_deductions))

                # Bank Entry
                default_bank_account = frappe.db.get_value("Company", self.company,
			"default_bank_account")
                
                if tot_deductions <= tot_earnings:
                        accounts.append({"account": default_bank_account,
                                         "credit_in_account_currency": (tot_earnings-tot_deductions),
                                         "against_account": 'Bank',
                                         "cost_center": 'Dummy-CEO - SMCL'})

                msgprint(_("Accounts: {0}").format(accounts))
                ss_list = []
		ss = frappe.get_doc({
			"doctype": "Journal Entry",
                        "voucher_type": 'Bank Entry',
                        "naming_series": 'Bank Payment Voucher',
                        "title": _('Salary for the month {0} and year {1}').format(self.month,
			self.fiscal_year),
			"fiscal_year": self.fiscal_year,
                        "user_remark": _('Payment of salary for the month {0} and year {1}').format(self.month,
			self.fiscal_year),
                        "posting_date": nowdate(),                     
			"company": self.company,
                        "total_amount_in_words": money_in_words((tot_earnings-tot_deductions)),
                        "accounts": accounts
		})

		if (tot_deductions or tot_earnings):
                        ss.insert()
                        #ss.submit()
		ss_list.append('Direct posting Journal Entry...')		                
                

        def make_journal_entry1(self, salary_account = None):
                self.get_account_rules()

	def make_journal_entry(self, salary_account = None):
		amount = self.get_total_salary()
		default_bank_account = frappe.db.get_value("Company", self.company,
			"default_bank_account")

		journal_entry = frappe.new_doc('Journal Entry')
		journal_entry.voucher_type = 'Bank Entry'
		journal_entry.user_remark = _('Payment of salary for the month {0} and year {1}').format(self.month,
			self.fiscal_year)
		journal_entry.fiscal_year = self.fiscal_year
		journal_entry.company = self.company
		journal_entry.posting_date = nowdate()
		journal_entry.set("accounts", [
			{
				"account": salary_account,
				"debit_in_account_currency": amount
			},
			{
				"account": default_bank_account,
				"credit_in_account_currency": amount
			},
		])
		return journal_entry.as_dict()
	
        # Ver 20160702.1 make_journal_entry1 is added by SSK
	def make_journal_entry2(self, salary_account = None):
		amount = self.get_total_salary()
		default_bank_account = frappe.db.get_value("Company", self.company,
			"default_bank_account")
		# Following line added by SSK
		salary_account = 'Salary Payable - SMCL'
		ss_list = []
		ss = frappe.get_doc({
			"doctype": "Journal Entry",
                        "voucher_type": 'Bank Entry',
			"fiscal_year": self.fiscal_year,
                        "user_remark": _('Payment of salary for the month {0} and year {1}').format(self.month,
			self.fiscal_year),
                        "posting_date": nowdate(),                     
			"company": self.company,
                        "accounts": [
                                {
                                        "account": salary_account,
                                        "debit_in_account_currency": amount,
                                        "account_type": 'Payable',
                                        "against_account": 'Bank of Bhutan Ltd - SMCL',
                                        "cost_center": 'Dummy-CEO - SMCL',
                                        "party_type": 'Employee',
                                        "party": 'EMP/0011'
                                },
                                {
                                        "account": default_bank_account,
                                        "credit_in_account_currency": amount,
                                        "account_type": 'Bank',
                                        "against_account": 'EMP/0011',
                                        "cost_center": 'Dummy-CEO - SMCL'
                                },
                        ]
		})
		ss.insert()
		ss_list.append('Direct posting Journal Entry...')		
		
@frappe.whitelist()
def get_month_details(year, month):
	ysd = frappe.db.get_value("Fiscal Year", year, "year_start_date")
	if ysd:
		from dateutil.relativedelta import relativedelta
		import calendar, datetime
		diff_mnt = cint(month)-cint(ysd.month)
		if diff_mnt<0:
			diff_mnt = 12-int(ysd.month)+cint(month)
		msd = ysd + relativedelta(months=diff_mnt) # month start date
		month_days = cint(calendar.monthrange(cint(msd.year) ,cint(month))[1]) # days in month
		med = datetime.date(msd.year, cint(month), month_days) # month end date
		return frappe._dict({
			'year': msd.year,
			'month_start_date': msd,
			'month_end_date': med,
			'month_days': month_days
		})
	else:
		frappe.throw(_("Fiscal Year {0} not found").format(year))
