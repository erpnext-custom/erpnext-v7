	# Copyrght (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime
import time
from frappe import _, json
from frappe.utils import flt, cint
from frappe.utils.data import get_last_day
from frappe.utils.data import flt, cint,add_days, cstr, flt, getdate, nowdate, rounded, date_diff

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_conditions(filters):
	branch_cond = consumption_date = rate_date = jc_date = insurance_date = rev_date = bench_date = tc_date = operator_date = le_date = ss_date= not_cdcll = dis = mr_date= ""

	if filters.get("branch"):
                branch_cond = " and eh.branch = \'"+str(filters.branch)+"\'"
        else:
                branch_cond = " and eh.branch like '%' "

        if filters.get("not_cdcl"):
                not_cdcll = " and not_cdcl = 0"
        else:
                not_cdcll = " and not_cdcl like '%' "

        if filters.get("include_disabled"):
               dis = " and is_disabled like '%' "
        else:
               dis  = " and is_disabled != 1 "


	consumption_date  = get_dates(filters, "vl", "from_date", "to_date")
	rate_date 	  = get_dates(filters, "pol", "date")
	jc_date	 	  = get_dates(filters, "jc", "posting_date", "finish_date")
	insurance_date    = get_dates(filters, "ins", "id.insured_date")
	reg_date          = get_dates(filters, "reg", "rd.registration_date")
	operator_date     = get_dates(filters, "op", "start_date", "end_date")
	tc_date	      	  = get_dates(filters, "tc", "posting_date")
	le_date		  = get_dates(filters, "le", "encashed_date")
	ss_date           = get_dates(filters, "ss", "start_date", "ifnull(end_date,curdate())")
	rev_date          = get_dates(filters, "revn", "ci.posting_date")
	bench_date        = get_dates(filters, "benchmark", "hi.from_date", "hi.to_date")
	mr_date           = get_dates(filters, "mr_pay", "from_date", "to_date")
	return branch_cond, consumption_date, rate_date, jc_date, insurance_date, reg_date, rev_date, bench_date, operator_date, tc_date, le_date, ss_date, not_cdcll, dis, mr_date

def get_dates(filters, module = "", from_date_column = "", to_date_column = ""):
	cond1 = ""
	cond2 = ""
	eh_cond = ""
	from_date,to_date,no_of_months, from_date1, to_date1, ra = get_date_conditions(filters)
	if from_date_column:
		cond1 = ("{0} between '%(from_date)s'  and '%(to_date)s'").format(from_date_column)
	if to_date_column:
		if module in ("op","ss", "benchmark"):
			cond2 = str(" or {0} between '%(from_date)s' and '%(to_date)s'").format(to_date_column)
		else:
			cond2 = str("and {0} between '%(from_date)s' and '%(to_date)s'").format(to_date_column)
	cond1 = cond1 % {"from_date": from_date, "to_date": to_date}
	cond2 = cond2 % {"from_date": from_date, "to_date": to_date}
	return "({0} {1})".format(cond1, cond2)

def get_date_conditions(filters):
	from_date = to_date = no_of_months = from_date1 = to_date1 = no_of_months1 = 0
	ra = []
	months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	no_of_months = 0

	def calc_dates(from_month, to_month):
		from_date = getdate(filters.get("fy") + "-" + str(from_month) + "-" + "01")
		to_date   = get_last_day(getdate(filters.get("fy") + "-" + str(to_month) + "-" + "01"))
		ra        = range(from_month, to_month+1)
		return from_date, to_date, (to_month-from_month)+1, ra
		
	
	def calc_dates_two(from_month, to_month):
                from_date1 = getdate(filters.get("fy") + "-" + str(from_month) + "-" + "01")
                to_date1   = get_last_day(getdate(filters.get("fy") + "-" + str(to_month) + "-" + "01"))
                return from_date1, to_date1



	if filters.get("period") in ("1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "1st Half Year", "2nd Half Year"):
		if filters.get("period") == "1st Quarter":
			from_date, to_date, no_of_months, ra  = calc_dates(1,3)
		elif filters.get("period") == "2nd Quarter":
			from_date,to_date,no_of_months, ra  = calc_dates(4,6)
		elif filters.get("period") == "3rd Quarter":
			from_date,to_date,no_of_months, ra  = calc_dates(7,9)
		elif filters.get("period") == "4th Quarter":
			from_date,to_date,no_of_months, ra  = calc_dates(10,12)
		elif filters.get("period") == "1st Half Year":
			from_date,to_date,no_of_months, ra  = calc_dates(1,6)
		elif filters.get("period") == "2nd Half Year":
			from_date,to_date,no_of_months, ra  = calc_dates(7,12)
		for i in ra:
                                from_date1, to_date1 = calc_dates_two(i,i)
	elif filters.get("period") in ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"):
		month_id     = months.index(filters.get("period"))+1
		from_date    = getdate(filters.get("fy") + "-" + str(month_id) + "-" + "01")
		to_date      = get_last_day(from_date)
		no_of_months = 1 
	elif filters.fy and (not filters.get("period")):
		from_date    = getdate(filters.get("fy")+ "-" + "01" + "-" + "01")
		to_date      = get_last_day(getdate(filters.get("fy") + "-" + "12" + "-" + "31"))
		no_of_months = 12
		ra = [1,2,3,4,5,6,7,8,9,10,11,12]
		#for i in ra:
		#	from_date1, to_date1, no_of_months1 = calc_dates(i,i)
	return from_date, to_date, no_of_months, from_date1, to_date1, ra


def get_data(filters):
	branch_cond, consumption_date, rate_date, jc_date, insurance_date, reg_date, rev_date, bench_date, operator_date, tc_date, le_date, ss_date, not_cdcll, dis, mr_date  =  get_conditions(filters)
	from_date, to_date, no_of_months, from_date1, to_date1, ra  = get_date_conditions(filters)
	frappe.msgprint("fr,: '{0}' to: {1}".format(from_date, to_date))
	data = []
	if filters.get("branch"):
                branch_cond = " and eh.branch = \'"+str(filters.branch)+"\'"
        else:
                branch_cond = " and eh.branch like '%' "

        if filters.get("not_cdcl"):
                not_cdcll = " and not_cdcl = 0"
        else:
                not_cdcll = " and not_cdcl like '%' "

        if filters.get("include_disabled"):
               dis = " and is_disabled like '%' "
        else:
               dis  = " and is_disabled != 1 "
	
	query = """
		select e.name as name, eh.branch as branch, e.equipment_number as equipment_number, 
			e.equipment_type as equipment_type, e.equipment_model as equipment_model
			from `tabEquipment` e, `tabEquipment History` eh 
			where eh.parent = e.name
			{0} {1} {2} 
			and ('{3}' between eh.from_date and ifnull(eh.to_date, now())
			or '{4}' between eh.from_date and ifnull(eh.to_date, now()))
			 group by eh.branch, eh.parent order by eh.branch, eh.parent
	""".format(not_cdcll, branch_cond, dis, from_date, to_date)
        equipments = frappe.db.sql(query, as_dict=1)
   	for eq in equipments:

                # `tabVehicle Logbook`
        	vl = frappe.db.sql("""
                        	select sum(ifnull(consumption,0)) as consumption
                        	from `tabVehicle Logbook`
                        	where equipment = '{0}'
                        	and   docstatus = 1
				and   {1} and  branch = '{2}'
                    """.format(eq.name,consumption_date, eq.branch), as_dict=1)[0]
                # `tabPOL`
            	pol = frappe.db.sql("""
                            	select (sum(qty*rate)/sum(qty)) as rate
                            	from `tabPOL`
                        	where branch = '{0}'
                        	and   docstatus = 1
                    """.format(eq.branch), as_dict=1)[0]

                # `tabJob Card`
            	jc = frappe.db.sql("""
                            	select sum(ifnull(goods_amount,0)) as goods_amount,
                            		sum(ifnull(services_amount,0)) as services_amount
                            	from `tabJob Card`
                            	where equipment = '{0}'
                            	and   docstatus = 1
				and   {1} and branch = '{2}'
                    """.format(eq.name,jc_date, eq.branch), as_dict=1)[0]

		#Insurance
		ins = frappe.db.sql("""
			 	select sum(ifnull(id.insured_amount,0)) as insurance
				from `tabInsurance Details` id,	`tabInsurance and Registration` ir
				where id.parent = ir.name and ir.equipment = '{0}'
				and   {1}
			 """.format(eq.name, insurance_date), as_dict=1)[0]
		#Reg fee
                reg = frappe.db.sql("""
                                select sum(ifnull(rd.registration_amount,0)) as r_amount
                                from `tabRegistration Details` rd, `tabInsurance and Registration` i  
                                where rd.parent = i.name  
                                and i.equipment = '{0}'
                                and   {1}
                        """.format(eq.name, reg_date), as_dict=1)[0]

		
		#Revenue from Hire of Equipments
                revn = frappe.db.sql("""
                                 select sum(ifnull(id.total_amount, 0)) as rev from `tabHire Invoice Details` id, `tabHire Charge Invoice` ci
                                 where ci.name = id.parent
                                 and id.equipment = '{0}'
                                 and {1}
                         """.format(eq.name, rev_date), as_dict=1)[0]

				
		#Looping via operator of the equipment to calculate the expensis related to operator
		c_operator = frappe.db.sql("""
                                select eo.operator, eo.employee_type, eo.start_date, eo.end_date , eo.name, eh.branch 
                                from `tabEquipment Operator` eo, `tabEquipment History` eh
                                where eo.parent = '{0}' and eo.parent = eh.parent and eh.branch = '{1}'
                                and   eo.docstatus < 2
                        """.format(eq.name, eq.branch), as_dict=1)
		travel_claim = 0.0
		e_amount     = 0.0
		gross_pay    = 0.0
		total_exp    = 0.0
		total_sal    = 0.0
		total_rev    = 0.0

		for co in c_operator:
			if co.employee_type =="Muster Roll Employee":
				mr_pay = frappe.db.sql("""
					           select sum(ifnull(mr.total_overall_amount,0)) as mr_payment
						   from `tabProcess MR Payment` mr, `tabMR Payment Item` mi
					           where mi.parent = mr.name
						   and mi.id_card ='{0}'
						   and mr.docstatus = 1
					           and {1} 
					""".format(co.operator, mr_date), as_dict =1) [0]
				travel_claim += 0.0
				e_amount += 0.0
				gross_pay += flt(mr_pay.mr_payment)

			elif co.employee_type == "Employee":	
				tc = frappe.db.sql("""
						select sum(ifnull(tc.total_claim_amount,0)) as travel_claim
						from `tabTravel Claim` tc
						where tc.employee = '{0}'
						and   tc.docstatus = 1
						and   {1}
					""".format(co.operator, tc_date), as_dict=1)[0]
			
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
						and ss.docstatus = 1
						and {1} group by employee
				      """.format(co.operator, ss_date),  as_dict=1)
				#frappe.msgprint(str(cem))
				if cem:
					for e in cem:
						total_days = flt(date_diff(e.end_date, e.start_date) + 1)
						if e.end_date < co.start_date:
							pass
						elif co.end_date and e.start_date > co.end_date:
							pass
						elif co.end_date and e.start_date > co.start_date and e.end_date < co.end_date:
							total_sal += flt(e.gross_pay)
						
						elif co.end_date and e.start_date <= co.start_date and e.end_date >= co.end_date:
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
				#frappe.msgprint(str(pol.rate))
			total_exp    += (flt(vl.consumption)*flt(pol.rate))+flt(ins.insurance)+flt(reg.r_amount) + flt(jc.goods_amount)+flt(jc.services_amount)+ travel_claim+e_amount+gross_pay
			total_rev    = flt(revn.rev)
		pro_target = 0.0
		
		#benchmar
		benchmark  = frappe.db.sql("""
                               select hi.rate_fuel as rat, hi.perf_bench as bn, 
                               hi.from_date as fr, hi.to_date as t
                               from  `tabHire Charge Item` hi, `tabHire Charge Parameter` hp
                               where hi.parent = hp.name 
                               and hp.equipment_type = '{0}'
			       and hp.equipment_model = '{1}'
			""".format(eq.equipment_type, eq.equipment_model), as_dict=1, debug =1)

		rate = []
		bench = []
		total_hc = 0
		for a in benchmark:
			from_date,to_date,no_of_months, from_date1, to_date1, ra  = get_date_conditions(filters)
			ta = ta1= ta2 =  ta3 = ta4 = 0.0
			if not a.t:
				a.t = getdate(filters.to_date)
				#from_date,to_date,no_of_months, from_date1, to_date1, no_of_months1, ra = get_date_conditions(filters)
			if a.fr >= from_date and a.t <= to_date:
				rate.append(a.rat) 
				bench.append(a.bn)
				total_hc   += flt(a.rat)*flt(a.bn)*8*no_of_months
		
			if a.fr <= from_date and a.t >= to_date:
                                rate.append(a.rat)
                                bench.append(a.bn)
                                total_hc += flt(a.rat)*flt(a.bn)*no_of_months*8

			#if filters.get("period") not in ("1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "1st Half Year", "2nd Half Year"):
			if from_date  < a.fr < to_date  and (a.t > to_date) and filters.get("period") in ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"):
				rate.append(a.rat)
				bench.append(a.bn)
				cal_date = date_diff(to_date, a.fr) + 1
				ta2 += flt(a.rat)*flt(a.bn)*8
				bench_date = date_diff(to_date, from_date) + 1
				total_hc += cal_date*ta2/bench_date

			if to_date > a.t > from_date and  a.fr < from_date and filters.get("period") in ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"):
				rate.append(a.rat)
				bench.append(a.bn)
				ta3  += flt(a.rat)*flt(a.bn)*8
				bench_date = date_diff(to_date, from_date) + 1
				cal_date = date_diff(a.t, from_date)+1
				total_hc += cal_date*ta3/bench_date 

			if from_date  < a.fr <= to_date  and (a.t > to_date) and filters.get("period")  in ("1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "1st Half Year", "2nd Half Year"):
				for i in ra:
					from_date1 = getdate(filters.get("fy") + "-" + str(i) + "-" + "01")
                			to_date1   = get_last_day(getdate(filters.get("fy") + "-" + str(i) + "-" + "01"))
					if from_date1 < a.fr <= to_date1 and (a.t > to_date1):
						rate.append(a.rat)
						bench.append(a.bn)
						cal_date = date_diff(to_date1, a.fr) + 1
						bench_date = date_diff(to_date1, from_date1) + 1
						ta4   += flt(a.rat)*flt(a.bn)*8
						total_hc += cal_date*ta4/bench_date
					else:
						rate.append(a.rat)
                                                bench.append(a.bn)
						total_hc   += flt(a.rat)*flt(a.bn)*8
			if to_date > a.t >= from_date and  (a.fr < from_date) and filters.get("period")	in ("1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "1st Half Year", "2nd Half Year"):
				for i in  ra:
					from_date1 = getdate(filters.get("fy") + "-" + str(i) + "-" + "01")
                                        to_date1   = get_last_day(getdate(filters.get("fy") + "-" + str(i) + "-" + "01"))
                                        if from_date1 < a.t <= to_date1 and (a.fr <  from_date1):
						rate.append(a.rat)
                                                bench.append(a.bn)
                                                cal_date = date_diff(a.t, from_date1) + 1
                                                bench_date = date_diff(to_date1, from_date1) + 1
                                                ta4   = flt(a.rat)*flt(a.bn)*8
                                                total_hc += cal_date*ta4/bench_date
                                        elif (from_date1 < a.fr and a.t < to_date1) or (a.fr < from_date1 and a.t > to_date1):
                                                rate.append(a.rat)
                                                bench.append(a.bn)
                                                total_hc   += flt(a.rat)*flt(a.bn)*8
				
		if not benchmark:
			benchmark = {"rat": 0, "bn": 0, "fr": '', "t": ''}
		#ben = [i*8 for i in bench]
                # utility % based on existance of revenue and benchmark target'''

		util_percent = 0

                if total_hc != 0.0:
                        util_percent = 100*total_rev/total_hc
			#frappe.msgprint("1 {0}".format(util_percent))

                elif flt(total_hc) == 0  and flt(total_rev) > 0:
                        util_percent = 100
			#frappe.msgprint("2 {0} ".format(util_percent))

                elif flt(total_hc) == 0.0 and flt(total_rev) <= 0.0:
                        util_percent = 0.0
			#frappe.msgprint("3 {0}".format(util_percent))

                else:
                        util_percent = 0.0
			#frappe.msgprint("4 {0}".format(util_percent))

		#frappe.msgprint(_("{0}, {1}, {2}").format(total_rev, total_hc, util_percent))
	
		data.append((	eq.branch,
			eq.name,
			eq.equipment_number,
			eq.equipment_type,
			eq.equipment_model,
			total_exp,
			total_rev,
			flt(total_rev-total_exp),
			list(set(rate)),
			list(set(bench)),
			flt(total_hc),
			round(flt(util_percent),2)
		))
	return tuple(data)

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
		("HC Rate/Hour") + ":Currency:120",
		("Utility/Month") + ":Data:120",
		("Benchmark Amount") + ":Currency:120",
		("Utility %") + ":Data:120"
	]
	return cols
