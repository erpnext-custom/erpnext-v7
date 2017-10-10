# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, json
from frappe.utils import flt, cint
from frappe.utils import flt, cint,add_days, cstr, flt, getdate, nowdate, rounded, date_diff
def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_conditions(filters):
	branch = consumption_date = rate_date = jc_date = insurance_date = rev_date = tc_date = operator_date = le_date = ss_date= ""
	if filters.get("branch"):
		branch += str(filters.branch)
	if filters.get("from_date") and filters.get("to_date"):
		consumption_date = get_dates(filters, "vl", "from_date", "to_date")
		rate_date 	 = get_dates(filters, "pol", "date")
		jc_date 	 = get_dates(filters, "jc", "posting_date", "finish_date")
		insurance_date   = get_dates(filters, "ins", "insured_date")
		operator_date    = get_dates(filters, "op", "start_date", "end_date")
		tc_date		 = get_dates(filters, "tc", "posting_date")
		le_date		 = get_dates(filters, "le", "encashed_date")
		ss_date		 = get_dates(filters, "ss", "start_date", "ifnull(end_date,curdate())")
		rev_date	 = get_dates(filters, "revn", "ci.posting_date")
		bench_date       = get_dates(filters, "benchmark", "hi.from_date", "hi.to_date")

	return branch, consumption_date, rate_date, jc_date, insurance_date, rev_date, bench_date, operator_date, tc_date, le_date, ss_date

def get_dates(filters, module = "", from_date_column = "", to_date_column = ""):
	cond1 = ""
	cond2 = ""

	if from_date_column:
		cond1 = ("{0} between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'").format(from_date_column)

	if to_date_column:
		if module in ("op","ss", "benchmark"):
			cond2 = str(" or {0} between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'").format(to_date_column)
		else:
			cond2 = str("and {0} between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'").format(to_date_column)

	return "({0} {1})".format(cond1, cond2)

def get_data(filters):
	branch, consumption_date, rate_date, jc_date, insurance_date, rev_date, bench_date, operator_date, tc_date, le_date, ss_date =  get_conditions(filters)
	data = []
	branch_cond = " where branch = '{0}'".format(branch) if branch else ""

	equipments = frappe.db.sql("""
                                select name, branch, equipment_number, equipment_type, equipment_model
                                from `tabEquipment`
				{0}
				order by branch, name
                        """.format(branch_cond), as_dict=1)
	#frappe.msgprint("{0}".format(equipments))
    	for eq in equipments:
		#frappe.msgprint("{0}".format(eq.equipment_type))
                # `tabVehicle Logbook`
        	vl = frappe.db.sql("""
                        	select sum(ifnull(consumption,0)) as consumption
                        	from `tabVehicle Logbook`
                        	where equipment = '{0}'
                        	and   docstatus = 1
				and   {1}
                    """.format(eq.name,consumption_date), as_dict=1)[0]

                # `tabPOL`
            	pol = frappe.db.sql("""
                            	select avg(rate) as rate
                            	from `tabPOL`
                        	where equipment = '{0}'
                        	and   docstatus = 1
				and   {1}
                    """.format(eq.name, rate_date), as_dict=1)[0]

                # `tabJob Card`
                # owned_by pending
            	jc = frappe.db.sql("""
                            	select sum(ifnull(goods_amount,0)) as goods_amount,
                            		sum(ifnull(services_amount,0)) as services_amount
                            	from `tabJob Card`
                            	where equipment = '{0}'
                            	and   docstatus = 1
				and   {1}
                    """.format(eq.name,jc_date), as_dict=1)[0]
	
		#Insurance
		ins = frappe.db.sql("""
			 	select sum(ifnull(id.insured_amount,0)) as insurance
				from `tabInsurance Details` id,	`tabInsurance and Registration` ir
				where id.parent = ir.name and ir.equipment = '{0}'
				and   ir.docstatus = 1
				and   {1}
			 """.format(eq.name, insurance_date), as_dict=1)[0]
	
		revn = frappe.db.sql("""
			 	 select sum(ifnull(id.total_amount, 0)) as rev from `tabHire Invoice Details` id, `tabHire Charge Invoice` ci
			 	 where ci.name = id.parent
			 	 and id.equipment = '{0}'
			 	 and {1}
			 """.format(eq.name, rev_date), as_dict=1)[0]

		 #benchmar
                benchmark  = frappe.db.sql("""
                               select ifnull(group_concat(round(hi.rate_fuel) separator '/'),0) as rat, ifnull(group_concat(hi.perf_bench separator '/'),0) bn, 
                               ifnull(sum(hi.rate_fuel*hi.perf_bench),0) as su, hi.from_date as fr, hi.to_date as t, hi.to_date-hi.from_date as dif
                               from  `tabHire Charge Item` hi, `tabHire Charge Parameter` hp
                               where hi.parent = hp.name 
			       and hp.equipment_type = '{0}'
			       and hp.equipment_model = '{1}'
                               and {2}
                       """.format(eq.equipment_type, eq.equipment_model,  bench_date), as_dict=1)[0]
		from_date  = flt(filters.get("from_date")) 
		to_date    = flt(filters.get("to_date"))
		bench_date = flt(date_diff(benchmark.t, benchmark.fr)+1)
		target     = 0.0
	    	
		#frappe.msgprint("from:{0}".format(benchmark.fr))
		#frappe.msgprint("to:{0}".format(benchmark.t))
		#frappe.msgprint("{0}".format(benchmark.dif))
		c_operator = frappe.db.sql("""
				select operator, start_date, end_date
				from `tabEquipment Operator` eo
				where eo.parent = '{0}'
				and   eo.docstatus < 2
				and   {1}
			""".format(eq.name, operator_date), as_dict=1)

		#frappe.msgprint(benchmark)
		travel_claim = 0.0
		e_amount     = 0.0
		gross_pay    = 0.0
		total_sal    = 0.0
		total_exp    = 0.0
		total_rev    = 0.0
		bench 	     = 0.0
		for co in c_operator:
			tc = frappe.db.sql("""
				select sum(ifnull(tc.total_claim_amount,0)) as travel_claim
				from `tabTravel Claim` tc
				where tc.employee = '{0}'
				and   tc.docstatus = 1
				and   {1}
			""".format(co.operator, tc_date), as_dict=1)[0]
			
			#frappe.msgprint("{0}".format(tc.travel_claim))
			#Leave Encashment Aomun

			lea = frappe.db.sql("""
					select sum(ifnull(le.encashment_amount,0)) as e_amount
					from `tabLeave Encashment` le
					where le.employee = '{0}'
					and   le.docstatus = 1
					and   {1}
				""".format(co.operator, le_date), as_dict=1)[0]

			cem = frappe.db.sql("""
			                select employee, gross_pay, start_date, end_date
                    			from `tabSalary Slip` ss 
                    			where employee = '{0}'
                   			and docstatus = 1
                    			and {1}
           		      """.format(co.operator, ss_date),  as_dict=1)
			
			if cem:
				for e in cem:
					total_days = flt(date_diff(e.end_date, e.start_date) + 1)
					if e.end_date < co.start_date:
						pass	
					elif co.end_date and e.start_date > co.end_date:
						pass
					elif co.end_date and e.start_date > co.start_date and e.end_date < co.end_date:
						total_sal += flt(e.gross_pay)
					#	frappe.msgprint("A")
					elif co.end_date and e.start_date <= co.start_date and e.end_date >= co.end_date:
					#	frappe.msgprint("B")
						days = date_diff(co.end_date, co.start_date) + 1
						total_sal += (flt(e.gross_pay) * days ) / total_days
					elif co.end_date and e.start_date > co.start_date and e.end_date > co.end_date:
						days = date_diff(co.end_date, e.start_date) + 1
						total_sal += (flt(e.gross_pay) * days ) / total_days
					elif co.end_date and e.start_date < co.start_date and e.end_date < co.end_date:
						days = date_diff(e.end_date, co.start_date) + 1
						total_sal += (flt(e.gross_pay) * days ) / total_days
					elif not co.end_date and e.start_date >= co.start_date:
						total_sal += flt(e.gross_pay)
					elif not co.end_date and e.start_date < co.start_date:
						days = date_diff(e.end_date, co.start_date) + 1
						total_sal += (flt(e.gross_pay) * days ) / total_days
					else:
						pass
				
			travel_claim += flt(tc.travel_claim)
			e_amount     += flt(lea.e_amount)
			gross_pay    += flt(total_sal)
			total_exp    += (flt(vl.consumption)*flt(pol.rate))+flt(ins.insurance)+flt(jc.goods_amount)+flt(jc.services_amount)+ travel_claim+e_amount+gross_pay
			total_rev    = flt(revn.rev)
		bench        = str(benchmark.rat)

		if from_date <flt(benchmark.fr) < to_date and flt(benchmark.t)>to_date:
			cal_date = date_diff(least(to_date, benchmark.t) - greatest(from_date,benchmark.fr)+1)
	    		target = cal_date*su/bench_date
			frappe.msgprint("a")	
	   	if from_date<flt(benchmark.t) < to_date and flt(benchmark.t) >to_date:
	   		cal_date = date_diff(least(from_date, benchmark.fr)+1)- date_diff(least(to_date, benchmark.t)+1)
			target   = cal_date*su/bech_date
			frappe.msgprint("b")	
	   	if from_date< flt(benchmark.fr) and flt(benchmark.t) < to_date:
			target = su
			frappe.msgprint("c")
		frappe.msgprint("target : {0}".format(target))
		# utility % based on existance of revenue and benchmark target
		if benchmark.su != 0:
				util_percent = 100*total_rev/benchmark.su

		elif benchmark.su == 0  and revn.rev > 0.0:
				util_percent = 100
		elif benchmark.su == 0 and revn.rev < 0.0:
				util_percent = 0.0
		else:
				pass
		data.append((	eq.branch,
				eq.name,
				eq.equipment_number,
				eq.equipment_type,
				eq.equipment_model,
				total_exp,
				total_rev,
				flt(total_rev-total_exp),
				bench,
				str(benchmark.bn),
				flt(benchmark.su),
				round(flt(util_percent),2)
			))
#	frappe.msgprint(type(bench))
    	return tuple(data)
#       return tuple()

def get_columns(filters):
	cols = [
		("Branch") + ":Data:120",
                ("ID") + ":Link/Equipment:120",
		("Registration No") + ":Data:120",
		("Equipment Type") + ":Data:120",
		("Equipment Model") + ":Data:120",
		("Total Expense") + ":Currency:120",
		("Total Revenue") + ":Currency:120",
		("R-E") + ":Currency:120",
		("HC Rate/Hour") + ":Data:120",
		("Utility/Month") + ":Data:120",
		("Total HC Amount") + ":Currency:120",
		("Utility %") + ":Data:120"

	]
	return cols

