# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
	comma_or, get_fullname, nowdate, money_in_words, get_first_day
from frappe.model.naming import make_autoname
from frappe import _
from frappe import msgprint
import datetime
from erpnext.hr.doctype.salary_structure.salary_structure import get_company_pf, \
     get_employee_gis, get_salary_tax

class SalaryIncrement(Document):
        def autoname(self):
		self.name = make_autoname(self.employee + '/.INC/.' + self.fiscal_year+self.month+ '/.#####')
		
        def validate(self):
                self.validate_dates()
		self.validate_increment()

	def on_submit(self):
		if self.docstatus == 1:
			self.update_salary_structure(self.employee, self.new_basic)

        def validate_dates(self):
		cur_year = getdate(nowdate()).year
		cur_month= getdate(nowdate()).month

		if int(self.fiscal_year) > int(cur_year):
			frappe.throw(_("Salary Increment Cannot be run for future years."))

		if int(self.fiscal_year) < int(cur_year):
			frappe.throw(_("Salary Increment Cannot be run for past years."))

		if int(self.month) != int(cur_month):
			frappe.throw(_("Salary Increment Can only be run for the current month."))

	def validate_increment(self):
		inc_list = frappe.db.sql("""
		select name
		from `tabSalary Increment`
		where employee = '%s'
		and fiscal_year = '%s'
		and month = '%s'
		and docstatus = 1
		""" % (self.employee, self.fiscal_year, self.month))

		if inc_list:
			frappe.msgprint("Salary Increment is already processed for Employee '{0} {1}'\
					for the Month: {2} and Year: {3}".format(self.employee, self.employee_name, \
					self.month, self.fiscal_year))

	def update_salary_structure(self, employee, new_basic):

		sal_struc_name = frappe.db.sql("""
		select name
		from `tabSalary Structure` st
		where st.employee = '%s'
		and is_active = 'Yes'
		and now() between ifnull(from_date,'0000-00-00') and ifnull(to_date,'2050-12-31')
		order by ifnull(from_date,'0000-00-00') desc 
		limit 1
		""" % (self.employee))
		
		sst = ""
		if sal_struc_name and new_basic > 0:
			sst = frappe.get_doc("Salary Structure", sal_struc_name[0][0])
			if sst:
                                gross_pay = 0.00
                                deductions = 0.00

                                #Earnings
                                for e in sst.earnings:
                                        if e.salary_component == "Basic Pay":
                                                e.db_set('amount',new_basic,update_modified=True)
                                                gross_pay += new_basic
                                        elif sst.eligible_for_corporate_allowance and e.salary_component == 'Corporate Allowance':
                                                calc_amt = 0
                                                calc_amt = round(new_basic*flt(sst.ca)*0.01)
                                                e.db_set('amount',calc_amt,update_modified=True)
                                                gross_pay += calc_amt
                                        elif sst.eligible_for_contract_allowance and e.salary_component == 'Contract Allowance':
                                                calc_amt = 0
                                                calc_amt = round(new_basic*flt(sst.contract_allowance)*0.01)
                                                e.db_set('amount',calc_amt,update_modified=True)
                                                gross_pay += calc_amt
                                        elif sst.eligible_for_communication_allowance and e.salary_component == 'Communication Allowance':
                                                calc_amt = 0
                                                calc_amt = round(flt(sst.communication_allowance))			
                                                e.db_set('amount',calc_amt,update_modified=True)
                                                gross_pay += calc_amt
                                        elif sst.eligible_for_psa and e.salary_component == 'PSA':
                                                calc_amt = 0
                                                calc_amt = round(new_basic*flt(sst.psa)*0.01)
                                                e.db_set('amount',calc_amt,update_modified = True)
                                                gross_pay += calc_amt
                                        elif sst.eligible_for_mpi and e.salary_component == 'MPI':
                                                calc_amt = 0
                                                calc_amt = round(new_basic*flt(sst.mpi)*0.01)
                                                e.db_set('amount',calc_amt,update_modified = True)
                                                gross_pay += calc_amt
                                        elif sst.eligible_for_officiating_allowance and e.salary_component == 'Officiating Allowance':
                                                calc_amt = 0
                                                calc_amt = round(new_basic*flt(sst.officiating_allowance)*0.01)
                                                e.db_set('amount',calc_amt,update_modified = True)
                                                gross_pay += calc_amt
                                        elif sst.eligible_for_temporary_transfer_allowance and e.salary_component == 'Temporary Transfer Allowance':
                                                calc_amt = 0
                                                calc_amt = (new_basic*flt(sst.temporary_transfer_allowance)*0.01)
                                                e.db_set('amount',calc_amt,update_modified = True)
                                                gross_pay += calc_amt
                                        elif sst.eligible_for_fuel_allowances and e.salary_component == 'Fuel Allowance':
                                                calc_amt = 0
                                                calc_amt = round(flt(sst.fuel_allowances))
                                                e.db_set('amount',calc_amt,update_modified = True)
                                                gross_pay += calc_amt
                                        else:
                                                gross_pay += e.amount

                                company_det = get_company_pf('2016')
                                employee_gis = get_employee_gis(sst.employee)
                                
                                # Deductions
                                for d in sst.deductions:
                                        if d.salary_component == 'Group Insurance Scheme':
                                                calc_gis_amt = 0
                                                calc_gis_amt = flt(employee_gis[0][0])
                                                d.db_set('amount',calc_gis_amt,update_modified = True)
                                                deductions += calc_gis_amt
                                        elif d.salary_component == 'PF':
                                                calc_pf_amt = 0;
                                                calc_pf_amt = round(new_basic*company_det[0][0]*0.01);
                                                d.db_set('amount',calc_pf_amt,update_modified = True)
                                                deductions += calc_pf_amt
                                        elif d.salary_component == 'Health Contribution':
                                                calc_health_amt = 0;
                                                calc_health_amt = round(new_basic*company_det[0][2]*0.01);
                                                d.db_set('amount',calc_health_amt,update_modified = True)
                                                deductions += calc_health_amt
                                        elif d.salary_component == 'Salary Tax':
                                                calc_tds_amt = 0;
                                        else:
                                                deductions += d.amount


                                if gross_pay:
                                        for d in sst.deductions:
                                                if d.salary_component == 'Salary Tax':
                                                        calc_tds_amt = 0;
                                                        calc_tds_amt = get_salary_tax(gross_pay-calc_pf_amt-calc_gis_amt)
                                                        d.db_set('amount',calc_tds_amt,update_modified = True)
                                                        deductions += calc_tds_amt

                                sst.db_set('total_earning',flt(gross_pay),update_modified = True)
                                sst.db_set('total_deduction',flt(deductions),update_modified = True)
                                sst.db_set('net_pay',flt(flt(gross_pay)-flt(deductions)),update_modified = True)
                                
                                sst.save()

@frappe.whitelist()
def get_employee_payscale(employee, gradecd, fiscal_year, month):
        payscale = frappe.db.get_value("Employee Sub-Group", filters=gradecd, \
                                       fieldname = ["minimum","maximum","increment"], as_dict = True)
        sal_struc_name = get_salary_structure(employee)
        
        if payscale:
                sal_struc= frappe.get_doc("Salary Structure",sal_struc_name)
                old_basic = 0.00
                new_basic = 0.00
                for d in sal_struc.earnings:
                        if d.salary_component == 'Basic Pay':
                                old_basic = flt(d.amount)

                if old_basic:
                        new_basic = flt(old_basic if old_basic else 0) + flt(payscale.increment if payscale.increment else 0.00)

                payscale["old_basic"] = flt(old_basic if old_basic else 0.00)
                payscale["new_basic"] = new_basic
        else:
                frappe.throw(_('Pay Scale not defined for grade: <a style="color: green" href="#Form/Employee Sub-Group/{0}">{0}</a>').format(gradecd))
        
        return payscale

def get_salary_structure(employee):
        salary_struc_list = frappe.db.sql("""
                        select name from `tabSalary Structure`
                        where employee = %s
                        and is_active = 'Yes'
                        and now() between ifnull(from_date,'0000-00-00') and ifnull(to_date,'2050-12-31')
                        order by ifnull(from_date,'0000-00-00') desc limit 1
                """,(employee))

        if salary_struc_list:
                return salary_struc_list[0][0]
        else:
                frappe.throw(_('No Active Salary Structure found for the employee <a style="color: green" href="#Form/Employee/{0}">{0}</a>.').format(employee))
                        
        return salary_struc_list[0][0]
