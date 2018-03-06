# Copyright (c) 2016, Druk Holding & Investments Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, date_diff
from frappe.utils.data import get_first_day, get_last_day, add_days
from erpnext.custom_utils import get_year_start_date, get_year_end_date

##
# Post casual leave on the first day of every month
##
def post_casual_leaves():
	date = getdate(frappe.utils.nowdate())
	if not (date.month == 1 and date.day == 1):
		return 0
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
	if not getdate(frappe.utils.nowdate()) == getdate(get_first_day(frappe.utils.nowdate())):
		return 0
 
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
                where now() between a.from_date and ifnull(a.to_date, now())
                and b.parent = a.name
                """)

        if flt(flt(gross_amt) if flt(gross_amt) else 0.00) > flt(flt(max_limit[0][0]) if flt(max_limit[0][0]) else 0.00):
                tax_amount = flt((((flt(gross_amt) if flt(gross_amt) else 0.00)-83333.00)*0.25)+11875.00)
        else:
                result = frappe.db.sql("""select b.tax from
                        `tabSalary Tax` a, `tabSalary Tax Item` b
                        where now() between a.from_date and ifnull(a.to_date, now())
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

        if result:
                return result[0][0]
        else:
                return 0.0

@frappe.whitelist()
def update_salary_structure(employee, new_basic, sal_struc_name=None, actual_basic=None):
	#sal_struc_name = frappe.db.sql("""
	#select name
	#from `tabSalary Structure` st
	#where st.employee = '%s'
	#and is_active = 'Yes'
	#and now() between ifnull(from_date,'0000-00-00') and ifnull(to_date,'2050-12-31')
	#order by ifnull(from_date,'0000-00-00') desc 
	#limit 1
	#""" % (employee))	

	sst = ""
	if sal_struc_name and new_basic > 0:
		#sst = frappe.get_doc("Salary Structure", sal_struc_name[0][0])
		sst = frappe.get_doc("Salary Structure", sal_struc_name)
		if sst:
			gross_pay = 0.00
			deductions = 0.00
			comm_amt = 0.00

			#Earnings
			for e in sst.earnings:
				per_or_lum = frappe.db.get_value("Salary Component", e.salary_component, "payment_method")
				if e.salary_component == "Basic Pay":
					e.db_set('amount',new_basic,update_modified=True)
					gross_pay += new_basic
				elif e.salary_component == 'Corporate Allowance':
					calc_amt = 0
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.ca)*0.01)
					else:
						calc_amt = round(flt(sst.ca))

					calc_amt = calc_amt if sst.eligible_for_corporate_allowance else 0
					
					e.db_set('amount',calc_amt,update_modified=True)
					gross_pay += calc_amt					
				elif e.salary_component == 'Contract Allowance':
					calc_amt = 0
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.contract_allowance)*0.01)
					else:
						calc_amt = round(flt(sst.contract_allowance))

					calc_amt = calc_amt if sst.eligible_for_contract_allowance else 0
					
					e.db_set('amount',calc_amt,update_modified=True)
					gross_pay += calc_amt
				elif e.salary_component == 'Communication Allowance':
					calc_amt = 0
					comm_amt = round(flt(sst.communication_allowance))
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.communication_allowance)*0.01)
					else:
						calc_amt = round(flt(sst.communication_allowance))

					calc_amt = calc_amt if sst.eligible_for_communication_allowance else 0
					comm_amt = calc_amt
					
					e.db_set('amount',calc_amt,update_modified=True)
					gross_pay += calc_amt
				elif e.salary_component == 'Underground Allowance':
					calc_amt = 0
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.underground)*0.01)
					else:
						calc_amt = round(flt(sst.underground))

					calc_amt = calc_amt if sst.eligible_for_underground else 0
					
					e.db_set('amount',calc_amt,update_modified = True)
					gross_pay += calc_amt
				elif e.salary_component == 'Shift Allowance':
					calc_amt = 0
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.shift)*0.01)
					else:
						calc_amt = round(flt(sst.shift))

					calc_amt = calc_amt if sst.eligible_for_shift else 0
					
					e.db_set('amount',calc_amt,update_modified = True)
					gross_pay += calc_amt
				elif e.salary_component == 'Difficult Area Allowance':
					calc_amt = 0
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.difficulty)*0.01)
					else:
						calc_amt = round(flt(sst.difficulty))

					calc_amt = calc_amt if sst.eligible_for_difficulty else 0
					
					e.db_set('amount',calc_amt,update_modified = True)
					gross_pay += calc_amt
				elif e.salary_component == 'High Altitude Allowance':
					calc_amt = 0
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.high_altitude)*0.01)
					else:
						calc_amt = round(flt(sst.high_altitude))

					calc_amt = calc_amt if sst.eligible_for_high_altitude else 0
					
					e.db_set('amount',calc_amt,update_modified = True)
					gross_pay += calc_amt
				elif e.salary_component == 'PDA':
					calc_amt = 0
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.pda)*0.01)
					else:
						calc_amt = round(flt(sst.pda))

					calc_amt = calc_amt if sst.eligible_for_pda else 0
					
					e.db_set('amount',calc_amt,update_modified = True)
					gross_pay += calc_amt
				elif e.salary_component == 'PSA':
					calc_amt = 0
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.psa)*0.01)
					else:
						calc_amt = round(flt(sst.psa))

					calc_amt = calc_amt if sst.eligible_for_psa else 0
					
					e.db_set('amount',calc_amt,update_modified = True)
					gross_pay += calc_amt
				elif e.salary_component == 'Deputation Allowance':
					calc_amt = 0
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.deputation)*0.01)
					else:
						calc_amt = round(flt(sst.deputation))

					calc_amt = calc_amt if sst.eligible_for_deputation else 0
					
					e.db_set('amount',calc_amt,update_modified = True)
					gross_pay += calc_amt
				elif e.salary_component == 'Scarcity Allowance':
					calc_amt = 0
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.scarcity)*0.01)
					else:
						calc_amt = round(flt(sst.scarcity))

					calc_amt = calc_amt if sst.eligible_for_scarcity else 0
					
					e.db_set('amount',calc_amt,update_modified = True)
					gross_pay += calc_amt
				elif e.salary_component == 'MPI':
					calc_amt = 0
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.mpi)*0.01)
					else:
						calc_amt = round(flt(sst.mpi))

					calc_amt = calc_amt if sst.eligible_for_mpi else 0
					
					e.db_set('amount',calc_amt,update_modified = True)
					gross_pay += calc_amt
				elif e.salary_component == 'Officiating Allowance':
					calc_amt = 0
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.officiating_allowance)*0.01)
					else:
						calc_amt = round(flt(sst.officiating_allowance))

					calc_amt = calc_amt if sst.eligible_for_officiating_allowance else 0
					
					e.db_set('amount',calc_amt,update_modified = True)
					gross_pay += calc_amt
				elif e.salary_component == 'Temporary Transfer Allowance':
					calc_amt = 0
					if per_or_lum == "Percent": 
						calc_amt = round(new_basic*flt(sst.temporary_transfer_allowance)*0.01)
					else:
						calc_amt = round(flt(sst.temporary_transfer_allowance))

					calc_amt = calc_amt if sst.eligible_for_temporary_transfer_allowance else 0
					
					e.db_set('amount',calc_amt,update_modified = True)
					gross_pay += calc_amt
				else:
					gross_pay += e.amount

			employee_gis = frappe.db.sql("""select a.gis
				from `tabEmployee Grade` a, `tabEmployee` b
				where b.employee = %s
				and b.employee_group = a.employee_group
				and b.employee_subgroup = a.employee_subgroup
				limit 1
				""",sst.employee);
			
			# Deductions
			calc_gis_amt    = 0
			calc_pf_amt     = 0
			calc_tds_amt    = 0
			calc_health_amt = 0
			
			for d in sst.deductions:
				if d.salary_component == 'Group Insurance Scheme':
					calc_gis_amt = 0
					calc_gis_amt = flt(employee_gis[0][0])
					calc_gis_amt = calc_gis_amt if sst.eligible_for_gis else 0
					d.db_set('amount',calc_gis_amt,update_modified = True)
					deductions += calc_gis_amt
				elif d.salary_component == 'PF':
					percent = frappe.db.get_single_value("HR Settings", "employee_pf")
					if not percent:
						frappe.throw("Setup Employee PF in HR Settings")
					calc_pf_amt = 0;
					calc_pf_amt = round(new_basic * flt(percent) * 0.01);
					calc_pf_amt = calc_pf_amt if sst.eligible_for_pf else 0
					d.db_set('amount',calc_pf_amt,update_modified = True)
					deductions += calc_pf_amt
				elif d.salary_component == 'Salary Tax' or d.salary_component == 'Health Contribution':
					calc_tds_amt = 0;
				else:
					deductions += d.amount


			if gross_pay:
				for d in sst.deductions:
					if d.salary_component == 'Salary Tax':
						calc_tds_amt = 0;
						calc_tds_amt = get_salary_tax(gross_pay-calc_pf_amt-calc_gis_amt-(0.5 * comm_amt))
						d.db_set('amount',calc_tds_amt,update_modified = True)
						deductions += calc_tds_amt
					
					if d.salary_component == 'Health Contribution':
						percent = frappe.db.get_single_value("HR Settings", "health_contribution")
						if not percent:
							frappe.throw("Setup Health Contribution Percent in HR Settings")
						calc_health_amt = 0;
						calc_health_amt = round(gross_pay * flt(percent) * 0.01);
						calc_health_amt = calc_health_amt if sst.eligible_for_health_contribution else 0
						d.db_set('amount',calc_health_amt,update_modified = True)
						deductions += calc_health_amt

			sst.db_set('total_earning',flt(gross_pay),update_modified = True)
			sst.db_set('total_deduction',flt(deductions),update_modified = True)
			sst.db_set('net_pay',flt(flt(gross_pay)-flt(deductions)),update_modified = True)
			if actual_basic:
				sst.actual_basic = actual_basic

			sst.save()
			return sst


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
		
