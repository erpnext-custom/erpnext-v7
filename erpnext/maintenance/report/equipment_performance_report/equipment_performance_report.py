	# Copyrght (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, json
from frappe.utils import flt, cint
from frappe.utils.data import get_last_day
from frappe.utils.data import flt, cint,add_days, cstr, flt, getdate, nowdate, rounded, date_diff
def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_conditions(filters):
	branch = consumption_date = rate_date = jc_date = insurance_date = rev_date = tc_date = operator_date = le_date = ss_date= ""
	if filters.get("branch"):
		branch += str(filters.branch)
		
	if filters.get("period"):
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
	f_from_date = f_to_date = get_date_conditions(filters)

	if from_date_column:
		cond1 = ("{0} between %(f_from_date)s  and %(f_to_date)s").format(from_date_column)

	if to_date_column:
		if module in ("op","ss", "benchmark"):
			cond2 = str(" or {0} between %(f_from_date)s and %(f_to_date)s").format(to_date_column)
		else:
			cond2 = str("and {0} between %(f_from_date)s and %(f_to_date)s").format(to_date_column)

	return "({0} {1})".format(cond1, cond2)

def get_date_conditions(filters):
	months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	no_of_months = 0

	def calc_dates(from_month, to_month):
		from_date = getdate(filters.get("fy") + "-" + str(from_month) + "-" + "01")
		to_date   = get_last_day(getdate(filters.get("fy") + "-" + str(to_month) + "-" + "01"))
		
		return from_date, to_date, (to_month-from_month)+1

	if filters.get("period") in ("1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "1st Half Year", "2nd Half Year"):
		if filters.get("period") == "1st Quarter":
			from_date,to_date,no_of_months = calc_dates(1,3)
		elif filters.get("period") == "2nd Quarter":
			from_date,to_date,no_of_months = calc_dates(4,6)
		elif filters.get("period") == "3rd Quarter":
			from_date,to_date,no_of_months = calc_dates(7,9)
		elif filters.get("period") == "4th Quarter":
			from_date,to_date,no_of_months = calc_dates(10,12)
		elif filters.get("period") == "1st Half Year":
			from_date,to_date,no_of_months = calc_dates(1,6)
		elif filters.get("period") == "2nd Half Year":
			from_date,to_date,no_of_months = calc_dates(7,12)
	else:
		month_id     = months.index(filters.get("period"))+1
		from_date    = getdate(filters.get("fy") + "-" + str(month_id) + "-" + "01")
		to_date      = get_last_day(from_date)
		no_of_months = 1 

	#frappe.msgprint(_("{0}, {1}, {2}").format(from_date, to_date, no_of_months))
	return from_date, to_date, no_of_months

	'''
	if filters.fy:
		f = frappe.utils.datetime.datetime(filters.fy, 1, 15)
		f1 =  frappe.utils.data.get_last_day (f)
		frappe.msgprint(f1)
		f_from_date = getdate(filters.fy,1,1)
		f_to_date   = getdate(filters.fy,12,12)
		no_of_month = 12	
        if filters.period == "Jan":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 1

        if filters.period == "Feb":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 1


        if filters.period == "Mar":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 1

        if filters.period == "Apr":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 1

        if filters.period == "May":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 1

        if filters.period == "Jun":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 1

        if filters.period == "Jul":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 1

        if filters.period == "Aug":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 1

        if filters.period == "Sep":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 1

        if filters.period == "Oct":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 1

        if filters.period == "Nov":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 1

	if filters.period == "Dec":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 1

        if filters.period == "1st Quarter":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 3

        if filters.period == "2nd Quarter":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 3

        if filters.period == "3rd Quarter":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 3

        if filters.period == "4th Quarter":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 3

        if filters.period == "1st Half Year":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 6

        if filters.period == "2nd Half Year":
                f_from_date = getdate(filtrs.fy, 1,1)
                f_to_date   = getdate(filters.fy, 15,1)
		no_of_month  = 6

        return f_from_date, f_to_date
	'''

def get_data(filters):
	branch, consumption_date, rate_date, jc_date, insurance_date, rev_date, bench_date, operator_date, tc_date, le_date, ss_date =  get_conditions(filters)
	data = []
	branch_cond = " where branch = '{0}'".format(branch) if branch else ""
	f_from_date = f_to_date = no_of_month = get_date_conditions(filters)

	equipments = frappe.db.sql("""
                                select name, branch, equipment_number, equipment_type, equipment_model
                                from `tabEquipment`
				{0}
				order by branch, name
                        """.format(branch_cond), as_dict=1)

    	for eq in equipments:

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
		#Revenue from Hire of Equipments
		revn = frappe.db.sql("""
			 	 select sum(ifnull(id.total_amount, 0)) as rev from `tabHire Invoice Details` id, `tabHire Charge Invoice` ci
			 	 where ci.name = id.parent
			 	 and id.equipment = '{0}'
			 	 and {1}
			 """.format(eq.name, rev_date), as_dict=1)[0]
		#frappe.msgprint("re {0}".format(revn.rev))
		
		#Looping via operator of the equipment to calculate the expensis related to operator
		c_operator = frappe.db.sql("""
				select operator, start_date, end_date
				from `tabEquipment Operator` eo
				where eo.parent = '{0}'
				and   eo.docstatus < 2
				and   {1}
			""".format(eq.name, operator_date), as_dict=1)

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
		pro_target = 0.0
		#benchmar
                '''benchmark  = frappe.db.sql("""
                               select hi.rate_fuel as rat, hi.perf_bench as bn, 
                               hi.from_date as fr, hi.to_date as t
                               from  `tabHire Charge Item` hi, `tabHire Charge Parameter` hp
                               where hi.parent = hp.name 
			       and hp.equipment_type = '{0}'
			       and hp.equipment_model = '{1}'
			       and (
					(hi.from_date between '%(from_date)s' and '%(to_date)s')
					or
					(hi.to_date between '%(from_date)s and '%(to_date)s')
				or
					('%(from_date)s' between hi.from_date and hi.to_date)
					or
					('%(to_date)s' between hi.from_date and hi.to_date)
				   )"""
                       .format(eq.equipment_type, eq.equipment_model) % {"from_date": getdate(filters.from_date), "to_date": getdate(filters.to_date)}, as_dict=1)'''
		

		benchmark  = frappe.db.sql("""
                               select hi.rate_fuel as rat, hi.perf_bench as bn, 
                               hi.from_date as fr, hi.to_date as t
                               from  `tabHire Charge Item` hi, `tabHire Charge Parameter` hp
                               where hi.parent = hp.name 
                               and hp.equipment_type = '{0}'
                               and hp.equipment_model = '{1}'
			""".format(eq.equipment_type, eq.equipment_model), as_dict=1)
		rate = []
		bench = []
		total_hc = 0
		for a in benchmark:
			ta = ta1= ta2 =  ta3 = 0.0
			if not a.t:
				a.t = getdate(filters.to_date)
			bench_date = date_diff(a.t, a.fr) + 1
 
			if a.fr >= f_from_date and a.t <= f_to_date:
				rate.append(a.rat) 
				bench.append(a.bn)
				frappe.msgprint("c")	
				#total_hc  += sum([i*j for i,j in zip(rate,bench)])
				total_hc   += flt(a.rat)*flt(a.bn)*8*no_of_month
				frappe.msgprint("ll{0}".format(total_hc))
				frappe.msgprint("rat{0}".format(a.rat))
				frappe.msgprint("bn {0}".format(a.bn))

			if f_from_date  <= a.fr <= f_to_date  and (a.t > f_to_date):
				rate.append(a.rat)
                                bench.append(a.bn)
				ta1 += flt(a.rat)*flt(a.bn)*8
				#ta1  = sum([i*j for i,j in zip(rate,bench)])
				#frappe.msgprint("ta {0}".format(ta))
				cal_date = date_diff(f_to_date, a.fr)+1
				total_hc += cal_date*no_of_month*ta1/bench_date
				frappe.msgprint("c1")
				frappe.msgprint("rat1{0}".format(a.rat))
                                frappe.msgprint("bn1 {0}".format(a.bn))
				frappe.msgprint("ta1 {0}".format(total_hc))
				frappe.msgprint("da1 {0}".format(cal_date))
				frappe.msgprint("ben_da1{0}".format(bench_date))


			if f_to_date >= a.t >= f_from_date and  a.fr < f_from_date:
				rate.append(a.rat)
                                bench.append(a.bn)
				ta2  += flt(a.rat)*flt(a.bn)*8
                               	#ta2  = sum([i*j for i,j in zip(rate,bench)])
				#frappe.msgprint("ta1 {0}".format(ta))
				cal_date = date_diff(a.t, f_from_date)+1
				total_hc += cal_date*no_of_month*ta2/bench_date 
				frappe.msgprint("c2")
				frappe.msgprint("rat2{0}".format(a.rat))
                                frappe.msgprint("bn2 {0}".format(a.bn))
				frappe.msgprint("ta2 {0}".format(ta2))
				frappe.msgprint("cal2 {0}".format(cal_date))
				frappe.msgprint("bench_date2{0}".format(bench_date))

			if a.fr < f_from_date and a.t > f_to_date:
				rate.append(a.rat)
				bench.append(a.bn)
				total_hc += flt(a.rat)*flt(a.bn)*no_of_month
				#cal_date = date_diff(f_from_date, f_to_date)) + 1
				#total_hc += cal_date*ta3/bench_date 
		#frappe.msgprint(str(list(set(rate))))		
		if not benchmark:
			benchmark = {"rat": 0, "bn": 0, "fr": '', "t": ''}

                # utility % based on existance of revenue and benchmark target'''
                if total_hc != 0:
                        util_percent = 100*total_rev/total_hc

                elif total_hc == 0  and revn.rev > 0.0:
                        util_percent = 100

                elif total_hc == 0 and revn.rev <= 0.0:
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
		("HC Rate/Hour") + ":Data:120",
		("Utility/Month") + ":Data:120",
		("Total HC Amount") + ":Currency:120",
		("Utility %") + ":Data:120"

	]
	return cols
