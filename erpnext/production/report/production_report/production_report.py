# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_child_cost_centers
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	conditions = get_conditions(filters)
	group_by = get_group_by(filters)
	order_by = get_order_by(filters)
	total_qty = '1'
	if filters.show_aggregate:
		total_qty = "sum(ppi.qty) as total_qty"
	# Uncomment below line of code for debug purposes only //Kinley Oorji 2021-08-21
	frappe.errprint("total_qty = "+str(total_qty)+" || conditions = "+str(conditions)+" || group_by = "+str(group_by)+" || order by = "+str(order_by))
	query = "select  pp.name as ref_doc, ppi.challan_no, pp.posting_date, ppi.item_code, ppi.item_name, ppi.item_group, ppi.item_sub_group, ppi.qty, ppi.uom, pp.branch, pp.location, pp.adhoc_production, pp.company, ppi.warehouse, (select ts.timber_class from `tabTimber Species` ts where ts.name = ppi.timber_species) as timber_class, (select ts.timber_type from `tabTimber Species` ts where ts.name = ppi.timber_species) as timber_type, ppi.timber_species, (select cc.parent_cost_center from `tabCost Center` cc where cc.name = (select b.cost_center from `tabBranch` b where b.name = pp.branch)) as region, {0}, pp.cable_line_no as cable_line_no, pp.production_area as production_area from `tabProduction` pp, `tabProduction Product Item` ppi  where pp.name = ppi.parent and pp.docstatus = 1 {1} {2} {3}".format(total_qty, conditions, group_by, order_by)
	abbr = " - " + str(frappe.db.get_value("Company", filters.company, "abbr"))
	# if frappe.session.user == "Administrator":
	# 	frappe.throw(query)

	total_qty = 0
	for a in frappe.db.sql(query, as_dict=1):
		a.region = str(a.region).replace(abbr, "")
		if filters.show_aggregate:
			a.qty = a.total_qty
		total_qty += flt(a.qty)
		data.append(a)
	data.append({"qty": total_qty, "region": frappe.bold("TOTAL")})

	return data

def get_group_by(filters):
	if filters.show_aggregate:
		group_by = " group by region, pp.branch, ppi.item_sub_group"
		# group_by = " group by pe.branch, pe.location, pe.item_sub_group"
	else:
		group_by = " "

	return group_by

def get_order_by(filters):
	return " order by region, pp.location, ppi.item_group, ppi.item_sub_group"

def get_conditions(filters):
	if not filters.cost_center:
		return ""

	# all_ccs = get_child_cost_centers(filters.cost_center)
	# if not all_ccs:
	# 	return " and pe.docstatus = 10"

	if not filters.branch:	
		# all_branch = [str("DUMMY")]
		# # for a in all_ccs:
		# branch = frappe.db.sql("select b.name as name from tabBranch b, `tabCost Center` cc where cc.parent_cost_center = %s and b.cost_center = cc.name", filters.cost_center, as_dict=True)
	

		# if branch:
		# 	for a in branch:
		# 		all_branch.append(str(a['name']))
		all_ccs = get_child_cost_centers(filters.cost_center)
		condition = " and pp.branch in (select b.name from `tabCost Center` cc, `tabBranch` b where b.cost_center = cc.name and cc.name in {0})".format(tuple(all_ccs))
	else:
		branch = str(filters.get("branch"))
		branch = branch.replace(' - NRDCL','')
		condition = " and pp.branch = \'"+branch+"\'"
		# frappe.throw("branch ="+branch+" condtion ="+condition)

	if filters.production_type != "All":
		condition += " and pp.production_type = '{0}'".format(filters.production_type)

	if filters.timber_type != "All":
		condition += " and exists(select 1 from `tabTimber Species` ts where ts.name = ppi.name and ts.timber_type  = '{0}')".format(filters.timber_type)

	if filters.location:
		condition += " and pp.location = '{0}'".format(filters.location)

	if filters.adhoc_production:
		condition += " and pp.adhoc_production = '{0}'".format(filters.adhoc_production)
	
	if filters.uom:
		condition += " and ppi.uom = '{0}'".format(filters.uom)
	
	if filters.supplier:
		condition += " and pp.supplier = '{0}'".format(filters.supplier)

	if filters.item_group:
		condition += " and ppi.item_group = '{0}'".format(filters.item_group)

	if filters.item_sub_group:
		condition += " and ppi.item_sub_group = '{0}'".format(filters.item_sub_group)

	if filters.item:
		condition += " and ppi.item_code = '{0}'".format(filters.item)
	
	if filters.get("timber_prod_group"):
		if filters.get("tp_sub_group"):
			condition += " and ppi.item_sub_group = '" + str(filters.tp_sub_group) + "'"
		
		else:
			if filters.timber_prod_group == "Timber By-Product":
				condition += " and ppi.item_sub_group in ('Firewood, Bhutan Furniture','BBPL firewood','Firewood(BBPL)','Firewood (Bhutan Ply)','Firewood','Post','Bakals','Woodchips','Briquette','Off-cuts/Sawn timber waste','Off-Cuts','Saw Dust')"

			elif filters.timber_prod_group == "Timber Finished Product":
				condition += " and ppi.item_sub_group in ('Joinery Products','Glulaminated Product')"

			elif filters.timber_prod_group == "Nursery and Plantation":
				condition += " and ppi.item_sub_group in ('Tree Seedlings','Flower Seedlings')"

			else:
				condition += " and ppi.item_sub_group in ('Log','Pole','Hakaries','Sawn','Field Sawn','Block','Block (Special Size)')"

	if filters.from_date and filters.to_date:
		condition += " and date(pp.posting_date) between '{0}' and '{1}'".format(filters.from_date, filters.to_date)

	if filters.timber_species:
		condition += " and ppi.timber_species = '{0}'".format(filters.timber_species)

	if filters.timber_class:
		condition += " and exists(select 1 from `tabTimber Species` ts where ts.name = ppi.timber_species and ts.timber_class  = '{0}')".format(filters.timber_class)

	if filters.warehouse:
		condition += " and ppi.warehouse = '{0}'".format(filters.warehouse)
	
	if filters.production_area:
		if filters.production_area != "All":
			condition += " and pp.production_area = '{0}'".format(filters.production_area)
	
	if filters.challan_no:
		condition += " and ppi.challan_no = '{}'".format(filters.challan_no)

	return condition

def get_columns(filters):
	columns = [
		{
			"fieldname": "region",
			"label": "Region",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "branch",
			"label": "Branch",
			"fieldtype": "Link",
			"options": "Branch",
			"width": 120
		},
		{
			"fieldname": "location",
			"label": "Location",
			"fieldtype": "Link",
			"options": "Location",
			"width": 120
		},
		{
			"fieldname": "item_group",
			"label": "Group",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "item_sub_group",
			"label": "Sub Group",
			"fieldtype": "Link",
			"options": "Item Sub Group",
			"width": 120
		},
		{
			"fieldname": "qty",
			"label": "Quantity",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "uom",
			"label": "UOM",
			"fieldtype": "Link",
			"options": "UoM",
			"width": 100
		},
	]

	if not filters.show_aggregate:
		columns.insert(0,{
			"fieldname": "ref_doc",
			"label": "PR Reference",
			"fieldtype": "Link",
			"options": "Production",
			"width": 120
		})
		columns.insert(1,{
			"fieldname": "challan_no",
			"label": "Challan No",
			"fieldtype": "Data",
			"width": 120
		})

		columns.insert(2, {
			"fieldname": "posting_date",
			"label": "Posting Date",
			"fieldtype": "Date",
			"width": 100
		})
	
		columns.insert(5, {
			"fieldname": "item_code",
			"label": "Material Code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		})
	
		columns.insert(8, {
			"fieldname": "timber_class",
			"label": "Class",
			"fieldtype": "Link",
			"options": "Timber Class",
			"width": 100
		})
		columns.insert(9, {
			"fieldname": "timber_species",
			"label": "Species",
			"fieldtype": "Link",
			"options": "Timber Species",
			"width": 100
		})
		columns.insert(10, {
			"fieldname": "timber_type",
			"label": "Type",
			"fieldtype": "Data",
			"width": 100
		})
		columns.insert(11, {
			"fieldname": "cable_line_no",
			"label": "Cable Line No",
			"fieldtype": "Data",
			"width": 100
		})
		columns.insert(12, {
                        "fieldname": "production_area",
                        "label": "Production Area",
                        "fieldtype": "Data",
                        "width": 100
                })
	
	return columns

@frappe.whitelist()
def get_cc_challan(cost_center, from_date, to_date):
	# 	frappe.msgprint(filters)
	# 	return frappe.db.sql(""" select ppi.challan_no as challan_no from `tabProduction` pr, `tabProduction Product Item` ppi where pr.name = ppi.parent and ppi.challan_no != \'\' """, as_dict=True)
	fd = from_date.split("-")
	td = to_date.split("-")
	from_d = fd[2]+"-"+fd[1]+"-"+fd[0]
	to_d = td[2]+"-"+td[1]+"-"+td[0]
	all_ccs = get_child_cost_centers(cost_center)
	return frappe.db.sql(""" select distinct ppi.challan_no as challan_no from `tabProduction` pr, `tabProduction Product Item` ppi, `tabProduction Entry` pe where pr.name = ppi.parent and ppi.challan_no != \'\' and pe.ref_doc = pr.name and pe.docstatus = 1 and date(pe.posting_date) between '{1}' and '{2}' and pr.branch in (select name from `tabBranch` b where b.cost_center in {0} )""".format(tuple(all_ccs),from_d,to_d), as_dict=True)

@frappe.whitelist()
def get_branch_challan(branch, from_date, to_date):
	branch = branch.replace(' - NRDCL','')
	fd = from_date.split("-")
	td = to_date.split("-")
	from_d = fd[2]+"-"+fd[1]+"-"+fd[0]
	to_d = td[2]+"-"+td[1]+"-"+td[0]
	return frappe.db.sql(""" select distinct ppi.challan_no as challan_no from `tabProduction` pr, `tabProduction Product Item` ppi, `tabProduction Entry` pe where pr.name = ppi.parent and ppi.challan_no != \'\' and pe.ref_doc = pr.name and pe.docstatus = 1 and date(pe.posting_date) between '{1}' and '{2}' and pr.branch = '{0}'""".format(branch,from_d,to_d), as_dict=True)

@frappe.whitelist()
def get_location_challan(location, from_date, to_date):
	fd = from_date.split("-")
	td = to_date.split("-")
	from_d = fd[2]+"-"+fd[1]+"-"+fd[0]
	to_d = td[2]+"-"+td[1]+"-"+td[0]
	return frappe.db.sql(""" select distinct ppi.challan_no as challan_no from `tabProduction` pr, `tabProduction Product Item` ppi, `tabProduction Entry` pe where pr.name = ppi.parent and ppi.challan_no != \'\' and pe.ref_doc = pr.name and pe.docstatus = 1 and date(pe.posting_date) between '{1}' and '{2}' and pe.location = '{0}'""".format(location,from_d,to_d), as_dict=True)
		
