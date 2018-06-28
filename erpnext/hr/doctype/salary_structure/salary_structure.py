# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SSK		                   03/08/2016         Following functions introducted
                                                                          i) get_employee_pf: fetching pf component
1.0               SSK                              04/08/2016         Following functions introducted
                                                                          i) get_employee_gis : fetching employee gis
                                                                          ii)get_salary_tax : fetching tds
1.0               SSK                              08/08/2016         Changes made to accommodate erpnext v7 changes
                                                                          i) Displaying only Earnings on earnings side
                                                                          ii) Displaying only Deductions on deductions side
1.0               SSK                              23/08/2016         Introducing Monthly Salary Deductions
1.0               SSK                              25/08/2016         Updating branch, department, division in salary slip
                                                                        as per employee record as on processing date
1.0               SSK                              27/08/2016         Salary Structure Overlap rectification
1.0               SSK                              28/08/2016         Added employee_subgroup to Salary Slip
1.0               SSK                              29/08/2016         Added method calculate_totals for use in
                                                                        Salary Increment
2.0               SSK                              27/02/2018         Methods
                                                                                validate_salary_component()
                                                                                salary_component_query()
                                                                        introducted inorder to restrict user from making
                                                                        mistakes by adding deduction salary_component type
                                                                        under earnings table vice versa.
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe

from frappe import msgprint
from frappe.utils import cstr, flt, cint, getdate, date_diff, nowdate
from frappe.utils.data import get_first_day, get_last_day, add_days
from frappe.model.naming import make_autoname
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name
from erpnext.hr.hr_custom_functions import get_month_details, get_company_pf, get_employee_gis, get_salary_tax, update_salary_structure
from erpnext.accounts.accounts_custom_functions import get_number_of_days
from erpnext.custom_utils import nvl
from frappe.desk.reportview import get_match_cond

class SalaryStructure(Document):
	def autoname(self):
		self.name = make_autoname(self.employee + '/.SST' + '/.#####')
		
	def validate(self):
		if self.is_active == 'No' and not self.to_date:
			frappe.throw("To Date is mandatory for Non Active Salary Structures")
		self.check_overlap()
		self.validate_amount()
		self.validate_employee()
		self.validate_joining_date()
		set_employee_name(self)
		self.check_multiple_active()
		self.validate_salary_component()

	def on_update(self):
		self.assign_employee_details()

        # Ver 2.0, following method introduced by SHIV on 2018/02/2017
        def validate_salary_component(self):
                for parentfield in ['earnings','deductions']:
                        parenttype = 'Earning' if parentfield == 'earnings' else 'Deduction'
                        for i in self.get(parentfield):
                                component_type = frappe.db.get_value("Salary Component",i.salary_component,"type")
                                if parenttype != component_type:
                                        frappe.throw(_('Salary Component <b>`{1}`</b> of type <b>`{2}`</b> cannot be added under <b>`{3}`</b> table. <br/> <b><u>Reference# : </u></b> <a href="#Form/Salary Structure/{0}">{0}</a>').format(self.name,i.salary_component,component_type,parentfield.title()),title="Invalid Salary Component")

                
	def get_employee_details(self):
		ret = {}
		det = frappe.db.sql("""select employee_name, branch, designation, department, division, section
			from `tabEmployee` where name = %s""", self.employee)
		if det:
			ret = {
				'employee_name': cstr(det[0][0]),
				'branch': cstr(det[0][1]),
				'designation': cstr(det[0][2]),
				'department': cstr(det[0][3]),
                                'division': cstr(det[0][4]),       #Ver 20160704.1 added by SSK
                                'section': cstr(det[0][5]),        #Ver 20160704.1 added by SSK
				'backup_employee': cstr(self.employee)
			}
		return ret

	def get_ss_values(self,employee):
		basic_info = frappe.db.sql("""select bank_name, bank_ac_no
			from `tabEmployee` where name =%s""", employee)
		ret = {'bank_name': basic_info and basic_info[0][0] or '',
			'bank_ac_no': basic_info and basic_info[0][1] or ''}
		return ret

	def make_table(self, doct_name, tab_fname, tab_name):
                # Ver 1.0 by SSK on 08/08/2016, Following line is commented and the subsequent if condition is added
                #list1 = frappe.db.sql("select name from `tab%s` where docstatus != 2" % doct_name)
                if (tab_fname == 'earnings'):
                        list1 = frappe.db.sql("select name, default_amount from `tab%s` where `docstatus` != 2 and `type` = 'Earning' and `default` = 1" % doct_name)
                else:
                        list1 = frappe.db.sql("select name, default_amount from `tab%s` where `docstatus` != 2 and `type` = 'Deduction' and `default` = 1 " % doct_name)
                        
		for li in list1:
			child = self.append(tab_fname, {})
			if(tab_fname == 'earnings'):
				child.salary_component = cstr(li[0])
				child.amount = flt(li[1])
			elif(tab_fname == 'deductions'):
				child.salary_component = cstr(li[0])
				child.amount = flt(li[1])

	def make_earn_ded_table(self):
		self.make_table('Salary Component','earnings','Salary Detail')
		self.make_table('Salary Component','deductions', 'Salary Detail')

	def check_overlap(self):
		existing = frappe.db.sql("""select name from `tabSalary Structure`
			where employee = %(employee)s and
			(
				(%(from_date)s >= ifnull(from_date,'0000-00-00') and %(from_date)s <= ifnull(to_date,'2199-12-31')) or
				(%(to_date)s >= ifnull(from_date,'0000-00-00') and %(to_date)s <= ifnull(to_date,'2199-12-31')) or
				(%(from_date)s <= ifnull(from_date,'0000-00-00') and %(to_date)s >= ifnull(to_date,'2199-12-31')))
			and name!=%(name)s
			and docstatus < 2""",
			{
				"employee": self.employee,
				"from_date": self.from_date,
				"to_date": self.to_date,
				"name": self.name or "No Name"
			}, as_dict=True)
			
		if existing:
			frappe.throw(_("Salary structure {0} already exist, more than one salary structure for same period is not allowed").format(existing[0].name))

	def validate_amount(self):
		if flt(self.net_pay) < 0 and self.salary_slip_based_on_timesheet:
			frappe.throw(_("Net pay cannot be negative"))

	def validate_employee(self):
		old_employee = frappe.db.get_value("Salary Structure", self.name, "employee")
		if old_employee and self.employee != old_employee:
			frappe.throw(_("Employee can not be changed"))

	def validate_joining_date(self):
		joining_date = getdate(frappe.db.get_value("Employee", self.employee, "date_of_joining"))
		if getdate(self.from_date) < joining_date:
			frappe.throw(_("From Date in Salary Structure cannot be lesser than Employee Joining Date."))

	def assign_employee_details(self):
		if self.employee:
			doc = frappe.get_doc("Employee", self.employee)
			self.db_set("employee_name", doc.employee_name)
			self.db_set("branch", doc.branch)
			self.db_set("department", doc.department)
			self.db_set("division", doc.division)
			self.db_set("section", doc.section)
			self.db_set("designation", doc.designation)

	def check_multiple_active(self):
		if self.is_active == 'Yes':
			result = frappe.db.sql("select 1 from `tabSalary Structure` where employee = %s and is_active = \'Yes\' and name != %s", (self.employee, self.name))
			if result:
				frappe.throw("Can not have multiple 'Active' Salary Structures")

	def calculate_totals(self, employee, new_basic):
                basic_pay = 0.00
                gross_pay = 0.00
                deductions = 0.00
                net_pay = 0.00

                for e in self.earnings:
                        if e.salary_component == 'Basic Pay':
                                e.amount = flt(new_basic)
                                basic_pay += round(flt(new_basic), 0)
				break

                gross_pay = flt(basic_pay)

                #
                # Calculating Earnings
                #
                for e in self.earnings:
                        calc_amt = 0.00
                        if e.salary_component == 'Basic Pay':
                                pass
                        elif self.eligible_for_corporate_allowance and e.salary_component == 'Corporate Allowance':
                                calc_amt = round(basic_pay*flt(self.ca)*0.01)
                                gross_pay += calc_amt
                                e.amount = calc_amt
                        elif self.eligible_for_contract_allowance and e.salary_component == 'Contract Allowance':
                                calc_amt = round(basic_pay*flt(self.contract_allowance)*0.01)
                                gross_pay += calc_amt
                                e.amount = calc_amt
                        elif self.eligible_for_communication_allowance and e.salary_component == 'Communication Allowance':
                                calc_amt = round(flt(self.communication_allowance))			
                                gross_pay += calc_amt
                                e.amount = calc_amt
                        elif self.eligible_for_psa and e.salary_component == 'PSA':
                                calc_amt = round(basic_pay*flt(self.psa)*0.01)
                                gross_pay += calc_amt
                                e.amount = calc_amt
                        elif self.eligible_for_mpi and e.salary_component == 'MPI':
                                calc_amt = round(basic_pay*flt(self.mpi)*0.01)
                                gross_pay += calc_amt
                                e.amount = calc_amt
                        elif self.eligible_for_officiating_allowance and e.salary_component == 'Officiating Allowance':
                                calc_amt = round(basic_pay*flt(self.officiating_allowance)*0.01)
                                gross_pay += calc_amt
                                e.amount = calc_amt
                        elif self.eligible_for_temporary_transfer_allowance and e.salary_component == 'Temporary Transfer Allowance':
                                calc_amt = (basic_pay*flt(self.temporary_transfer_allowance)*0.01)
                                gross_pay += calc_amt
                                e.amount = calc_amt
                        elif self.eligible_for_fuel_allowances and e.salary_component == 'Fuel Allowance':
                                calc_amt = round(flt(self.fuel_allowances))
                                gross_pay += calc_amt
                                e.amount = calc_amt
                        else:
                                gross_pay += e.amount

                #
                # Calculating Deductions
                #
                company_det = get_company_pf('2016')
                for d in self.deductions:
                        if d.salary_component == 'Group Insurance Scheme':
                                calc_gis_amt = flt(get_employee_gis(self.employee))
                                d.amount = calc_gis_amt
                                deductions += calc_gis_amt
                        elif d.salary_component == 'PF':
				percent = frappe.db.get_single_value("HR Settings", "employee_pf")
				if not percent:
					frappe.throw("Setup PF Percent in HR Settings")
                                calc_pf_amt = 0;
                                calc_pf_amt = round(basic_pay*flt(percent)*0.01);
                                d.amount = calc_pf_amt
                                deductions += calc_pf_amt
                        elif d.salary_component == 'Health Contribution':
				percent = frappe.db.get_single_value("HR Settings", "health_contribution")
				if not percent:
					frappe.throw("Setup Health Contribution Percent in HR Settings")
                                calc_health_amt = 0;
                                calc_health_amt = round(gross_pay*flt(percent)*0.01);
                                d.amount = calc_health_amt
                                deductions += calc_health_amt
                        elif d.salary_component == 'Salary Tax':
                                calc_tds_amt = 0;
                                calc_tds_amt = get_salary_tax(gross_pay-calc_pf_amt-calc_gis_amt-(0.5 * flt(self.communication_allowance)))
                                d.amount = calc_tds_amt
                                deductions += calc_tds_amt
                        else:
                                deductions += d.amount

@frappe.whitelist()
def make_salary_slip(source_name, target_doc=None):
	def postprocess(source, target):
                # Ver 1.0 Begins added by SSK on 25/08/201, updating branch, department, division in salary slip
                gross_amt = 0.00
		comm_amt = 0.00
		basic_amt = 0.00
                employee = frappe.get_doc("Employee",source.employee)
                target.branch = employee.branch
                target.department = employee.department
                target.division = employee.division
                target.cost_center = employee.cost_center
                target.designation = employee.designation
                target.section = employee.section
                target.employee_subgroup = employee.employee_subgroup # Ver 1.0 Begins, added by SSK on 28/08/2016
                #frappe.msgprint(_("StartDate: {0} EndDate: {1}").format(target.start_date,target.end_date))
                # Ver 1.0 Ends
		m_details = get_month_details(target_doc.fiscal_year, target_doc.month)
		#days = cint(date_diff(get_first_day(add_days(nowdate(), -11)), getdate(employee.date_of_joining)))
		#days_month = 1 + cint(get_number_of_days(get_first_day((add_days(nowdate(), -11))), get_last_day((add_days(nowdate(), -11)))))
		old_basic = 0
		prorated = 0
		actual_days = 0
		
		#if days < days_month and days != 0:
		if m_details.month_start_date < source.from_date or (source.to_date and m_details.month_end_date > source.to_date):
			for a in source.get('earnings'):
				if a.salary_component == 'Basic Pay':
					old_basic = round(flt(a.amount), 0)
					#Do prorating of salary
					if m_details.month_start_date < source.from_date and (source.to_date and m_details.month_end_date > source.to_date):
						actual_days = 1 + cint(date_diff(source.to_date, source.from_date))
					elif m_details.month_start_date < source.from_date: 
						actual_days = 1 + cint(date_diff(m_details.month_end_date, source.from_date))
					else:
						actual_days = 1 + cint(date_diff(source.to_date, m_details.month_start_date))
					#actual_days = 1 + cint(date_diff(get_last_day(add_days(nowdate(), -13)), getdate(employee.date_of_joining)))	
					#total = 1 + cint(date_diff(get_last_day(add_days(nowdate(), -13)), get_first_day(add_days(nowdate(), -13))))
					total = m_details.month_days
					new_basic = round(flt((flt(actual_days) / flt(total)) * old_basic, 2), 0)
					source = update_salary_structure(str(source.employee), flt(new_basic), source.name, old_basic)
					if not source:
						frappe.throw("There is either no salary structure or the payroll processing is done before time")
					prorated = 1
					frappe.msgprint("Prorated the salary for " + str(source.employee_name))
					break
			
		# copy earnings and deductions table
		for key in ('earnings', 'deductions'):
			for d in source.get(key):
                                amount          = flt(d.amount)
                                deductible_amt  = 0.0
                                deducted_amt    = 0.0
                                outstanding_amt = 0.0
                                                
                                if d.from_date:
                                        if (target.start_date <= d.from_date <= target.end_date) or ((d.from_date <= target.end_date) and (nvl(d.to_date,target.end_date) >= target.start_date)):                
                                                if key == 'deductions':
                                                        if flt(d.total_deductible_amount) > 0:
                                                                if flt(d.total_outstanding_amount) > 0:
                                                                        if flt(amount) >= flt(d.total_outstanding_amount):
                                                                                amount          = flt(d.total_outstanding_amount)
                                                                else:
                                                                        amount = 0
                                        else:
                                                amount = 0                
                                elif d.to_date:
                                        if (target.start_date <= d.to_date <= target.end_date) or ((d.to_date >= target.start_date) and (nvl(d.from_date,target.start_date) <= target.end_date)):
                                                if key == 'deductions':
                                                        if flt(d.total_deductible_amount) > 0:
                                                                if flt(d.total_outstanding_amount) > 0:
                                                                        if flt(amount) >= flt(d.total_outstanding_amount):
                                                                                amount          = flt(d.total_outstanding_amount)
                                                                else:
                                                                        amount = 0
                                        else:
                                                amount = 0
                                else:
                                        if key == 'deductions':
                                                if flt(d.total_deductible_amount) > 0:
                                                        if flt(d.total_outstanding_amount) > 0:
                                                                if flt(amount) >= flt(d.total_outstanding_amount):
                                                                        amount          = flt(d.total_outstanding_amount)

                                                        else:
                                                                amount = 0

                                if flt(d.total_deductible_amount) > 0:
                                        if flt(d.total_outstanding_amount) > 0:
                                                deductible_amt  = flt(d.total_deductible_amount)
                                                deducted_amt    = flt(d.total_deducted_amount) + flt(amount)
                                                outstanding_amt = flt(d.total_outstanding_amount) - flt(amount)

                                target.append(key, {
                                        'salary_component'         : d.salary_component,
                                        'depends_on_lwp'           : d.depends_on_lwp,
					'institution_name'          : d.institution_name,
					'reference_type'           : d.reference_type,
					'reference_number'         : d.reference_number,
                                        'ref_docname'              : d.name,
                                        'from_date'                : d.from_date,
                                        'to_date'                  : d.to_date,
                                        'amount'                   : flt(amount),
                                        'default_amount'           : flt(amount),
                                        'total_deductible_amount'  : flt(deductible_amt),
                                        'total_deducted_amount'    : flt(deducted_amt),
                                        'total_outstanding_amount' : flt(outstanding_amt)
                                })
                                
                                '''
                                if d.from_date and d.to_date:
                                        if ((d.from_date <= target.start_date <= d.to_date) or (d.from_date <= target.end_date <= d.to_date)):
                                                target.append(key, {
                                                        'amount': d.amount,
                                                        'default_amount': d.amount,
                                                        'depends_on_lwp' : d.depends_on_lwp,
                                                        'salary_component' : d.salary_component,
                                                        'institution_name' : d.institution_name,
                                                        'reference_type' : d.reference_type,
                                                        'reference_number' : d.reference_number,
                                                        'from_date' : d.from_date,
                                                        'to_date' : d.to_date,
                                                        'total_deductible_amount' : d.total_deductible_amount,
                                                        'total_deducted_amount' : (d.total_deducted_amount+d.amount),
                                                        'total_outstanding_amount' : (d.total_deductible_amount-(d.total_deducted_amount+d.amount)) if d.total_deductible_amount else 0
                                                })
                                else:
                                        target.append(key, {
                                                'amount': d.amount,
                                                'default_amount': d.amount,
                                                'depends_on_lwp' : d.depends_on_lwp,
                                                'salary_component' : d.salary_component,
						'institution_name' : d.institution_name,
						'reference_type' : d.reference_type,
						'reference_number' : d.reference_number,
                                        })
                                '''

                for e in target.get('earnings'):
                        if e.salary_component == 'Basic Pay':
                        	basic_amt = (flt(e.amount))
                        if e.salary_component == 'Communication Allowance':
                        	comm_amt = (flt(e.amount))
			gross_amt += flt(e.amount)

                gross_amt += (flt(target.arrear_amount) + flt(target.leave_encashment_amount))

		pf = gis = health = 0.00
                for d in target.get('deductions'):
                        if not flt(gross_amt):
                                d.amount = 0
                        else:
                                if d.salary_component == 'PF': 
                                        percent = frappe.db.get_single_value("HR Settings", "employee_pf")
                                        if not percent:
                                                frappe.throw("Setup PF Percent in HR Settings")
                                        pf = round(basic_amt*flt(percent)*0.01);
                                        d.amount = pf
                                if d.salary_component == 'Group Insurance Scheme':
                                        gis = flt(get_employee_gis(source.employee))
                                        d.amount = gis
                                if d.salary_component == 'Health Contribution': 
                                        percent = frappe.db.get_single_value("HR Settings", "health_contribution")
                                        if not percent:
                                                frappe.throw("Setup Health Contribution Percent in HR Settings")
                                        health = round(gross_amt*flt(percent)*0.01);
                                        d.amount = health


		tax_included = 0
                for d in target.get('deductions'):
                        if not flt(gross_amt):
                                d.amount = 0
                        else:
                                if d.salary_component == 'Salary Tax':
                                        if not tax_included:
                                                tax_amt = get_salary_tax(flt(gross_amt) - flt(gis) - flt(pf) - (flt(comm_amt) * 0.5))
                                                d.amount = flt(tax_amt)
                                                tax_included = 1
                #frappe.msgprint(_("gross_amt: {0}, gis: {1}, pf: {2}, comm_amt: {3}, tax: {4}").format(flt(gross_amt),flt(gis),flt(pf),flt(comm_amt),flt(tax_amt)))                        
		target.run_method("pull_emp_details")
		target.run_method("get_leave_details")
		target.run_method("calculate_net_pay")
		target.payment_days = actual_days
		if prorated == 1:
			update_salary_structure(str(source.employee), flt(old_basic), source.name)
			

	doc = get_mapped_doc("Salary Structure", source_name, {
		"Salary Structure": {
			"doctype": "Salary Slip",
			"field_map": {
				"total_earning": "gross_pay",
				"name": "salary_structure",
				"actual_basic": "actual_basic"
			}
		}
	}, target_doc, postprocess, ignore_child_tables=True)

	return doc

# Ver 2.0, Following method added by SHIV on 2018/02/27
@frappe.whitelist()
def salary_component_query(doctype, txt, searchfield, start, page_len, filters):
        return frappe.db.sql(""" 
                        select
                                name,
                                type,
                                payment_method
                        from `tabSalary Component`
                        where type = %(component_type)s
                        and (
                                {key} like %(txt)s
                                or
                                type like %(txt)s
                                or
                                payment_method like %(txt)s
                        )
                        {mcond}
                        order by
                                if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
                                if(locate(%(_txt)s, type), locate(%(_txt)s, type), 99999),
                                if(locate(%(_txt)s, payment_method), locate(%(_txt)s, payment_method), 99999),
                                idx desc,
                                name, type, payment_method
                        limit %(start)s, %(page_len)s
                        """.format(**{
                                'key': searchfield,
                                'mcond': get_match_cond(doctype)
                        }),
                        {
                "txt": "%%%s%%" % txt,
                "_txt": txt.replace("%", ""),
                "start": start,
                "page_len": page_len,
                "component_type": 'Earning' if filters['parentfield'] == 'earnings' else 'Deduction'
            })
