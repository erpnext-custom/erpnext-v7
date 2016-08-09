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
			where t1.docstatus!=2 and t2.docstatus != 2 and 
			ifnull(t2.salary_slip_based_on_timesheet,0) = 0 and t1.name = t2.employee
		%s """% cond)

		return emp_list

	def get_filter_condition(self):
		self.check_mandatory()

		cond = ''
		for f in ['company', 'branch', 'department', 'designation', 'branch', 'department', 'division']:
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
					"salary_slip_based_on_timesheet": 0,
					"fiscal_year": self.fiscal_year,
					"employee": emp[0],
					"month": self.month,
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
			log = """
				<b>Salary Slips Submitted:</b> <br><br>%s
				""" % ('<br>'.join(submitted_ss))

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
                items = []
                cond = self.get_filter_condition()
                
                items.extend(frappe.db.sql("""select t1.branch, t1.department, t1.division,t2.cost_center,
                        sum(t1.rounded_total) as total_amt
                         from `tabSalary Slip` t1, `tabDivision` t2
                        where t2.name = t1.division
                          and t2.dpt_name = t1.department
                          and t2.branch = t1.branch
                          and t1.month = %s
                          and t1.fiscal_year = %s
                          and t1.docstatus = 0 
                          %s
                        group by t1.branch,t1.department,t1.division,t2.cost_center
                """ % (self.month, self.fiscal_year, cond),as_dict=1))
                #msgprint(_("Items: {0}").format(items))

                #
                # GL Mapping
                #
                accounts = []
                tot_deductions = 0
                tot_earnings = 0
                default_payable_account = 'Salary Payable - SMCL'
                default_gpf_account = 'GPF Contribution (Employer) - SMCL'
                default_gis_account = frappe.db.get_value("Salary Component", 'Group Insurance Scheme',"gl_head")
                default_pf_account = frappe.db.get_value("Salary Component", 'PF',"gl_head")
                default_loan_account = frappe.db.get_value("Salary Component", 'NPPF Loan',"gl_head")
                default_saving_account = frappe.db.get_value("Salary Component", 'RICB Scheme',"gl_head")
                default_tax_account = frappe.db.get_value("Salary Component", 'Salary Tax',"gl_head")
                default_health_account = frappe.db.get_value("Salary Component", 'Health Contribution',"gl_head")
                default_saladv_account = frappe.db.get_value("Salary Component", 'Salary Advance Deductions',"gl_head")

                for item in items:
                        deductions = []
                        earnings = []
                        item_deductions = 0
                        item_earnings = 0

                        #
                        # Deductions
                        #
                        query = """select dt.gl_head as account,
                                sum(amount) as credit_in_account_currency,
                                '%s' as against_account,
                                '%s' as cost_center,
                                0 as party_check
                                from `tabSalary Detail` sd, `tabSalary Slip` ss, `tabSalary Component` dt
                               where ss.name = sd.parent
                                 and sd.amount > 0
                                 and dt.name = sd.salary_component
                                 and ss.month = '%s'
                                 and ss.fiscal_year = %s
                                 and ss.docstatus = 0
                                 and ss.branch = '%s'
                                 and ss.department = '%s'
                                 and ss.division = '%s'
                                 and dt.gl_head <> '%s'
                                 and dt.type = 'Deduction'
                               group by dt.gl_head
                                """ % (default_payable_account,item['cost_center'],self.month, self.fiscal_year, item['branch'], item['department'], item['division'], default_saladv_account)
                        deductions.extend(frappe.db.sql(query, as_dict=1))

                        # Salary Advance
                        query2 = """select dt.gl_head as account,
                                sum(amount) as credit_in_account_currency,
                                '%s' as against_account,
                                '%s' as cost_center,
                                0 as party_check,
                                'Payable' as account_type,
                                'Employee' as party_type,
                                ss.employee as party
                                from `tabSalary Detail` sd, `tabSalary Slip` ss, `tabSalary Component` dt
                               where ss.name = sd.parent
                                 and sd.amount > 0
                                 and dt.name = sd.salary_component
                                 and ss.month = '%s'
                                 and ss.fiscal_year = %s
                                 and ss.docstatus = 0
                                 and ss.branch = '%s'
                                 and ss.department = '%s'
                                 and ss.division = '%s'
                                 and dt.gl_head = '%s'
                                 and dt.type = 'Deduction'
                               group by dt.gl_head, ss.employee
                                """ % (default_payable_account,item['cost_center'],self.month, self.fiscal_year, item['branch'], item['department'], item['division'], default_saladv_account)
                        deductions.extend(frappe.db.sql(query2, as_dict=1))                        
                        accounts.extend(deductions)

                        # Total Deductions
                        for deduction in deductions:
                                item_deductions += deduction['credit_in_account_currency']
                                tot_deductions += deduction['credit_in_account_currency']

                        #
                        # Earnings
                        #
                        query = """select et.gl_head as account,
                                sum(amount) as debit_in_account_currency,
                                '%s' as against_account,
                                '%s' as cost_center,
                                0 as party_check
                                from `tabSalary Detail` se, `tabSalary Slip` ss, `tabSalary Component` et
                               where ss.name = se.parent
                                 and se.amount > 0
                                 and et.name = se.salary_component
                                 and et.type = 'Earning'
                                 and ss.month = '%s'
                                 and ss.fiscal_year = %s
                                 and ss.docstatus = 0
                                 and ss.branch = '%s'
                                 and ss.department = '%s'
                                 and ss.division = '%s'
                               group by et.gl_head
                                """ % (default_payable_account,item['cost_center'],self.month, self.fiscal_year, item['branch'], item['department'], item['division'])
                        earnings.extend(frappe.db.sql(query, as_dict=1))
                        accounts.extend(earnings)

                        # Total Earnings
                        for earning in earnings:
                                item_earnings += earning['debit_in_account_currency']
                                tot_earnings += earning['debit_in_account_currency']

                        if item_deductions <= item_earnings:
                                accounts.append({"account": default_payable_account,
                                                 "credit_in_account_currency": (item_earnings-item_deductions),
                                                 "cost_center": item['cost_center'],
                                                 "party_check": 0})
                                
                                
                #msgprint(_("Total Earnings: {0} \nTotal Deductions: {1} \nNetPay: {2}").format(tot_earnings,tot_deductions,(tot_earnings-tot_deductions)))

                #if tot_deductions <= tot_earnings:
                #        accounts.append({"account": 'Salary Payable - SMCL',
                #                         "credit_in_account_currency": (tot_earnings-tot_deductions),
                #                         "against_account": 'Bank',
                #                         "cost_center": 'Dummy-CEO - SMCL',
                #                         "party_check": 0})

                # Remittance
                bank = []
                gis = []                
                pf = []
                loan = []
                saving = []                
                tax = []
                health = []
                temp = []

                tot_bank = 0
                tot_gis = 0
                tot_pf = 0
                tot_loan = 0
                tot_saving = 0
                tot_tax = 0
                tot_health = 0
                
                #msgprint(_("{0}").format(default_payable_account))
                #msgprint(_("{0}").format(default_gis_account))
                #msgprint(_("{0}").format(default_pf_account))
                #msgprint(_("{0}").format(default_loan_account))
                #msgprint(_("{0}").format(default_saving_account))
                #msgprint(_("{0}").format(default_tax_account))
                #msgprint(_("{0}").format(default_health_account))
                                
                for list_item in accounts:
                        #msgprint(_("{0}").format(list_item['account']))
                        if default_payable_account == list_item['account']:
                                bank.append({"account": list_item['account'],
                                                 "debit_in_account_currency": list_item['credit_in_account_currency'],
                                                 "cost_center": list_item['cost_center'],
                                                 "party_check": 0})
                                tot_bank += list_item['credit_in_account_currency']
                        elif default_gis_account == list_item['account']:
                                gis.append({"account": list_item['account'],
                                                 "debit_in_account_currency": list_item['credit_in_account_currency'],
                                                 "cost_center": list_item['cost_center'],
                                                 "party_check": 0})
                                tot_gis += list_item['credit_in_account_currency']
                        elif default_pf_account == list_item['account']:
                                # Employee PF
                                pf.append({"account": list_item['account'],
                                                 "debit_in_account_currency": list_item['credit_in_account_currency'],
                                                 "cost_center": list_item['cost_center'],
                                                 "party_check": 0})
                                tot_pf += list_item['credit_in_account_currency']

                                # Employer PF
                                pf.append({"account": default_gpf_account,
                                                 "debit_in_account_currency": list_item['credit_in_account_currency'],
                                                 "cost_center": list_item['cost_center'],
                                                 "party_check": 0})
                                tot_pf += list_item['credit_in_account_currency']                                
                        elif default_loan_account == list_item['account']:
                                loan.append({"account": list_item['account'],
                                                 "debit_in_account_currency": list_item['credit_in_account_currency'],
                                                 "cost_center": list_item['cost_center'],
                                                 "party_check": 0})
                                tot_loan += list_item['credit_in_account_currency']
                        elif default_saving_account == list_item['account']:
                                saving.append({"account": list_item['account'],
                                                 "debit_in_account_currency": list_item['credit_in_account_currency'],
                                                 "cost_center": list_item['cost_center'],
                                                 "party_check": 0})
                                tot_saving += list_item['credit_in_account_currency']
                        elif default_tax_account == list_item['account']:
                                tax.append({"account": list_item['account'],
                                                 "debit_in_account_currency": list_item['credit_in_account_currency'],
                                                 "cost_center": list_item['cost_center'],
                                                 "party_check": 0})
                                temp.append({"account": list_item['account'],
                                                 "debit_in_account_currency": list_item['credit_in_account_currency'],
                                                 "cost_center": list_item['cost_center'],
                                                 "party_check": 0})                                
                                tot_tax += list_item['credit_in_account_currency']
                        elif default_health_account == list_item['account']:
                                health.append({"account": list_item['account'],
                                                 "debit_in_account_currency": list_item['credit_in_account_currency'],
                                                 "cost_center": list_item['cost_center'],
                                                 "party_check": 0})
                                temp.append({"account": list_item['account'],
                                                 "debit_in_account_currency": list_item['credit_in_account_currency'],
                                                 "cost_center": list_item['cost_center'],
                                                 "party_check": 0})                                
                                tot_health += list_item['credit_in_account_currency']

                if tot_bank:
                        # To Salary Payable
                        title = _('Salary [{0}{1}] - To Payables').format(self.month, self.fiscal_year)
                        user_remark = _('Salary [{0}{1}] - To Payables').format(self.month, self.fiscal_year)
                        self.post_journal_entry(title, user_remark, accounts, 0, tot_earnings, tot_deductions)

                        # To Bank
                        title = _('Salary [{0}{1}] - To Bank').format(self.month, self.fiscal_year)
                        user_remark = _('Salary [{0}{1}] - To Bank').format(self.month, self.fiscal_year)
                        self.post_journal_entry(title, user_remark, bank, 1, tot_bank, 0)

                if tot_gis:
                        # GIS
                        title = _('Salary [{0}{1}] - GIS Remittance').format(self.month, self.fiscal_year)
                        user_remark = _('Salary [{0}{1}] - GIS Remittance').format(self.month, self.fiscal_year)
                        self.post_journal_entry(title, user_remark, gis, 1, tot_gis, 0)                        

                if tot_pf:
                        # PF
                        title = _('Salary [{0}{1}] - PF Remittance').format(self.month, self.fiscal_year)
                        user_remark = _('Salary [{0}{1}] - PF Remittance').format(self.month, self.fiscal_year)
                        self.post_journal_entry(title, user_remark, pf, 1, tot_pf, 0)                        

                if tot_loan:
                        # LOAN
                        title = _('Salary [{0}{1}] - LOAN Remittance').format(self.month, self.fiscal_year)
                        user_remark = _('Salary [{0}{1}] - LOAN Remittance').format(self.month, self.fiscal_year)
                        self.post_journal_entry(title, user_remark, loan, 1, tot_loan, 0)                        

                if tot_saving:
                        # SAVINGS
                        title = _('Salary [{0}{1}] - SAVINGS Remittance').format(self.month, self.fiscal_year)
                        user_remark = _('Salary [{0}{1}] - SAVINGS Remittance').format(self.month, self.fiscal_year)
                        self.post_journal_entry(title, user_remark, saving, 1, tot_saving, 0)                        
                '''
                if tot_tax:
                        # TAX
                        title = _('Salary [{0}{1}] - TAX Remittance').format(self.month, self.fiscal_year)
                        user_remark = _('Salary [{0}{1}] - TAX Remittance').format(self.month, self.fiscal_year)
                        self.post_journal_entry(title, user_remark, tax, 1, tot_tax, 0)

                if tot_health:
                        # HEALTH
                        title = _('Salary [{0}{1}] - HEALTH Remittance').format(self.month, self.fiscal_year)
                        user_remark = _('Salary [{0}{1}] - HEALTH Remittance').format(self.month, self.fiscal_year)
                        self.post_journal_entry(title, user_remark, health, 1, tot_health, 0)                                                
                #msgprint(_("{0}").format(gis))
                #msgprint(_("{0}").format(str(gis).replace('credit_in_account_currency','debit_in_account_currency')))
                '''
                if (tot_tax or tot_health):
                        # TAX & HEALTH
                        title = _('Salary [{0}{1}] - TAX & HEALTH Remittance').format(self.month, self.fiscal_year)
                        user_remark = _('Salary [{0}{1}] - TAX & HEALTH Remittance').format(self.month, self.fiscal_year)
                        self.post_journal_entry(title, user_remark, temp, 1, (tot_tax+tot_health), 0)                                                                        
                
        # Ver 20160706.1 added by SSK
        def post_journal_entry(self, title, user_remark, accounts, bank_entry_req, tot_earnings, tot_deductions):
                from frappe.utils import money_in_words
                ss_list = []
                default_bank_account = frappe.db.get_value("Company", self.company,"default_bank_account")
                
                if bank_entry_req == 0:
                        ss = frappe.get_doc({
                                "doctype": "Journal Entry",
                                "voucher_type": 'Journal Entry',
                                "naming_series": 'Journal Voucher',
                                "title": title,
                                "fiscal_year": self.fiscal_year,
                                "user_remark": user_remark,
                                "posting_date": nowdate(),                     
                                "company": self.company,
                                "total_amount_in_words": money_in_words((tot_earnings-tot_deductions)),
                                "accounts": accounts
                        })

                        if (tot_deductions or tot_earnings):
                                ss.insert()
                                #ss.submit()
                        ss_list.append('Direct posting Journal Entry...')
                else:
                        accounts.append({"account": default_bank_account,
                                        "credit_in_account_currency": (tot_earnings-tot_deductions),
                                        "cost_center": 'Dummy-CEO - SMCL',
                                        "party_check": 0})                        
                        
                        ss = frappe.get_doc({
                                "doctype": "Journal Entry",
                                "voucher_type": 'Bank Entry',
                                "naming_series": 'Bank Payment Voucher',
                                "title": title,
                                "fiscal_year": self.fiscal_year,
                                "user_remark": user_remark,
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
                msgprint(_("Payslip posting to Accounts complete..."))
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
