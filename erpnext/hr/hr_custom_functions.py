# Copyright (c) 2016, Druk Holding & Investments Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cint
from frappe.utils.data import get_first_day, get_last_day, add_days
from erpnext.custom_utils import get_year_start_date, get_year_end_date

##
# Post casual leave on the first day of every month
##
def post_casual_leaves():
	date = add_days(frappe.utils.nowdate(), 10)
	start = get_year_start_date(date);
	end = get_year_end_date(date);

        # Shiv 2019/01/22 ticket#1333, Following line replaced by subsequent
	#employees = frappe.db.sql("select name, employee_name from `tabEmployee` where status = 'Active' and employment_type in (\'Regular employees\', \'Contract\')", as_dict=True)
	employees = frappe.db.sql("select name, employee_name from `tabEmployee` where status = 'Active' and employment_type not in (\'Temporary\')", as_dict=True)
	for e in employees:
		if not frappe.db.exists("Leave Allocation", {"employee": e.name, "leave_type": "Casual Leave", "from_date": start, "to_date": end, "docstatus": ("<",2)}):
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

        # Shiv 2019/01/22 ticket#1333, Following line replaced by subsequent
        #employees = frappe.db.sql("select name, employee_name from `tabEmployee` where status = 'Active' and employment_type in (\'Regular employees\', \'Contract\')", as_dict=True)	
	employees = frappe.db.sql("select name, employee_group, employee_name from `tabEmployee` where status = 'Active' and employment_type not in (\'Temporary\')", as_dict=True)
	for e in employees:
		if not frappe.db.exists("Leave Allocation", {"employee": e.name, "leave_type": "Earned Leave", "from_date": start, "to_date": end, "docstatus": ("<",2)}):
			la = frappe.new_doc("Leave Allocation")
			la.employee = e.name
			la.employee_name = e.employee_name
			la.leave_type = "Earned Leave"
			la.from_date = str(start)
			la.to_date = str(end)
			la.carry_forward = cint(1)
			la.new_leaves_allocated = flt(2.5)
			la.submit()
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

# VER#2.0#CDCL#886: Following code is added by SHIV on 06/09/2018
@frappe.whitelist()
def get_payroll_settings(employee=None):
	settings = {}
        if employee:
                settings = frappe.db.sql("""
                        select
                                e.employee_group,
                                e.employee_subgroup,
                                d.sws_contribution,
                                d.gis,
                                g.health_contribution,
                                g.employee_pf,
                                g.employer_pf
                        from `tabEmployee` e, `tabEmployee Group` g, `tabEmployee Grade` d
                        where e.name = '{0}'
                        and g.name = e.employee_group
                        and d.employee_group = g.name
                        and d.name = e.employee_subgroup
                """.format(employee), as_dict=True);
        settings = settings[0] if settings else settings
        return settings


#function to get the difference between two dates
@frappe.whitelist()
def get_date_diff(start_date, end_date):
	if start_date is None:
		return 0
	elif end_date is None:
		return 0
	else:	
		return frappe.utils.data.date_diff(end_date, start_date) + 1;
