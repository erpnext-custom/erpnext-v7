# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_child_cost_centers, get_period_date
from frappe.utils import flt, rounded
from erpnext.custom_utils import get_production_groups
from erpnext.production.doctype.production_target.production_target import get_target_value
from frappe.utils.data import get_first_day, get_last_day, add_days
import math

def execute(filters=None):
	build_filters(filters)
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def build_filters(filters):
	per = []
	filters.is_company = frappe.db.get_value("Cost Center", filters.cost_center, "is_company")
	filters.from_date, filters.to_date = get_period_date(filters.fiscal_year, filters.report_period, filters.cumulative)

def get_data(filters):
	data = []
	cc_condition = get_cc_conditions(filters)

	group_by = get_group_by(filters)
	order_by = get_order_by(filters)

	f_date = filters.from_date.split("-")
	t_date = filters.to_date.split("-")

	start_month = int(f_date[1])
	end_month = int(t_date[1])
	if start_month < 10:
		start_date = f_date[0]+"-0"+str(start_month)+"-01"
	else:
		start_date = f_date[0]+"-"+str(start_month)+"-01"

	if int(end_month) < 10:
		end_month_start_date = f_date[0]+"-0"+str(end_month)+"-01"
	else:
		end_month_start_date = f_date[0]+"-"+str(end_month)+"-01"
	
	end_date = get_last_day(end_month_start_date)
	conditions = get_filter_conditions(filters, start_date, end_date)
	
	abbr = " - " + str(frappe.db.get_value("Company", filters.company, "abbr"))

	overall_target = 0.0
	overall_achieved = 0.0
	overall_achieved_percent = 0.0

	#query = "select pe.cost_center, pe.branch, pe.location, cc.parent_cost_center as region, sum(qty) as total_qty from `tabProduction Entry` pe RIGHT JOIN `tabCost Center` cc ON cc.name = pe.cost_center where 1 = 1 {0} {1} {2} {3}".format(cc_condition, conditions, group_by, order_by)
	# query = "select pe.cost_center, pe.branch, pe.location, cc.parent_cost_center as region from `tabProduction Target` pe, `tabCost Center` cc where cc.name = pe.cost_center and cc.parent_cost_center != 'Regional Office - NRDCL' and pe.fiscal_year = {0} {1} {2} {3}".format(filters.fiscal_year, cc_condition, group_by, order_by)
	# if filters.branch:
	query = "select pei.uom, pe.cost_center, pe.branch, pei.location, cc.parent_cost_center as region from `tabProduction Target` pe, `tabProduction Target Item` pei, `tabCost Center` cc where cc.name = pe.cost_center and pe.name = pei.parent and cc.parent_cost_center != 'Regional Office - NRDCL' and pe.fiscal_year = {0} {1} {2} {3}".format(filters.fiscal_year, cc_condition, group_by, order_by)
	# else:
	# 	query = "select cc.parent_cost_center as region from `tabProduction Target` pe, `tabCost Center` cc where cc.name = pe.cost_center and cc.parent_cost_center != 'Regional Office - NRDCL' and pe.fiscal_year = {0} {1} {2} {3}".format(filters.fiscal_year, cc_condition, group_by, order_by)
	# frappe.msgprint(query)
	for a in frappe.db.sql(query, as_dict=1):
		#frappe.msgprint("{0}".format(a.location))
		if not filters.display_monthly:
			total_timber = 0
			if filters.branch:
				if a.location:
					target = get_target_value("Production", a.location, a.uom, filters.production_group, filters.fiscal_year, start_date, end_date, True)
					row = [a.branch, a.location,  target, a.uom]
					cond = " and location = '{0}'".format(a.location)
				else:
					target = get_target_value("Production", a.cost_center, a.uom, filters.production_group, filters.fiscal_year, start_date, end_date)
					row = [a.branch, a.location,target, a.uom]
					branch_n = str(filters.branch)
					branch_n = branch_n.replace(' - NRDCL','')
					cond = " and branch = '{0}'".format(branch_n)
				#cond += " and branch = '{0}'".format(filters.branch)
			else:
				# frappe.msgprint(a.cost_center)
				# if filters.is_company:
				# target = get_target_value("Production", a.region, filters.production_group, filters.fiscal_year, start_date, end_date)
				target = get_target_value("Production", a.cost_center, a.uom, filters.production_group, filters.fiscal_year, start_date, end_date)
				# all_ccs = get_child_cost_centers(a.region)
				ccs = []
				all_ccs = frappe.db.sql("""
					select name from `tabCost Center` where parent_cost_center = '{0}'
					""".format(a.region), as_dict= True)
				if all_ccs:
					for i in all_ccs:
						ccs.append(str(i.name))
				if len(ccs) > 1:
					cond = " and cost_center in {0} ".format(tuple(ccs))
				else:
					cond = " and cost_center in ('DUMMY')"	
				# a.region = str(a.region).replace(abbr, "")
				row = [a.branch, a.region, target, a.uom]
				# else:
				# 	target = get_target_value("Production", a.cost_center, filters.production_group, filters.fiscal_year, filters.from_date, filters.to_date)
				# 	# frappe.msgprint(str(target))
				# 	row = [a.branch, target]
				# 	cond = " and cost_center = '{0}'".format(a.cost_center)
			total = 0
			for b in get_production_groups(filters.production_group):
				# query = "select sum(pe.qty) from `tabProduction Entry` pe where 1 = 1 {0} and pe.item_sub_group = '{1}' {2}".format(conditions, str(b), cond)
				query = "select sum(pe.qty) from `tabProduction Entry` pe where 1 = 1 {0} and pe.item_sub_group = '{1}' {2}".format(conditions, str(b), cond)
				# qty = frappe.db.sql("select sum(pe.qty) from `tabProduction Entry` pe where 1 = 1 {0} and pe.item_sub_group = '{1}' {2}".format(conditions, str(b), cond))
				qty = frappe.db.sql("select sum(pe.qty) from `tabProduction Entry` pe where 1 = 1 {0} and pe.item_sub_group = '{1}' and pe.branch = '{2}' and pe.uom = '{3}' {4} ".format(conditions, str(b), a.branch, a.uom, cond))
				# frappe.msgprint(str(qty))
				qty = qty and qty[0][0] or 0
				row.append(rounded(qty, 2))
				total += flt(qty)
				total_timber += flt(qty)

			if filters.branch:
				row.insert(4, rounded(total, 2))
			else:
				row.insert(4, rounded(total, 2))

			# if target == 0:
			# 	target = 1
			# if filters.production_group == "Timber":
			# 	row.append(total_timber)
			row.append(total)
			
			percentage = rounded(100 * (total/target),2) if target != 0 else 0
			# frappe.throw(str(percentage))
			if filters.branch:
				# if percentage <= rounded(100,2):
				row.insert(5, percentage)
				# else:
				# 	row.insert(5, rounded(100,2))
			else:
				# if percentage <= rounded(100,2):
				row.insert(5, percentage)
				# else:
				# 	row.insert(5,rounded(100,2))

			if target > 1:
				overall_target +=  target
			overall_achieved += total 
			
			data.append(row)
		else:
			for c_month in range(start_month, end_month+1):
				total_timber = 0
				
				if c_month < 10:
					start_date = f_date[0]+"-0"+str(c_month)+"-01"
				else:
					start_date = f_date[0]+"-"+str(c_month)+"-01"
				
				fdate_split = start_date.split("-")
				
				end_date = get_last_day(start_date)
				e_date = str(end_date)
				tdate_split = e_date.split("-")
				if fdate_split[1] == '02':
					tdate_split[2] = "29"
						
				if filters.branch:
					if a.location:
						# branch = str(filters.branch)
						# branch = branch.replace(' - NRDCL','')
						if frappe.session.user == "Adminsitrator":
							frappe.msgprint("here 1 "+str(a.branch))
						target = get_target_value("Production", a.location, a.uom, filters.production_group, filters.fiscal_year, start_date, end_date, True)
						row = [a.branch, a.location, target, a.uom]
						cond = " and location = '{0}'".format(a.location)
						# cond += " and branch = '{0}'".format(branch)
					else:
						if frappe.session.user == "Adminsitrator":
							frappe.msgprint("here 2 "+str(a.branch))
						target = get_target_value("Production", a.cost_center, a.uom, filters.production_group, filters.fiscal_year, start_date, end_date, True)
						row = [a.branch, a.location, target, a.uom]
						branch_n = str(filters.branch)
						branch_n = branch_n.replace(' - NRDCL','')
						cond = " and branch = '{0}'".format(branch_n)
				else:
					target = get_target_value("Production", a.region,a.uom, filters.production_group, filters.fiscal_year, start_date, end_date)
					ccs = []
					all_ccs = frappe.db.sql("""
						select name from `tabCost Center` where parent_cost_center = '{0}'
						""".format(a.region), as_dict= True)
					if all_ccs:
						for i in all_ccs:
							ccs.append(str(i.name))
					if len(ccs) > 1:
						cond = " and cost_center in {0} ".format(tuple(ccs))	
					else:
						cond = " and cost_center in ('DUMMY')"
					# a.region = str(a.region).replace(abbr, "")
					row = [a.branch, a.region,  rounded(target,2), a.uom]
					# else:
					# 	target = get_target_value("Production", a.cost_center, filters.production_group, filters.fiscal_year, start_date, end_date)
					# 	row = [a.branch, target]
					# 	cond = " and cost_center = '{0}'".format(a.cost_center)
						
	
				total = 0
				for b in get_production_groups(filters.production_group):
					condition = " and DATE(pe.posting_date) between '"+ str(start_date) + "' and '"+ str(end_date) +"'"
					# query = "select sum(pe.qty) from `tabProduction Entry` pe where 1 = 1 {0} and pe.item_sub_group = '{1}' {2}".format(condition, str(b), cond)
					qty = frappe.db.sql("select sum(pe.qty) from `tabProduction Entry` pe where 1 = 1 {0} and pe.item_sub_group = '{1}' {2}".format(condition, str(b), cond))
					# if frappe.session.user == "Administrator":
					# 	frappe.msgprint(query)
					# frappe.msgprint(str(qty)+" "+str(condition)+" "+str(b)+" "+str(cond))
					qty = qty and qty[0][0] or 0
					row.append(rounded(qty, 2))
					total += flt(rounded(qty,2))
					total_timber += flt(qty)
				# row.insert(2, rounded(total, 2))
				# if target == 0:
				# 	target = 1
				if filters.branch:
					row.insert(4, rounded(total, 2))
					# if target == 0:
					# 	target = 1
					achieved_percent = rounded(100 * total/target, 2) if target != 0 else 0
					# if achieved_percent > rounded(100,2):
					# 	row.insert(5, rounded(100,2))
					# else:
					row.insert(5, achieved_percent)
				else:
					row.insert(4, rounded(total, 2))
					# if target == 0:
					# 	target = 1
					achieved_percent = rounded(100 * total/target, 2) if target != 0 else 0
					# if achieved_percent > rounded(100,2):
					# 	row.insert(5, rounded(100,2))
					# else:
					row.insert(5, achieved_percent)		
				rp_from_date = "-" + fdate_split[1] + "-" + fdate_split[2]
				rp_to_date = "-" + tdate_split[1] + "-" + tdate_split[2]
				month = frappe.db.get_value("Report Period", {'from_date':rp_from_date, 'to_date':rp_to_date}, 'name')
				if filters.production_group == "Timber":
					row.append(total)
				if target >  0:
					# if frappe.session.user == "Administrator":
					# 	frappe.msgprint(str(target))
					overall_target +=  target
				
				overall_achieved += total 
					
				row.append(month)
				# frappe.msgprint("{0} and {1}".format(target, total))
				data.append(row)
	if overall_target > 0:
		overall_achieved_percent = rounded((overall_achieved/overall_target)*100, 2)
		# if overall_achieved_percent > flt(100):
		# 	overall_achieved_percent = flt(100)
	elif overall_target == 0 and overall_achieved > 0:
		overall_achieved_percent = rounded(100,2)
	else:
		total_achieved_percent = 0.0
	# overall_target = math.ceil(overall_target)
	# if frappe.session.user == "Administrator":
		# frappe.throw(str(overall_target))
	if filters.uom:
		if filters.branch:
			row = ["Total", "",  overall_target, "",overall_achieved, overall_achieved_percent]
		else:
			row = ["Total", "",   overall_target,"", overall_achieved, overall_achieved_percent]
	else:	
		if filters.branch:
			row = ["Total", "", overall_target,"", overall_achieved, overall_achieved_percent]
		else:
			row = ["Total", "", overall_target, "", overall_achieved, overall_achieved_percent]
	data.append(row)
	# frappe.throw(str(data))

	return data

def get_group_by(filters):
	if filters.branch:
		group_by = " group by region, branch, location, pei.uom"
	else:
		# if filters.is_company:
		group_by = " group by region, branch, pei.uom"
		# else:
		# 	group_by = " group by region, branch"

	return group_by

def get_order_by(filters):
	return " order by region, location"

def get_cc_conditions(filters):
	condition = ""
	
	if not filters.cost_center:
		return " and pe.docstatus = 10"
	else:
		if filters.branch:
			branch = str(filters.branch)
			branch = branch.replace(' - NRDCL','')
			condition += " and pe.branch = '"+branch+"'"

		else:
			ccs = []
			all_ccs = frappe.db.sql("""
				select name from `tabCost Center` where parent_cost_center = '{0}'
			""".format(filters.cost_center), as_dict= True)
			for i in all_ccs:
				ccs.append(str(i.name))
			condition += " and cc.name in {0} ".format(tuple(ccs))
	if filters.uom:
		condition += " and pei.uom = '{0}'".format(filters.uom)
	return condition

def get_filter_conditions(filters, start_date, end_date):
	condition = ""
	
	if filters.location:
		condition += " and pe.location = '{0}'".format(filters.location)

	if start_date and end_date:
		condition += " and DATE(pe.posting_date) between '{0}' and '{1}'".format(start_date, end_date)

	return condition

def get_columns(filters):
	if filters.branch:
			columns = ["Branch:Link/Branch:150", "Location:Link/Location:150", "Target Qty:Float:120", "UOM:Link/UOM:50", "Achieved Qty:Float:120", "Ach. Percent:Percent:100"]
	else:
		# if filters.is_company:
		columns = ["Branch:Link/Branch:150", "Region:Link/Cost Center:150", "Target Qty:Float:120", "UOM:Link/UOM:50", "Achieved Qty:Float:120", "Ach. Percent:Percent:100"]

	for a in get_production_groups(filters.production_group):
		columns.append(str(str(a) + ":Float:90"))

	if filters.production_group == "Timber":
		columns.append("Total:Float:120")

	if filters.display_monthly:
		columns.append("Month:Data:120")
	
	
	return columns

