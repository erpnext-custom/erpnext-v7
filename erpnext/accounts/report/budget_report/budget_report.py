# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import formatdate
import time
from erpnext.accounts.utils import get_fiscal_year
from erpnext.controllers.trends import get_period_date_ranges, get_period_month_ranges

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns(filters)
	period_month_ranges = get_period_month_ranges(filters["period"], filters["fiscal_year"])
	cam_map = get_costcenter_account_month_map(filters)

	data = []
	for cost_center, cost_center_items in cam_map.items():
		for account, monthwise_data in cost_center_items.items():
			row = [cost_center, account]
			totals = [0, 0, 0, 0]
			for relevant_months in period_month_ranges:
				period_data = [0, 0, 0, 0]
				for month in relevant_months:
					month_data = monthwise_data.get(month, {})
					for i, fieldname in enumerate(["target", "actual", "commit", "variance"]):
						value = flt(month_data.get(fieldname))
						period_data[i] += value
						totals[i] += value
				period_data[3] = period_data[0] - period_data[1] - period_data[2]
				row += period_data
			totals[3] = totals[0] - totals[1] - totals[2]
			row += totals
			data.append(row)

	return columns, sorted(data, key=lambda x: (x[0], x[1], x[2]))

def get_columns(filters):
	for fieldname in ["fiscal_year", "period", "company"]:
		if not filters.get(fieldname):
			label = (" ".join(fieldname.split("_"))).title()
			msgprint(_("Please specify") + ": " + label,
				raise_exception=True)

	columns = [_("Cost Center") + ":Link/Cost Center:120", _("Account") + ":Link/Account:120"]

	group_months = False if filters["period"] == "Monthly" else True

	for from_date, to_date in get_period_date_ranges(filters["period"], filters["fiscal_year"]):
		for label in [_("Total Budget") + " (%s)", _("Budget Consumed") + " (%s)", _("Budget Committed") + " (%s)",_("Available Budget") + " (%s)"]:
			if group_months:
				label = label % (formatdate(from_date, format_string="MMM") + " - " + formatdate(from_date, format_string="MMM"))
			else:
				label = label % formatdate(from_date, format_string="MMM")

			columns.append(label+":Float:120")

	return columns + [_("Total") + ":Float:120", _("Total Consumed") + ":Float:120",
			_("Total Committed") + ":Float:120",_("Total Available") + ":Float:120"]

#Get cost center & target details
def get_costcenter_target_details(filters):
	return frappe.db.sql("""select cc.name, cc.distribution_id,
		cc.parent_cost_center, bd.account, bd.budget_allocated
		from `tabCost Center` cc, `tabBudget Detail` bd
		where bd.parent=cc.name and bd.fiscal_year=%s and
		cc.company=%s order by cc.name""" % ('%s', '%s'),
		(filters.get("fiscal_year"), filters.get("company")), as_dict=1)

#Get target distribution details of accounts of cost center
def get_target_distribution_details(filters):
	target_details = {}

	for d in frappe.db.sql("""select md.name, mdp.month, mdp.percentage_allocation
		from `tabMonthly Distribution Percentage` mdp, `tabMonthly Distribution` md
		where mdp.parent=md.name and md.fiscal_year=%s""", (filters["fiscal_year"]), as_dict=1):
			target_details.setdefault(d.name, {}).setdefault(d.month, flt(d.percentage_allocation))

	return target_details

#Get actual details from gl entry
def get_actual_details(filters):
	ac_details = frappe.db.sql("""select gl.account, gl.debit, gl.credit,
		gl.cost_center, MONTHNAME(gl.posting_date) as month_name
		from `tabGL Entry` gl, `tabBudget Detail` bd
		where gl.fiscal_year=%s and company=%s
		and bd.account=gl.account and bd.parent=gl.cost_center""" % ('%s', '%s'),
		(filters.get("fiscal_year"), filters.get("company")), as_dict=1)

	cc_actual_details = {}
	for d in ac_details:
		cc_actual_details.setdefault(d.cost_center, {}).setdefault(d.account, []).append(d)
	
	return cc_actual_details

#Get commited budget details from purchase order
def get_committed_details(filters):
	com_details = frappe.db.sql("""
	SELECT poi.cost_center, poi.budget_account, poi.amount, MONTHNAME(poi.schedule_date) AS month_name
	FROM `tabPurchase Order Item` AS poi 
	JOIN `tabBudget Detail` AS bd
 	  ON poi.cost_center = bd.parent AND poi.budget_account = bd.account
        JOIN `tabPurchase Order` AS po
	  ON po.name = poi.parent
	LEFT JOIN `tabPurchase Invoice Item` AS pii
	  ON pii.purchase_order = po.name
	LEFT JOIN `tabPurchase Invoice` AS pi
	  ON pi.name = pii.parent
	WHERE (po.status IN ('To Receive and Bill', 'To Bill') OR pi.outstanding_amount > 0) AND bd.fiscal_year=%s""",filters['fiscal_year'], as_dict=True)

	cc_committed_details = {}
	for d in com_details:
		cc_committed_details.setdefault(d.cost_center, {}).setdefault(d.budget_account, []).append(d)
	
	return cc_committed_details

def get_costcenter_account_month_map(filters):
	import datetime
	costcenter_target_details = get_costcenter_target_details(filters)
	tdd = get_target_distribution_details(filters)
	actual_details = get_actual_details(filters)
	commit_details = get_committed_details(filters);

	cam_map = {}

	for ccd in costcenter_target_details:
		for month_id in range(1, 13):
			month = datetime.date(2013, month_id, 1).strftime('%B')

			cam_map.setdefault(ccd.name, {}).setdefault(ccd.account, {})\
				.setdefault(month, frappe._dict({
					"target": 0.0, "actual": 0.0, "commit":0.0
				}))

			tav_dict = cam_map[ccd.name][ccd.account][month]

			month_percentage = tdd.get(ccd.distribution_id, {}).get(month, 0) \
				if ccd.distribution_id else 100.0/12

			tav_dict.target = flt(ccd.budget_allocated) * month_percentage / 100

			for ad in actual_details.get(ccd.name, {}).get(ccd.account, []):
				if ad.month_name == month:
						tav_dict.actual += flt(ad.debit) - flt(ad.credit)

			for com in commit_details.get(ccd.name, {}).get(ccd.account, []):
				if com.month_name == month:
						tav_dict.commit += flt(com.amount)

	return cam_map
