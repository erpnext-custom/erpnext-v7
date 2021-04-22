# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
# project_invoice.py
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SHIV		 2021/04/09                            Original Version
									* Created for the purpose of maintaining all assets
									  related bugfixes
-------------------------------------------------------------------------------------------------------------------------- 
'''
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
from frappe.utils import flt, cint, now
from frappe.utils.data import get_first_day, get_last_day, add_years, date_diff, today, get_first_day, get_last_day


def ppe():
	from_date = '2020-01-01'
	to_date = '2020-12-31'
	for a in frappe.db.sql("SELECT a.name, b.fixed_asset_account as fa, b.accumulated_depreciation_account as acc, 
				b.depreciation_expense_account as dep 
			from `tabAsset Category` a, `tabAsset Category Account` b 
			where a.name = b.parent", as_dict=True):
		# gross opening
		for i in frappe.db.sql("""
			""") 
			pass

def ppe_temp():
	data = []
	for a in frappe.db.sql("SELECT a.name, b.fixed_asset_account as fa, b.accumulated_depreciation_account as acc, 
				b.depreciation_expense_account as dep 
			from `tabAsset Category` a, `tabAsset Category Account` b 
			where a.name = b.parent", as_dict=True):
		gross_opening = get_values(a.fa, filters.to_date, filters.from_date, filters.cost_center, opening=True)[0]
		gross = get_values(a.fa, filters.to_date, filters.from_date, filters.cost_center)[0]
		dep_opening = get_values(a.acc, filters.to_date, filters.from_date, filters.cost_center, opening=True)[0]
		acc_dep = get_values(a.acc, filters.to_date, filters.from_date, filters.cost_center)[0]
		# following line commented by SHIV on 2021/03/10 as it is not used anywhere
		#dep = get_values(a.dep, filters.to_date, filters.from_date, filters.cost_center)[0]
		adj = get_values(a.acc, filters.to_date, filters.from_date, filters.cost_center, adjustment=True)[0]		

		g_open = flt(gross_opening.debit) - flt(gross_opening.credit)
		g_addition = flt(gross.debit)
		g_adjustment = flt(gross.credit)
		g_total = g_open + g_addition - g_adjustment 
		d_open = -1 * (flt(dep_opening.debit) - flt(dep_opening.credit))
		dep_adjust = flt(acc_dep.debit)
		adj_adjust = flt(adj.credit)
		dep_addition = flt(acc_dep.credit) - flt(adj.credit)
		dep_add = flt(acc_dep.credit)
		d_total = d_open + dep_add  - flt(dep_adjust)

		row = [ 
			a.name,
			g_open,
			g_addition,
			g_adjustment,
			g_total,
			d_open,
			dep_addition,
			dep_adjust,
			adj_adjust,
			d_total,
			flt(g_total) - flt(d_total) 
		]	
		data.append(row)

def get_values(account, to_date, from_date, cost_center=None, opening=False, cwip=False, adjustment=False):
#	query = "select sum(debit) as debit, sum(credit) as credit from `tabGL Entry` where account = \'" + str(account) + "\' and docstatus = 1"
	if cwip:
		query = "select sum(debit) as debit, sum(credit) as credit from `tabGL Entry` where account in " + str(account) + " and docstatus = 1 "
	elif adjustment:
		query = "select sum(debit) as debit, sum(credit) as credit from `tabGL Entry` where account = \'" + str(account) + "\' and docstatus = 1 and is_depreciation_adjustment = 'Yes'"
	else:
		query = "select sum(debit) as debit, sum(credit) as credit from `tabGL Entry` where account = \'" + str(account) + "\' and docstatus = 1"
	if not opening:
		query += " and posting_date between \'" + str(from_date) + "\' and \'" + str(to_date) + "\'"
	else:
		query += " and posting_date < \'" + str(from_date) + "\'"
	if cost_center:
		query += " and cost_center = \'" + str(cost_center) + "\'"

	query += " and voucher_type not in ('Period Closing Voucher', 'Asset Movement', 'Bulk Asset Transfer')"
	#query += " and voucher_type not in ('Period Closing Voucher')"
	#if account == "Machinery & Equipment(10 Years) - CDCL":
	#	frappe.msgprint(" Query : {}".format(query))
	value = frappe.db.sql(query, as_dict=True)

	return value
