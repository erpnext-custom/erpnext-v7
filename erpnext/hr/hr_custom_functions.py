# Copyright (c) 2016, Druk Holding & Investments Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cint, getdate, date_diff
from frappe.utils.data import get_first_day, get_last_day, add_days
from erpnext.custom_utils import get_year_start_date, get_year_end_date

##
# Post casual leave on the first day of every month
##
def post_casual_leaves():
	date = add_days(frappe.utils.nowdate(), 10)
	start = get_year_start_date(date);
	end = get_year_end_date(date);
	employees = frappe.db.sql("select name, employee_name from `tabEmployee` where status = 'Active'", as_dict=True)
	for e in employees:
		la = frappe.new_doc("Leave Allocation")
		la.employee = e.name
		la.employee_name = e.employee_name
		la.leave_type = "Casual Leave"
		la.from_date = str(start)
		la.to_date = str(end)
		la.carry_forward = cint(0)
		la.new_leaves_allocated = flt(10)
		la.submit()

##
# Post earned leave on the first day of every month
##
def post_earned_leaves():
	date = add_days(frappe.utils.nowdate(), -20)
	start = get_first_day(date);
	end = get_last_day(date);
	
	employees = frappe.db.sql("select name, employee_name, date_of_joining from `tabEmployee` where status = 'Active'", as_dict=True)
	for e in employees:
		if cint(date_diff(end, getdate(e.date_of_joining))) > 14:
			la = frappe.new_doc("Leave Allocation")
			la.employee = e.name
			la.employee_name = e.employee_name
			la.leave_type = "Earned Leave"
			la.from_date = str(start)
			la.to_date = str(end)
			la.carry_forward = cint(1)
			la.new_leaves_allocated = flt(2.5)
			la.submit()
		else:
			pass

#function to get the difference between two dates
@frappe.whitelist()
def get_date_diff(start_date, end_date):
	if start_date is None:
		return 0
	elif end_date is None:
		return 0
	else:	
		return frappe.utils.data.date_diff(end_date, start_date) + 1;

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
def get_company_pf(fiscal_year=None):
        #result = frappe.db.sql("""
        #       select employee_pf, employer_pf, health_contribution, retirement_age
        #        from `tabFiscal Year`
        #        where now() between year_start_date and year_end_date
        #        limit 1
        #        """);
	employee_pf = frappe.db.get_single_value("HR Settings", "employee_pf")
	if not employee_pf:
		frappe.throw("Setup Employee PF in HR Settings")
	employer_pf = frappe.db.get_single_value("HR Settings", "employer_pf")
	if not employer_pf:
		frappe.throw("Setup Employer PF in HR Settings")
	health_contribution = frappe.db.get_single_value("HR Settings", "health_contribution")
	if not health_contribution:
		frappe.throw("Setup Health Contribution in HR Settings")
	retirement_age = frappe.db.get_single_value("HR Settings", "retirement_age")
	if not retirement_age:
		frappe.throw("Setup Retirement Age in HR Settings")
        result = ((flt(employee_pf), flt(employer_pf), flt(health_contribution), flt(retirement_age)),)
	return result

# Ver 1.0 added by SSK on 04/08/2016, Fetching GIS component
@frappe.whitelist()
def get_employee_gis(employee):
        #msgprint(employee);
        result = frappe.db.sql("""select a.gis
                from `tabEmployee Grade` a, `tabEmployee` b
                where b.employee = %s
                and b.employee_group = a.employee_group
                and b.employee_subgroup = a.employee_subgroup
                limit 1
                """,employee);
	return result

@frappe.whitelist()
def update_salary_structure(employee, new_basic):
	sal_struc_name = frappe.db.sql("""
	select name
	from `tabSalary Structure` st
	where st.employee = '%s'
	and is_active = 'Yes'
	and now() between ifnull(from_date,'0000-00-00') and ifnull(to_date,'2050-12-31')
	order by ifnull(from_date,'0000-00-00') desc 
	limit 1
	""" % (employee))
	
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

			#company_det = frappe.db.sql("""
			#	select employee_pf, employer_pf, health_contribution, retirement_age
			#	from `tabFiscal Year`
			#	where now() between year_start_date and year_end_date
			#	limit 1
			#	""");
			employee_gis = frappe.db.sql("""select a.gis
				from `tabEmployee Grade` a, `tabEmployee` b
				where b.employee = %s
				and b.employee_group = a.employee_group
				and b.employee_subgroup = a.employee_subgroup
				limit 1
				""",sst.employee);
			
			# Deductions
			for d in sst.deductions:
				if d.salary_component == 'Group Insurance Scheme':
					calc_gis_amt = 0
					calc_gis_amt = flt(employee_gis[0][0])
					d.db_set('amount',calc_gis_amt,update_modified = True)
					deductions += calc_gis_amt
				elif d.salary_component == 'PF':
					percent = frappe.db.get_single_value("HR Settings", "employee_pf")
					if not percent:
						frappe.throw("Setup Employee PF in HR Settings")
					calc_pf_amt = 0;
					calc_pf_amt = round(new_basic * flt(percent) * 0.01);
					d.db_set('amount',calc_pf_amt,update_modified = True)
					deductions += calc_pf_amt
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
					
					if d.salary_component == 'Health Contribution':
						percent = frappe.db.get_single_value("HR Settings", "health_contribution")
						if not percent:
							frappe.throw("Setup Health Contribution Percent in HR Settings")
						calc_health_amt = 0;
						calc_health_amt = round(gross_pay * flt(percent) * 0.01);
						d.db_set('amount',calc_health_amt,update_modified = True)
						deductions += calc_health_amt

			sst.db_set('total_earning',flt(gross_pay),update_modified = True)
			sst.db_set('total_deduction',flt(deductions),update_modified = True)
			sst.db_set('net_pay',flt(flt(gross_pay)-flt(deductions)),update_modified = True)
			
			sst.save()
			return sst


