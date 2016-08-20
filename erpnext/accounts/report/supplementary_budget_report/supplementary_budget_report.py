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
	query = "select to_cc, to_acc, amount, posted_date as date from `tabSupplementary Details` where posted_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"

	if filters.to_cc:
		query+=" and to_cc = \'" + filters.to_cc  + "\'"

	if filters.to_acc:
		query+=" and to_account = \'" + filters.to_acc  + "\'"

	sup_data = frappe.db.sql(query, as_dict=True)

	data = []

	if sup_data:
		for a in sup_data:
			row = {
				"to_cc": a.to_cc,
				"to_acc": a.to_acc,
				"amount": a.amount,
				"date": a.date,
			}
			data.append(row)
	
	return data

def get_columns():
	return [
		{
			"fieldname": "date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "to_cc",
			"label": _("To Cost Center"),
			"fieldtype": "Link",
			"options":"Cost Center",
			"width": 200
		},
		{
			"fieldname": "to_acc",
			"label": _("To Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 230
		},
		{
			"fieldname": "amount",
			"label": _("Amount"),
			"fieldtype": "Currency",
			"width": 130
		}
	]

