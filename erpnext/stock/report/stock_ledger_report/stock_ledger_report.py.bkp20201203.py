# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.utils import get_child_cost_centers


def execute(filters):
	columns = get_columns()
	sl_entries = get_stock_ledger_entries(filters)
	item_details = get_item_details(filters)
	opening_row = get_opening_balance(filters, columns)
	
	data = []
	
	if opening_row:
		data.append(opening_row)

	for sle in sl_entries:
		item_detail = item_details[sle.item_code]
		if sle.voucher_type == "POL":
			sle.voucher_type = "Receive POL"
		if filters.timber_class:
			if item_detail.timber_class == filters.timber_class: 
				data.append([sle.item_code, sle.posting_date, sle.posting_time, item_detail.item_name, item_detail.timber_class, item_detail.item_group, item_detail.item_sub_group, sle.branch,
				sle.warehouse,
				item_detail.stock_uom, sle.actual_qty, sle.qty_after_transaction,
				(sle.incoming_rate if sle.actual_qty > 0 else 0.0),
				sle.valuation_rate, sle.stock_value, sle.voucher_type, sle.voucher_no,
				sle.vehicle_no, sle.transporter_name, sle.company])
		else:
				data.append([sle.item_code, sle.posting_date, sle.posting_time, item_detail.item_name, item_detail.timber_class, item_detail.item_group, item_detail.item_sub_group, sle.branch,
				sle.warehouse,
				item_detail.stock_uom, sle.actual_qty, sle.qty_after_transaction,
				(sle.incoming_rate if sle.actual_qty > 0 else 0.0),
				sle.valuation_rate, sle.stock_value, sle.voucher_type, sle.voucher_no,
				sle.vehicle_no, sle.transporter_name, sle.company])
			
	return columns, data

def get_columns():
	return [_("Material Code") + ":Link/Item:130", _("Date") + ":Date:95", _("Time") + "Time:95", _("Material Name") + "::120", _("Timber Class") + ":Link/Timber Class:100", _("Material Group") + ":Link/Item Group:100", _("Material Sub Group") + ":Link/Item Sub Group:100",
	 	_("Branch") + ":Link/Branch:100", _("Warehouse") + ":Link/Warehouse:100",
		_("Stock UOM") + ":Link/UOM:100", _("Qty") + ":Float:50", _("Balance Qty") + ":Float:100",
		_("Incoming Rate") + ":Currency:110", _("MAP") + ":Currency:110", _("Balance Value") + ":Currency:110",
		_("Transaction Type") + "::110", _("Transaction No.") + ":Dynamic Link/"+_("Transaction Type")+":100", _("Vehicle No") + ":Data:100", _("Transporter") + ":Data:100", _("Company") + ":Link/Company:100"
	]

def get_stock_ledger_entries(filters):
	return frappe.db.sql("""select * from (select posting_date, posting_time,
			item_code, CASE WHEN voucher_type='Stock Entry' THEN (select branch from `tabStock Entry` where name = voucher_no) WHEN voucher_type = 'Delivery Note' THEN (select branch from `tabDelivery Note` where name = voucher_no) WHEN voucher_type = 'Production' THEN
			(select branch from `tabProduction` where name = voucher_no) WHEN voucher_type = 'Purchase Receipt' THEN (select branch from `tabPurchase Receipt` where name = voucher_no) ELSE 'None' END as branch, 
			warehouse, actual_qty, qty_after_transaction, incoming_rate, valuation_rate,
			stock_value, voucher_type, voucher_no, batch_no, serial_no, 
			CASE voucher_type WHEN 'Stock Entry' THEN (select vehicle_no from `tabStock Entry` where name = voucher_no) WHEN 'Delivery Note' THEN (select lr_no from `tabDelivery Note` where name = voucher_no) ELSE 'None' END as vehicle_no, 
			CASE voucher_type WHEN 'Stock Entry' THEN (select transporter_name from `tabStock Entry` where name = voucher_no) WHEN 'Delivery Note' THEN (select transporter_name1 from `tabDelivery Note` where name = voucher_no) ELSE 'None' END as transporter_name, company
		from `tabStock Ledger Entry`
		where company = %(company)s and
			posting_date between %(from_date)s and %(to_date)s
			{sle_conditions}
			order by posting_date asc, posting_time asc, name asc) as data {branch_cond}"""\
		.format(sle_conditions=get_sle_conditions(filters), branch_cond=get_branch_conditions(filters)),  filters, as_dict=1)

def get_item_details(filters):
	item_details = {}
	for item in frappe.db.sql("""select i.name, i.item_name, CASE WHEN i.species is not null THEN (select ts.timber_class from `tabTimber Species` ts where i.species = ts.species) ELSE 'None' END as timber_class, i.description, i.item_group, i.item_sub_group,
			i.brand, i.stock_uom from `tabItem` i {item_conditions}"""\
			.format(item_conditions=get_item_conditions(filters)), filters, as_dict=1):
		item_details.setdefault(item.name, item)
	return item_details

def get_item_conditions(filters):
	conditions = []
	if filters.get("item_code"):
		conditions.append("name=%(item_code)s")
	if filters.get("brand"):
		conditions.append("brand=%(brand)s")
	if filters.get("item_group"):
		conditions.append("item_group=%(item_group)s")
	if filters.get("timber_prod_group"):
		if filters.get("tp_sub_group"):
			conditions.append("item_sub_group = '" + str(filters.tp_sub_group) + "'")
		
		else:
			if filters.timber_prod_group == "Timber By-Product":
				conditions.append("item_sub_group in ('Firewood, Bhutan Furniture','BBPL firewood','Firewood(BBPL)','Firewood (Bhutan Ply)','Firewood','Post','Bakals','Woodchips','Briquette','Off-cuts/Sawn timber waste','Off-Cuts','Saw Dust')")

			elif filters.timber_prod_group == "Timber Finished Product":
				conditions.append("item_sub_group in ('Joinery Products','Glulaminated Product')")

			elif filters.timber_prod_group == "Nursery and Plantation":
				conditions.append("item_sub_group in ('Tree Seedlings','Flower Seedlings')")

			else:
				conditions.append("item_sub_group in ('Log','Pole','Hakaries','Sawn','Field Sawn','Block','Block (Special Size)')")

	
	if filters.get("item_sub_group"):
		conditions.append("item_sub_group=%(item_sub_group)s")
	# if filters.get("timber_class"):
	# 	conditions.append("timber_class=%(timber_class)s")
	
	return "where {}".format(" and ".join(conditions)) if conditions else ""

# def timber_class_cond(filters):
# 	conditions=[]
# 	if filters.get("timber_class"):
# 		conditions.append("timber_class=%(timber_class)s")
# 	# else:
# 	# 	frappe.throw("Please Set Material Group To Timber Products")
# 	return "".format(" and ".join(conditions)) if conditions else ""

def get_sle_conditions(filters):
	conditions = []
	item_conditions=get_item_conditions(filters)
	if item_conditions:
		conditions.append("""item_code in (select name from tabItem
			{item_conditions})""".format(item_conditions=item_conditions))
	if filters.get("warehouse"):
		conditions.append("warehouse=%(warehouse)s")
	if filters.get("voucher_no"):
		conditions.append("voucher_no=%(voucher_no)s")
	if filters.get("transaction_type"):
		conditions.append("voucher_type=%(transaction_type)s")

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_branch_conditions(filters):
	cond = "where 1=1"
	if filters.cost_center:
    		all_ccs = get_child_cost_centers(filters.cost_center)
		cond+=" and warehouse in (select w.name from `tabWarehouse` w, `tabWarehouse Branch` wb where w.name = wb.parent and wb.branch in (select name from `tabBranch` where cost_center in {0}) )".format(tuple(all_ccs))

	if filters.branch:
		branch = str(filters.branch)
		branch = branch.replace(' - NRDCL','')
		cond += " and warehouse in (select w.name from `tabWarehouse` w, `tabWarehouse Branch` wb where w.name = wb.parent and wb.branch = '"+branch+"')"

	return cond


def get_opening_balance(filters, columns):
	if not (filters.item_code and filters.warehouse and filters.from_date):
		return

	from erpnext.stock.stock_ledger import get_previous_sle
	last_entry = get_previous_sle({
		"item_code": filters.item_code,
		"warehouse": filters.warehouse,
		"posting_date": filters.from_date,
		"posting_time": "00:00:00"
	})
	
	row = [""]*len(columns)
	row[1] = _("'Opening'")
	for i, v in ((9, 'qty_after_transaction'), (11, 'valuation_rate'), (12, 'stock_value')):
			row[i] = last_entry.get(v, 0)
		
	return row
