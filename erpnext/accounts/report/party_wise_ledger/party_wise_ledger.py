# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SHIV		                   31/10/2016         Party Entries agains Sale of Mines,
                                                                      Normal/Abnormal Loss entries are excluded aswel
                                                                      as requested by Hap Dorji
2.0               SHIV                             11/12/2018         Following points covered
                                                                        1. cost_center column added in the report
                                                                        2. group_by_party option provided
                                                                        3. get_balances method introduced to replace
                                                                                existing logic and for better performance.
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''
from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.utils import get_child_cost_centers
from frappe.utils import flt, cint, getdate
# from erpnext.accounts.report.trial_balance.trial_balance import validate_filters


def execute(filters=None):
	validate_filters(filters)
	check_accounts(filters)

	show_party_name = is_party_name_visible(filters)
	
	columns = get_columns(filters, show_party_name)
	data = get_data(filters, show_party_name)

	return columns, data

def validate_filters(filters):
	if not filters.fiscal_year:
		frappe.throw(_("Fiscal Year {0} is required").format(filters.fiscal_year))

	fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=True)
	if not fiscal_year:
		frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
	else:
		filters.year_start_date = getdate(fiscal_year.year_start_date)
		filters.year_end_date = getdate(fiscal_year.year_end_date)

	if not filters.from_date:
		filters.from_date = filters.year_start_date

	if not filters.to_date:
		filters.to_date = filters.year_end_date

	filters.from_date = getdate(filters.from_date)
	filters.to_date = getdate(filters.to_date)

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))

	if (filters.from_date < filters.year_start_date) or (filters.from_date > filters.year_end_date):
		frappe.msgprint(_("From Date should be within the Fiscal Year. Assuming From Date = {0}")\
			.format(formatdate(filters.year_start_date)))

		filters.from_date = filters.year_start_date

	if (filters.to_date < filters.year_start_date) or (filters.to_date > filters.year_end_date):
		frappe.msgprint(_("To Date should be within the Fiscal Year. Assuming To Date = {0}")\
			.format(formatdate(filters.year_end_date)))
		filters.to_date = filters.year_end_date

# Following code added by SHIV on 2018/12/11
# For better performance
def get_data(filters, show_party_name):
	party_name_field = "customer_name" if filters.get("party_type")=="Customer" else "supplier_name" if filters.get("party_type")=="Supplier" else "employee_name" if filters.get("party_type")=="Employee" else "equipment_model"
	if not filters.get("inter_company"):
		parties = frappe.get_all(filters.get("party_type"), fields = ["name", party_name_field], order_by="name")
	elif filters.get("party_type") == "Employee":
		parties = frappe.get_all(filters.get("party_type"), fields = ["name", party_name_field], order_by="name")
	else:
		parties = frappe.get_all(filters.get("party_type"), fields = ["name", party_name_field], filters = {"inter_company": 1}, order_by="name")
	
	company_currency = frappe.db.get_value("Company", filters.company, "default_currency")

	party_balances = get_balances(filters)

	data = []
	tot_op_dr, tot_op_cr, total_debit, total_credit, tot_cl_dr, tot_cl_cr = 0, 0, 0, 0, 0, 0
	for party in parties:
                if party_balances.get(party.name):
                        for cc, values in party_balances.get(party.name).iteritems():
                                row = {"party": party.name, "cost_center": cc}
                                opening_debit, opening_credit, debit, credit = values
                                
                                #row = { "party": party.name}
                                if show_party_name:
                                        row["party_name"] = party.get(party_name_field)

                                '''     
                                # opening
                                opening_debit, opening_credit = opening_balances.get(party.name, [0, 0])
                                row.update({
                                        "opening_debit": opening_debit,
                                        "opening_credit": opening_credit
                                })
                                '''
                                tot_op_dr += flt(opening_debit)
                                tot_op_cr += flt(opening_credit)
                                '''
                                # within period
                                debit, credit = balances_within_period.get(party.name, [0, 0])
                                row.update({
                                        "debit": debit,
                                        "credit": credit
                                })
                                '''
                                row.update({"opening_debit": opening_debit, "opening_credit": opening_credit, "debit": debit, "credit": credit})
                                
                                # totals
                                total_debit += debit
                                total_credit += credit
                                
                                # closing
                                closing_debit, closing_credit = toggle_debit_credit(opening_debit + debit, opening_credit + credit)
                                row.update({
                                        "closing_debit": closing_debit,
                                        "closing_credit": closing_credit
                                })

                                tot_cl_dr += flt(closing_debit)
                                tot_cl_cr += flt(closing_credit)
                                
                                row.update({
                                        "currency": company_currency
                                })
                                
                                has_value = False
                                if (opening_debit or opening_credit or debit or credit or closing_debit or closing_credit):
                                        has_value  =True
                                
                                if cint(filters.show_zero_values) or has_value:
                                        data.append(row)

	# Add total row
	if total_debit or total_credit:
		data.append({
			"party": "'" + _("Totals") + "'",
                        "opening_debit": tot_op_dr,
			"opening_credit": tot_op_cr,
			"debit": total_debit,
			"credit": total_credit,
			"currency": company_currency,
                        "closing_debit": tot_cl_dr,
			"closing_credit": tot_cl_cr
		})
	
	return data

# Following code added and commented by SHIV on 2018/11/12
# This method basically introduced cost_center wise party details while using the existing
#       methods get_opening_balances and get_balances_within_period which seem to execute
#       similar queries twice resulting in performance issue.
"""
def get_data(filters, show_party_name):
	#party_name_field = "customer_name" if filters.get("party_type")=="Customer" else "supplier_name"
	#Party type to be shown in the report Kinley Tsheirng
	party_name_field = "customer_name" if filters.get("party_type")=="Customer" else "supplier_name" if filters.get("party_type")=="Supplier" else "employee_name"
	if not filters.get("inter_company"):
		parties = frappe.get_all(filters.get("party_type"), fields = ["name", party_name_field], order_by="name")
	elif filters.get("party_type") == "Employee":
		parties = frappe.get_all(filters.get("party_type"), fields = ["name", party_name_field], order_by="name")
	else:
		parties = frappe.get_all(filters.get("party_type"), fields = ["name", party_name_field], filters = {"inter_company": 1}, order_by="name")
	
	company_currency = frappe.db.get_value("Company", filters.company, "default_currency")
	opening_balances = get_opening_balances(filters)
	balances_within_period = get_balances_within_period(filters)

	data = []
	tot_op_dr, tot_op_cr, total_debit, total_credit, tot_cl_dr, tot_cl_cr = 0, 0, 0, 0, 0, 0

	for party in parties:
                cc_list = []

                if opening_balances.get(party.name):
                        for cc in opening_balances.get(party.name):
                                if cc not in cc_list:
                                        cc_list.append(cc)

                if balances_within_period.get(party.name):
                        for cc in balances_within_period.get(party.name):
                                if cc not in cc_list:
                                        cc_list.append(cc)

                if filters.get("group_by_party"):
                        pass
                else:
                for cc in cc_list:
                        #row = { "party": party.name }  #Replaced by following line by SHIV on 2018/12/11
                        row = {"party": party.name, "cost_center": cc}
                        
                        if show_party_name:
                                row["party_name"] = party.get(party_name_field)

                        # opening
                        #opening_debit, opening_credit = opening_balances.get(party.name, [0, 0])       #Replaced by following line by SHIV on 2018/12/11
                        opening_debit, opening_credit = opening_balances.get(party.name).get(cc, [0,0]) if opening_balances.get(party.name) else [0,0]
                        
                        row.update({
                                "opening_debit": opening_debit,
                                "opening_credit": opening_credit
                        })

                        tot_op_dr += flt(opening_debit)
                        tot_op_cr += flt(opening_credit)
                        
                        # within period
                        #debit, credit = balances_within_period.get(party.name, [0, 0])         #Replaced by following line by SHIV on 2018/12/11
                        debit, credit = balances_within_period.get(party.name).get(cc, [0,0]) if balances_within_period.get(party.name) else [0, 0]
                        
                        row.update({
                                "debit": debit,
                                "credit": credit
                        })
                        
                        # totals
                        total_debit += debit
                        total_credit += credit
                        
                        # closing
                        closing_debit, closing_credit = toggle_debit_credit(opening_debit + debit, opening_credit + credit)
                        row.update({
                                "closing_debit": closing_debit,
                                "closing_credit": closing_credit
                        })

                        tot_cl_dr += flt(closing_debit)
                        tot_cl_cr += flt(closing_credit)
                        
                        row.update({
                                "currency": company_currency
                        })
                        
                        has_value = False
                        if (opening_debit or opening_credit or debit or credit or closing_debit or closing_credit):
                                has_value  =True
                        
                        if cint(filters.show_zero_values) or has_value:
                                data.append(row)

	# Add total row
	if total_debit or total_credit:
		data.append({
			"party": "'" + _("Totals") + "'",
                        "opening_debit": tot_op_dr,
			"opening_credit": tot_op_cr,
			"debit": total_debit,
			"credit": total_credit,
			"currency": company_currency,
                        "closing_debit": tot_cl_dr,
			"closing_credit": tot_cl_cr
		})
	
	return data
"""

# Following code commented by SHIV on 2018/12/11
"""
def get_data(filters, show_party_name):
	#party_name_field = "customer_name" if filters.get("party_type")=="Customer" else "supplier_name"
	#Party type to be shown in the report Kinley Tsheirng
	party_name_field = "customer_name" if filters.get("party_type")=="Customer" else "supplier_name" if filters.get("party_type")=="Supplier" else "employee_name"
	if not filters.get("inter_company"):
		parties = frappe.get_all(filters.get("party_type"), fields = ["name", party_name_field], order_by="name")
	elif filters.get("party_type") == "Employee":
		parties = frappe.get_all(filters.get("party_type"), fields = ["name", party_name_field], order_by="name")
	else:
		parties = frappe.get_all(filters.get("party_type"), fields = ["name", party_name_field], filters = {"inter_company": 1}, order_by="name")
	
	company_currency = frappe.db.get_value("Company", filters.company, "default_currency")
	opening_balances = get_opening_balances(filters)
	balances_within_period = get_balances_within_period(filters)
	
	data = []
	tot_op_dr, tot_op_cr, total_debit, total_credit, tot_cl_dr, tot_cl_cr = 0, 0, 0, 0, 0, 0
	for party in parties:
		row = { "party": party.name }
		if show_party_name:
			row["party_name"] = party.get(party_name_field)
		
		# opening
		opening_debit, opening_credit = opening_balances.get(party.name, [0, 0])
		row.update({
			"opening_debit": opening_debit,
			"opening_credit": opening_credit
		})

		tot_op_dr += flt(opening_debit)
		tot_op_cr += flt(opening_credit)
		
		# within period
		debit, credit = balances_within_period.get(party.name, [0, 0])
		row.update({
			"debit": debit,
			"credit": credit
		})
		
		# totals
		total_debit += debit
		total_credit += credit
		
		# closing
		closing_debit, closing_credit = toggle_debit_credit(opening_debit + debit, opening_credit + credit)
		row.update({
			"closing_debit": closing_debit,
			"closing_credit": closing_credit
		})

		tot_cl_dr += flt(closing_debit)
		tot_cl_cr += flt(closing_credit)
		
		row.update({
			"currency": company_currency
		})
		
		has_value = False
		if (opening_debit or opening_credit or debit or credit or closing_debit or closing_credit):
			has_value  =True
		
		if cint(filters.show_zero_values) or has_value:
			data.append(row)

	# Add total row
	if total_debit or total_credit:
		data.append({
			"party": "'" + _("Totals") + "'",
                        "opening_debit": tot_op_dr,
			"opening_credit": tot_op_cr,
			"debit": total_debit,
			"credit": total_credit,
			"currency": company_currency,
                        "closing_debit": tot_cl_dr,
			"closing_credit": tot_cl_cr
		})
	
	return data
"""

def get_balances(filters):
        filters.accounts    = None if filters.get("accounts") == '%' else filters.get("accounts")
        # filters.cost_center = None if filters.get("cost_center") == '%' else filters.get("cost_center")
        cond = ""
	if not filters.cost_center:
		return ""
	if not filters.branch:
		a= ''
		all_ccs = get_child_cost_centers(filters.cost_center)
		a = " and cost_center in {0}".format(tuple(all_ccs))
		cond = a
		# frappe.msgprint("{}".format(cond))

	else:
		branch = str(filters.get("branch"))
		cond = " and cost_center = \'"+branch+"\'"
        cond += " and account = '{0}'".format(filters.accounts) if filters.get("accounts") else ""
        # cond += " and cost_center in '{0}'".format(cond)
        sql = """
		select
                        {group_by} as cost_center,
                        sum(case when ifnull(is_opening, 'No') = 'Yes' or posting_date < '{from_date}' then ifnull(debit,0) else 0 end) as opening_debit,
                        sum(case when ifnull(is_opening, 'No') = 'Yes' or posting_date < '{from_date}' then ifnull(credit,0) else 0 end) as opening_credit,
                        sum(case when ifnull(is_opening, 'No') = 'No' and posting_date between '{from_date}' and '{to_date}' then ifnull(debit,0) else 0 end) as debit,
                        sum(case when ifnull(is_opening, 'No') = 'No' and posting_date between '{from_date}' and '{to_date}' then ifnull(credit,0) else 0 end) as credit
		from `tabGL Entry` as ge
		where company='{company}' 
		and ifnull(party_type, '') = '{party_type}' and ifnull(party, '') != ''
		and posting_date <= '{to_date}'
		{cond}
		and ge.account not in ('Normal Loss - SMCL','Abnormal Loss - SMCL', 'TDS - 2%% - CDCL', 'TDS - 3%% - CDCL', 'TDS - 5%% - CDCL', 'TDS - 10%% - CDCL')
		and not exists(select 1 from `tabAccount` as ac
                                where ac.name = ge.account
                                and ac.parent_account = 'Sale of mines product - SMCL')
	group by {group_by}""".format(
                company = filters.company,
                from_date = filters.from_date,
                to_date = filters.to_date,
                party_type = filters.party_type,
			
                group_by = "party,''" if filters.get("group_by_party") else "party, cost_center",
				cond = cond
        )
	# frappe.msgprint("{}".format(sql))
	gle = frappe.db.sql(sql, as_dict=True)
	
	balances = frappe._dict()
	# frappe.msgprint("test. '{}'.".format(balances))
	for d in gle:
		opening_debit, opening_credit = toggle_debit_credit(d.opening_debit, d.opening_credit)
                balances.setdefault(d.party, frappe._dict()).setdefault(d.cost_center, [opening_debit, opening_credit, flt(d.debit), flt(d.credit)])
	return balances
	
def get_opening_balances(filters):
        # Ver 1.0 by SSK on 31/10/2016 Begins, Following condition is added
        '''
        and ge.account not in ('Normal Loss - SMCL','Abnormal Loss - SMCL')
        and not exists(select 1 from `tabAccount` as ac
                        where ac.name = ge.account
                        and ac.parent_account = 'Sale of mines product - SMCL')
        '''
	cond = ""
    	if not filters.cost_center:
		return ""
	if not filters.branch:
		all_ccs = get_child_cost_centers(filters.cost_center)
		cond = " and cost_center in (select b.name from `tabCost Center` cc, `tabBranch` b where b.cost_center = cc.name and cc.name in {0})".format(tuple(all_ccs))

	else:
		branch = str(filters.get("branch"))
		branch = branch.replace(' - NRDCL','')
		cond = " and cost_center = \'"+branch+"\'"   
	
	gle = frappe.db.sql("""
		select party, cost_center, sum(debit) as opening_debit, sum(credit) as opening_credit 
		from `tabGL Entry` as ge
		where company=%(company)s 
		and ifnull(party_type, '') = %(party_type)s and ifnull(party, '') != ''
		and (posting_date < %(from_date)s or ifnull(is_opening, 'No') = 'Yes')
		and account LIKE %(account)s
		and cost_center in %(cost_center)s
		and ge.account not in ('Normal Loss - SMCL','Abnormal Loss - SMCL', 'TDS - 2%% - CDCL', 'TDS - 3%% - CDCL', 'TDS - 5%% - CDCL', 'TDS - 10%% - CDCL')
		and not exists(select 1 from `tabAccount` as ac
                                where ac.name = ge.account
                                and ac.parent_account = 'Sale of mines product - SMCL')
		group by party, cost_center""", {
			"company": filters.company,
			"from_date": filters.from_date,
			"party_type": filters.party_type,
			"account": filters.accounts,
			"cost_center": cond
		}, as_dict=True)
		
	opening = frappe._dict()
	for d in gle:
		opening_debit, opening_credit = toggle_debit_credit(d.opening_debit, d.opening_credit)
		#opening.setdefault(d.party, [opening_debit, opening_credit])           #Replaced by following line by SHIV on 2018/12/11
		opening.setdefault(d.party, frappe._dict()).setdefault(d.cost_center, [opening_debit, opening_credit])
		
	return opening
	
def get_balances_within_period(filters):
        # Ver 1.0 by SSK on 31/10/2016 Begins, Following condition is added
        '''
        and ge.account not in ('Normal Loss - SMCL','Abnormal Loss - SMCL')
        and not exists(select 1 from `tabAccount` as ac
                        where ac.name = ge.account
                        and ac.parent_account = 'Sale of mines product - SMCL')
        '''
    	cond = ""
    	if not filters.cost_center:
		return ""
	if not filters.branch:
		all_ccs = get_child_cost_centers(filters.cost_center)
		cond = " and cost_center in (select b.name from `tabCost Center` cc, `tabBranch` b where b.cost_center = cc.name and cc.name in {0})".format(tuple(all_ccs))

	else:
		branch = str(filters.get("branch"))
		branch = branch.replace(' - NRDCL','')
		cond = " and cost_center = \'"+branch+"\'"   
	gle = frappe.db.sql("""
		select party, cost_center, sum(debit) as debit, sum(credit) as credit 
		from `tabGL Entry` as ge
		where company=%(company)s 
		and ifnull(party_type, '') = %(party_type)s and ifnull(party, '') != ''
		and posting_date >= %(from_date)s and posting_date <= %(to_date)s 
		and ifnull(is_opening, 'No') = 'No'
		and account LIKE %(account)s
		and cost_center in  %(cost_center)s
		and ge.account not in ('Normal Loss - SMCL','Abnormal Loss - SMCL', 'TDS - 2%% - CDCL', 'TDS - 3%% - CDCL', 'TDS - 5%% - CDCL', 'TDS - 10%% - CDCL')
                and not exists(select 1 from `tabAccount` as ac
                                where ac.name = ge.account
                                and ac.parent_account = 'Sale of mines product - SMCL')		
		group by party, cost_center""", {
			"company": filters.company,
			"from_date": filters.from_date,
			"to_date": filters.to_date,
			"party_type": filters.party_type,
			"cost_center": cond,
			"account": filters.accounts
		}, as_dict=True)
		
	balances_within_period = frappe._dict()
	for d in gle:
		#balances_within_period.setdefault(d.party, [d.debit, d.credit])        #Replaced by following line by SHIV on 2018/12/11
                balances_within_period.setdefault(d.party, frappe._dict()).setdefault(d.cost_center, [d.debit, d.credit])
		
	return balances_within_period
	
def toggle_debit_credit(debit, credit):
	if flt(debit) > flt(credit):
		debit = flt(debit) - flt(credit)
		credit = 0.0
	else:
		credit = flt(credit) - flt(debit)
		debit = 0.0
		
	return debit, credit
	
def get_columns(filters, show_party_name):
	columns = [
		{
			"fieldname": "party",
			"label": _(filters.party_type),
			"fieldtype": "Link",
			"options": filters.party_type,
			"width": 200
		},
		{
			"fieldname": "opening_debit",
			"label": _("Opening (Dr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "opening_credit",
			"label": _("Opening (Cr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "debit",
			"label": _("Debit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "credit",
			"label": _("Credit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "closing_debit",
			"label": _("Closing (Dr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "closing_credit",
			"label": _("Closing (Cr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		}
	]
	
	if show_party_name:
		columns.insert(1, {
			"fieldname": "party_name",
			"label": _(filters.party_type) + " Name",
			"fieldtype": "Data",
			"width": 200
		})

	if not filters.get("group_by_party"):
                columns.append({
			"fieldname": "cost_center",
			"label": _("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 200
		})
	return columns
		
def is_party_name_visible(filters):
	if filters.get("party_type") == "Employee":
		return True;

	show_party_name = False
	if filters.get("party_type") == "Customer":
		party_naming_by = frappe.db.get_single_value("Selling Settings", "cust_master_name")
	elif filters.get("party_type") == "Equipment":
		party_naming_by = "Equipment Number"
		show_party_name = True
	else:
		party_naming_by = frappe.db.get_single_value("Buying Settings", "supp_master_name")
		
	if party_naming_by == "Naming Series":
		show_party_name = True
		
	return show_party_name

def check_accounts(filters):
	if not filters.accounts:
		filters.accounts = '%'
