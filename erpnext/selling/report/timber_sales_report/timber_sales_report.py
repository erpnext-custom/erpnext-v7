# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.utils import get_child_cost_centers

def execute(filters=None):
        columns, data = get_columns(filters), get_data(filters)
        return columns, data

def get_columns(filters=None):
	if filters.aggregate:
		if filters.report_by == "Sales Order":
			columns = [
				_("Branch") + ":Link/Sales Order:150",
				_("Transaction Type") + ":Data:150", 
				_("Location") + ":Link/Location:120",
				_("Customer") + ":Link/Customer:150",
				_("Customer Name") + ":Data:200",
				_("Sub Item Group") + ":Data:150",
				_("Sales Qty") + ":Float:120",
				_("Delivered Qty") + ":Float:120",
				_("UOM") + ":Link/UOM:120",
				_("Rate") + ":Currency:120",
				_("Amount") + ":Currency:120"
			]

		else:
			columns = [
				_("Branch") + ":Link/Sales Order:150",
				_("Transaction Type") + ":Data:150", 
				# _("Location") + ":Data/120",
				# _("Customer") + ":Link/Customer:150",
				# _("Customer Group") + ":Data:200",
				_("Sub Item Group") + ":Data:150",
				_("Delivered Qty") + ":Float:120",
				_("UOM") + ":Data:90", 
				_("Amount") + ":Currency:120",
				_("Net Total")+":Currency:120",
			]
	elif filters.summary:
		if filters.report_by == "Sales Order":
			columns = [
				_("Posting Date") + ":Date:100",
				_("Sales Order") + ":Link/Sales Order:100",
				_("Region") + ":Data:150",
				_("Branch") + ":Link/Branch:120",
				_("Transaction Type") + ":Data:150", 
				_("Customer") + ":Link/Customer:150",
				_("Customer Number") + ":Data:100", 
				_("Customer Group") + ":Data:200", 
				_("Sub Group") + ":Data:100",
				_("Actual Qty") + ":Float:90",
				_("Qty Delivered") + ":Float:90",
				_("UOM") + ":Data:90",
				_("Amount") + ":Currency:100",
				# _("Discount") + ":Currency:120",
				# _("Additional Cost") + ":Currency:120",
				_("Net Total")+":Currency:120"
			]

		else:
			columns = [
				_("Posting Date") + ":Date:100",
				_("Delivery Note") + ":Link/Delivery Note:100", 
				_("Sales Order") + ":Link/Sales Order:100", 
				_("Region") + ":Data:150",
				_("Branch") + ":Link/Branch:120",
				_("Transaction Type") + ":Data:150", 
				_("Customer") + ":Link/Customer:150", 
				_("Customer Number") + ":Data:100", 
				_("Customer Group") + ":Data:200", 
				_("Sub Group") + ":Data:100", 
				_("Qty Delivered") + ":Float:90",
				_("UOM") + ":Data:90",
				_("Amount") + ":Currency:100",
				# _("Discount") + ":Currency:120",
				# _("Additional Cost") + ":Currency:120",
				_("Net Total")+":Currency:120"
				# _("Vehicle") + ":Link/Vehicle:120", 
				# _("Driver") + ":Data:120", 
				# _("Contact No") + ":Data:120",
				# _("Transporation Rate") + ":Float:100", 
				# _("Distance") + ":Float:100", 
				# _("Transportation Charges") + ":Currency:100",
			]
	else:
		if filters.report_by == "Sales Order":
			columns = [
				_("Posting Date") + ":Date:100", 
				_("Sales Order") + ":Link/Sales Order:100", 
				_("Region") + ":Data:150",
				_("Branch") + ":Link/Branch:120", 
				_("Location") + ":Link/Location:120",
				_("Transaction Type") + ":Data:150", 
				_("Customer") + ":Link/Customer:150", 
				_("Customer Group") + ":Data:200", 
				_("Item Code") + ":Link/Item: 80", 
				_("Timber Class") + ":Link/Timber Class:100", 
				_("Timber Species") + ":Link/Timber Species:100", 
				_("Timber Type") + ":Data:100", 
				_("Lot No.") + ":Link/Lot List:100", 
				_("Item Name") + ":Data:150", 
				_("Sub Group") + ":Data:100",
				_("Actual Qty") + ":Float:90", 
				_("Qty Delivered") + ":Float:90",
				_("UOM") + ":Data:90",
				_("Rate") + ":Float:90", 
				_("Amount") + ":Currency:100",
				_("Discount") + ":Currency:120",
				_("Additional Cost") + ":Currency:120",
				_("Net Total")+":Currency:120",
				_("Challan Cost")+":Currency:120"
			]
		else:
			columns = [
				_("Posting Date") + ":Date:100", 
				_("Delivery Note") + ":Link/Delivery Note:100", 
				_("Sales Order") + ":Link/Sales Order:100", 
				_("Region") + ":Data:150",
				_("Branch") + ":Link/Branch:120", 
				_("Location") + ":Link/Location:120",
				_("Transaction Type") + ":Data:150", 
				_("Customer") + ":Link/Customer:150", 
				_("Customer Group") + ":Data:200",
				_("Item Code") + ":Link/Item: 80", 
				_("Timber Class") + ":Link/Timber Class:100", 
				_("Timber Species") + ":Link/Timber Species:100", 
				_("Timber Type") + ":Data:100", 
				_("Lot No.") + ":Link/Lot List:100",
				_("Item Name") + ":Data:150", 
				_("Sub Group") + ":Data:100",
				_("Qty Delivered") + ":Float:90", 
				_("UOM") + ":Data:90", 
				_("Rate") + ":Float:90", 
				_("Amount") + ":Currency:100",
				_("Discount") + ":Currency:120",
				_("Additional Cost") + ":Currency:120",
				_("Net Total")+":Currency:120",
				_("Challan Cost")+":Currency:120",
				_("Transporation Rate") + ":Float:100",
				_("Distance") + ":Float:100", 
				_("Transportation Charges") + ":Currency:100",	
				_("Vehicle") + ":Link/Vehicle:120",
				_("Driver") + ":Data:120", 
				_("Contact No") + ":Data:120"
			]
	return columns

def get_data(filters=None):
	cond = get_conditions(filters)
	outer_cond = get_outer_cond(filters)
	data = []
	
	if filters.report_by == "Sales Order":
		if filters.aggregate:
			cols = """
				so.branch, 
				CASE
					WHEN is_allotment=1 THEN "Is Allotment"
					WHEN is_credit=1 THEN "Is Credit Sale"
					WHEN is_rural_sale=1 THEN "Is Rural Sale"
					WHEN export=1 THEN "Is Export"
					WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
					ELSE "None"
				END as transaction_type,
				so.location, so.customer, so.customer_group, i.item_sub_group, sum(soi.qty) as qty, 
				sum(soi.delivered_qty), 
				CASE 
					WHEN soi.conversion_req=1 THEN soi.sales_uom
					ELSE soi.stock_uom
				END as uom, soi.rate, sum(soi.amount)
			"""
			group_by = "group by so.branch, i.item_sub_group"
			order_by = ""
		
		elif filters.summary:
			cols = """
				so.transaction_date,
				so.name, (select cc.parent_cost_center from `tabCost Center` cc where cc.name = (select b.cost_center from `tabBranch` b where b.name = so.branch)) as region,
				so.branch,
				CASE
					WHEN is_allotment=1 THEN "Is Allotment"
					WHEN is_credit=1 THEN "Is Credit Sale"
					WHEN is_rural_sale=1 THEN "Is Rural Sale"
					WHEN export=1 THEN "Is Export"
					WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
					ELSE "None"
				END as transaction_type,
				so.customer, (select mobile_no from `tabCustomer` where name=so.customer) as customer_number, so.customer_group, 
				i.item_sub_group, sum(soi.qty) as qty, sum(soi.delivered_qty),
				CASE 
					WHEN soi.conversion_req=1 THEN soi.sales_uom
					ELSE soi.stock_uom
				END as uom, sum(soi.amount),
				sum(soi.amount) - so.discount_or_cost_amount + so.additional_cost - so.challan_cost
			"""
			group_by = " group by so.customer"
			order_by = "order by so.transaction_date"

		else:
			cols = """
				so.transaction_date, so.name, (select cc.parent_cost_center from `tabCost Center` cc where cc.name = (select b.cost_center from `tabBranch` b where b.name = so.branch)) as region,
				so.branch, so.location,
				CASE
					WHEN is_allotment=1 THEN "Is Allotment"
					WHEN is_credit=1 THEN "Is Credit Sale"
					WHEN is_rural_sale=1 THEN "Is Rural Sale"
					WHEN export=1 THEN "Is Export"
					WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
					ELSE "None"
				END as transaction_type, 
				so.customer, so.customer_group, soi.item_code, ts.timber_class,
				ts.species, ts.timber_type, soi.lot_number, soi.item_name, i.item_sub_group,
				sum(soi.qty) as qty, sum(soi.delivered_qty),
				CASE 
					WHEN soi.conversion_req=1 THEN soi.sales_uom
					ELSE soi.stock_uom
				END as uom, sum(soi.rate), sum(soi.amount),
				so.discount_or_cost_amount, so.additional_cost,
				sum(soi.amount) - so.discount_or_cost_amount + so.additional_cost - so.challan_cost, so.challan_cost
			"""
			group_by = "group by so.name"
			order_by = "order by so.transaction_date"

		
		query = """
			select * from (
			select {0}
			from `tabSales Order` so 
			inner join `tabSales Order Item` soi on so.name = soi.parent 
			inner join `tabItem` i on soi.item_code = i.name
			left join `tabTimber Species` ts on i.species = ts.species
			where so.docstatus = 1 and i.item_group = "Timber Products"
			{1} {2} {3} ) as data where 1 = 1 {4}
			""".format(cols, cond, group_by, order_by, outer_cond)

	else:
		if filters.aggregate:
			cols = """
				dn.branch,
				CASE
					WHEN is_allotment=1 THEN "Is Allotment"
					WHEN is_credit=1 THEN "Is Credit Sale"
					WHEN is_rural_sale=1 THEN "Is Rural Sale"
					WHEN export=1 THEN "Is Export"
					WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
					ELSE "None"
				END as transaction_type,
				i.item_sub_group, sum(dni.qty) as qty,
				CASE 
					WHEN dni.conversion_req=1 THEN dni.sales_uom
					ELSE dni.stock_uom
				END as uom, sum(dni.amount),
				sum(dni.amount) - dn.discount_or_cost_amount + dn.additional_cost - dn.challan_cost
			"""
			group_by = "group by dn.branch, i.item_sub_group"
			order_by = ""
		
		elif filters.summary:
			cols = """
					dn.posting_date, dn.name, dni.against_sales_order,
					(select cc.parent_cost_center from `tabCost Center` cc where cc.name = (select b.cost_center from `tabBranch` b where b.name = dn.branch)) as region,
					dn.branch,
					CASE
						WHEN is_allotment=1 THEN "Is Allotment"
						WHEN is_credit=1 THEN "Is Credit Sale"
						WHEN is_rural_sale=1 THEN "Is Rural Sale"
						WHEN export=1 THEN "Is Export"
						WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
						ELSE "None"
					END as transaction_type,
					dn.customer, (select mobile_no from `tabCustomer` where name=dn.customer) as customer_number, dn.customer_group,
					i.item_sub_group, sum(dni.qty) as qty,
					CASE 
						WHEN dni.conversion_req=1 THEN dni.sales_uom
						ELSE dni.stock_uom
					END as uom, sum(dni.amount), 
					sum(dni.amount) - dn.discount_or_cost_amount + dn.additional_cost - dn.challan_cost
				"""
			group_by = " group by dn.customer"
			order_by = "order by dn.posting_date"
		
		else:
			cols = """
					dn.posting_date, dn.name, dni.against_sales_order, 
					(select cc.parent_cost_center from `tabCost Center` cc where cc.name = (select b.cost_center from `tabBranch` b where b.name = dn.branch)) as region,
					dn.branch, dn.location,
					CASE
						WHEN is_allotment=1 THEN "Is Allotment"
						WHEN is_credit=1 THEN "Is Credit Sale"
						WHEN is_rural_sale=1 THEN "Is Rural Sale"
						WHEN export=1 THEN "Is Export"
						WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
						ELSE "None"
					END as transaction_type,
					dn.customer, dn.customer_group, dni.item_code, ts.timber_class,
					ts.species,ts.timber_type, dni.lot_number, dni.item_name, i.item_sub_group, 
					sum(dni.qty) as qty,
					CASE 
						WHEN dni.conversion_req=1 THEN dni.sales_uom
						ELSE dni.stock_uom
					END as uom, sum(dni.rate), sum(dni.amount), dn.discount_or_cost_amount, dn.additional_cost, 
					sum(dni.amount) - dn.discount_or_cost_amount + dn.additional_cost - dn.challan_cost, dn.challan_cost,
					dn.transportation_rate, dn.total_distance, dn.transportation_charges,
					dn.vehicle, dn.drivers_name, dn.contact_no
				"""
			group_by = "group by dn.name"
			order_by = "order by dn.posting_date"
		
		query = """
			select * from(
			select {0}
			from `tabDelivery Note` dn 
			inner join `tabDelivery Note Item` dni on dn.name = dni.parent
			inner join `tabItem` i on dni.item_code = i.name
			left join `tabTimber Species` ts on i.species = ts.species
			where dn.docstatus = 1 and i.item_group = "Timber Products"
			{1} {2} {3}) as data where 1 = 1 {4}
			""".format(cols, cond, group_by, order_by, outer_cond)
	
	data = frappe.db.sql(query)
	return data

def get_outer_cond(filters=None):
	outer_cond = ""
	if filters.get("volume"):
		outer_cond += " and data.qty = {0}".format(filters.get("volume"))
	return outer_cond

def get_conditions(filters=None):
	cond=""
	
	if filters.from_date and filters.to_date:
		if filters.report_by == "Sales Order":
			cond += " and so.transaction_date between '" + str(filters.from_date) + "' and '" + str(filters.to_date) + "'"
		else:
			cond += " and dn.posting_date between '" + str(filters.from_date) + "' and '" + str(filters.to_date) + "'"

	if filters.cost_center:
		all_ccs = get_child_cost_centers(filters.cost_center)
		if filters.report_by == "Sales Order":
			cond += " and so.branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))
		else:
			cond += " and dn.branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))

	if filters.branch:
		branch = str(filters.branch)
		branch = branch.replace(' - NRDCL','')
		if filters.report_by == "Sales Order":
			cond += " and so.branch = '"+branch+"'"
		else:
			cond += " and dn.branch = '"+branch+"'"	

	if filters.timber_species:
		if filters.report_by == "Sales Order":
			cond += """ and '{0}' in (select ts.species from `tabItem` i, `tabTimber Species` ts where ts.species = i.species  
			and i.item_code = soi.item_code)""".format(filters.timber_species)
		else:
			cond += """ and '{0}' in (select ts.species from `tabItem` i, `tabTimber Species` ts where ts.species = i.species  
			and i.item_code = dni.item_code)""".format(filters.timber_species)

	if filters.timber_class:
		if filters.report_by == "Sales Order":
			cond += """ and '{0}' in (select ts.timber_class from `tabItem` i, `tabTimber Species` ts where ts.species = i.species 
			and i.item_code = soi.item_code)""".format(filters.timber_class)
		else:
			cond += """ and '{0}' in (select ts.timber_class from `tabItem` i, `tabTimber Species` ts where ts.species = i.species 
			and i.item_code = dni.item_code)""".format(filters.timber_class)

	if filters.timber_type != 'All':
		if filters.report_by == "Sales Order":
			cond += """ and '{0}' in (select ts.timber_type from `tabItem` i, `tabTimber Species` ts where ts.species = i.species 
			and i.item_code = soi.item_code)""".format(filters.timber_type)
		else:
			cond += """ and '{0}' in (select ts.timber_type from `tabItem` i, `tabTimber Species` ts where ts.species = i.species 
			and i.item_code = dni.item_code)""".format(filters.timber_type)
				
	# if filters.item_group:
	# 	cond += " and i.item_group = '" + str(filters.item_group) + "'"
	#	cond += " and exists (select 1 from `tabItem` i where i.item_group = '"+ str(filters.item_group) +"' and i.item_code = soi.item_code)"

	if filters.item_group:
		if filters.report_by == "Sales Order":
			if filters.item_group == "Timber By-Product":
				cond += " and i.item_sub_group in ('Firewood, Bhutan Furniture','BBPL firewood','Firewood(BBPL)','Firewood (Bhutan Ply)','Firewood','Post','Bakals','Woodchips','Briquette','Off-cuts/Sawn timber waste','Off-Cuts','Saw Dust')"
			elif filters.item_group == "Timber Finished Product":
				cond += " and i.item_sub_group in ('Joinery Products','Glulaminated Product')"
			elif filters.item_group == "Nursery and Plantation":
				cond += " and i.item_sub_group in ('Tree Seedlings','Flower Seedlings')"
			else:
				cond += " and i.item_sub_group in ('Log','Pole','Hakaries','Sawn','Field Sawn','Block','Block (Special Size)')"
		else:
			if filters.item_group == "Timber By-Product":
				cond += " and dni.item_sub_group in ('Firewood, Bhutan Furniture','BBPL firewood','Firewood(BBPL)','Firewood (Bhutan Ply)','Firewood','Post','Bakals','Woodchips','Briquette','Off-cuts/Sawn timber waste','Off-Cuts','Saw Dust')"
			elif filters.item_group == "Timber Finished Product":
				cond += " and dni.item_sub_group in ('Joinery Products','Glulaminated Product')"
			elif filters.item_group == "Nursery and Plantation":
				cond += " and dni.item_sub_group in ('Tree Seedlings','Flower Seedlings')"
			else:
				cond += " and dni.item_sub_group in ('Log','Pole','Hakaries','Sawn','Field Sawn','Block','Block (Special Size)')"

	if filters.item_sub_group:
		if filters.report_by == "Sales Order":
			cond += " and i.item_sub_group = '" + str(filters.item_sub_group) + "'"
		else:
			cond += " and dni.item_sub_group = '" + str(filters.item_sub_group) + "'"

	if filters.item:
		if filters.report_by == "Sales Order":
			cond += " and i.item_code = '" + str(filters.item) + "'"
		else:
			cond += " and dni.item_code = '" + str(filters.item) + "'"

	if filters.customer:
		if filters.report_by == "Sales Order":
			cond += " and so.customer = '"+str(filters.customer)+"'"
		else:
			cond += " and dn.customer = '"+str(filters.customer)+"'"

	if filters.customer_group:
		if filters.report_by == "Sales Order":
			cond += " and so.customer_group = '"+str(filters.customer_group)+"'"
		else:
			cond += " and dn.customer_group = '"+str(filters.customer_group)+"'"

	if filters.warehouse:
		if filters.report_by == "Sales Order":
			cond += " and soi.warehouse = '" + str(filters.warehouse) + "'"
		else:
			cond += " and dni.warehouse = '" + str(filters.warehouse) + "'"
		
	if filters.location and filters.report_by == "Delivery Note":
		cond += " and dni.location = '" + str(filters.location) + "'"

	if filters.uom:
		if filters.report_by == "Sales Order":
			cond += " and CASE WHEN soi.conversion_req=1 THEN soi.sales_uom ELSE soi.stock_uom END = '"+str(filters.uom)+"'"
		else:
			cond += " and CASE WHEN dni.conversion_req=1 THEN dni.sales_uom ELSE dni.stock_uom END = '"+str(filters.uom)+"'"

	if filters.transaction_type:
		if filters.report_by == "Sales Order":
			if filters.transaction_type == "Is Allotment":
				cond += " and so.is_allotment = 1"
			elif filters.transaction_type == "Is Credit Sale":
				cond += " and so.is_credit = 1"
			elif filters.transaction_type == "Is Rural Sale":
				cond += " and so.is_rural_sale = 1"
			elif filters.transaction_type == "Is Export":
				cond += " and so.export = 1"
			elif filters.transaction_type == "Is Kidu Sale":
				cond += " and so.is_kidu_sale = 1"
			else:
				cond += " and so.is_allotment != 1 and so.is_credit != 1 and so.is_rural_sale != 1 and so.export != 1 and so.is_kidu_sale != 1"
		else:
			if filters.transaction_type == "Is Allotment":
				cond += " and dn.is_allotment = 1"
			elif filters.transaction_type == "Is Credit Sale":
				cond += " and dn.is_credit = 1"
			elif filters.transaction_type == "Is Rural Sale":
				cond += " and dn.is_rural_sale = 1"
			if filters.transaction_type == "Is Export":
				cond += " and dn.export = 1"
			elif filters.transaction_type == "Is Kidu Sale":
				cond += " and dn.is_kidu_sale = 1"
			else:
				cond += " and dn.is_allotment != 1 and dn.is_credit != 1 and dn.is_rural_sale != 1 and dn.export != 1 and dn.is_kidu_sale != 1"

	return cond

@frappe.whitelist()
def get_item_sub_group(item_group):
	# branch = frappe.db.get_value("Branch", {"cost_center":cost_center}, "name")
	# branch = branch.replace(' - NRDCL','')
	if item_group == 'Timber By-Product':
		sql = """ select name as name from `tabItem Sub Group` where name in ('Firewood, Bhutan Furniture','BBPL firewood','Firewood(BBPL)','Firewood (Bhutan Ply)','Firewood','Post','Bakals','Woodchips','Briquette','Off-cuts/Sawn timber waste','Off-Cuts','Saw Dust') """
	elif item_group == 'Timber Finished Product':
		sql = """ select name as name from `tabItem Sub Group` where name in ('Joinery Products','Glulaminated Product') """
	elif item_group == 'Nursery and Plantation':
		sql = """ select name as name from `tabItem Sub Group` where name in ('Tree Seedlings','Flower Seedlings') """
	else:
		sql = """ select name as name from `tabItem Sub Group` where name in ('Log','Pole','Hakaries','Sawn','Field Sawn','Block','Block (Special Size)') """

	return frappe.db.sql(sql,as_dict=True)