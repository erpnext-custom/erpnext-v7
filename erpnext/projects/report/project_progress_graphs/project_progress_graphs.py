# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, scrub
from frappe.utils import add_days, getdate, formatdate, get_first_day, get_last_day, date_diff, add_years, flt
#from frappe.utils.data import get_first_day, get_last_day, add_days

from frappe import _
from erpnext.accounts.utils import get_fiscal_year

def execute(filters=None):
        columns = get_columns(filters)
	data, chart = get_periodic_data(filters, columns)
	return columns, data, None,  chart

def get_columns(filters):
        columns =[
                {
                        "label": _(""),
                        "fieldname": "label",
                        "fieldtype": "Data",
                        "width": 140
                }]

        ranges = get_period_date_ranges(filters)
        for dummy, end_date in ranges:
                period = get_period(end_date, filters)
                columns.append({
                        "label": _(period),
                        "fieldname": scrub(period),
                        "fieldtype": "Data",
                        "width": 120
                })

        return columns
def get_periodic_data(filters, columns):
	data1 = []
	data2 = []
	chart = 0
	target = {'label': 'Target'}
	achievement = {'label': 'Achievement'}
	target_tot = 0.0
	achievement_tot = 0.0
	ranges = get_period_date_ranges(filters)
	for from_date, to_date in ranges:
		query = construct_query(filters, from_date, to_date)
                period = get_period(to_date, filters)
		for t in frappe.db.sql(query, as_dict = 1, debug = 1):
			doc = frappe.get_doc("Project", t.parent)
			if getdate(t.start_date) > getdate(from_date) and getdate(t.end_date) < getdate(to_date):
				hol_list = holiday_list(t.start_date, t.end_date, doc.holiday_list)
				duration = date_diff(t.end_date, t.start_date) + 1 - flt(hol_list)
				target_tot += round(flt(duration) * flt(t.one_day_weightage), 4)
				achievement_tot += round(flt(duration) * flt(t.one_day_achievement), 4)
			
			if getdate(t.start_date) == getdate(from_date) and getdate(t.end_date) == getdate(to_date):
				hol_list = holiday_list(t.end_date, t.start_date, doc.holiday_list)
				duration = date_diff(t.end_date, t.start_date)
				target_tot += round(flt(duration) * flt(t.one_day_achievement), 4)
				achievement_tot += round(flt(duration) * flt(t.one_day_achievement), 4)

			if getdate(t.start_date) < getdate(from_date) and getdate(from_date) <= getdate(t.end_date) < getdate(to_date):
				hol_list = holiday_list(from_date, t.end_date, doc.holiday_list)
				duration = date_diff(t.end_date, from_date) + 1 - flt(hol_list)
				target_tot += round(flt(duration) * flt(t.one_day_weightage),4)
				achievement_tot += round(flt(duration) * flt(t.one_day_achievement), 4)
			
			if getdate(to_date) > getdate(t.start_date) > getdate(from_date) and getdate(t.end_date) > getdate(to_date):
				hol_list = holiday_list(t.start_date, to_date, doc.holiday_list)
				duration = date_diff(to_date, t.start_date) + 1
				target_tot += round(flt(duration) * flt(t.one_day_weightage),4)
				achievement_tot += round(flt(duration) * flt(t.one_day_achievement), 4)

			if getdate(t.start_date) < getdate(from_date) and getdate(t.end_date) > getdate(to_date):
				hol_lost = holiday_list(from_date, to_date, doc.holiday_list)
				duration = date_diff(to_date, from_date) + 1 - flt(hol_list)
				target_tot += round(flt(duration) * flt(t.one_day_weightage),4)
				achievement_tot += round(flt(duration) * flt(t.one_day_achievement), 4)
			
		target.setdefault(scrub(period), round(target_tot, 4))
		achievement.setdefault(scrub(period), round(achievement_tot, 4))
        data1.append(target)
	data2.append(achievement)
	if data1 and data2:
		chart = get_chart_data(columns, target,  achievement)
        return data1+data2, chart

def construct_query(filters, from_date, to_date):
	cond = " and is_group != 1"
	date_cond = " and 1 = 1"
	if filters.get("project"):
		cond = " and parent in ( select name from `tabProject` where parent_project = '{0}')".format(filters.get("project"))

	if filters.get("activity"):
		cond = " and parent = '{0}'".format(filters.get("activity"))
	if from_date and to_date:
		#date_cond = " and 1 = 1"
		date_cond = " and ((start_date between '{0}' and '{1}') or (end_date between '{0}' and '{1}') or ('{0}' between start_date and end_date) or ('{1}' between start_date and end_date))".format(from_date, to_date)
	query = """select name, start_date, end_date, one_day_weightage, one_day_achievement, is_group, parent, task
                                from `tabActivity Tasks`  where
                                docstatus <= 1 {0}""".format(date_cond)
	query += cond
	return query 
	



def get_chart_data(columns, target, achievement):
        x_intervals = ['x'] + [d.get("label") for d in columns[1:]]

        asset_data, liability_data =  [], []

        for p in columns[1:]:
                if target:
                        asset_data.append(target.get(p.get("fieldname")))
                if achievement:
                        liability_data.append(achievement.get(p.get("fieldname")))

        columns = [x_intervals]
        if asset_data:
                columns.append(["Target"] + asset_data)
        if liability_data:
                columns.append(["Achievement"] + liability_data)

        return {
                "data": {
                        'x': 'x',
                        'columns': columns
                }
        }
               
def get_period_date_ranges(filters):
                from dateutil.relativedelta import relativedelta
                from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
		start_date = get_first_day(from_date)
                increment = {
                        "Monthly": 1,
                        "Quarterly": 3,
                        "Half-Yearly": 6,
                        "Yearly": 12
                }.get(filters.range,1)

                periodic_daterange = []
                for dummy in range(1, 53, increment):
                        if filters.range == "Weekly":
                                period_end_date = start_date + relativedelta(days=6)
                        else:
                                period_end_date = start_date + relativedelta(months=increment, days=-1)

                        if period_end_date > to_date:
                                period_end_date = to_date
                        periodic_daterange.append([from_date, period_end_date])

                        start_date = period_end_date + relativedelta(days=1)
			from_date = period_end_date + relativedelta(days=1)

                        if period_end_date == to_date:
                                break
                return periodic_daterange



def get_period(posting_date, filters):
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        if filters.range == 'Weekly':
                period = "Week " + str(posting_date.isocalendar()[1]) + " " + str(posting_date.year)
        elif filters.range == 'Monthly':
                period = str(months[posting_date.month - 1]) + " " + str(posting_date.year)
        elif filters.range == 'Quarterly':
                period = "Quarter " + str(((posting_date.month-1)//3)+1) +" " + str(posting_date.year)
        else:
                year = get_fiscal_year(posting_date, company=filters.company)
                period = str(year[2])
        return period


def holiday_list(from_date, to_date, hol_list):
        holidays = 0.0
        if hol_list:
                holidays = frappe.db.sql("""select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
        where h1.parent = h2.name and h1.holiday_date between %s and %s
        and h2.name = %s""", (from_date, to_date, hol_list))[0][0]
        return holidays

