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
		#msgprint(_("salary_strucure.py.get_employee_details"))
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
				(%(from_date)s > from_date and %(from_date)s < to_date) or
				(%(to_date)s > from_date and %(to_date)s < to_date) or
				(%(from_date)s <= from_date and %(to_date)s >= to_date))
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

@frappe.whitelist()
def make_salary_slip(source_name, target_doc=None):
	def postprocess(source, target):
		# copy earnings and deductions table
		for key in ('earnings', 'deductions'):
			for d in source.get(key):
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
        #msgprint(gross_amt);
        result = frappe.db.sql("""select b.tax from
                `tabSalary Tax` a, `tabSalary Tax Item` b
                where now() between a.from_date and a.to_date
                and b.parent = a.name
                and %s between b.lower_limit and b.upper_limit
                limit 1
                """,gross_amt);
        #msgprint(_("Result set: {0}").format(result))
        return result     
		
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
