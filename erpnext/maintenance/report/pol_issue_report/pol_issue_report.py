# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr


def execute(filters=None):
	columns = get_columns();
	queries = construct_query(filters);
	data = get_data(queries, filters);

	return columns, data

def get_data(query, filters=None):
	data = []
	datas = frappe.db.sql(query, as_dict=True);
	for d in datas:
		row = [d.pol_type, d.uom, d.received, d.issued, flt(d.received) - flt(d.issued)]
		data.append(row);
	return data

def construct_query(filters=None):
		query = "select p.branch, p.pol_type, (select uom from `tabPOL Type` pt where pt.name = p.pol_type) as uom, sum(p.qty) as received, (select sum(c.qty) from `tabConsumed POL` c where c.branch = \'" + str(filters.branch) + "\' and c.pol_type = p.pol_type and c.docstatus = 1 and c.date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\') as issued from `tabPOL` as p where p.branch = \'" + str(filters.branch) + "\' and p.docstatus = 1 and p.date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\' group by p.branch, p.pol_type "

		return query;

def get_columns():
	return [
		("POL Type") + ":Data:120",
		("UOM") + ":Data:90",
		 ("Recieved") + ":Data:120",
		("Issued") + ":Data:120",
		("Balance") + ":Data:120"
	]
