
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
		row = [d.branch, d.pol_type, d.uom, d.opening, d.received, d.issued, flt(d.opening) + flt(d.received) - flt(d.issued)]
		data.append(row);
	return data

def construct_query(filters=None):
		if not filters.branch:
			filters.branch = '%'

		query = """
			select branch, pol_type, uom,
				SUM(opening) opening,
				SUM(received) received,
				SUM(issued) issued
			FROM (
			select p.branch, p.date AS dates, p.pol_type, pt.uom,
				CASE
					WHEN p.date < '%(from_date)s' THEN p.qty
					ELSE 0
				END AS opening,
				CASE
					WHEN p.date >= '%(from_date)s' THEN p.qty
					ELSE 0
				END AS received,
				0 issued
			FROM   `tabPOL` p, `tabPOL Type` pt
			WHERE  pt.name = p.pol_type

			AND    p.date <= '%(to_date)s'
			UNION ALL
			select pc.branch, pc.date AS dates, pc.pol_type, pt.uom,
				CASE
					WHEN pc.date < '%(from_date)s' THEN -1*pc.qty
					ELSE 0
				END AS opening,
				0 received,
				CASE
					WHEN pc.date >= '%(from_date)s' THEN pc.qty
					ELSE 0
				END AS received
			FROM   `tabConsumed POL` pc, `tabPOL Type` pt
			WHERE  pt.name = pc.pol_type

			AND    pc.date <= '%(to_date)s'
			) AS X
			where branch like '%(branch)s'
			GROUP BY branch, pol_type, uom
			""" % {'from_date': str(filters.from_date), 'to_date': str(filters.to_date), 'branch': str(filters.branch)}
		#frappe.msgprint(query)
		return query;

def get_columns():
	return [
		("Branch") + ":Data:120",
		("POL Type") + ":Data:120",
		("UOM") + ":Data:90",
		("Opening Qty") +":Data:120",
		 ("Recieved") + ":Data:120",
		("Issued") + ":Data:120",
		("Balance") + ":Data:120"
	]
