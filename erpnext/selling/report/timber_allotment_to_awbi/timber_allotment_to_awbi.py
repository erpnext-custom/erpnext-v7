# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_child_cost_centers


def execute(filters=None):
        columns = get_columns()
        data = get_data(filters)
        return columns, data


def get_data(filters):
        # query = """ select c.name, c.dzongkhag, c.location, c.customer_group, c.mobile_no, so.allotment_date, soi.qty from `tabCustomer` c inner join `tabSales Order` so  on c.name= so.customer inner join  `tabSales Order Item` soi  on so.name = soi.parent where  c.customer_group = 'AWBI' and so.docstatus = 1 """
        query = """select c.name, c.dzongkhag, c.location, c.customer_group, c.mobile_no, so.allotment_date,
soi.qty  from `tabCustomer` c, `tabSales Order` so, `tabSales Order Item` soi
where c.name = so.customer  and so.docstatus = 1 and soi.parent = so.name"""
        # if filters.branch:
        #         query += " and so.branch = '{0}'".format(filters.branch)
        if not filters.cost_center:
		return ""

	if not filters.branch:	
		all_ccs = get_child_cost_centers(filters.cost_center)
		# query += " and so.branch in {0}".format(tuple(all_ccs))
                query += " and so.branch in (select b.name from `tabCost Center` cc, `tabBranch` b where b.cost_center = cc.name and cc.name in {0})".format(tuple(all_ccs))

	else:
		branch = str(filters.get("branch"))
		branch = branch.replace(' - NRDCL','')
		query += " and so.branch = \'"+branch+"\'"
        # if filters.from_date and filters.to_date:
        #         query += " and so.allotment_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
        if filters.customer: 
                query += " and c.customer_name = '{0}'".format(filters.get("customer"))
        frappe.msgprint(query)
        return frappe.db.sql(query)
        # frappe.msgprint(str(data))
        # return data

def get_columns():
        return [
                ("Name of Firm") + ":Link/Customer:190",
                ("Dzongkha") + ":Data:120",
                ("Location") + ":Data:120",
                ("Type Of Industry") + ":Data:120",
                ("Contact No.")+ ":Data:100",
                ("Date of Allotment") + ":Date:120",
                ("Total(Cft)") + ":Float:120",
        ] 


