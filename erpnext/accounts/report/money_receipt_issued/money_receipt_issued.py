# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
        columns =get_columns()
        data =get_data(filters)
        return columns, data

def get_columns():
        return [
                ("Doctype") + " :Data: 100",
                ("Document #") + " :Data:150",
                ("Money Receipt No.") + ":data:120",
                ("MR Date") + ":date:120",
                ("MR Amount") + ":Currency:100",
                ("Cost Center")+":data:200",
        ]

def get_data(filters):
	query = """
                select 'Project Payment' as doctype, name as docname, money_receipt_no, posting_date, total_amount, cost_center 
                from `tabProject Payment`
                where docstatus = 1 and payment_type = 'Receive' and  posting_date between '{from_date}' and '{to_date}'
                {cond1} 
                union
                select 'Payment Entry' as doctype, name as docname, money_receipt_no, posting_date, received_amount, pl_cost_center 
                from `tabPayment Entry`
                where docstatus = 1 and payment_type = 'Receive' and posting_date between '{from_date}' and '{to_date}'
                {cond2}          
                union
                select 'Mechanical Payment' as doctype, name as docname, money_receipt_no, posting_date, net_amount, cost_center 
                from `tabMechanical Payment`  
                where docstatus = 1 and posting_date between '{from_date}' and '{to_date}'
                {cond1}
                order by posting_date
        """.format(
                from_date = filters.get("from_date"),
                to_date = filters.get("to_date"),
                cond1 = " and cost_center = '{0}'".format(filters.get("cost_center")) if filters.get("cost_center") else "",
                cond2 = " and pl_cost_center = '{0}'".format(filters.get("cost_center")) if filters.get("cost_center") else ""
        )

	return frappe.db.sql(query)
