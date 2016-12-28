# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def validate_filters(filters):

	if not filters.fiscal_year:
		frappe.throw(_("Fiscal Year {0} is required").format(filters.fiscal_year))

	fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=True)
	if not fiscal_year:
		frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
	else:
		filters.year_start_date = getdate(fiscal_year.year_start_date)
		filters.year_end_date = getdate(fiscal_year.year_end_date)

	if not filters.from_date:
		filters.from_date = filters.year_start_date

	if not filters.to_date:
		filters.to_date = filters.year_end_date

	filters.from_date = getdate(filters.from_date)
	filters.to_date = getdate(filters.to_date)

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))

	if (filters.from_date < filters.year_start_date) or (filters.from_date > filters.year_end_date):
		frappe.msgprint(_("From Date should be within the Fiscal Year. Assuming From Date = {0}")\
			.format(formatdate(filters.year_start_date)))

		filters.from_date = filters.year_start_date

	if (filters.to_date < filters.year_start_date) or (filters.to_date > filters.year_end_date):
		frappe.msgprint(_("To Date should be within the Fiscal Year. Assuming To Date = {0}")\
			.format(formatdate(filters.year_end_date)))
		filters.to_date = filters.year_end_date

def get_data(filters):
	query = "select asset_quantity_, name, asset_name, asset_category, presystem_issue_date, (select employee_name from tabEmployee as emp where emp.name = ass.issued_to) as issued_to, cost_center, purchase_date, gross_purchase_amount, (select sum(depreciation_amount) from `tabDepreciation Schedule` as ds where ds.parent = ass.name and ds.schedule_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\') as depreciation_amount, (select sum(depreciation_income_tax) from `tabDepreciation Schedule` as ds where ds.parent = ass.name and ds.schedule_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\') as depreciation_income_tax from tabAsset as ass where docstatus = 1"

	if filters.cost_center:
		query+=" and ass.cost_center = \'" + filters.cost_center + "\'"

	if filters.asset_category:
		query+=" and ass.asset_category = \'" + filters.asset_category + "\'"

	asset_data = frappe.db.sql(query, as_dict=True)

	data = []

	if asset_data:
		for a in asset_data:
			net_useful_life = flt(a.gross_purchase_amount) - flt(a.depreciation_amount)
			net_income_tax = flt(a.gross_purchase_amount) - flt(a.depreciation_income_tax)
			row = {
				"asset_code": a.name,
				"asset_name": a.asset_name,
				"asset_category": a.asset_category,
				"issued_to": a.issued_to,
				"cost_center": a.cost_center,
				"date_of_issue": a.purchase_date,
				"qty": a.asset_quantity_,
				"amount": a.gross_purchase_amount,
				"dep_useful_life": a.depreciation_amount,
				"dep_income_tax": a.depreciation_income_tax,
				"net_useful_life": net_useful_life,
				"net_income_tax": net_income_tax,
				"presystem_issue_date": a.presystem_issue_date
			}
			data.append(row)
	
	return data

def get_columns():
	return [
		{
			"fieldname": "asset_code",
			"label": _("Asset Code"),
			"fieldtype": "Link",
			"options": "Asset",
			"width": 200
		},
		{
			"fieldname": "asset_name",
			"label": _("Asset Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "asset_category",
			"label": _("Asset Category"),
			"fieldtype": "Link",
			"options":"Asset Category",
			"width": 200
		},
		{
			"fieldname": "issued_to",
			"label": _("Issued To"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "cost_center",
			"label": _("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 130
		},
		{
			"fieldname": "presystem_issue_date",
			"label": _("Original Issue Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "date_of_issue",
			"label": _("Dep Start Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "qty",
			"label": _("Quantity"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "amount",
			"label": _("Amount"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "dep_useful_life",
			"label": _("Useful Life"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "dep_income_tax",
			"label": _("Income Tax"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "net_useful_life",
			"label": _("Net Useful Life"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "net_income_tax",
			"label": _("Net Income Tax"),
			"fieldtype": "Currency",
			"width": 120
		}
	]

