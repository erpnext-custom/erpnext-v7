# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns();
	data = get_data(filters);

	return columns, data

def get_data(filters=None):
	data = []
	if filters.warehouse:
		query = "select m.item_code as m_code, m.item_name as m_name, m.uom as m_uom,  sum(m.qty) as m_qty, p.item_code as p_code, p.item_name as p_name, p.uom as p_uom, sum(p.qty) as p_qty from `tabProduction Product Item` p inner join `tabProduction Material Item` m on p.parent=m.parent and m.parent in (select name from `tabProduction` where branch=\'" + str(filters.branch) + "\' and posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\' and warehouse = \'" + str(filters.warehouse) + "\') group by m.item_code;"
	else:
		 query = "select m.item_code as m_code, m.item_name as m_name, m.uom as m_uom,  sum(m.qty) as m_qty, p.item_code as p_code, p.item_name as p_name, p.uom as p_uom, sum(p.qty) as p_qty from `tabProduction Product Item` p inner join `tabProduction Material Item` m on p.parent=m.parent and m.parent in (select name from `tabProduction` where branch=\'" + str(filters.branch) + "\' and posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\') group by m.item_code;"
	
	for r in frappe.db.sql(query, as_dict=True):
		recovery_percent = round((r.p_qty/r.m_qty) * 100, 2)
		#frappe.msgprint("m qty:\'" + str(r.m_qty) + "\' p qty:\'" + str(r.p_qty)+"\'")	
		row = [r.m_code, r.m_name, r.m_uom, r.m_qty, r.p_code, r.p_name, r.p_uom, r.p_qty, recovery_percent]
                data.append(row)
	return data;

def get_columns():
    return [
            ("Material Code") + ":Data:150",
            ("Material Name") + ":Data:150",
            ("Material UOM") + ":Data:80",
	    ("Material Qty") + ":Float:80",
            ("Product Code") + ":Data:100",
            ("Product Name") + ":Data:100",
            ("Product UOM") + ":Data:80",
            ("Product Qty") + ":Float:80",
            ("Recovery %") + ":Data:100",
    ]
