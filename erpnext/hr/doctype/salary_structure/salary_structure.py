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
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe

from frappe import msgprint
from frappe.utils import cstr, flt, getdate
from frappe.model.naming import make_autoname
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name

class SalaryStructure(Document):
	def autoname(self):
		self.name = make_autoname(self.employee + '/.SST' + '/.#####')
		
	def validate(self):
		self.check_overlap()
		self.validate_amount()
		self.validate_employee()
		self.validate_joining_date()
		set_employee_name(self)

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
                        list1 = frappe.db.sql("select name from `tab%s` where `docstatus` != 2 and `type` = 'Earning' and `default` = 1" % doct_name)
                else:
                        list1 = frappe.db.sql("select name from `tab%s` where `docstatus` != 2 and `type` = 'Deduction' and `default` = 1 " % doct_name)
                        
		for li in list1:
			child = self.append(tab_fname, {})
			if(tab_fname == 'earnings'):
				child.salary_component = cstr(li[0])
				child.amount = 0
			elif(tab_fname == 'deductions'):
				child.salary_component = cstr(li[0])
				child.amount = 0

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

	def calculate_totals(self, employee, new_basic):
                basic_pay = 0.00
                gross_pay = 0.00
                deductions = 0.00
                net_pay = 0.00

                for e in self.earnings:
                        if e.salary_component == 'Basic Pay':
                                e.amount = flt(new_basic)
                                basic_pay += flt(new_basic)

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
                frappe.msgprint(company_det)
                for d in self.deductions:
                        if d.salary_component == 'Group Insurance Scheme':
                                calc_gis_amt = flt(get_employee_gis(self.employee))
                                d.amount = calc_gis_amt
                                deductions += calc_gis_amt
                        elif d.salary_component == 'PF':
                                calc_pf_amt = 0;
                                calc_pf_amt = round(basic_pay*company_det.employee_pf*0.01);
                                d.amount = calc_pf_amt
                                deductions += calc_pf_amt
                        elif d.salary_component == 'Health Contribution':
                                calc_health_amt = 0;
                                calc_health_amt = round(gross_pay*company_det.health_contribution*0.01);
                                d.amount = calc_health_amt
                                deductions += calc_health_amt
                        elif d.salary_component == 'Salary Tax':
                                calc_tds_amt = 0;
                                calc_tds_amt = get_salary_tax(gross_pay-calc_pf_amt-calc_gis_amt)
                                d.amount = calc_tds_amt
                                deductions += calc_tds_amt
                        else:
                                deductions += d.amount

@frappe.whitelist()
def make_salary_slip(source_name, target_doc=None):
	def postprocess(source, target):
                # Ver 1.0 Begins added by SSK on 25/08/201, updating branch, department, division in salary slip
                employee = frappe.get_doc("Employee",source.employee)
                target.branch = employee.branch
                target.department = employee.department
                target.division = employee.division
                target.designation = employee.designation
                target.section = employee.section
                target.employee_subgroup = employee.employee_subgroup # Ver 1.0 Begins, added by SSK on 28/08/2016
                # Ver 1.0 Ends
		# copy earnings and deductions table
		for key in ('earnings', 'deductions'):
			for d in source.get(key):
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
                                                'salary_component' : d.salary_component
                                        })                                        
                                        
		target.run_method("pull_emp_details")
		target.run_method("get_leave_details")
		target.run_method("calculate_net_pay")
			

	doc = get_mapped_doc("Salary Structure", source_name, {
		"Salary Structure": {
			"doctype": "Salary Slip",
			"field_map": {
				"total_earning": "gross_pay",
				"name": "salary_structure"
			}
		}
	}, target_doc, postprocess, ignore_child_tables=True)

	return doc

# Ver 1.0 added by SSK on 04/08/2016, Fetching TDS component
@frappe.whitelist()
def get_salary_tax(gross_amt):
        tax_amount = 0
        max_limit = frappe.db.sql("""select max(b.upper_limit)
                from `tabSalary Tax` a, `tabSalary Tax Item` b
                where now() between a.from_date and a.to_date
                and b.parent = a.name
                """)

        if flt(flt(gross_amt) if flt(gross_amt) else 0.00) > flt(flt(max_limit[0][0]) if flt(max_limit[0][0]) else 0.00):
                tax_amount = flt((((flt(gross_amt) if flt(gross_amt) else 0.00)-83333.00)*0.25)+11875.00)
        else:
                result = frappe.db.sql("""select b.tax from
                        `tabSalary Tax` a, `tabSalary Tax Item` b
                        where now() between a.from_date and a.to_date
                        and b.parent = a.name
                        and %s between b.lower_limit and b.upper_limit
                        limit 1
                        """,gross_amt)
                if result:
                        tax_amount = flt(result[0][0])
                else:
                        tax_amount = 0
        
        return tax_amount
		
# Ver 1.0 added by SSK on 03/08/2016, Fetching PF component
@frappe.whitelist()
def get_company_pf(fiscal_year):
        result = frappe.db.sql("""
                select employee_pf, employer_pf, health_contribution, retirement_age
                from `tabFiscal Year`
                where now() between year_start_date and year_end_date
                limit 1
                """);
        return result

# Ver 1.0 added by SSK on 04/08/2016, Fetching GIS component
@frappe.whitelist()
def get_employee_gis(employee):
        #msgprint(employee);
        result = frappe.db.sql("""select a.gis
                from `tabEmployee Sub-Group` a, `tabEmployee` b
                where b.employee = %s
                and b.employee_group = a.employee_group
                and b.employee_subgroup = a.employee_subgroup
                limit 1
                """,employee);
        #msgprint(result);
        return result     
