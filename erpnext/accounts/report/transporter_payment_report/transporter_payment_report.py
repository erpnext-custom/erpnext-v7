# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_data(filters):
	data = []
	query = "select branch, (select cost_center from `tabBranch` where name = branch limit 1), posting_date, equipment, registration_no, \
		total_trip, gross_amount, pol_amount, other_deductions, amount_payable, cheque_no, cheque_date \
		from `tabTransporter Payment` where docstatus =1"
	if filters.branch:
		query += " and branch = '{0}'".format(filters.get("branch"))
	if filters.get("from_date") and filters.get("to_date"):
		query += " and ((from_date between '{0}' and '{1}') or (to_date between '{0}' and '{1}'))".format(filters.get("from_date"), filters.get("to_date"))

	for d in frappe.db.sql(query, as_dict =1):
		cc = frappe.get_doc("Branch", d.branch).cost_center
		row = [d.branch, cc, d.posting_date, d.equipment, d.registration_no, d.total_trip, d.gross_amount, d.pol_amount, d.other_deductions, \
				d.amount_payable, d.cheque_no, d.cheque_date]
		data.append(row)
	return data


def get_columns():
	return [
		_("Branch") + ":Link/Branch:170",
		_("Cost Center") + ":Link/Cost Center:170",
		_("Posting Date") + ":Date:100",
		_("Equipment") + "::100",
		_("Registration No") + "::100",
		_("Total Trips") + "::30",
		_("Gross Amount") + ":Currency:100",
		_("POL Amount") + ":Currency:100",
		_("Other Deductions") + ":Currency:100",
		_("Amount Payable") + ":Currency:100",
		_("Cheque No") + "::80",
		_("Cheque Date") + ":Date:100"
]

