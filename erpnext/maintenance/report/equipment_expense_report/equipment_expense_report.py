# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	columns = get_columns()
	query = construct_query(filters)
	data = get_data(query, filters = None)

	return columns,data
def get_data(query, filters=None):
	data = []
	datas = frappe.db.sql(query, as_dict=True);
	for d in datas:
		row = [d.r, d.ty, d.na, d.cu, round(d.gds,2), round(d.svc,2),flt(d.drawn)*flt(d.rate), d.gs, d.ta, d.le, d.de,
		flt(d.gds)+flt(d.svc)+flt(d.drawn)+flt(d.gs)+flt(d.ta)+flt(d.le)+flt(d.de)]
		data.append(row);
	return data


def construct_query(filters):

	query = """select jc.equipment_number r, jc.equipment_type ty, sum(jc.goods_amount) gds, sum(jc.services_amount) svc, jc.name na, jc.customer cu,
	sum(ss.leave_encashment_amount) as le, sum(ss.gross_pay) as gs,
	(select sum(a.consumption) from `tabVehicle Logbook` a ,`tabEquipment` eq
	where  a.equipment_number = eq.equipment_number and a.from_date between %(from_date)s and %(to_date)s
	and a.to_date between %(from_date)s and %(to_date)s and a.docstatus = 1) as consumed,
	(select avg(pol.rate) from `tabPOL` pol, `tabEquipment` r where pol.equipment_number = r.equipment_number
	and pol.date between '%(from_date)s' and '%(to_date)s'   and pol.docstatus = 1) as rate,
	(select sum(((st.deputation)/100)*st.net_pay) from `tabSalary Structure` st where st.employee in (select q.current_operator from `tabEquipment` q where q.equipment_number = jc.equipment_number)
	and st.from_date between %(from_date)s and %(to_date)s and st.to_date between %(from_date)s and %(to_date)s) de,
	(select sum(tc.total_claim_amount) from `tabTravel Claim` tc , `tabEquipment` z where tc.employee = z.current_operator
	and tc.posting_date between %(from_date)s and %(to_date)s) ta
	from  `tabSalary Slip` ss, `tabJob Card` jc
	where jc.equipment_number  in (select k.equipment_number from `tabEquipment` k where k.current_operator = ss.employee)"""  %{"from_date": str(filters.from_date), "to_date": str(filters.to_date),"branch": str(filters.branch)}

	if filters.get("branch"):
		query += " and jc.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		 query += " and jc.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	query += " group by jc.equipment_number "
	frappe.msgprint(query)
	return query


def get_columns():
	cols = [
		("Registration No") + ":data:120",
		("Equipment Type.") + ":data:120",
		("Job Card")+":Link/Job Card:120",
		("Customer")+":data:120",
		("Goods Amount(Nu.)")+":currency:100",
		("Service Amount(Nu.)")+":currency:100",
		("HSD Amount(Nu.)")+":currency:100",
		("Gross Salary(Nu.)")+":currency:100",
		("Travel Claim(Nu.)")+":currency:100",
		("Leave Encashment(Nu.)")+":currency:120",
		("Deputation Allowance(Nu.)")+":currency:100",
		("Total Expense(Nu.)")+":currency:100",

	]
	return cols
