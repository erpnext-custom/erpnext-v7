# Copyright (c) 2016, Druk Holding & Investments Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

'''
---------------------------------------------------------------------------------------------------------------------------
Version          Author            CreatedOn          ModifiedOn          Remarks
------------ ---------------  ------------------ -------------------  -----------------------------------------------------
2.0#CDCL#886      SSK	          06/09/2018                          Moved retirement_age, health_contribution, employee_pf,
                                                                         employer_pf from "HR Settings" to "Employee Group"
---------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, date_diff
from frappe.utils.data import get_first_day, get_last_day, add_days
from erpnext.custom_utils import get_year_start_date, get_year_end_date
import json

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

# ++++++++++++++++++++ VER#2.0#CDCL#886 BEGINS ++++++++++++++++++++
# VER#2.0#CDCL#886: Following code is commented by SHIV on 06/09/2018
'''		
# Ver 1.0 added by SSK on 03/08/2016, Fetching PF component
@frappe.whitelist()
def get_company_pf(fiscal_year=None, employee=None):
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
                and b.employee_subgroup = a.name
                limit 1
                """,employee);

        if result:
                return result[0][0]
        else:
                return 0.0
'''

# VER#2.0#CDCL#886: Following code is added by SHIV on 06/09/2018
@frappe.whitelist()
def get_employee_group_settings(employee=None):
        settings = {}
        if employee:
                settings = frappe.db.sql("""
                        select
                                a.employee_group,
                                a.name employee_grade,
                                a.gis,
                                c.health_contribution,
                                c.employee_pf,
                                c.employer_pf
                        from `tabEmployee Grade` a, `tabEmployee` b, `tabEmployee Group` c
                        where b.employee = '{0}'
                        and c.name = b.employee_group
                        and a.employee_group = b.employee_group
                        and a.name = b.employee_subgroup
                        limit 1
                """.format(employee), as_dict=True);
        settings = settings[0] if settings else settings
        return settings
# +++++++++++++++++++++ VER#2.0#CDCL#886 ENDS +++++++++++++++++++++

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
