# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	
	return columns, data

def get_data(filters):
        data = []
        
        tl = frappe.db.sql("""
                        select
                                rtc.cost_center,
                                rtc.account,
                                rtc.account_code,
                                sum(ifnull(rtc.target_amount,0)) as target_amount,
                                0 as achieved_amount
                        from `tabRevenue Target Account` as rtc, `tabRevenue Target` as rt
                        where rt.fiscal_year = "{0}"
                        and   rtc.parent     = rt.name
                        group by cost_center, account, account_code
                        order by cost_center, account, account_code
                """.format(filters.get(fiscal_year)), as_dict=1)

        for t in tl:
                achieved_amount = 0.0
                
                a = frappe.db.sql("""
                                select
                                        sum(ifnull(credit,0)-ifnull(debit,0)) as achieved_amount
                                from `tabJournal Entry Account` je, `tabAccount` a
                                where a.name = t.account
                                and   je.account     = "{0}"
                                and   je.cost_center = "{1}"
                                and   je.docstatus   = 1
                        """.format(t.account, t.cost_center), as_dict=1)[0]

                if a:
                        achieved_amount = flt(a.achieved_amount)

                t["achieved_amount"] = a
                data.append(t)

        return data

def get_columns():
        return [
                {
                        "fieldname": "cost_center",
                        "label": _("Cost Center"),
                        "fieldtype": "Link",
                        "options": "Cost Center",
                        "width": 300
                },
                {
                        "fieldname": "account",
                        "label": _("Account"),
                        "fieldtype": "Data",
                        "width": 300
                },
                {
                        "fieldname": "account_code",
                        "label": _("Account Code"),
                        "width": 100
                },
                {
                        "fieldname": "target_amount",
                        "label": _("Target Amount"),
                        "fieldtype": "Currency",
                        "width": 150
                },
                {
                        "fieldname": "achieved_amount",
                        "label": _("Achieved Amount"),
                        "fieldtype": "Currency",
                        "width": 100
                },
        ]
