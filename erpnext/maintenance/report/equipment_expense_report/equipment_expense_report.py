# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

#def get_data(filters):
        #values = []
def get_data(filters=None):
	data = []
	equipments = frappe.db.sql("""
                                select name, equipment_number, equipment_type
                                from `tabEquipment`
                        """, as_dict=1)

    	for eq in equipments:
		#frappe.msgprint("{0}".format(eq))
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
			 select sum(ifnull(id.insured_amount,0)) as insurange  from `tabInsurance Details` id,
			`tabInsurance and Registration` ir where id.parent = ir.name and ir.equipment = '{0}'
			and ir.docstatus = 1
			 """.format(eq.name), as_dict=1)[0]


		#v1.append(	#frappe.msgprint(values)
		c_operator = frappe.db.sql("""
			select e.current_operator from `tabEquipment` e
			where e.name = '{0}' and e.docstatus = 1 """.format(eq.name), as_dict=1)

		tc = {"travel_claim": 0}
		lea = {"e_amount": 0}
		ss = {"gross_pay": 0}
		#frappe.msgprint(c_operator)
		for co in c_operator:
			frappe.msgprint("test")
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
			'''    		vals.append((tc.travel_claim, lea.e_amount, ss.gross_pay))
		#        frappe.msgprint(_("{0}").format(tuple(lea)))
			v = values+vals'''
		#frappe.msgprint(eq.name)
		#frappe.msgprint("{0}".format(tc))
		data.append((eq.name,eq.equipment_number,eq.equipment_type,flt(vl.consumption)*flt(pol.rate),flt(ins.insurance),flt(jc.goods_amount),flt(jc.services_amount), flt(tc["travel_claim"]),flt(lea["e_amount"]),flt(ss["gross_pay"])))
	#frappe.msgprint(str(data))
    	return tuple(data)
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
