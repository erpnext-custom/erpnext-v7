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
	data1 = []
	query = """
		select 
			name,
			branch, 
			(select cost_center from `tabBranch` where name = branch limit 1), 
			posting_date, equipment, registration_no, 
			total_trip, gross_amount, pol_amount, other_deductions, amount_payable, cheque_no, cheque_date
		from `tabTransporter Payment` 
		where docstatus =1
	"""

	if filters.branch:
		query += " and branch = '{0}'".format(filters.get("branch"))
	if filters.get("from_date") and filters.get("to_date"):
		query += " and ((from_date between '{0}' and '{1}') or (to_date between '{0}' and '{1}'))".format(filters.get("from_date"), filters.get("to_date"))

	for d in frappe.db.sql(query, as_dict =1):
		cc = frappe.get_doc("Branch", d.branch).cost_center
		eq = frappe.db.get_values("Equipment", {"name": d.equipment, "is_disabled": 0}, ["equipment_type", "owner_name", "bank_name", \
					"account_number","bank_full_name","bank_branch", "ifs_code"], as_dict=True)
		if eq:
			equipment_type = eq[0].equipment_type 
			owner_name = eq[0].owner_name
			bank_name = eq[0].bank_name
			bank_full_name = eq[0].bank_full_name
			account_number = eq[0].account_number
			ifs_code = eq[0].ifs_code
			bank_branch = eq[0].bank_branch
			if filters.get("equipment_type") and equipment_type == filters.get("equipment_type"):
				row = [d.name,d.branch, cc, d.posting_date, d.equipment, d.registration_no, equipment_type, d.total_trip, d.gross_amount, \
				d.pol_amount, d.other_deductions, d.amount_payable, d.cheque_no, d.cheque_date, owner_name, bank_name, bank_full_name, bank_branch, account_number, \
				ifs_code]
				data.append(row)
			else:
				row = [d.name,d.branch, cc, d.posting_date, d.equipment, d.registration_no, equipment_type, d.total_trip, d.gross_amount, \
				d.pol_amount, d.other_deductions, d.amount_payable, d.cheque_no, d.cheque_date, owner_name, bank_name,bank_full_name, bank_branch, account_number, \
				ifs_code]
				data1.append(row)
	if filters.get("equipment_type"):
		return data
	else:
		return data1

def get_columns():
	return [
		_("Transporter Number") + ":Link/Transporter Payment:100",
		_("Branch") + ":Link/Branch:170",
		_("Cost Center") + ":Link/Cost Center:170",
		_("Posting Date") + ":Date:100",
		_("Equipment") + ":Link/Equipment:100",
		_("Registration No") + "::100",
		_("Equipment Type") + "::130",
		_("Total Trips") + "::60",
		_("Gross Amount") + ":Currency:100",
		_("POL Amount") + ":Currency:100",
		_("Other Deductions") + ":Currency:100",
		_("Amount Payable") + ":Currency:100",
		_("Cheque No") + "::80",
		_("Cheque Date") + ":Date:100",
		_("Equipment Owner") + "::100",
		_("Bank Name") + ":Link/Financial Institution:80",
		_("Bank Full Name") + "::150",
		_("Bank Branch") + ":Data:80",
		_("Account Number") + "::100",
		_("IFS Code") + "::100",


]

