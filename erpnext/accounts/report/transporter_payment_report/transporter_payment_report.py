# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = getcolumns()
	data = getdata(filters)

	return columns, data

def getdata(filters=None):
	
	query = """select p.name as name, p.branch as branch, p.cost_center as cost_center, p.posting_date as posting_date, p.owner,
		i.delivery_note as delivery_note, i.amount as amount, p.cheque_no as cheque_no, p.cheque_date  as cheque_date 
		from  `tabMechanical Payment` p inner join `tabTransporter Payment Item` i 
		on p.name = i.parent where p.docstatus = 1 and p.payment_for='Transporter Payment' """

	if filters.from_date and filters.to_date:
		query += " and p.posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"

	if filters.branch:
		query +=" and p.branch = \'" + str(filters.branch) + "\'"

	if filters.cost_center:
		query +=" and p.cost_center = \'" + str(filters.cost_center) + "\'"

	query += "order by p.posting_date"
	data = frappe.db.sql(query)

	return data

def getcolumns():
	return [
		("Transporter Payment") + ":Link/Mechanical Payment:150",
		("Branch") + ":Link/Branch:160",
		("Cost Center") + ":Link/Cost Center:160",
		("Posting Date") + ":Date:100",
		("Created By") + ":Link/User:150",
		("Delivery Note") + ":Link/Delivery Note:120",
		("Amount") + ":Currency:100",
		("Cheque No") + ":Data:120",
		("Cheque Date") + ":Date:100"
	     ]

