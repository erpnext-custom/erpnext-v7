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
from frappe.utils import flt, cint, now, getdate
from frappe.utils.data import get_first_day, get_last_day, add_years, date_diff, today, get_first_day, get_last_day


def post_depreciation_entries(asset=None):
	for asset in get_depreciable_assets(asset):
		make_depreciation_entry(asset)
		frappe.db.commit()

def get_depreciable_assets(asset):
	cond = " and a.name = '{}'".format(asset) if asset else ""
	return frappe.db.sql_list("""select distinct a.name
		from `tabAsset` a, tmp_missingje_nov2020 t, `tabDepreciation Schedule` ds
		where a.name = t.name
		AND ds.parent = a.name
		AND ds.schedule_date = '2021-01-01'
		AND NOT EXISTS(SELECT 1
			FROM `tabJournal Entry` je
			WHERE je.name = ds.journal_entry)
		{}
	""".format(cond))

@frappe.whitelist()
def make_depreciation_entry(asset_name, date=None):
	print('Posting entries for Asset : {}'.format(asset_name))
	frappe.has_permission('Journal Entry', throw=True)
	
	if not date:
		date = today()

	asset = frappe.get_doc("Asset", asset_name)
	
	#if asset.disable_depreciation:
	#	frappe.throw("Depreciation disabled for this asset")


	fixed_asset_account, accumulated_depreciation_account, depreciation_expense_account = \
		get_depreciation_accounts(asset)

	#depreciation_cost_center = frappe.db.get_value("Company", asset.company, "depreciation_cost_center")
	depreciation_cost_center = asset.cost_center
	
	value_after_dep = 0
	for d in asset.get("schedules"):
		if str(d.schedule_date) == '2021-01-01':
			print('{}'.format(d.schedule_date))
			je = frappe.new_doc("Journal Entry")
			je.voucher_type = "Depreciation Entry"
			je.posting_date = d.schedule_date
			je.company = asset.company
			je.branch = asset.branch
			je.remark = "Depreciation Entry against {0} worth {1}".format(asset_name, d.depreciation_amount)

			je.append("accounts", {
				"account": accumulated_depreciation_account,
				"credit_in_account_currency": d.depreciation_amount,
				"reference_type": "Asset",
				"reference_name": asset.name,
				"cost_center": depreciation_cost_center
			})

			je.append("accounts", {
				"account": depreciation_expense_account,
				"debit_in_account_currency": d.depreciation_amount,
				"reference_type": "Asset",
				"reference_name": asset.name,
				"cost_center": depreciation_cost_center
			})

			je.flags.ignore_permissions = True
			je.submit()

			d.db_set("journal_entry", je.name)
			value_after_dep = flt(asset.gross_purchase_amount) - flt(d.accumulated_depreciation_amount) - flt(asset.residual_value)

	#asset.db_set("value_after_depreciation", value_after_dep)
	#asset.set_status()

	return asset

def get_depreciation_accounts(asset):
	fixed_asset_account = accumulated_depreciation_account = depreciation_expense_account = None
	
	accounts = frappe.db.get_value("Asset Category Account",
		filters={'parent': asset.asset_category, 'company_name': asset.company},
		fieldname = ['fixed_asset_account', 'accumulated_depreciation_account',
			'depreciation_expense_account'], as_dict=1)

	if accounts:	
		fixed_asset_account = accounts.fixed_asset_account
		accumulated_depreciation_account = accounts.accumulated_depreciation_account
		depreciation_expense_account = accounts.depreciation_expense_account
		
	if not accumulated_depreciation_account or not depreciation_expense_account:
		accounts = frappe.db.get_value("Company", asset.company,
			["accumulated_depreciation_account", "depreciation_expense_account"])
		
		if not accumulated_depreciation_account:
			accumulated_depreciation_account = accounts[0]
		if not depreciation_expense_account:
			depreciation_expense_account = accounts[1]

	if not fixed_asset_account or not accumulated_depreciation_account or not depreciation_expense_account:
		frappe.throw(_("Please set Depreciation related Accounts in Asset Category {0} or Company {1}")
			.format(asset.asset_category, asset.company))

	return fixed_asset_account, accumulated_depreciation_account, depreciation_expense_account
