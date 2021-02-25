# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, scrub
from frappe.utils import add_days, getdate, formatdate, get_first_day, get_last_day, date_diff, add_years, flt
#from frappe.utils.data import get_first_day, get_last_day, add_days

from frappe import _
from erpnext.accounts.utils import get_fiscal_year
#import numpy as np

def execute(filters=None):
        columns = get_columns(filters)
	data, chart = get_periodic_data(filters, columns)
	return columns, data, """<div style="background-color:blue;color:white;padding-top:0px;">
  <p>Graph Is Plotted Below La</p>
</div>""", chart

def get_columns(filters):
        columns =[
                {
                        "label": _(""),
                        "fieldname": "label",
                        "fieldtype": "Data",
                        "width": 100
                }]

        ranges = get_period_date_ranges(filters)
        for dummy, end_date in ranges:
                period = get_period(end_date, filters)
                columns.append({
                        "label": _(period),
                        "fieldname": scrub(period),
                        "fieldtype": "Data",
                        "width": 80
                })
        return columns
def get_periodic_data(filters, columns):
	data1 = []
	data2 = []
	chart = 0
	target = {'label': '<b> Target </b>'}
	achievement = {'label': '<b> Achievement </b>'}
	target_tot = 0.0
	achievement_tot = 0.0
	ranges = get_period_date_ranges(filters)
	for from_date, to_date in ranges:
		target_tot = get_target_query(filters, from_date, to_date)
		achievement_tot  = get_achievement_query(filters, from_date, to_date)
		period = get_period(to_date, filters)
		if target_tot:
			target.setdefault(scrub(period), round(flt(target_tot), 2))
		else:
			target.setdefault(scrub(period), None)

		if achievement_tot:
			achievement.setdefault(scrub(period), round(flt(achievement_tot), 2))
		else:
			achievement.setdefault(scrub(period), None)
        data1.append(target)
	data2.append(achievement)
	chart = get_chart_data(columns, target,  achievement)
        return data1+data2, chart

def get_target_query(filters, from_date, to_date):
	query = """ select sum(a.percent_completed_overall/100* a.ga_weightage) as percent_completed from `tabTarget Entry Sheet`  a 
			where a.to_date <= '{0}' and exists (select 1 from `tabTarget Entry Sheet` b where b.from_date >= '{0}')
			""".format(to_date)
	if filters.get("project"):
		query = """ select sum(a.percent_completed/100 * a.activity_weightage) as percent_completed from 
			`tabTarget Entry Sheet`  a  where a.to_date <= '{0}' 
			and exists (select 1 from `tabTarget Entry Sheet` b where b.from_date >= '{0}')
                        """.format(to_date)
		query += """ and project_parent = '{0}'""".format(filters.get("project"))

	if filters.get("activity"):
		query = """ select a.percent_completed from `tabTarget Entry Sheet`  a where 
			a.to_date between '{0}' and '{1}' and project = '{2}'""".format(from_date, to_date, filters.get("activity"))
 
	query += " order by a.to_date desc limit 1"
	data = frappe.db.sql(query, as_dict = 1)
	data   = data[0].percent_completed if data else 0.0
	return flt(data)
	
def get_achievement_query(filters, from_date, to_date):
	query = """ select sum(ifnull(a.percent_completed_overall, 0)) as percent_completed from `tabAchievement Entry Sheet` a where 
		a.posting_date <= '{0}' and exists ( select 1 from `tabAchievement Entry Sheet` b 
			where b.posting_date >= '{0}')""".format(to_date)

	if filters.get("project"):
		query += " and project_parent = '{0}'".format(filters.get("project"))

	if filters.get("activity"):
		query =  """ select sum(ifnull(a.percent_completed,0)) as percent_completed  from `tabAchievement Entry Sheet` a 
			where a.project = '{0}' and a.posting_date <= '{1}' and exists (select 1 from `tabAchievement Entry Sheet` b 
			where b.posting_date >= '{2}' and b.project = '{0}')""".format(filters.get('activity'), to_date, from_date)

	data = frappe.db.sql(query, as_dict = 1, debug =1)
	data  = data[0].percent_completed if data else 0.0
	return data


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
        chart =  {
                "data": { 'x': 'x', 'columns': columns},
		"size": {"width": 1100, "height": 500},
		"grid": {'x': { 'show': 'true'}, 'y': {'show': 'true'}},
		"zoom": {"enabled": "true"},
		"color": { "pattern": ['#00ff00', '#0000ff']},
		"padding": {"right": 0, "left": 80, "bottom":40},
		"title": {"text": 'Progress Graph! if the achievement stroke(blue) is above the target stroke(green), it means we are ahead of our schedules at that point of time'},
	}     
	chart["chart_type"] = "spline"

	return chart
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
                        periodic_daterange.append([start_date, period_end_date])

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
