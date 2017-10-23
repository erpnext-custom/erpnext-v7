# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_columns():
	return [
                ("Project") + ":Link/Project:180",
                ("Posting Date") + ":Date:80",
                ("Cost Center") + ":Data:120",
                ("Party") + ":Data:120",
                ("Payment Type")+ ":Data:100",
		("Status") + ":Data:120",
                ("Paid Amount") + ":Currency:120",
                ("Total Amount") + ":Currency:120",
                ("TDS Amount") + ":Currency:120",
                
        ]

def get_data(filters):
        query =  """
                        select 
                                p.project_name,
                                pp.posting_date, 
                                pp.cost_center, 
                                pp.party, 
                                pp.payment_type, 
				pp.status,
                                pp.paid_amount, 
                                pp.total_amount,
                                pp.tds_amount 
                               
                        from `tabProject Payment` as pp, `tabProject` as p 
                        where pp.docstatus =1
                        and   p.name = pp.project
        """
        if filters.get("project"):
                query += ' and project = "{0}"'.format(str(filters.project))


	if filters.get("from_date") and filters.get("to_date"):
                query += " and posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

        elif filters.get("from_date") and not filters.get("to_date"):
                query += " and posting_date >= \'" + str(filters.from_date) + "\'"
        elif not filters.get("from_date") and filters.get("to_date"):
                query += " and posting_date <= \'" + str(filters.to_date) + "\'"

        query += " order by posting_date desc"
        return frappe.db.sql(query)

