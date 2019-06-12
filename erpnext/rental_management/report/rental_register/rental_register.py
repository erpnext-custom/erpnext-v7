# For license information, please see license.txt
# Frappe Technologiss Pvt. Ltd. and contributors
	
from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_columns():
	return [
		("Branch") + ":Link/Branch:120",
		("CID No. ") + ":Link/Tanent Bill:120",
		("Tanent Name") + ":Data:120",
		("Ministry/Agency.") + ":Data:120",
		("Department") + ":Data:100",
		("Dzongkhag") +":Data:100",
		("Location")+":Data:100",
		("Town Category") +":Data:100",
		("Building Category") +":Data:100",
		("Classification") + ":Data:150",
		("Block No.") + ":Data:120",
                ("Flat No. ") + ":Data:120",
		("Fiscal Year") + ":Data:80",
		("Month") + " :Data:80",
                ("Rent Amount") + ":Currency:120",
                ("Penalty.")+ ":Currency:120",
                ("Total.") + ":Currency:120",
	
	]

def get_data(filters):
	status = "1=1"
	if filters.get("status") == "Draft":
		status = "docstatus = 0"
	if filters.get("status") == "Submitted":
		status = "docstatus = 1"

	query = """select branch, tenant,  tenant_name, ministry_agency, department, dzongkhag, location, town_category, building_category,'class', block_no, flat_no,fiscal_year, month,  rent_amount, 'penalty', rent_amount from `tabRental Bill` where {0}""".format(status)
	if filters.get("dzongkhag"):
		query += " and dzongkhag = \'" + str(filters.dzongkhag) + "\'"
	if filters.get("location"):
		query += " and location = \'" + str(filters.location) + "\' "
	if filters.get("town"):
		query += " and town_category = \'" + str(filters.town) + "\' "
	if filters.get("building_category"):
		query += " and building_category = \'" + str(filters.building_category) + "\' "
	if filters.get("month"):
		query += " and month = {0}".format(filters.get("month"))
	if filters.get("fiscal_year"):
		query += " and fiscal_year ={0}".format(filters.get("fiscal_year"))
	return frappe.db.sql (query)
