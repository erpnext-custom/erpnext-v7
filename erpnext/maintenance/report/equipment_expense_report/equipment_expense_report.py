# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint

def execute(filters=None):
	columns = get_columns(filters)
	querry = construct_querry(filters)
	data = get_data(filters)
	return columns, querry, data

#def get_data(filters):
        #values = []
def get_data(filters=None):
	data = []
	#datas = frappe.db.sql(query, as_dict=True);
	for d in values:
		row = [d.eq.name, d.eq.equipment_number, d.eq.equipment_type, d.vl.consumption, d.jc.goods_amount, d.jc.services_amount, d.ins.insu, d.tc.travel_claim,d.lea.e_amount]
		data.append(row);
	return data


def construct_querry(filters):
	values = []
	equipments = frappe.db.sql("""
                                select name, equipment_number, equipment_type
                                from `tabEquipment`
                        """, as_dict=1)

    	for eq in equipments:
                # `tabVehicle Logbook`
        	vl = frappe.db.sql("""
                            select sum(ifnull(consumption,0)) as consumption
                            from `tabVehicle Logbook`
                            where equipment = '{0}'
                            and docstatus = 1
                    """.format(eq.name), as_dict=1)[0]

                # `tabPOL`
            	pol = frappe.db.sql("""
                            select avg(rate) as rate
                            from `tabPOL`
                            where equipment = '{0}'
                            and docstatus = 1
                    """.format(eq.name), as_dict=1)[0]

                # `tabJob Card`
                # owned_by pending
            	jc = frappe.db.sql("""
                            select sum(ifnull(goods_amount,0)) as goods_amount,
                            sum(ifnull(services_amount,0)) as services_amount
                            from `tabJob Card`
                            where equipment = '{0}'
                            and docstatus = 1
                    """.format(eq.name), as_dict=1)[0]
				#Insurance

		ins = frappe.db.sql("""
			 select sum(ifnull(id.insured_amount,0)) as insu  from `tabInsurance Details` id,
			`tabInsurance and Registration` ir where id.parent = ir.name and ir.equipment = '{0}'
			and ir.docstatus = 1
			 """.format(eq.name), as_dict=1)
		#frappe.msgprint(ins)		#Total Travel Claim

		#frappe.msgprint(values)
	c_operator = frappe.db.sql("""
			select e.current_operator from `tabEquipment` e
			where e.name = '{0}' and e.docstatus = 1 """.format(eq.name), as_dict=1)
	#frappe.msgprint(c_operator)
	for co in c_operator:
		tc = frappe.db.sql("""
				select sum(ifnull(tc.total_claim_amount,0)) as travel_claim
				from `tabTravel Claim` tc where tc.employee = '{0}'
				and tc.docstatus = 1
			""".format(co.current_operator), as_dict=1)

			#Leave Encashment Aomunt
		lea = frappe.db.sql("""
				select sum(ifnull(le.encashment_amount,0)) as e_amount from `tabLeave Encashment` le
				where and le.employee = '{0}'
				and le.docstatus = 1
			""".format(co.current_operator), as_dict=1)

                	# `tabSalary Slip`
        	ss = frappe.db.sql("""
	                     select sum(ifnull(gross_pay,0)) as gross_pay
	                     from `tabSalary Slip` ss where ss.employee = '{0}'
	                     and ss.docstatus = 1
	               """.format(co.current_operator),  as_dict=1)

		#frappe.msgprint(co)
		'''values.append((eq.name,
				eq.equipment_number,
				eq.equipment_type,
				vl.consumption,
				jc.goods_amount,
				jc.services_amount))

    		vals.append((tc.travel_claim, lea.e_amount, ss.gross_pay))
#        frappe.msgprint(_("{0}").format(tuple(lea)))
	v = values+vals'''
    	values.append((eq.name,eq.equipment_number,eq.equipment_type,vl.consumption,jc.goods_amount,jc.services_amount))
 	frappe.msgprint(values)
    	return values
#       return tuple()

def get_columns(filters):
	cols = [
                ("ID") + ":Link/Equipment:120",
		("Registration No") + ":Data:120",
		("Equipment Type") + ":Data:120",
                ("HSD Consumption") + ":Float:120",
                ("Insurance") + ":Float:120",
                ("Goods Amount") + ":Float:120",
                ("Services Amount") + ":Float:120",
		("Gross Pay") + ":Float:120",
		("Leave Encashment") + ":Currency:120",
		("Travel Claim") + ":Currency:120",
		("Total Expense") + ":Currency:120"
	]
	return cols
