# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr, rounded
from erpnext.accounts.report.financial_statements_emines \
	import filter_accounts, set_gl_entries_by_account, filter_out_zero_value_rows

def execute(filters=None):
	columns = get_columns()
	data = get_accounts(filters)
	return columns, data

def get_accounts(filters):
	data = []
	for a in frappe.db.sql("SELECT a.name, b.fixed_asset_account as fa, b.accumulated_depreciation_account as acc, b.depreciation_expense_account as dep from `tabAsset Category` a, `tabAsset Category Account` b where a.name = b.parent", as_dict=True):
		gross_opening = get_values(a.fa, filters.to_date, filters.from_date, filters.cost_center, opening=True)
		gross = get_values(a.fa, filters.to_date, filters.from_date, filters.cost_center)
		dep_opening = get_values(a.acc, filters.to_date, filters.from_date, filters.cost_center, opening=True)
		dep = get_values(a.dep, filters.to_date, filters.from_date, filters.cost_center)

		gross_opening = gross_opening[0]
		gross = gross[0]
		dep_opening = dep_opening[0]
		dep = dep[0]

		g_open = flt(gross_opening.debit) - flt(gross_opening.credit)
		g_total = g_open + flt(gross.debit) - flt(gross.credit)
		d_open = -1 * (flt(dep_opening.debit) - flt(dep_opening.credit))
		d_total = d_open + flt(dep.debit) - flt(dep.credit)

		row = {
			"asset_category": a.name,
			"gross_opening": g_open,
			"gross_addition": gross.debit,
			"gross_adjustment": gross.credit,
			"gross_total": g_total,
			"dep_opening": d_open,
			"dep_addition": dep.debit,
			"dep_adjustment": dep.credit,
			"dep_total": d_total,
			"net_block": flt(g_open) + flt(d_total) 
		}
		data.append(row)

	#FOr CWIP Account
	cwip_acc = []
	cwip_accounts_gl = frappe.db.sql("select name from tabAccount where parent_account = 'Capital Work in Progress - SMCL'", as_dict=True)
	for account in cwip_accounts_gl:
		cwip_acc.append(str(account.name))
	cwip_accounts = tuple(cwip_acc)

	cwip_open = get_values(cwip_accounts, filters.to_date, filters.from_date, filters.cost_center, opening=True, cwip=True)
	cwip = get_values(cwip_accounts, filters.to_date, filters.from_date, filters.cost_center, cwip=True)

	cwip_open = cwip_open[0]
	cwip = cwip[0]

	c_open = flt(cwip_open.debit) - flt(cwip_open.credit)
	c_total = c_open + flt(cwip.debit) - flt(cwip.credit)

	row = {
		"asset_category": "Capital Work in Progress",
		"gross_opening": c_open,
		"gross_addition": cwip.debit,
		"gross_adjustment": cwip.credit,
		"gross_total": c_total,
		"dep_opening": '',
		"dep_addition": '',
		"dep_adjustment": '',
		"dep_total": '',
		"net_block": c_total 
	}
	data.append(row)
	return data

def get_values(account, to_date, from_date, cost_center=None, opening=False, cwip=False):
	if cwip:
		query = "select sum(debit) as debit, sum(credit) as credit from `tabGL Entry` where account in " + str(account) + " and docstatus = 1 "
	else:
		query = "select sum(debit) as debit, sum(credit) as credit from `tabGL Entry` where account = \'" + str(account) + "\' and docstatus = 1 "
	if not opening:
		query += " and posting_date between \'" + str(from_date) + "\' and \'" + str(to_date) + "\'"
	else:
		query += "and posting_date < \'" + str(from_date) + "\'"
	if cost_center:
		query += " and cost_center = \'" + str(cost_center) + "\'"

	value = frappe.db.sql(query, as_dict=True)

	return value


def get_columns():
	return [
		{
			"fieldname": "asset_category",
			"label": _("Asset Category"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "gross_opening",
			"label": _("Gross Opening"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "gross_addition",
			"label": _("Gross Addition"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "gross_adjustment",
			"label": _("Gross Adjustment"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "gross_total",
			"label": _("Gross Total"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "dep_opening",
			"label": _("Acc. Dep. Opening"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "dep_addition",
			"label": _("Dep. Addition"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "dep_adjustment",
			"label": _("Dep. Adjustment"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "dep_total",
			"label": _("Dep. Total"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "net_block",
			"label": _("Net Block"),
			"fieldtype": "Currency",
			"width": 150
		}
]
