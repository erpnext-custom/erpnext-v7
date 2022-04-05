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
	conditions, machine_name_cond = get_conditions(filters)
	group_by = get_group_by(filters)
	order_by = get_order_by(filters)
	if filters.get("show_aggregate"):
		query = """
			select 
				(select cc.parent_cost_center from `tabCost Center` cc where cc.name = (select b.cost_center from `tabBranch` b where b.name = pp.branch)) as region, 
				pp.branch, ppi.item_group, ppi.item_sub_group, sum(ppi.qty) as total_qty, ppi.uom 
			from
				`tabProduction` pp
				inner join `tabProduction Product Item` ppi on pp.name = ppi.parent
			where 
				pp.docstatus = 1 {0} {1} {2}
			""".format(conditions, group_by, order_by)

		abbr = " - " + str(frappe.db.get_value("Company", filters.company, "abbr"))
		total_qty = 0
		for a in frappe.db.sql(query, as_dict=1):
			a.region = str(a.region).replace(abbr, "")
			if filters.show_aggregate:
				total_qty += flt(a.total_qty)
			data.append(a)

		data.append({
			"region": frappe.bold("TOTAL"),
			"total_qty": total_qty
			})

	else:
		query = """
			select * from( select
				pp.name as ref_doc, ppi.challan_no, pp.posting_date, 
				(select cc.parent_cost_center from `tabCost Center` cc where cc.name = (select b.cost_center from `tabBranch` b where b.name = pp.branch)) as region, 
				pp.branch, pp.location,
				(select GROUP_CONCAT('<a href="desk#Form/Equipment/',pmd.machine_name,'">',pmd.machine_name,'</a>') from `tabProduction Machine Details` pmd where pp.name = pmd.parent) as machine_name,
				ppi.item_code, ppi.item_name, ppi.item_group, ppi.item_sub_group, 
				(select ts.timber_class from `tabTimber Species` ts where ts.name = ppi.timber_species) as timber_class, 
				(select ts.timber_type from `tabTimber Species` ts where ts.name = ppi.timber_species) as timber_type, ppi.timber_species, 
				pp.cable_line_no as cable_line_no, pp.production_area as production_area,
				ppi.qty, ppi.uom, pmi.qty as rm_qty, pmi.cull_qty, pmi.actual_qty, round((ppi.qty*100)/pmi.actual_qty,2) as recovery_rate
			from
				`tabProduction` pp
				left join `tabProduction Product Item` ppi on pp.name = ppi.parent
				left join `tabProduction Material Item` pmi on pp.name = pmi.parent 
			where 
				pp.docstatus = 1 {0} {1} {2}) data {3}
			""".format(conditions, group_by, order_by, machine_name_cond)
				
		abbr = " - " + str(frappe.db.get_value("Company", filters.company, "abbr"))
		total_qty = 0
		for a in frappe.db.sql(query, as_dict=1):
			a.region = str(a.region).replace(abbr, "")
			total_qty += flt(a.qty)
			data.append(a)

		data.append({
			"region": frappe.bold("TOTAL"),
			"qty": total_qty
			})

	return data

def get_group_by(filters):
	if filters.show_aggregate:
		group_by = " group by region, pp.branch, ppi.item_sub_group	"
		# group_by = " group by pe.branch, pe.location, pe.item_sub_group"
	else:
		# group_by = " "
		group_by = " group by pp.name, ppi.item_code, ppi.qty"

	return group_by

def get_order_by(filters):
	# return " order by region, pp.location, ppi.item_group, ppi.item_sub_group"
	return " order by pp.posting_date"

def get_conditions(filters):
	if not filters.cost_center:
		return "", ""

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
	machine_name_cond = ""
	if filters.machine_name:
		machine_name_cond += " and data.machine_name = '{}'".format(filters.machine_name)

	return condition, machine_name_cond

def get_columns(filters):
	if filters.get("show_aggregate"):
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
				"fieldname": "total_qty",
				"label": "Product Qty",
				"fieldtype": "Float",
				"width": 100
			},
			{
				"fieldname": "uom",
				"label": "UOM",
				"fieldtype": "Link",
				"options": "UoM",
				"width": 100
			}
		]
	else:
		columns = [
			{
				"fieldname": "ref_doc",
				"label": "PR Reference",
				"fieldtype": "Link",
				"options": "Production",
				"width": 120
			},
			{
				"fieldname": "challan_no",
				"label": "Challan No",
				"fieldtype": "Data",
				"width": 120
			},
			{
				"fieldname": "posting_date",
				"label": "Posting Date",
				"fieldtype": "Date",
				"width": 100
			},
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
				"fieldname": "machine_name",
				"label": "Machine Name",
				"fieldtype": "Link",
				"options": "Equipment",
				"width": 250
			},
			{
				"fieldname": "item_code",
				"label": "Material Code",
				"fieldtype": "Link",
				"options": "Item",
				"width": 150
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
				"fieldname": "timber_class",
				"label": "Class",
				"fieldtype": "Link",
				"options": "Timber Class",
				"width": 100
			},
			{
				"fieldname": "timber_species",
				"label": "Species",
				"fieldtype": "Link",
				"options": "Timber Species",
				"width": 100
			},
			{
				"fieldname": "timber_type",
				"label": "Type",
				"fieldtype": "Data",
				"width": 100
			},
			{
				"fieldname": "cable_line_no",
				"label": "Cable Line No",
				"fieldtype": "Data",
				"width": 100
			}, 
			{
				"fieldname": "production_area",
				"label": "Production Area",
				"fieldtype": "Data",
				"width": 100
			},
			{
				"fieldname": "qty",
				"label": "Product Qty",
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
			{
				"fieldname": "rm_qty",
				"label": "Raw Material Qty",
				"fieldtype": "Float",
				"width": 100
			}, 
			{
				"fieldname": "cull_qty",
				"label": "Cull Quantity",
				"fieldtype": "Float",
				"width": 100
			}, 
			{
				"fieldname": "actual_qty",
				"label": "Actual Qty",
				"fieldtype": "Float",
				"width": 100
			}, 
			{
				"fieldname": "recovery_rate",
				"label": "Recovery %",
				"fieldtype": "Data",
				"width": 100
			}
		]
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

@frappe.whitelist()
def get_cost_center_based_equipments(cost_center):
	# branch = frappe.db.get_value("Branch", {"cost_center":cost_center}, "name")
	# branch = branch.replace(' - NRDCL','')
	sql = """ select name from `tabEquipment` e where branch in (select name from `tabBranch` where cost_center in (select name from `tabCost Center` where parent_cost_center = '{}')) """.format(cost_center)

	return frappe.db.sql(sql,as_dict=True)
		
