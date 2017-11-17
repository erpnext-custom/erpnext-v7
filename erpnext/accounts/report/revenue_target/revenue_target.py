# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import (flt, getdate, get_first_day, get_last_day,
	add_months, add_days, formatdate)
                          
def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	
	return columns, data

def get_data(filters):
        data = []
        tot_target_amount   = 0.0
        tot_achieved_amount = 0.0
        tot_balance_amount  = 0.0
                
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
                """.format(filters.get("fiscal_year")), as_dict=1)

        for t in tl:
                achieved_amount     = 0.0
                balance_amount      = 0.0
                
                a = frappe.db.sql("""
                                select
                                        sum(ifnull(jea.credit,0)-ifnull(jea.debit,0)) as achieved_amount
                                from `tabJournal Entry Account` as jea, `tabJournal Entry` as je
                                where jea.account     = "{0}"
                                and   jea.cost_center = "{1}"
                                and   je.name         = jea.parent
                                and   je.posting_date between '{2}' and '{3}'
                                and   je.docstatus    = 1
                        """.format(t.account, t.cost_center, filters.get("from_date"), filters.get("to_date")), as_dict=1)[0]

                if a:
                        achieved_amount = flt(a.achieved_amount)

                t["achieved_amount"] = flt(achieved_amount)
                t["balance_amount"]  = flt(t.target_amount)-flt(achieved_amount)
                t["achievement"]     = (flt(achieved_amount)/flt(t.target_amount if t.target_amount else 1))*100

                tot_target_amount   += flt(t.target_amount)
                tot_achieved_amount += flt(achieved_amount)
                
                data.append(t)

        data.append({
                "account": "TOTAL",
                "target_amount": flt(tot_target_amount),
                "achieved_amount": flt(tot_achieved_amount),
                "balance_amount": flt(tot_target_amount)-flt(tot_achieved_amount),
                "achievement": (flt(tot_achieved_amount)/flt(tot_target_amount if tot_target_amount else 1))*100
        })        

        return data

def get_columns():
        return [
                {
                        "fieldname": "cost_center",
                        "label": _("Cost Center"),
                        "fieldtype": "Link",
                        "options": "Cost Center",
                        "width": 250
                },
                {
                        "fieldname": "account",
                        "label": _("Account"),
                        "fieldtype": "Link",
                        "options": "Account",
                        "width": 250
                },
                {
                        "fieldname": "account_code",
                        "label": _("Account Code"),
                        "fieldtype": "Data",
                        "width": 80
                },
                {
                        "fieldname": "target_amount",
                        "label": _("Target Amount"),
                        "fieldtype": "Currency",
                        "width": 130
                },
                {
                        "fieldname": "achieved_amount",
                        "label": _("Achieved Amount"),
                        "fieldtype": "Currency",
                        "width": 130
                },
                {
                        "fieldname": "balance_amount",
                        "label": _("Balance Amount"),
                        "fieldtype": "Currency",
                        "width": 130
                },
                {
                        "fieldname": "achievement",
                        "label": _("Achievement"),
                        "fieldtype": "Percent",
                        "width": 100
                },
        ]
