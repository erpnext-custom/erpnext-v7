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

def get_data(filters):
        values = []

        equipments = frappe.db.sql("""
                                select name, equipment_number, equipment_type
                                from `tabEquipment`
                        """, as_dict=1)
	frappe.msgprint("INSIDE")
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

		# Insurance
		ins = frappe.db.sql("""
						select id.insured_amount as insur from `tabInsurance Details` id,`tabInsurance and Registration` ir
						where id.parent = ir.name and ir.equipment = '{0}'
						and ir.docstatus = 1
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


		#Total Travel Claim
		c_operator = frappe.db.sql(	"""select e.current_operator from `tabEquipment` e
						where e.name = '{0}' and e.docstatus = 1 """.format(eq.name), as_dict=1)
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
						""".format(co.current_operator), as_dict=1)[0]

			# `tabSalary Slip`
			ss = frappe.db.sql("""
				       select sum(ifnull(gross_pay,0)) as gross_pay
				       from `tabSalary Slip` ss where ss.employee = '{0}'
				       and ss.docstatus = 1
					""".format(co.current_operator) as_dict=1)[0]


		values.append((eq.name,
			   eq.equipment_number,
			   eq.equipment_type,
			   vl.consumption,
			   pol.rate,
			   jc.goods_amount,
			   jc.services_amount,
			   ins.insur))

        #frappe.msgprint(_("{0}").format(tuple(values)))
	return tuple(values)

def get_columns(filters):
	cols = [
                ("ID") + ":Link/Equipment:120",
		("Registration No") + ":Data:120",
		("Equipment Type") + ":Data:120",
                ("Consumption") + ":Float:120",
                ("Rate") + ":Float:120",
                ("Goods Amount") + ":Float:120",
                ("Services Amount") + ":Float:120",
				("Insurance Amount") + ":Float:120"
	]
	return cols
