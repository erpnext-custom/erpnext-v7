# Copyright (c) 2016, Druk Holding & Investments Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.utils import date_diff, get_last_day

##
#Return number of days between two dates or zero 
##
def get_number_of_days(end_date=None, start_date=None):
	if start_date and end_date:
		num_of_days = date_diff(start_date, end_date)
	else:
		num_of_days = 0
	
	return num_of_days

# Ver 20160627.1 by SSK, Fetching the latest
@frappe.whitelist()
def get_loss_tolerance():
    loss_tolerance = frappe.db.sql("select name,loss_tolerance,loss_qty_flat from `tabLoss Tolerance` order by creation desc limit 1;");
    #msgprint(_("Fetching Loss Tolerance {0}").format(loss_tolerance))
    return (loss_tolerance);

# Ver 20160627.1 by SSK, Fetching the latest
@frappe.whitelist()
def get_parent_cost_center(temp):
    parent_cc = frappe.db.sql("select name from `tabCost Center`;");
    return (parent_cc);

##
#Return all the child cost centers of the current cost center
##
def get_child_cost_centers(current_cs=None):
	allchilds = allcs = [];
	cs_name = cs_par_name = "";

	if current_cs:
	  #Get all cost centers
	  allcs = frappe.db.sql("SELECT name, parent_cost_center FROM `tabCost Center`", as_dict=True);
	  #get the current cost center name
	  query ="SELECT name, parent_cost_center FROM `tabCost Center` where name = \"" + current_cs + "\";";
	  current = frappe.db.sql(query, as_dict=True);

	  if(current):
	    for a in current:
    		cs_name = a['name'];
    		cs_par_name = a['parent_cost_center'];

	    #loop through the cost centers to search for the child cost centers
	    allchilds.append(cs_name);
	    for b in allcs:
    		for c in allcs:
    		      if(c['parent_cost_center'] in allchilds):
        			 if(c['name'] not in allchilds):
        			    allchilds.append(c['name']);

	return allchilds;

##
#Return all the child accounts of the current accounts
##
def get_child_accounts(current_acc=None):
	allchilds = allacc = [];
	acc_name = acc_parent_name = "";

	if current_acc:
	  #Get all cost centers
	  allacc = frappe.db.sql("SELECT name, parent_account FROM `tabAccount`", as_dict=True);
	  #get the current cost center name
	  query ="SELECT name, parent_account FROM `tabAccount` where name = \"" + current_acc + "\";";
	  current = frappe.db.sql(query, as_dict=True);

	  if(current):
	    for a in current:
    		acc_name = a['name'];
    		acc_parent_name = a['parent_account'];

	    #loop through the cost centers to search for the child cost centers
	    allchilds.append(acc_name);

	    for b in allacc:
    		for c in allacc:
    		      if(c['parent_account'] in allchilds):
        			 if(c['name'] not in allchilds):
        			    allchilds.append(c['name']);

	return allchilds;


##
#Get the budget consumed in the financial year
##
def get_budget_consumed_final(self, fiscal, com):
	gl_budgets = frappe.db.sql("""select gl.account, gl.debit, gl.credit,
			gl.cost_center from `tabGL Entry` gl, `tabBudget Detail` bd
			where gl.fiscal_year=%s and company=%s and bd.account=gl.account
			and bd.parent=gl.cost_center"""% ('%s','%s'),
			(fiscal if fiscal else get_fiscal_year(), com if com else get_company), as_dict=True);

	gl_consumed_budgets = frappe._dict()
	for d in gl_budgets:
		gl_consumed_budgets.setdefault((d.cost_center + " " + d.account), 0)
		gl_consumed_budgets[(d.cost_center + " " + d.account)] += (flt(flt(d.debit) - flt(d.credit)))

    	in_budgets = frappe.db.sql("""
            select poi.cost_center, poi.budget_account, pii.amount
            from `tabPurchase Receipt Item` as pii
            JOIN `tabPurchase Order Item` as poi
	           ON pii.prevdoc_docname = poi.parent
            JOIN `tabBudget Detail` as bd
	           ON poi.cost_center = bd.parent AND poi.budget_account = bd.account
            WHERE bd.fiscal_year = %S AND bd.company=%s
            """%('%s','%s'), (fiscal if fiscal else get_fiscal_year(), com if com else get_company), as_dict=True)

	invoice_consumed_budget = frappe._dict()
	for d in in_budgets:
		invoice_consumed_budget.setdefault((d.cost_center + " " + d.account), 0)
		invoice_consumed_budget[(d.cost_center + " " + d.account)] += (flt(flt(d.debit) - flt(d.credit)))



##
#Get the budget allocated in the financial year
##
def get_budget_allocated_final(self, fiscal, com):
	return frappe._dict(frappe.db.sql("select concat(parent,\" \",account) AS mcc_acc, budget_allocated from `tabBudget Detail` WHERE fiscal_year=\'" + str(fiscal if fiscal else get_fiscal_year()) + "\'"))

##
#Get commited budget details from purchase order
##
def get_budget_committed_final(self, fiscal, com):
        com_details = frappe._dict(frappe.db.sql("""
	    SELECT concat(poi.cost_center,\" \", poi.budget_account) AS cc_acc, poi.amount
		FROM `tabPurchase Order Item` AS poi
	    JOIN `tabBudget Detail` AS bd
	        ON poi.cost_center = bd.parent AND poi.budget_account = bd.account
	    JOIN `tabPurchase Order` AS po
	        ON po.name = poi.parent
		LEFT JOIN `tabPurchase Invoice Item` AS pii
			ON pii.purchase_order = po.name
		LEFT JOIN `tabPurchase Invoice` AS pi
			ON pi.name = pii.parent
	    WHERE (po.status IN ('To Receive and Bill', 'To Bill') OR pi.outstanding_amount > 0)
                            AND bd.fiscal_year=%s""",fiscal if fiscal else get_fiscal_year()))

	return com_details

##
#Set default fiscal year
##
def get_fiscal_year(self):
    return frappe.utils.nowdate()[:4]

##
#Set default company
##
def get_company(self):
    return frappe.defaults.get_user_default("company")

##
#Get the budget consumed in the financial year
##
def get_budget_consumed(self, fiscal, com):
	consumed_budgets = frappe.db.sql("""select gl.account, gl.debit, gl.credit,
			gl.cost_center from `tabGL Entry` gl, `tabBudget Detail` bd
			where gl.fiscal_year=%s and company=%s and bd.account=gl.account
			and bd.parent=gl.cost_center"""% ('%s','%s'),
			(fiscal, com), as_dict=True);

	con_details = frappe._dict()
	for d in consumed_budgets:
		con_details.setdefault((d.cost_center + " " + d.account), 0)
		con_details[(d.cost_center + " " + d.account)] += (flt(flt(d.debit) - flt(d.credit)))
	return con_details;

##
#Get the budget allocated in the financial year
#
def get_budget_allocated(self, fiscal, com):
	return frappe._dict(frappe.db.sql("select concat(parent,\" \",account) AS mcc_acc, budget_allocated from `tabBudget Detail` WHERE fiscal_year=\'" + str(fiscal) + "\'"))


#Get commited budget details from purchase order
def get_budget_committed(self, fiscal, com):
        com_details = frappe._dict(frappe.db.sql("""
	        SELECT concat(poi.cost_center,\" \", poi.budget_account) AS cc_acc, poi.amount
		FROM `tabPurchase Order Item` AS poi
	        JOIN `tabBudget Detail` AS bd
	        	        ON poi.cost_center = bd.parent AND poi.budget_account = bd.account
	        JOIN `tabPurchase Order` AS po
	                ON po.name = poi.parent
		LEFT JOIN `tabPurchase Invoice Item` AS pii
			ON pii.purchase_order = po.name
		LEFT JOIN `tabPurchase Invoice` AS pi
			ON pi.name = pii.parent
	        WHERE (po.status IN ('To Receive and Bill', 'To Bill') OR pi.outstanding_amount > 0) AND bd.fiscal_year=%s""",fiscal))

	return com_details
