# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	validate_filters(filters);
	columns = get_columns();
	queries = construct_query(filters);
	data = get_data(queries, filters);

	return columns, data

def get_data(query, filters=None):
	data = []
	datas = frappe.db.sql(query, (filters.from_date, filters.to_date), as_dict=True);
	for d in datas:
		row = [d.item_code, d.item_name, d.qty, d.custodian, d.cost_center, d.issued_date, d.amount]
		data.append(row);
	return data

def construct_query(filters=None):
	query = """select id.item_code, id.item_name, id.qty, (select c.cost_center from tabEmployee as c where c.name = id.issued_to) as cost_center,
	(select e.employee_name from tabEmployee as e where e.name = id.issued_to) as custodian, id.issued_date, id.amount 
	from `tabAsset Issue Details` as id where id.docstatus = 1 and id.issued_date between %s and %s
	order by id.issued_date asc
	"""
	return query;

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


def get_columns():
	return [
		{
		  "fieldname": "item_code",
		  "label": "Material Code",
		  "fieldtype": "Link",
		  "options": "Item",
		  "width": 200
		},
		{
		  "fieldname": "item_name",
		  "label": "Material Name",
		  "fieldtype": "Data",
		  "width": 150
		},
		{
		  "fieldname": "qty",
		  "label": "Quantity",
		  "fieldtype": "Data",
		  "width": 100
		},
		{
		  "fieldname": "issued_to",
		  "label": "Custodian",
		  "fieldtype": "Link",
		  "options": "Employee",
		  "width": 130
		},
		{
		  "fieldname": "cost_center",
		  "label": "Cost Center",
	      	  "fieldtype": "Link",
	          "options": "Cost Center",
		  "width": 170
		  },
		{
		  "fieldname": "issued_date",
		  "label": "Issued Date",
		  "fieldtype": "Date",
		  "width": 100
		},
		{
		  "fieldname": "amount",
		  "label": "Gross Amount",
		  "fieldtype": "Currency",
		  "width": 200
		}
	]
