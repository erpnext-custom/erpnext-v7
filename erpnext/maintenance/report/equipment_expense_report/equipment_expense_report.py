# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	columns = get_columns()
	query = construct_query(filters)
	data = get_data(query, filters = None)

def get_conditions(filters):
	branch = consumption_date = rate_date = jc_date = insurance_date =  reg_date = tc_date = operator_date = le_date = ss_date= reg_date = not_cdcl = disable =  ""
	if filters.get("branch"):
		branch += str(filters.branch)

	if filters.get("not_cdcl"):
                not_cdcl +=  "0"
        
        if filters.get("include_disabled"):
                disable  += " "
        else:
                disable  += "0" 

	if filters.get("from_date") and filters.get("to_date"):
		consumption_date = get_dates(filters, "vl", "from_date", "to_date")
		rate_date 	 = get_dates(filters, "pol", "date")
		jc_date 	 = get_dates(filters, "jc", "finish_date")
		insurance_date   = get_dates(filters, "ins", "insured_date")
		operator_date    = get_dates(filters, "op", "start_date", "end_date")
		tc_date		 = get_dates(filters, "tc", "posting_date")		
		le_date		 = get_dates(filters, "le", "encashed_date")
		ss_date		 = get_dates(filters, "ss", "start_date", "ifnull(end_date,curdate())")
		reg_date	 = get_dates(filters, "reg", "registration_date")
	
	return branch, consumption_date, rate_date, jc_date, insurance_date, reg_date,  operator_date, tc_date, le_date, ss_date, not_cdcl, disable

def get_dates(filters, module = "", from_date_column = "", to_date_column = ""):
	cond1 = ""
	cond2 = ""
	if from_date_column:
		cond1 = ("{0} between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'").format(from_date_column)
	
	if to_date_column:
		if module in ("op","ss"):
			cond2 = str(" or {0} between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'").format(to_date_column)
		else:
			cond2 = str("and {0} between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'").format(to_date_column)

	return "({0} {1})".format(cond1, cond2)

def get_data(filters):
	branch, consumption_date, rate_date, jc_date, insurance_date,  reg_date, operator_date, tc_date, le_date, ss_date, not_cdcl, disable  =  get_conditions(filters)
	#frappe.msgprint(reg_date)
	data = []
	branch_cond = " branch = '{0}'".format(branch) if branch else "branch = branch"
        not_cdcll = " where not_cdcl = '{0}'".format(not_cdcl) if not_cdcl else "where not_cdcl = not_cdcl"
        dis     = " is_disabled = '{0}'".format(disable)
        #branch_cond = " where branch = '{0}'".format(branch) if branch else ""

        equipments = frappe.db.sql("""
                                select name, branch, equipment_number, equipment_type, equipment_model
                                from `tabEquipment`
                                {0} and 
                                {1} and 
                                {2}
                                order by branch, name
                        """.format(not_cdcll, branch_cond, dis), as_dict=1)

	'''equipments = frappe.db.sql("""
                                select name, branch, equipment_number, equipment_type
                                from `tabEquipment`
                                {0}
                                order by branch, name
                        """.format(branch_cond), as_dict=1)'''

	frappe.msgprint(equipments)
    	for eq in equipments:
		#:frappe.msgprint("{0}".format(eq))
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
				{2}
                    """.format(eq.name, rate_date, rate_cond), as_dict=1)[0]

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

	if filters.get("branch"):
		query += " and jc.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		 query += " and jc.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
		 # and start_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\' OR end_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	query += " group by k.equipment_number "
	return query

def get_columns():
	cols = [
		("Registration No") + ":data:120",
		("Equipment Type.") + ":data:120",
		("Goods Amount(Nu.)")+":currency:100",
		("Service Amount(Nu.)")+":currency:100",
		("HSD Amount(Nu.)")+":currency:100",
		("Gross Salary(Nu.)")+":currency:100",
		("Travel Claim(Nu.)")+":currency:100",
		("Leave Encashment(Nu.)")+":currency:120",
		("Total Expense(Nu.)")+":currency:100",
	]
	return cols
