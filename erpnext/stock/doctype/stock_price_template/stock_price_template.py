# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
2.0		  SSK		                   07/08/2018         Code changed to take work with search fileds
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.desk.reportview import get_match_cond

class StockPriceTemplate(Document):
	pass

#select stock entry templates based on dates
@frappe.whitelist()
def get_template_list(doctype, txt, searchfield, start, page_len, filters): 
	if filters['naming_series']:
		'''
		res = frappe.db.sql("""
			SELECT 
				name, 
				template_name 
			FROM `tabStock Price Template` 
			WHERE '{0}'  BETWEEN from_date AND to_date 
			AND naming_series = '{1}' 
			AND docstatus = 1 
			AND purpose= '{2}'
			ORDER BY from_date desc, creation desc
		""".format(filters['posting_date'],filters['naming_series'],filters['purpose']))
		'''

                # ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
                # Following code commented and subsequent added by SHIV on 2018/08/07
                '''
		res = frappe.db.sql("""
			select
				name,
				concat('<b style="font-size: 115%;">',template_name,'</b>') template_name,
				concat('<b style="color:green;">','Nu.',format(rate_amount,2),'</b>') rate_amount,
				concat('(',date_format(from_date,'%d/%m/%Y'),' - ',date_format(to_date,'%d/%m/%Y'),')') date_range,
				concat(item_code,' : ',item_name) item_name
			from `tabStock Price Template`
			where name in (
				select max(name)
				from `tabStock Price Template`
				where '{0}' between from_date and ifnull(to_date,now())
				and naming_series = '{1}'
				and docstatus = 1
				and purpose = '{2}'
				group by item_code
			)
		""".format(filters['posting_date'],filters['naming_series'],filters['purpose']))
                '''

                res = frappe.db.sql("""
			select 
				name,
				template_name,
				rate_amount,
				from_date,
				to_date,
				item_code,
				item_name
			from `tabStock Price Template` 
			where %(posting_date)s between from_date and to_date 
			and naming_series = %(naming_series)s 
			and docstatus = 1 
			and is_disabled = 0 
			and purpose= %(purpose)s
			and (
                                {key} like %(txt)s
                                or
                                template_name like %(txt)s
                                or
                                item_code like %(txt)s
                        )
                        {mcond}
			group by item_code, naming_series, purpose
			order by
                                if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
                                if(locate(%(_txt)s, template_name), locate(%(_txt)s, template_name), 99999),
                                if(locate(%(_txt)s, item_code), locate(%(_txt)s, item_code), 99999),
                                idx desc,
                                creation desc
                        limit %(start)s, %(page_len)s
		""".format(**{
                                'key': searchfield,
                                'mcond': get_match_cond(doctype)
                }),
                {
			"txt": "%%%s%%" % txt,
			"_txt": txt.replace("%", ""),
			"start": start,
			"page_len": page_len,
                        "posting_date": filters['posting_date'],
                        "naming_series": filters['naming_series'],
                        "purpose": filters['purpose']
		})
                # +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++

		return res;
	

#Get item values from "Initial Stock Templates" during stock entry
@frappe.whitelist()
def get_initial_values(name):
	result = frappe.db.sql("SELECT a.item_code, a.item_name, a.uom, a.rate_currency, a.rate_amount, b.expense_account, b.selling_cost_center, b.stock_uom FROM `tabStock Price Template` AS a, tabItem AS b WHERE a.item_name = b.item_name AND a.name = \'" + str(name) + "\'", as_dict=True);
	return result;

#Get item rates
@frappe.whitelist()
def get_item_rate(tran_type, item_code, tran_date):
        if tran_type == 'Sales':
                table_name = 'tabStock Price Template Item'
        elif tran_type == 'COP':
                table_name = 'tabStock Price Template Buying'
        else:
                frappe.throw(_("Transaction should be eaither of COP or Sales."),title="Wrong Transaction")
                
        result = frappe.db.sql("""
                        select
                                a.item_code,
                                a.item_name,
                                a.uom,
                                a.rate_currency,
                                i.rate,
                                b.expense_account,
                                b.selling_cost_center,
                                b.stock_uom
                        from
                                `tabStock Price Template` as a,
                                `{0}` as i,
                                `tabItem` as b
                        where a.item_code = '{1}'
                        and b.name = a.item_code
                        and i.parent = a.name
                        and '{2}' between i.from_date and ifnull(i.to_date, now())
                        """.format(table_name, item_code, tran_date), as_dict=True)

        if result:
                if len(result) > 1:
                        frappe.throw(_("{0}: Multiple rates found for the given date.").format(item_code), title="Too Many Values Found")
                else:
                        return result
        else:
                frappe.throw(_("Please define '{0}' rate in Selling -> COP/Sales Price Template.").format(tran_type),title="No Data Found")
