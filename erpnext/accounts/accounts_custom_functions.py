# Copyright (c) 2016, Druk Holding & Investments Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

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
			for b in allcs:
				if(b['parent_cost_center'] == cs_name):
					allchilds.append(str(b['name']));
					for c in allcs:
						if(c['parent_cost_center'] == b['name']):
							allchilds.append(str(c['name']));
			
			#lastly add itself 
			allchilds.append(str(cs_name));	
	
	return allchilds;

