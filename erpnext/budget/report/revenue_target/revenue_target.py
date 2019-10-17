# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import collections
from frappe import _
from frappe.utils import (flt, getdate, get_first_day, get_last_day,
	add_months, add_days, formatdate)
                          
def execute(filters=None):
	data = get_data(filters)
	columns = get_columns(filters)
	
	return columns, data

def get_conditions(filters):
	conditions = ""
	if filters.get("cost_center"):
		conditions =  "and cost_center = '{0}'".format(filters.get("cost_center"))

	return conditions
                
def get_data(filters):
        data = []
	data = get_records(filters)
	        
        return data

def get_columns(filters):
        columns = []
        if filters.get("groupby") == 'Group by Cost Center':
                columns.extend([{
                        "fieldname": "cost_center",
                        "label": _("Cost Center"),
                        "fieldtype": "Link",
                        "options": "Cost Center",
                        "width": 250
                }])
        elif filters.get("groupby") == 'Group by Account':
                columns.extend([{
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
                }])
        else:
                columns.extend([{
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
                }])
                
        columns.extend([
                {
                        "fieldname": "target_amount",
                        "label": _("Initial Target"),
                        "fieldtype": "Currency",
                        "width": 130
                },
                {
                        "fieldname": "adjustment_amount",
                        "label": _("Adjustments"),
                        "fieldtype": "Currency",
                        "width": 130
                },
                {
                        "fieldname": "net_target_amount",
                        "label": _("Final Target"),
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
        ])
        return columns

def get_records(filters):
        temp_list             = {}
        data_list             = []
        tot_target_amount     = 0.0
        tot_adjustment_amount = 0.0
        tot_net_target_amount = 0.0
        tot_achieved_amount   = 0.0

        cond      = get_conditions(filters)
        
        tl = frappe.db.sql("""
                        select
                                x.cost_center,
                                x.account,
                                x.account_code,
                                x.target_amount,
                                x.adjustment_amount,
                                x.net_target_amount,
                                (
                                select
                                        sum(ifnull(gl.credit,0)-ifnull(gl.debit,0))
                                from `tabGL Entry` as gl
                                where gl.docstatus = 1
                                and gl.posting_date between '{2}' and '{3}'
                                and gl.cost_center = x.cost_center
                                and gl.account = x.account
                                ) as achieved_amount
                        from
                        (
                        select
                                rtc.cost_center,
                                rtc.account,
                                rtc.account_code,
                                sum(ifnull(rtc.target_amount,0)) as target_amount,
                                sum(ifnull(rtc.adjustment_amount,0)) as adjustment_amount,
                               (sum(ifnull(rtc.target_amount,0)) + sum(ifnull(rtc.adjustment_amount,0))) as net_target_amount
 
                        from `tabRevenue Target Account` as rtc, `tabRevenue Target` as rt
                        where rt.fiscal_year = '{0}'
			{1}
                        and   rtc.parent     = rt.name
			and   rt.docstatus   = 1
                        group by rtc.cost_center, rtc.account, rtc.account_code
                        ) as x
                """.format(filters.get("fiscal_year"),cond,filters.get("from_date"),filters.get("to_date")), as_dict=1)

        if filters.get("groupby") == 'Group by Cost Center':
                for t in tl:
                        if temp_list.has_key(t.cost_center):
                                temp_list[t.cost_center]['target_amount']     += flt(t.target_amount)
                                temp_list[t.cost_center]['adjustment_amount'] += flt(t.adjustment_amount)
                                temp_list[t.cost_center]['net_target_amount'] += flt(t.net_target_amount)
                                temp_list[t.cost_center]['achieved_amount']   += flt(t.achieved_amount)
                        else:
                                temp_list[t.cost_center] = {'cost_center': t.cost_center, 'account': '', 'account_code': '','target_amount': flt(t.target_amount), 'adjustment_amount': flt(t.adjustment_amount), 'net_target_amount': flt(t.net_target_amount), 'achieved_amount': flt(t.achieved_amount)}
        elif filters.get("groupby") == 'Group by Account':
                for t in tl:
                        if temp_list.has_key(t.account):
                                temp_list[t.account]['target_amount']     += flt(t.target_amount)
                                temp_list[t.account]['adjustment_amount'] += flt(t.adjustment_amount)
                                temp_list[t.account]['net_target_amount'] += flt(t.net_target_amount)
                                temp_list[t.account]['achieved_amount']   += flt(t.achieved_amount)
                        else:
                                temp_list[t.account] = {'cost_center': '', 'account': t.account, 'account_code': t.account_code,'target_amount': flt(t.target_amount), 'adjustment_amount': flt(t.adjustment_amount), 'net_target_amount': flt(t.net_target_amount), 'achieved_amount': flt(t.achieved_amount)}
        else:
                for t in tl:
                        temp_list[str(t.cost_center)+"_"+str(t.account)] = t
                        

        for t in collections.OrderedDict(sorted(temp_list.items())):
                temp_list[t]['balance_amount'] = flt(temp_list[t]['net_target_amount']) - flt(temp_list[t]['achieved_amount'])
                temp_list[t]['achievement']    = (flt(temp_list[t]['achieved_amount'])/flt(temp_list[t]['net_target_amount'] if temp_list[t]['net_target_amount'] else 1))*100
                tot_target_amount             += flt(temp_list[t]['target_amount'])
                tot_adjustment_amount         += flt(temp_list[t]['adjustment_amount'])
                tot_net_target_amount         += flt(temp_list[t]['net_target_amount'])
                tot_achieved_amount           += flt(temp_list[t]['achieved_amount'])

                data_list.append(temp_list[t])
                
        if data_list:
                data_list.append({
                        "account": "TOTAL",
                        "target_amount": flt(tot_target_amount),
                        "adjustment_amount": flt(tot_adjustment_amount),
                        "net_target_amount": flt(tot_net_target_amount),
                        "achieved_amount": flt(tot_achieved_amount),
                        "balance_amount": flt(tot_net_target_amount)-flt(tot_achieved_amount),
                        "achievement": (flt(tot_achieved_amount)/flt(tot_net_target_amount if tot_net_target_amount else 1))*100
                })
        
        return data_list
