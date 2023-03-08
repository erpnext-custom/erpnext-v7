from __future__ import unicode_literals
# from tabnanny import check
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint, nowdate, getdate, formatdate
from frappe.core.doctype.user.user import send_sms

def get_frappe_dict(filters):
	import ast
	if isinstance(filters, unicode):
		filters = ast.literal_eval(filters)
		filters = frappe._dict(filters)
	return filters

def add_user_roles(user, role):
	user = frappe.get_doc("User", user)
	user.flags.ignore_permissions = True

	if user and role:
		user.add_roles(role)

def remove_user_roles(user, role):
	user = frappe.get_doc("User", user)
	user.flags.ignore_permissions = True

	if user and role:
		user.remove_roles(role)


@frappe.whitelist()
def get_vehicle_list(user):
        """ 
		get active vehicle list based on `user` 
        """
	vl = frappe.db.sql("""
		select 
			v.name,
			v.vehicle_capacity,
			ifnull(
				(
					select dc.confirmation_status
					from `tabDelivery Confirmation` dc
					where dc.vehicle = v.name
					and confirmation_status = 'In Transit'
					limit 1
				),
				ifnull((
					select load_status
					from `tabLoad Request` lr
					where lr.vehicle = v.name
					and lr.load_status = 'Queued'
					limit 1
				),'Available')
			) vehicle_status,
			(select count(*) + 1
			from `tabLoad Request` lr1 
			where lr1.load_status = "Queued"
			and lr1.vehicle_capacity = v.vehicle_capacity
			and lr1.creation < (select max(lr2.creation)
						from `tabLoad Request` lr2
						where lr2.vehicle = v.name
						and lr2.load_status = lr1.load_status
						)
			) as queue_count,
			lr.location, lr.customer_name, lr.contact_mobile, lr.delivery_note
		from `tabVehicle` v
		left join `tabLoad Request` lr
                        on lr.vehicle = v.name
                        and lr.load_status = "Loaded" 
		where v.user = "{0}" 
		and v.vehicle_status = 'Active'
		and v.common_pool = 1
		order by v.user, v.name
	""".format(user), as_dict=True)

        if not vl:
                frappe.throw(_("No Vehicle List found"))
        return vl

''' ########## Ver.2020.11.09 Begins, Phase-II ########## '''
# following method is created to accommodate Phase-II by SHIV on 2020/11/09 
@frappe.whitelist()
def get_branch_source_query(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	""" get list of `CRM Branch`s based on `Item Sub Group` 
	    used under:
		1. Site Registration
	"""
	if not filters.get("product_category"):
		frappe.throw(_("Please select a material first"))

	bl = frappe.db.sql("""
		select distinct cbs.branch, 
			(case
				when cbs.has_common_pool = 1 then 'Has Common Pool facility'
				else '<span style = "color:white;padding: 0px 5px;border-radius: 2px; background-color:tomato;">Does not have Common Pool facility</span>'
			end) as has_common_pool_msg
		from 
			`tabCRM Branch Setting` cbs
		where cbs.product_category = "{}"
	""".format(filters.get("product_category")))

	if not bl:
		frappe.throw(_("No material source found"))
	return bl

# following method commented and a new one with the same name is created to accommodate Phase-II changes, by SHIV on 2020/11/09
'''
@frappe.whitelist()
def get_branch_source_query(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	""" get list of `CRM Branch`s based on `Item Sub Group` 
	    used under:
		1. Site Registration
	"""
	if not filters.get("item_sub_group"):
		frappe.throw(_("Please select a material first"))

	bl = frappe.db.sql("""
		select distinct cbs.branch, 
			(case
				when cbs.has_common_pool = 1 then 'Has Common Pool facility'
				else '<span style = "color:white;padding: 0px 5px;border-radius: 2px; background-color:tomato;">Does not have Common Pool facility</span>'
			end) as has_common_pool_msg
		from 
			`tabCRM Branch Setting` cbs, 
			`tabCRM Branch Setting Item` cbsi,
			`tabItem` i,
			`tabSelling Price` sp,
			`tabSelling Price Branch` spb,
			`tabSelling Price Rate` spr
		where cbsi.item_sub_group = "{0}"
		and cbsi.has_stock = 1
		and cbs.name = cbsi.parent
		and i.name	= cbsi.item
		and DATE(now()) between sp.from_date and sp.to_date
		and spb.parent  = sp.name
		and spb.branch  = cbs.branch
		and spr.parent  = sp.name
		and spr.price_based_on = 'Item'
		and spr.particular = i.name
	""".format(filters.get("item_sub_group")))

	if not bl:
		frappe.throw(_("No material source found"))
	return bl
'''

# following method is created to accommodate Phase-II by SHIV on 2020/11/09 
@frappe.whitelist()
def get_branch_source(product_category):
	""" get list of `CRM Branch`s based on `Item Sub Group` 
	    used under:
		1. Site Registration
	"""
	if not product_category:
		frappe.throw(_("Please select a material first"))

	bl = frappe.db.sql("""
		select distinct cbs.branch, 
			(case
				when cbs.has_common_pool = 1 then 'Has Common Pool facility'
				else '<span style = "color:white;padding: 0px 5px;border-radius: 2px; background-color:tomato;">Does not have Common Pool facility</span>'
			end) as has_common_pool_msg,
			cbs.has_common_pool,
			cbs.allow_self_owned_transport,
			cbs.allow_other_transport
		from 
			`tabCRM Branch Setting` cbs 
		where cbs.product_category = "{}" 
	""".format(product_category), as_dict=True)

	if not bl:
		frappe.throw(_("No material source found"))
	return bl

# following method commented and a new one with the same name is created to accommodate Phase-II changes, by SHIV on 2020/11/09
'''
@frappe.whitelist()
def get_branch_source(item_sub_group):
	""" get list of `CRM Branch`s based on `Item Sub Group` 
	    used under:
		1. Site Registration
	"""
	if not item_sub_group:
		frappe.throw(_("Please select a material first"))

	bl = frappe.db.sql("""
		select distinct cbs.branch, 
			(case
				when cbs.has_common_pool = 1 then 'Has Common Pool facility'
				else '<span style = "color:white;padding: 0px 5px;border-radius: 2px; background-color:tomato;">Does not have Common Pool facility</span>'
			end) as has_common_pool_msg,
			cbs.has_common_pool,
			cbs.allow_self_owned_transport,
			cbs.allow_other_transport
		from 
			`tabCRM Branch Setting` cbs, 
			`tabCRM Branch Setting Item` cbsi,
			`tabItem` i,
			`tabSelling Price` sp,
			`tabSelling Price Branch` spb,
			`tabSelling Price Rate` spr
		where cbsi.item_sub_group = "{0}"
		and cbsi.has_stock = 1
		and cbs.name = cbsi.parent
		and i.name	= cbsi.item
		and DATE(now()) between sp.from_date and sp.to_date
		and spb.parent  = sp.name
		and spb.branch  = cbs.branch
		and spr.parent  = sp.name
		and spr.price_based_on = 'Item'
		and spr.particular = i.name
	""".format(item_sub_group), as_dict=True)

	if not bl:
		frappe.throw(_("No material source found"))
	return bl
'''
''' ########## Ver.2020.11.09 Ends ########## '''

@frappe.whitelist()
def get_slider_images():
	return frappe.db.sql("""
		select banner from `tabSlider Images`
	""", as_dict=True)

#Added by Kinley Dorji to get items based on item sub group in Product Category 2020/12/30
@frappe.whitelist()
def get_pc_items(product_category=None, item = None):
	if product_category:
		data = []
		item_list =  frappe.db.sql("""
			select name, item_name from `tabItem` where item_sub_group in (select item_sub_group from `tabProduct Category Item` where parent = '{}');
		""".format(product_category), as_dict=True)
		for d in item_list:
			data.append({"name":d.name+":"+d.item_name})
		return data

	elif item:
		return frappe.db.sql("""
			select item_name, stock_uom from `tabItem` where name = {};
		""".format(item), as_dict=True)
	

@frappe.whitelist()
def get_branch_source_for_item(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	""" get list of `CRM Branch`s based on `Item` """
	if not filters.get("item"):
		frappe.throw(_("Please select a material first"))

	bl = frappe.db.sql("""
		select distinct cbs.branch, 
			has_common_pool,
			(case
				when cbs.has_common_pool = 1 then 'Has Common Pool facility'
				else '<span style = "color:white;padding: 0px 5px;border-radius: 2px; background-color:tomato;">Does not have Common Pool facility</span>'
			end) as has_common_pool_msg
		from `tabCRM Branch Setting` cbs, `tabCRM Branch Setting Item` cbsi
		where cbsi.item = "{0}"
		and cbsi.has_stock = 1
		and cbs.name = cbsi.parent
	""".format(filters.get("item")))

	if not bl:
		frappe.throw(_("No material source found"))
	return bl

@frappe.whitelist()
def get_items(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	""" get list of `Item`s based on CRM Branch """
	if not filters.get("branch"):
		frappe.throw(_("Please select branch first"))

	il = frappe.db.sql("""
		select i.name item, i.item_name, i.item_sub_group, i.stock_uom
		from `tabCRM Branch Setting` cbs, `tabCRM Branch Setting Item` cbsi, `tabItem` i
		where cbs.branch = "{0}"
		and cbsi.parent = cbs.name
		and cbsi.has_stock = 1
		and i.name = cbsi.item
		order by i.item_sub_group, i.name
	""".format(filters.get("branch")))

	if not il:
		frappe.throw(_("No materials found"))
	return il

'''########## Ver.2020.11.19 Begins ##########'''
# following method is created as a replacement for the old one to accomodate Phase-II on 2020/11/19
@frappe.whitelist()
def get_site_items(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	""" returns item list 
		WARNING: Please do not change the column order as the mobile app has direct impact
	    used under:
			1. Customer Order
	"""
	
	filters = get_frappe_dict(filters)
	cond = ""

	if not filters.get("product_category"):
		frappe.throw(_("Product Category is mandatory"))
	elif filters.get("product_category") == "Timber By Products" and not filters.get("item_type"):
		frappe.throw(_("Please select an Item Type first"))

	if not filters.get("site") and frappe.db.exists("Product Category", {"name": filters.get("product_category"), "site_required": 1}):
		frappe.throw(_("Please select a Site first"))

	if filters.get("site"):
		# items are filtered based on sub groups defined under product category of the site
		cond = """
			where exists(select 1
				from `tabSite Item` si, `tabProduct Category Item` pci
				where si.parent = "{}"
				and pci.parent = si.product_category
				and pci.item_sub_group = i.item_sub_group)
		""".format(filters.get("site"))
	else:
		# filter items directly based on sub groups defined under selected product category
		cond = """
			where exists(select 1
				from `tabProduct Category Item` pci
				where pci.parent = "{}"
				and pci.item_sub_group = i.item_sub_group)
		""".format(filters.get("product_category"))

	# item_type based filters (passed only for By-Products)
	if filters.get("item_type"):
		cond += ' and i.item_sub_group = "{}"'.format(filters.get("item_type"))

	il = frappe.db.sql("""
		select i.name item, i.item_name, i.item_sub_group, i.stock_uom
		from `tabItem` i
		{}
		and exists(select 1
			from 
				`tabCRM Branch Setting` cbs, 
				`tabCRM Branch Setting Item` cbsi,
				`tabSelling Price` sp,
				`tabSelling Price Branch` spb,
				`tabSelling Price Rate` spr
			where cbsi.item = i.name
			and cbsi.has_stock = 1
			and cbs.name = cbsi.parent
			and spb.branch 	= cbs.branch
			and sp.name 	= spb.parent
			and DATE(now()) between sp.from_date and sp.to_date
			and spr.parent 	= sp.name 
			and spr.price_based_on = 'Item'
			and spr.particular = cbsi.item
			and (
				cbs.has_common_pool = 0
				or
				exists(select 1
					from 
						`tabSite Distance` sd
					where sd.parent = "{}" 
					and sd.branch 	= cbs.branch
					and sd.item_sub_group = i.item_sub_group
				)
			)
		)
	""".format(cond, filters.get("site")))

	if not il:
		frappe.throw(_("No materials found"))
	return il

#to get lots alloted to customer Kinley Dorji
@frappe.whitelist()
def get_lot_allotments(site=None):
	cond = ""
	data = []
	if site:
		cond = " and la.site = '{0}'".format(site)
	else:
		frappe.throw("Please select site")
	
	result = frappe.db.sql("""
		select distinct la.name, la.posting_date from `tabLot Allotment` la, `tabLot Allotment Lots` lal where la.name = lal.parent and la.docstatus = 1 {}
		and not exists(select 1
				from `tabSales Order Item` s
				where s.lot_number = lal.lot_number
				and s.docstatus != 2)
		""".format(cond), as_dict = True)

	for i in result:
		data.append({"data":i.name+"-"+str(i.posting_date)})
	if data:
		return data
	else:
		frappe.throw("There are no alloted lots for your site(s).")

@frappe.whitelist()
def get_lots(allotment_no = None):
	cond = ""
	results = []
	lots = []
	if allotment_no:
		cond = " and c.name = '{0}'".format(allotment_no)
	else:
		frappe.throw("Please Select Allotment Number")
	result = frappe.db.sql("""
		select round(total_volume,2) as total_volume, total_pieces, round(total_amount,2) as total_amount,
		round(discount_amount,2) as discount, round(additional_cost,2) as additional, round(total_payable,2) as total_payable,
		challan_cost, allotment_type from `tabLot Allotment` c where docstatus = 1 {} """.format(cond), as_dict = True)
	lots = frappe.db.sql("select @rownumber:=@rownumber+1 as id, a.lot_number, round(a.total_volume,2) as total_volume, round(a.total_amount,2) as total_amount, round(a.payable_amount,2) as payable_amount, ifnull(round(a.discount, 2),0) as discount, ifnull(round(a.additional, 2),0) as additional, pieces from `tabLot Allotment Lots` a, `tabLot Allotment Details` b, `tabLot Allotment` c, (select @rownumber := 0) t where b.lot_number = a.lot_number and c.name = a.parent and c.name = b.parent {0} and c.docstatus = 1 group by a.lot_number".format(cond), as_dict=True)
	
	# if not result:
	# 	frappe.throw("No Lots Are Alloted To Your Site")
	# else:
	# 
	results.append({"lots":lots})
	results.append({"details":result})

	return results

#below api added to get info on unsold lot info //Kinley Dorji 2021/02/13
@frappe.whitelist()
def lot_details(branch=None, lot_number=None):
	if branch == None and lot_number ==None:
		return frappe.db.sql("""
			select distinct l.branch as branch from `tabLot List` l where l.sales_order is NULL and l.production is NULL and l.stock_entry is NULL and l.docstatus = 1
			and not exists(select 1
					from `tabLot Allotment Lots` la
					where la.lot_number = l.name
					and la.docstatus != 2)
		""", as_dict=True)
	elif branch and lot_number == None:
		return frappe.db.sql("""
			select name, branch, location, warehouse, total_volume from `tabLot List` l where l.sales_order is NULL and l.production is NULL and l.stock_entry is NULL and l.docstatus = 1
			and l.branch = '{}'
			and not exists(select 1
					from `tabLot Allotment Lots` la
					where la.lot_number = l.name
					and la.docstatus != 2)
		""".format(branch), as_dict = True)
	
	elif branch == None and lot_number:
		return frappe.db.sql("""
			select item, item_name, item_sub_group, t_species, timber_class, total_volume, total_pieces
			from `tabLot List Details` where parent = '{}'
		""".format(lot_number), as_dict = True)

#to get lots details of a lot Kinley Dorji
@frappe.whitelist()
def get_lot_details(lot_number = None):
	cond = ""
	if lot_number:
		cond = " and a.lot_number = '{0}'".format(lot_number)

	details = frappe.db.sql("""select @rownumber:=@rownumber+1 as id, lot_number, item, item_name, item_sub_group,
	a.branch, location, price_template, round(a.total_volume,2) as total_volume, a.total_pieces,
	round(price_list_rate,2) as price_list_rate, round(rate,2) as rate, round(amount,2) as amount,
	round(a.discount_amount,2) as discount_amount, round(a.additional_cost,2) as additional_cost
	from `tabLot Allotment Details` a, `tabLot Allotment` b, (select @rownumber := 0) t
	where b.name = a.parent {0} and b.docstatus = 1""".format(cond), as_dict = True)
	 
	return details

# following method is replaced with the above one to accomodate Phase-II on 2020/11/19
'''
@frappe.whitelist()
def get_site_items(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	""" get all site items 
		WARNING: Please do not change the column order as the mobile app has direct impact
	    used under:
		1. Customer Order
	"""
	
	filters = get_frappe_dict(filters)

	if not filters.get("site"):
		frappe.throw(_("Please select a Site first"))
	il = frappe.db.sql("""
		select i.name item, i.item_name, i.item_sub_group, i.stock_uom
		from `tabItem` i
		where exists(select 1
				from `tabSite Item` si
				where si.parent = "{0}"
				and si.item_sub_group = i.item_sub_group)
		and exists(select 1
			from 
				`tabCRM Branch Setting` cbs, 
				`tabCRM Branch Setting Item` cbsi,
				`tabSelling Price` sp,
				`tabSelling Price Branch` spb,
				`tabSelling Price Rate` spr
			where cbsi.item = i.name
			and cbsi.has_stock = 1
			and cbs.name = cbsi.parent
			and spb.branch 	= cbs.branch
			and sp.name 	= spb.parent
			and DATE(now()) between sp.from_date and sp.to_date
			and spr.parent 	= sp.name 
			and spr.price_based_on = 'Item'
			and spr.particular = cbsi.item
			and (
				cbs.has_common_pool = 0
				or
				exists(select 1
					from 
						`tabSite Distance` sd
					where sd.parent = "{0}" 
					and sd.branch 	= cbs.branch
					and sd.item_sub_group = i.item_sub_group
				)
			)
		)
	""".format(filters.get("site")))

	if not il:
		frappe.throw(_("No materials found"))
	return il
'''

@frappe.whitelist()
def get_crm_dzongkhags(product_category = None, item_type = None, item = None):
	bl = frappe.db.sql("""
		select distinct dzongkhag as name
		from 
			`tabCRM Branch Setting` cbs
		inner join `tabBranch` b
			on b.name = cbs.branch
		inner join `tabCRM Branch Setting Item` cbsi 
			on cbsi.parent = cbs.name
			and cbsi.has_stock = 1
		inner join `tabItem` i
			on i.name = cbsi.item
		where i.name = {item}
		and cbs.product_category = '{product_category}'
		and exists(select 1
				from `tabSelling Price` sp, `tabSelling Price Branch` spb, `tabSelling Price Rate` spr
				where DATE(now()) between sp.from_date and sp.to_date
				and spb.parent = sp.name
				and spb.branch = cbs.branch
				and spr.parent = sp.name
				and spr.price_based_on = 'Item'
				and spr.particular = i.name)
	""".format(item = item, product_category = product_category), as_dict=True)
	return bl

# following method is created as a replacement for the following one to accommodate Phase-II by SHIV on 2020/11/19
@frappe.whitelist()
def get_branch_rate_query(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	""" get list of source branches along with rates based on selected item/item_sub_group or both 
	    used under:
		1. Customer Order
	    conditions:
		list of branches are returned based on following conditions
			1. Branches are pulled from 'CRM Branch Setting'
			2. Return only branches having stock(has_stock) for selected item
			3. Return all branches with no common pool facility
			4. If is a common pool branch, return only branches having rates defined
				under 'Selling Price' asof current date, distance defined under 
				'Site Distance' table, and 'Transportation Rate' exists.
	"""
	if filters.get("product_group") != "Timber Prime Products":
		cond 	  = []
		site_cond = ""
		tbp_cond = ""
		columns   = []
		if not filters.get("item_sub_group") and not filters.get("item") and not filters.get("product_group") == "Sawn Timber":
			frappe.throw(_("Please select a material first"))
		if filters.get("product_category") == "Timber By Products":
			if filters.get("destination_dzongkhag"):
				tbp_cond = """
					and exists(select 1 from
					`tabBranch` b where b.name = cbs.branch and b.dzongkhag = '{}'
					)
				""".format(filters.get("destination_dzongkhag"))
			else:
				frappe.throw("Please Select Destination Dzongkhag First")
		else:
			tbp_cond = " and 1 = 1"
		if filters.get("product_group") != "Sawn Timber":
			if filters.get("item"):
				cond.append('cbsi.item = "{0}" '.format(filters.get("item")))
				#columns.extend(["concat('Rate: Nu.',round(spr.selling_price,2),'/',i.stock_uom) as item_rate"])
				#columns.extend(["concat('Lead Time: ',(case when cbs.has_common_pool = 1 then cbs.lead_time else null end),' Days') as lead_time"])
				columns.extend(["concat('Lead Time: ',cbs.lead_time,' Days') as lead_time"])
			if filters.get("item_sub_group"):
				cond.append('cbsi.item_sub_group = "{0}"'.format(filters.get("item_sub_group")))
		else:
			cond.append("cbsi.item_sub_group = 'Sawn'")
			columns.extend(["concat('Lead Time: ',cbs.lead_time,' Days') as lead_time"])

		if filters.get("site"):
			site_cond = """
				and (
					cbs.has_common_pool = 0
					or exists(select 1
						from `tabSite Distance` sd
						where sd.parent = "{}"
						and sd.branch 	= cbs.branch
						and sd.item_sub_group = i.item_sub_group
						and ifnull(sd.distance,0) > 0
						and exists(select 1
							from `tabTransportation Rate` tr
							where tr.branch = sd.branch
							and tr.item_sub_group = sd.item_sub_group
							and sd.distance between tr.from_distance and tr.to_distance))
				)
			""".format(filters.get("site"))

		cond = " and ".join(cond)
		columns = ", ".join(columns)

		bl = frappe.db.sql("""
			select distinct  
				cbs.branch,
				(case
					when cbs.has_common_pool = 1 then 'Has Common Pool facility'
					else '<span style = "color:white;padding: 0px 5px;border-radius: 2px; background-color:tomato;">Does not have Common Pool facility</span>'
				end) as has_common_pool_msg,
				{columns}
			from 
				`tabCRM Branch Setting` cbs,
				`tabCRM Branch Setting Item` cbsi,
				`tabItem` i
			where {cond}
			{tbp_cond}
			and cbs.name 	= cbsi.parent
			and i.name 	= cbsi.item
			and cbsi.has_stock = 1
			and exists(select 1
					from `tabSelling Price` sp, `tabSelling Price Branch` spb, `tabSelling Price Rate` spr
					where DATE(now()) between sp.from_date and sp.to_date
					and spb.parent = sp.name
					and spb.branch = cbs.branch
					and spr.parent = sp.name
					and spr.price_based_on = 'Item'
					and spr.particular = i.name)
			{site_cond}
		""".format(cond=cond, site_cond=site_cond, tbp_cond=tbp_cond, columns=columns))

		#if not bl:
		#	frappe.throw(_("Rates not available for this material"))
		return bl
	else:
		bl = []
		#if not bl:
		#	frappe.throw(_("Rates not available for this material"))
		return bl

# following method is replaced by the above one to accommodate Phase-II by SHIV on 2020/11/19
'''
@frappe.whitelist()
def get_branch_rate_query(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	""" get list of source branches along with rates based on selected item/item_sub_group or both 
	    used under:
		1. Customer Order
	    conditions:
		list of branches are returned based on following conditions
			1. Branches are pulled from 'CRM Branch Setting'
			2. Return only branches having stock(has_stock) for selected item
			3. Return all branches with no common pool facility
			4. If is a common pool branch, return only branches having rates defined
				under 'Selling Price' asof current date, distance defined under 
				'Site Distance' table, and 'Transportation Rate' exists.
	"""
	cond 	  = []
	site_cond = ""
	columns   = []
	if not filters.get("item_sub_group") and not filters.get("item"):
		frappe.throw(_("Please select a material first"))

	if filters.get("item"):
		cond.append('cbsi.item = "{0}" '.format(filters.get("item")))
		#columns.extend(["concat('Rate: Nu.',round(spr.selling_price,2),'/',i.stock_uom) as item_rate"])
		#columns.extend(["concat('Lead Time: ',(case when cbs.has_common_pool = 1 then cbs.lead_time else null end),' Days') as lead_time"])
		columns.extend(["concat('Lead Time: ',cbs.lead_time,' Days') as lead_time"])
	if filters.get("item_sub_group"):
		cond.append('cbsi.item_sub_group = "{0}" '.format(filters.get("item_sub_group")))
	if filters.get("site"):
		site_cond = """
			and (
				cbs.has_common_pool = 0
				or exists(select 1
					from `tabSite Distance` sd
					where sd.parent = "{0}"
					and sd.branch 	= cbs.branch
					and sd.item_sub_group = i.item_sub_group
					and ifnull(sd.distance,0) > 0
					and exists(select 1
						from `tabTransportation Rate` tr
						where tr.branch = sd.branch
						and tr.item_sub_group = sd.item_sub_group
						and sd.distance between tr.from_distance and tr.to_distance))
			)
		""".format(filters.get("site"))

	cond = " and ".join(cond)
	columns = ", ".join(columns)

	bl = frappe.db.sql("""
		select distinct  
			cbs.branch,
			(case
				when cbs.has_common_pool = 1 then 'Has Common Pool facility'
				else '<span style = "color:white;padding: 0px 5px;border-radius: 2px; background-color:tomato;">Does not have Common Pool facility</span>'
			end) as has_common_pool_msg,
			{columns}
		from 
			`tabCRM Branch Setting` cbs, 
			`tabCRM Branch Setting Item` cbsi,
			`tabItem` i
		where {cond}
		and cbs.name 	= cbsi.parent
		and i.name 	= cbsi.item
		and cbsi.has_stock = 1
		and exists(select 1
				from `tabSelling Price` sp, `tabSelling Price Branch` spb, `tabSelling Price Rate` spr
				where DATE(now()) between sp.from_date and sp.to_date
				and spb.parent = sp.name
				and spb.branch = cbs.branch
				and spr.parent = sp.name
				and spr.price_based_on = 'Item'
				and spr.particular = i.name)
		{site_cond}
	""".format(cond=cond, site_cond=site_cond, columns=columns))

	#if not bl:
	#	frappe.throw(_("Rates not available for this material"))
	return bl 

@frappe.whitelist()
def get_branch_rate_query_old(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	""" get list of source branches along with rates based on selected item/item_sub_group or both 
	    used under:
		1. Customer Order
	    conditions:
		list of branches are returned based on following conditions
			1. Branches are pulled from 'CRM Branch Setting'
			2. Return only branches having stock(has_stock) for selected item
			3. Return all branches with no common pool facility
			4. If is a common pool branch, return only branches having rates defined
				under 'Selling Price' asof current date, distance defined under 
				'Site Distance' table, and 'Transportation Rate' exists.
	"""
	cond 	  = []
	site_cond = ""
	columns   = []
	if not filters.get("item_sub_group") and not filters.get("item"):
		frappe.throw(_("Please select a material first"))

	if filters.get("item"):
		cond.append('cbsi.item = "{0}" '.format(filters.get("item")))
		columns.extend(["concat('Rate: Nu.',round(spr.selling_price,2),'/',i.stock_uom) as item_rate"])
		columns.extend(["concat('Lead Time: ',(case when cbs.has_common_pool = 1 then cbs.lead_time else null end),' Days') as lead_time"])
	if filters.get("item_sub_group"):
		cond.append('cbsi.item_sub_group = "{0}" '.format(filters.get("item_sub_group")))
	if filters.get("site"):
		site_cond = """
			and (
				cbs.has_common_pool = 0
				or exists(select 1
					from `tabSite Distance` sd
					where sd.parent = "{0}"
					and sd.branch 	= cbs.branch
					and sd.item	= i.name
					and ifnull(sd.distance,0) > 0
					and exists(select 1
						from `tabTransportation Rate` tr
						where tr.branch = sd.branch
						and sd.distance between tr.from_distance and tr.to_distance))
			)
		""".format(filters.get("site"))

	cond = " and ".join(cond)
	columns = ", ".join(columns)

	bl = frappe.db.sql("""
		select distinct  
			cbs.branch,
			(case
				when cbs.has_common_pool = 1 then 'Has Common Pool facility'
				else '<span style = "color:white;padding: 0px 5px;border-radius: 2px; background-color:tomato;">Does not have Common Pool facility</span>'
			end) as has_common_pool_msg,
			{columns}
		from 
			`tabCRM Branch Setting` cbs, 
			`tabCRM Branch Setting Item` cbsi,
			`tabItem` i,
			`tabSelling Price` sp,
			`tabSelling Price Branch` spb,
			`tabSelling Price Rate` spr
		where {cond}
		and cbs.name 	= cbsi.parent
		and i.name 	= cbsi.item
		and cbsi.has_stock = 1
		and DATE(now()) between sp.from_date and sp.to_date
		and spb.parent 	= sp.name
		and spb.branch 	= cbs.branch
		and spr.parent	= sp.name
		and spr.price_based_on = 'Item'
		and spr.particular = i.name
		{site_cond}
	""".format(cond=cond, site_cond=site_cond, columns=columns))

	#if not bl:
	#	frappe.throw(_("Rates not available for this material"))
	return bl
'''

# following method is create as a replacement for the following one to accommodate Phase-II by SHIV on 2020/11/19
@frappe.whitelist()
def get_branch_rate(branch=None, item_sub_group=None, item=None, site=None, product_category=None, destination_dzongkhag=None):
	""" get list of source branches along with rates based on selected item/item_sub_group or both 
	    used under:
		1. Customer Order
	    conditions:
		list of branches are returned based on following conditions
			1. Branches are pulled from 'CRM Branch Setting'
			2. Return only branches having stock(has_stock) for selected item
			3. Return all branches with no common pool facility
			4. If is a common pool branch, return only branches having rates defined
				under 'Selling Price' asof current date, distance defined under 
				'Site Distance' table, and 'Transportation Rate' exists.
	"""
	cond 	  = []
	site_cond = ""
	tbp_cond = ""
	columns   = ["cbs.branch", "cbs.has_common_pool", "cbs.allow_self_owned_transport", "cbs.allow_other_transport"]
	if not item_sub_group and not item:
		frappe.throw(_("Please select a material first"))
	if destination_dzongkhag:
		tbp_cond = """ and exists(select 1 from `tabBranch` b where b.name = cbs.branch and b.dzongkhag = '{}')""".format(destination_dzongkhag)

	if branch:
		cond.append('cbs.branch = "{0}" '.format(branch))
	if item:
		cond.append('cbsi.item = "{0}" '.format(item))
		#columns.extend(["cbs.lead_time", "spr.selling_price as item_rate"])
		columns.extend(["cbs.lead_time"])
	if item_sub_group:
		cond.append('cbsi.item_sub_group = "{0}" '.format(item_sub_group))
	if site:
		site_cond = """
			and (
				cbs.has_common_pool = 0
				or exists(select 1
					from `tabSite Distance` sd
					where sd.parent = "{0}"
					and sd.branch 	= cbs.branch
					and sd.item_sub_group = i.item_sub_group
					and ifnull(sd.distance,0) > 0
					and exists(select 1
						from `tabTransportation Rate` tr
						where tr.branch = sd.branch
						and tr.item_sub_group = sd.item_sub_group
						and sd.distance between tr.from_distance and tr.to_distance))
			)
		""".format(site)

	cond = " and ".join(cond)
	columns = ", ".join(columns)
	bl = frappe.db.sql("""
		select distinct  
			{columns},
			(case
				when cbs.has_common_pool = 1 then 'Has Common Pool facility'
				else '<span style = "color:white;padding: 0px 5px;border-radius: 2px; background-color:tomato;">Does not have Common Pool facility</span>'
			end) as has_common_pool_msg,
			sd.distance,
			tr.name tr_name,
			tr.rate tr_rate,
			i.stock_uom
		from 
			`tabCRM Branch Setting` cbs
		inner join `tabCRM Branch Setting Item` cbsi 
			on cbsi.parent = cbs.name
			and cbsi.has_stock = 1
		inner join `tabItem` i
			on i.name = cbsi.item
		left join `tabSite Distance` sd
			on sd.parent = "{site}"
			and sd.branch= cbs.branch
			and sd.item_sub_group = i.item_sub_group
		left join `tabTransportation Rate` tr
			on tr.branch = cbs.branch
			and tr.item_sub_group = i.item_sub_group
			and ifnull(sd.distance,0) between tr.from_distance and tr.to_distance
			and DATE(now()) between from_date and to_date
		where {cond}
		{tbp_cond}
		and exists(select 1
				from `tabSelling Price` sp, `tabSelling Price Branch` spb, `tabSelling Price Rate` spr
				where DATE(now()) between sp.from_date and sp.to_date
				and spb.parent = sp.name
				and spb.branch = cbs.branch
				and spr.parent = sp.name
				and spr.price_based_on = 'Item'
				and spr.particular = i.name)
		{site_cond}
	""".format(cond=cond, site_cond=site_cond, tbp_cond=tbp_cond, columns=columns, site=site), as_dict=True)

	#if not bl:
	#	frappe.throw(_("Rates not available for this material"))
	return bl

# following code is replaced by above method to accommodate Phase-II by SHIV on 2020/11/19
'''
@frappe.whitelist()
def get_branch_rate(branch=None, item_sub_group=None, item=None, site=None):
	""" get list of source branches along with rates based on selected item/item_sub_group or both 
	    used under:
		1. Customer Order
	    conditions:
		list of branches are returned based on following conditions
			1. Branches are pulled from 'CRM Branch Setting'
			2. Return only branches having stock(has_stock) for selected item
			3. Return all branches with no common pool facility
			4. If is a common pool branch, return only branches having rates defined
				under 'Selling Price' asof current date, distance defined under 
				'Site Distance' table, and 'Transportation Rate' exists.
	"""
	cond 	  = []
	site_cond = ""
	columns   = ["cbs.branch", "cbs.has_common_pool", "cbs.allow_self_owned_transport", "cbs.allow_other_transport"]
	if not item_sub_group and not item:
		frappe.throw(_("Please select a material first"))

	if branch:
		cond.append('cbs.branch = "{0}" '.format(branch))
	if item:
		cond.append('cbsi.item = "{0}" '.format(item))
		#columns.extend(["cbs.lead_time", "spr.selling_price as item_rate"])
		columns.extend(["cbs.lead_time"])
	if item_sub_group:
		cond.append('cbsi.item_sub_group = "{0}" '.format(item_sub_group))
	if site:
		site_cond = """
			and (
				cbs.has_common_pool = 0
				or exists(select 1
					from `tabSite Distance` sd
					where sd.parent = "{0}"
					and sd.branch 	= cbs.branch
					and sd.item_sub_group = i.item_sub_group
					and ifnull(sd.distance,0) > 0
					and exists(select 1
						from `tabTransportation Rate` tr
						where tr.branch = sd.branch
						and tr.item_sub_group = sd.item_sub_group
						and sd.distance between tr.from_distance and tr.to_distance))
			)
		""".format(site)

	cond = " and ".join(cond)
	columns = ", ".join(columns)
	bl = frappe.db.sql("""
		select distinct  
			{columns},
			(case
				when cbs.has_common_pool = 1 then 'Has Common Pool facility'
				else '<span style = "color:white;padding: 0px 5px;border-radius: 2px; background-color:tomato;">Does not have Common Pool facility</span>'
			end) as has_common_pool_msg,
			sd.distance,
			tr.name tr_name,
			tr.rate tr_rate,
			i.stock_uom
		from 
			`tabCRM Branch Setting` cbs
		inner join `tabCRM Branch Setting Item` cbsi 
			on cbsi.parent = cbs.name
			and cbsi.has_stock = 1
		inner join `tabItem` i
			on i.name = cbsi.item
		left join `tabSite Distance` sd
			on sd.parent = "{site}"
			and sd.branch= cbs.branch
			and sd.item_sub_group = i.item_sub_group
		left join `tabTransportation Rate` tr
			on tr.branch = cbs.branch
			and tr.item_sub_group = i.item_sub_group
			and ifnull(sd.distance,0) between tr.from_distance and tr.to_distance
		where {cond}
		and exists(select 1
				from `tabSelling Price` sp, `tabSelling Price Branch` spb, `tabSelling Price Rate` spr
				where DATE(now()) between sp.from_date and sp.to_date
				and spb.parent = sp.name
				and spb.branch = cbs.branch
				and spr.parent = sp.name
				and spr.price_based_on = 'Item'
				and spr.particular = i.name)
		{site_cond}
	""".format(cond=cond, site_cond=site_cond, columns=columns, site=site), as_dict=True)

	#if not bl:
	#	frappe.throw(_("Rates not available for this material"))
	return bl

@frappe.whitelist()
def get_branch_rate_old(branch=None, item_sub_group=None, item=None, site=None):
	""" get list of source branches along with rates based on selected item/item_sub_group or both 
	    used under:
		1. Customer Order
	    conditions:
		list of branches are returned based on following conditions
			1. Branches are pulled from 'CRM Branch Setting'
			2. Return only branches having stock(has_stock) for selected item
			3. Return all branches with no common pool facility
			4. If is a common pool branch, return only branches having rates defined
				under 'Selling Price' asof current date, distance defined under 
				'Site Distance' table, and 'Transportation Rate' exists.
	"""
	cond 	  = []
	site_cond = ""
	columns   = ["cbs.branch", "cbs.has_common_pool", "cbs.allow_self_owned_transport", "cbs.allow_other_transport"]
	if not item_sub_group and not item:
		frappe.throw(_("Please select a material first"))

	if branch:
		cond.append('cbs.branch = "{0}" '.format(branch))
	if item:
		cond.append('cbsi.item = "{0}" '.format(item))
		columns.extend(["cbs.lead_time", "spr.selling_price as item_rate"])
	if item_sub_group:
		cond.append('cbsi.item_sub_group = "{0}" '.format(item_sub_group))
	if site:
		site_cond = """
			and (
				cbs.has_common_pool = 0
				or exists(select 1
					from `tabSite Distance` sd
					where sd.parent = "{0}"
					and sd.branch 	= cbs.branch
					and sd.item	= i.name
					and ifnull(sd.distance,0) > 0
					and exists(select 1
						from `tabTransportation Rate` tr
						where tr.branch = sd.branch
						and sd.distance between tr.from_distance and tr.to_distance))
			)
		""".format(site)

	cond = " and ".join(cond)
	columns = ", ".join(columns)
	bl = frappe.db.sql("""
		select distinct  
			{columns},
			(case
				when cbs.has_common_pool = 1 then 'Has Common Pool facility'
				else '<span style = "color:white;padding: 0px 5px;border-radius: 2px; background-color:tomato;">Does not have Common Pool facility</span>'
			end) as has_common_pool_msg,
			sd.distance,
			tr.name tr_name,
			tr.rate tr_rate,
			sp.name as selling_price,
			i.stock_uom
		from 
			`tabCRM Branch Setting` cbs
		inner join `tabCRM Branch Setting Item` cbsi 
			on cbsi.parent = cbs.name
			and cbsi.has_stock = 1
		inner join `tabItem` i
			on i.name = cbsi.item
		inner join `tabSelling Price` sp
			on DATE(now()) between sp.from_date and sp.to_date
		inner join `tabSelling Price Branch` spb
			on spb.parent = sp.name
			and spb.branch = cbs.branch
		inner join `tabSelling Price Rate` spr
			on spr.parent = sp.name
			and spr.price_based_on = 'Item'
			and spr.particular = i.name
		left join `tabSite Distance` sd
			on sd.parent = "{site}"
			and sd.branch= cbs.branch
			and sd.item = cbsi.item
		left join `tabTransportation Rate` tr
			on tr.branch = cbs.branch
			and tr.item_sub_group = i.item_sub_group
			and ifnull(sd.distance,0) between tr.from_distance and tr.to_distance
		where {cond}
		{site_cond}
	""".format(cond=cond, site_cond=site_cond, columns=columns, site=site), as_dict=True)

	#if not bl:
	#	frappe.throw(_("Rates not available for this material"))
	return bl
'''

# following method is created as a replacedment for the following one to accommodate Phase-II by SHIV on 2020/11/19
@frappe.whitelist()
def get_branch_location_query(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	if not filters.get("item"):
		frappe.throw(_("Please select required Material first"))
	if not filters.get("branch"):
		frappe.throw(_("Please select Source Branch first"))

	bl = frappe.db.sql("""
		select distinct 
			(case
				when spr.location is null then "Departmental"
				when ifnull(spr.location,'') = '' then "Departmental"
				else spr.location
			end) as name,
			spr.parent as selling_price,
			concat('Rate: Nu.',round(spr.selling_price,2),'/-') as item_rate
		from `tabSelling Price` sp, `tabSelling Price Branch` spb, `tabSelling Price Rate` spr
		where DATE(now()) between sp.from_date and sp.to_date  
		and spb.parent = sp.name
		and spb.branch = "{branch}"
		and spr.parent = sp.name 
		and spr.price_based_on = "Item"
		and spr.particular = "{item}"
		and (
			spr.location is null 
			or 
			ifnull(spr.location,'') = ''
			or
			exists(select 1
				from `tabLocation` l
				where l.name = spr.location 
				and l.branch = spb.branch
				and l.is_crm_item = 1
			)
		)
	""".format(branch=filters.get("branch"), item=filters.get("item")), as_dict=False)

	return bl

# following code is replaced with the above one to accommodate Phase-II by SHIV on 2020/11/19
'''
@frappe.whitelist()
def get_branch_location_query(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	if not filters.get("item"):
		frappe.throw(_("Please select required Material first"))
	if not filters.get("branch"):
		frappe.throw(_("Please select Source Branch first"))

	bl = frappe.db.sql("""
		select distinct 
			(case
				when spr.location is null then "Departmental"
				when ifnull(spr.location,'') = '' then "Departmental"
				else spr.location
			end) as name,
			spr.parent as selling_price,
			concat('Rate: Nu.',round(spr.selling_price,2),'/-') as item_rate
		from `tabSelling Price` sp, `tabSelling Price Branch` spb, `tabSelling Price Rate` spr
		where DATE(now()) between sp.from_date and sp.to_date  
		and spb.parent = sp.name
		and spb.branch = "{branch}"
		and spr.parent = sp.name 
		and spr.price_based_on = "Item"
		and spr.particular = "{item}"
		and (
			spr.location is null 
			or 
			ifnull(spr.location,'') = ''
			or
			exists(select 1
				from `tabLocation` l
				where l.name = spr.location 
				and l.branch = spb.branch
				and l.is_crm_item = 1
			)
		)
	""".format(branch=filters.get("branch"), item=filters.get("item")), as_dict=False)

	return bl
'''

# following code is commented by SHIV on 2020/11/19
'''
@frappe.whitelist()
def get_branch_location_query_bkp20200218(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	if not filters.get("item"):
		frappe.throw(_("Please select required Material first"))
	if not filters.get("branch"):
		frappe.throw(_("Please select Source Branch first"))

	bl = frappe.db.sql("""
		select distinct 
			spr.location as name,
			spr.parent as selling_price,
			concat('Rate: Nu.',round(spr.selling_price,2),'/-') as item_rate
		from `tabSelling Price` sp, `tabSelling Price Branch` spb, `tabSelling Price Rate` spr
		where DATE(now()) between sp.from_date and sp.to_date  
		and spb.parent = sp.name
		and spb.branch = "{branch}"
		and spr.parent = sp.name 
		and spr.price_based_on = "Item"
		and spr.particular = "{item}"
		and spr.location is not null
		and exists(select 1
			from `tabLocation` l
			where l.name = spr.location 
			and l.branch = spb.branch
			and l.is_crm_item = 1
		)
	""".format(branch=filters.get("branch"), item=filters.get("item")), as_dict=False)

	return bl
'''

@frappe.whitelist()
def get_branch_location(site, item, branch=None, location=None):
	cond = []
	site_cond = ''
	if not item:
		frappe.throw(_("Please select required Material first"))

	if branch:
		cond.append('spb.branch = "{0}"'.format(branch))
	if location:
		if location == "Departmental":
			cond.append('(spr.location is null or ifnull(spr.location,"") = "" or spr.location = "{0}")'.format(location))
		else:
			cond.append('spr.location = "{0}"'.format(location))
	
	# item_uom = frappe.db.get_value('Item', item, 'stock_uom')
	# if item_uom:
	# 	check_uom = frappe.db.sql("select 1 from `tabSelling Price` sp, `tabSelling Price Rate` spr where spr.parent = sp.name and spr.particular='{0}' and spr.selling_uom='{1}'".format(item, item_uom))
	# 	if check_uom:
	# 		cond.append('IF(spr.selling_uom IS NULL,"",spr.selling_uom) = "{0}"'.format(item_uom))
	# 	else:
	# 		cond.append('IF(spr.selling_uom IS NULL,"",spr.selling_uom) = ""')

	cond = " and ".join(cond)
	cond = " and "+cond if cond else cond

	if site:
		site_cond = """
			and (
				cbs.has_common_pool = 0
				or exists(select 1
					from `tabSite Distance` sd
					where sd.parent = "{0}"
					and sd.branch 	= cbs.branch
					and sd.item_sub_group = i.item_sub_group
					and ifnull(sd.distance,0) > 0
					and exists(select 1
						from `tabTransportation Rate` tr
						where tr.branch = sd.branch
						and tr.item_sub_group = sd.item_sub_group
						and sd.distance between tr.from_distance and tr.to_distance))
			)
		""".format(site)

	query = """
		select distinct 
			spb.branch,
			(case
				when spr.location is null then "Departmental"
				when ifnull(spr.location,'') = '' then "Departmental"
				else spr.location
			end) as location,
			spr.parent as selling_price,
			spr.selling_price as item_rate,
			cbs.lead_time,
			(case
				when spr.location is null then
					(case
						when exists(select 1
								from `tabSelling Price Rate` spr2, `tabLocation` l2
								where spr2.parent = spr.parent
								and spr2.location is not null
								and l2.name = spr2.location
								and l2.branch = spb.branch
								and l2.is_crm_item = 1) then 0
						else 1
					end)
				else 1
			end) display
		from 
			`tabSelling Price` sp, 
			`tabSelling Price Branch` spb, 
			`tabSelling Price Rate` spr,
			`tabItem` i,
			`tabCRM Branch Setting` cbs,
			`tabCRM Branch Setting Item` cbsi
		where DATE(now()) between sp.from_date and sp.to_date  
		and spb.parent = sp.name
		and spr.parent = sp.name 
		and spr.price_based_on = "Item"
		and spr.particular = "{item}"
		and i.name = "{item}"
		and (ifnull(spr.selling_uom,'') = '' or ifnull(spr.selling_uom,'') = i.stock_uom)
		{cond}
		and (
			spr.location is null
			or
			ifnull(spr.location,'') = ''
			or
			exists(select 1
				from `tabLocation` l
				where l.name = spr.location 
				and l.branch = spb.branch
				and l.is_crm_item = 1
			)
		)
		and cbs.branch = spb.branch
		and cbsi.parent = cbs.name
		and cbsi.item = "{item}"
		and cbsi.has_stock = 1
		{site_cond}
		order by spb.branch, cbs.lead_time
	""".format(cond=cond, item=item, site_cond=site_cond)

	bl = frappe.db.sql(query, as_dict=True)
	return bl

# following method is replaced with the above one to accommodate Phase-II by SHIV on 2020/11/19
'''
@frappe.whitelist()
def get_branch_location(site, item, branch=None, location=None):
	cond = []
	site_cond = ''
	if not item:
		frappe.throw(_("Please select required Material first"))

	if branch:
		cond.append('spb.branch = "{0}"'.format(branch))
	if location:
		if location == "Departmental":
			cond.append('(spr.location is null or ifnull(spr.location,"") = "" or spr.location = "{0}")'.format(location))
		else:
			cond.append('spr.location = "{0}"'.format(location))

	cond = " and ".join(cond)
	cond = " and "+cond if cond else cond

	if site:
		site_cond = """
			and (
				cbs.has_common_pool = 0
				or exists(select 1
					from `tabSite Distance` sd
					where sd.parent = "{0}"
					and sd.branch 	= cbs.branch
					and sd.item_sub_group = i.item_sub_group
					and ifnull(sd.distance,0) > 0
					and exists(select 1
						from `tabTransportation Rate` tr
						where tr.branch = sd.branch
						and tr.item_sub_group = sd.item_sub_group
						and sd.distance between tr.from_distance and tr.to_distance))
			)
		""".format(site)

	bl = frappe.db.sql("""
		select distinct 
			spb.branch,
			(case
				when spr.location is null then "Departmental"
				when ifnull(spr.location,'') = '' then "Departmental"
				else spr.location
			end) as location,
			spr.parent as selling_price,
			spr.selling_price as item_rate,
			cbs.lead_time,
			(case
				when spr.location is null then
					(case
						when exists(select 1
								from `tabSelling Price Rate` spr2, `tabLocation` l2
								where spr2.parent = spr.parent
								and spr2.location is not null
								and l2.name = spr2.location
								and l2.branch = spb.branch
								and l2.is_crm_item = 1) then 0
						else 1
					end)
				else 1
			end) display
		from 
			`tabSelling Price` sp, 
			`tabSelling Price Branch` spb, 
			`tabSelling Price Rate` spr,
			`tabItem` i,
			`tabCRM Branch Setting` cbs,
			`tabCRM Branch Setting Item` cbsi
		where DATE(now()) between sp.from_date and sp.to_date  
		and spb.parent = sp.name
		and spr.parent = sp.name 
		and spr.price_based_on = "Item"
		and spr.particular = "{item}"
		and i.name = "{item}"
		{cond}
		and (
			spr.location is null
			or
			ifnull(spr.location,'') = ''
			or
			exists(select 1
				from `tabLocation` l
				where l.name = spr.location 
				and l.branch = spb.branch
				and l.is_crm_item = 1
			)
		)
		and cbs.branch = spb.branch
		and cbsi.parent = cbs.name
		and cbsi.item = "{item}"
		and cbsi.has_stock = 1
		{site_cond}
		order by spb.branch, cbs.lead_time
	""".format(cond=cond, item=item, site_cond=site_cond), as_dict=True)

	return bl
'''

# following methods are commented by SHIV on 2020/11/19
'''
@frappe.whitelist()
def get_branch_location_bkp20200218(site, item, branch=None, location=None):
	cond = []
	site_cond = ''
	if not item:
		frappe.throw(_("Please select required Material first"))

	if branch:
		cond.append('spb.branch = "{0}"'.format(branch))
	if location:
		cond.append('spr.location = "{0}"'.format(location))

	cond = " and ".join(cond)
	cond = " and "+cond if cond else cond

	if site:
		site_cond = """
			and (
				cbs.has_common_pool = 0
				or exists(select 1
					from `tabSite Distance` sd
					where sd.parent = "{0}"
					and sd.branch 	= cbs.branch
					and sd.item_sub_group = i.item_sub_group
					and ifnull(sd.distance,0) > 0
					and exists(select 1
						from `tabTransportation Rate` tr
						where tr.branch = sd.branch
						and tr.item_sub_group = sd.item_sub_group
						and sd.distance between tr.from_distance and tr.to_distance))
			)
		""".format(site)

	bl = frappe.db.sql("""
		select distinct 
			spb.branch,
			spr.location,
			spr.parent as selling_price,
			spr.selling_price as item_rate,
			cbs.lead_time,
			(case
				when spr.location is null then
					(case
						when exists(select 1
								from `tabSelling Price Rate` spr2, `tabLocation` l2
								where spr2.parent = spr.parent
								and spr2.location is not null
								and l2.name = spr2.location
								and l2.branch = spb.branch
								and l2.is_crm_item = 1) then 0
						else 1
					end)
				else 1
			end) display
		from 
			`tabSelling Price` sp, 
			`tabSelling Price Branch` spb, 
			`tabSelling Price Rate` spr,
			`tabItem` i,
			`tabCRM Branch Setting` cbs,
			`tabCRM Branch Setting Item` cbsi
		where DATE(now()) between sp.from_date and sp.to_date  
		and spb.parent = sp.name
		and spr.parent = sp.name 
		and spr.price_based_on = "Item"
		and spr.particular = "{item}"
		and i.name = "{item}"
		{cond}
		and (
			spr.location is null
			or
			exists(select 1
				from `tabLocation` l
				where l.name = spr.location 
				and l.branch = spb.branch
				and l.is_crm_item = 1
			)
		)
		and cbs.branch = spb.branch
		and cbsi.parent = cbs.name
		and cbsi.item = "{item}"
		and cbsi.has_stock = 1
		{site_cond}
		order by spb.branch, cbs.lead_time
	""".format(cond=cond, item=item, site_cond=site_cond), as_dict=True)

	return bl

@frappe.whitelist()
def get_branch_location_old(item, branch=None, location=None):
	cond = []
	if not item:
		frappe.throw(_("Please select required Material first"))

	if branch:
		cond.append('spb.branch = "{0}"'.format(branch))
	if location:
		cond.append('spr.location = "{0}"'.format(location))

	cond = " and ".join(cond)
	cond = " and "+cond if cond else cond

	bl = frappe.db.sql("""
		select distinct 
			spb.branch,
			spr.location,
			spr.parent as selling_price,
			spr.selling_price as item_rate,
			cbs.lead_time
		from 
			`tabSelling Price` sp, 
			`tabSelling Price Branch` spb, 
			`tabSelling Price Rate` spr,
			`tabCRM Branch Setting` cbs,
			`tabCRM Branch Setting Item` cbsi
		where DATE(now()) between sp.from_date and sp.to_date  
		and spb.parent = sp.name
		and spr.parent = sp.name 
		and spr.price_based_on = "Item"
		and spr.particular = "{item}"
		{cond}
		and (
			spr.location is null
			or
			exists(select 1
				from `tabLocation` l
				where l.name = spr.location 
				and l.branch = spb.branch
				and l.is_crm_item = 1
			)
		)
		and cbs.branch = spb.branch
		and cbsi.parent = cbs.name
		and cbsi.item = "{item}"
		and cbsi.has_stock = 1
		order by spb.branch, cbs.lead_time
	""".format(cond=cond, item=item), as_dict=True)

	return bl
'''
'''########## Ver.2020.11.19 Ends ##########'''

@frappe.whitelist()
def get_vehicles(user, site=None, transport_mode=None):
	cond = ""

	if transport_mode:
		if transport_mode == "Self Owned Transport":
			if not user:
				frappe.throw(_("Please select a customer first"))
			cond = """and v.user = "{}" and v.is_boulder = 0""".format(user)

		if transport_mode == "Private Pool":
			if not site:
				frappe.throw(_("Please select a site first"))

			cond = """
				and exists(select 1
					from `tabSite` s, `tabSite Private Pool` spp
					where s.name 	= "{}"
					and s.allow_private_pool = 1
					and spp.parent 	= s.name
					and spp.vehicle = v.name)
			""".format(site)
	else:
		cond = """and v.user = "{}" """.format(user)

	vl = frappe.db.sql("""
		select 
			v.name vehicle,
			v.drivers_name,
			v.contact_no,
			v.vehicle_capacity
		from `tabVehicle` v
		where v.vehicle_status = "Active"
		{cond}
	""".format(cond=cond), as_dict=True)
	if not vl:
		for i in frappe.db.get_all("Transport Request",{"user": user, "docstatus": 0, "self_arranged": 1}):
			frappe.throw(_("Your request for vehicle registration (Request ID#{0}) is awaiting approval").format(i.name))

		frappe.throw(_("Please register a vehicle first"))
	return vl

@frappe.whitelist()
def get_vehicles_old(user):
	cond = ""

	cond = """and v.user = "{}" """.format(user)

	vl = frappe.db.sql("""
		select 
			v.name vehicle,
			v.drivers_name,
			v.contact_no,
			v.vehicle_capacity
		from `tabVehicle` v
		where v.vehicle_status = "Active"
		{cond}
	""".format(cond=cond), as_dict=True)
	if not vl:
		for i in frappe.db.get_all("Transport Request",{"user": user, "docstatus": 0, "self_arranged": 1}):
			frappe.throw(_("Your request for vehicle registration (Request ID#{0}) is awaiting approval").format(i.name))

		frappe.throw(_("Please register a vehicle first"))
	return vl

@frappe.whitelist()
def get_vehicles_query(doctype, txt, searchfield, start, page_len, filters):
        from erpnext.controllers.queries import get_match_cond
	cond = ""

	if filters.get("transport_mode") == "Self Owned Transport":
		if not filters.get("user"):
			frappe.throw(_("Please select a customer first"))
		cond = """and v.user = "{}" """.format(filters.get("user"))

	if filters.get("transport_mode") == "Private Pool":
		if not filters.get("site"):
			frappe.throw(_("Please select a site first"))

		cond = """
			and exists(select 1
				from `tabSite` s, `tabSite Private Pool` spp
				where s.name 	= "{}"
				and s.allow_private_pool = 1
				and spp.parent 	= s.name
				and spp.vehicle = v.name)
		""".format(filters.get("site"))

	return frappe.db.sql("""
			select 
				name, 
				drivers_name, 
				contact_no,
				vehicle_capacity 
			from `tabVehicle` v
			where v.vehicle_status = 'Active'
			{cond}
		""".format(cond=cond, key=frappe.db.escape(searchfield),
		 match_condition=get_match_cond(doctype)), {
		'txt': "%%%s%%" % frappe.db.escape(txt)
	})

@frappe.whitelist()
def get_site(user=frappe.session.user):
	return frappe.db.get_all("Site", "*", {"user": user, "enabled": 1})

@frappe.whitelist()
def get_branch_warehouse(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	""" get all warehouses based on selected branch  """
	if not filters.get("branch"):
		frappe.throw(_("Please select a Branch first"))
	il = frappe.db.sql("""
		select wh.name
		from `tabWarehouse` wh
		where wh.disabled = 0
		and exists(select 1
				from `tabWarehouse Branch` whb
				where whb.parent = wh.name
				and whb.branch = "{0}")
	""".format(filters.get("branch")))

	if not il:
		frappe.throw(_("No warehouse found for the selected branch"))
	return il

@frappe.whitelist()
def filter_vehicle_customer_order(doctype, txt, searchfield, start, page_len, filters):
        from erpnext.controllers.queries import get_match_cond
	if filters.get("customer_order"):
                user_id, transport_mode = frappe.db.get_value("Customer Order", filters.get("customer_order"), ["user","transport_mode"])
        else:
                transport_mode = "Others"

        if filters.get("select_vehicle_queue") or transport_mode == "Common Pool":
		local_distance_limit = frappe.db.get_value("CRM Branch Setting", filters.get("branch"), "local_distance")
                if filters.get("distance") > flt(local_distance_limit) or filters.get("select_vehicle_queue"):
			return frappe.db.sql("""select vehicle, requesting_date_time, token from `tabLoad Request`
						where load_status = 'Queued'
						and crm_branch = '{0}'
						and vehicle_capacity = '{1}'
						order by requesting_date_time, token limit 5
					""".format(filters.get("branch"), filters.get("total_quantity"), key=frappe.db.escape(searchfield),
					 match_condition=get_match_cond(doctype)), {
					'txt': "%%%s%%" % frappe.db.escape(txt)
				})
		else:
			 return frappe.db.sql("""
					 select name, drivers_name, contact_no from `tabVehicle`
                                        where vehicle_status = 'Active'
                                        and ({key} like %(txt)s
                                                or drivers_name like %(txt)s
                                                or contact_no like %(txt)s)
                                        {mcond}
                                order by
                                        if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
                                        if(locate(%(_txt)s, drivers_name), locate(%(_txt)s, drivers_name), 99999),
                                        if(locate(%(_txt)s, contact_no), locate(%(_txt)s, contact_no), 99999),
                                        idx desc,
                                        name, drivers_name, contact_no
                                limit %(start)s, %(page_len)s""".format(**{
                                        'key': searchfield,
                                        'mcond': get_match_cond(doctype)
                                }), {
                                        'txt': "%%%s%%" % txt,
                                        '_txt': txt.replace("%", ""),
                                        'start': start,
                                        'page_len': page_len
				})

	if transport_mode in ["Self Owned Transport", "Private Pool"]:
		cond = " and v.user = '{0}'".format(user_id) if transport_mode == "Self Owned Transport" else ""
		user_id = frappe.db.get_value("Customer Order", filters.get("customer_order"),"user")
		cond += " and v.user = '{}'".format(user_id)
		if transport_mode == "Private Pool":
			return frappe.db.sql("""select name, drivers_name, contact_no from `tabVehicle` v
						where v.vehicle_status = 'Active'
						{0}
						and exists(
							select 1 from `tabCustomer Order Vehicle` c 
							where c.parent = '{1}' 
							and c.vehicle = v.name  
						)
						{match_condition}
					""".format(cond, filters.get("customer_order"), key=frappe.db.escape(searchfield),
					 match_condition=get_match_cond(doctype)), {
					'txt': "%%%s%%" % frappe.db.escape(txt)
				})
		else:
			return frappe.db.sql("""select name, drivers_name, contact_no from `tabVehicle` v
						where v.vehicle_status = 'Active'
						{0}
						{match_condition}
					""".format(cond, filters.get("customer_order"), key=frappe.db.escape(searchfield),
					 match_condition=get_match_cond(doctype)), {
					'txt': "%%%s%%" % frappe.db.escape(txt)
				})
	else:
		'''
                return frappe.db.sql("""select vehicle_no, drivers_name, contact_no from `tabVehicle`
                                        where vehicle_status = 'Active'
                                """.format(key=frappe.db.escape(searchfield),
                                 match_condition=get_match_cond(doctype)), {
                                'txt': "%%%s%%" % frappe.db.escape(txt)
                        })
		'''
		return frappe.db.sql("""
				select name, drivers_name, contact_no from `tabVehicle`
					where vehicle_status = 'Active'
					and ({key} like %(txt)s
						or drivers_name like %(txt)s
						or contact_no like %(txt)s)
					{mcond}
				order by
					if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
					if(locate(%(_txt)s, drivers_name), locate(%(_txt)s, drivers_name), 99999),
					if(locate(%(_txt)s, contact_no), locate(%(_txt)s, contact_no), 99999),
					idx desc,
					name, drivers_name, contact_no
				limit %(start)s, %(page_len)s""".format(**{
					'key': searchfield,
					'mcond': get_match_cond(doctype)
				}), {
					'txt': "%%%s%%" % txt,
					'_txt': txt.replace("%", ""),
					'start': start,
					'page_len': page_len
		})

'''########## Ver.2020.11.12 Begins, Phase-II by SHIV ##########'''
# following method is commented as no longer required by SHIV on 2020/11/20
'''
@frappe.whitelist()
def get_limit_details_old(site, branch, item):
	""" get quantity limit checks from CRM Branch Setting"""
	limits 	= frappe._dict()
	item_sub_group = frappe.db.get_value("Item", item, "item_sub_group")
	if not site:
		frappe.throw(_("Site is mandatory to get quantity limit details"))
	elif not branch:
		frappe.throw(_("Branch is mandatory to get quantity limit details"))
	elif not item:
		frappe.throw(_("Item is mandatory to get quantity limit details"))

	if frappe.db.exists("Site Item", {"parent": site, "item_sub_group": item_sub_group}):
		si = frappe.get_doc("Site Item", {"parent": site, "item_sub_group": item_sub_group})
		limits.update({
			'site_item_name': si.name,
			'total_available_quantity': flt(si.balance_quantity)
		})
	else:
		frappe.throw(_("Material {0} not found under Site").format(item_sub_group))

	st = frappe.get_doc("Site Type", frappe.db.get_value("Site", site, "site_type"))
	if cint(st.apply_limit_check):
		filters = {'site': site, 'branch': branch, 'item': item}
		cbsi = frappe.db.sql("""
			select *
			from `tabCRM Branch Setting Item` cbsi
			where cbsi.item = "{item}"
			and exists(select 1
				from `tabCRM Branch Setting` cbs
				where cbs.branch = "{branch}"
				and cbsi.parent = cbs.name) 
		""".format(**filters), as_dict=True)
		if not cbsi:
			frappe.throw(_("Material {0} not found under CRM Branch Setting").format(item))

		ll = frappe.db.sql("""
				select 
					ifnull(sum((case 
						when DATE(now()) between date_add(now(), interval -1 day) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as daily_ordered_quantity,
					ifnull(sum((case 
						when DATE(now()) between date_add(now(), interval -7 day) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as weekly_ordered_quantity,
					ifnull(sum((case 
						when DATE(now()) between date_add(now(), interval -1 month) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as monthly_ordered_quantity,
					ifnull(sum((case 
						when DATE(now()) between date_add(now(), interval -1 year) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as yearly_ordered_quantity,
					ifnull(sum(ifnull(total_quantity,0)),0) total_ordered_quantity
				from `tabCustomer Order`
				where site = "{site}"
				and branch = "{branch}"
				and item = "{item}"
				and docstatus = 1
				and DATE(now()) between date_add(now(), interval -1 year) and now()
		""".format(**filters), as_dict=True)
		limits.update({'has_limit': frappe._dict({
			'daily_quantity_limit': flt(cbsi[0].daily_quantity_limit),
			'daily_ordered_quantity': flt(ll[0].daily_ordered_quantity),
			'weekly_quantity_limit': flt(cbsi[0].weekly_quantity_limit),
			'weekly_ordered_quantity': flt(ll[0].weekly_ordered_quantity),
			'monthly_quantity_limit': flt(cbsi[0].monthly_quantity_limit),
			'monthly_ordered_quantity': flt(ll[0].monthly_ordered_quantity),
			'yearly_quantity_limit': flt(cbsi[0].yearly_quantity_limit),
			'yearly_ordered_quantity': flt(ll[0].yearly_ordered_quantity),
			'total_ordered_quantity': flt(ll[0].total_ordered_quantity)
		})})
	else:
		pass
	return limits
'''

# following method is created as a replacement for the following one to accommodate Phase-II changes by SHIV on 2020/11/20
# added new parameter selection based on to fetch respective values Kinley Dorji 2020/11/30
@frappe.whitelist()
def get_limit_details(product_category, customer, site, branch, item, selection_based_on):
	""" get quantity limit checks from CRM Branch Setting"""
	limits 	= frappe._dict()
	cond = ""

	if not product_category:
		frappe.throw(_("Product Category is mandatory to get quantity limit details"))
	elif product_category and not site and frappe.db.exists('Product Category', {'name': product_category, 'site_required': 1}):
		frappe.throw(_("Site is mandatory to get quantity limit details"))
	elif not branch and selection_based_on != "Lot":
		frappe.throw(_("Branch is mandatory to get quantity limit details"))
	# item will be validated only if selection based on is not Lot; Kinley Dorji 2020/11/30
	elif not item and selection_based_on != "Lot" and selection_based_on != "Measurement":
		frappe.throw(_("Item is mandatory to get quantity limit details"))

	if site and frappe.db.exists("Site Item", {"parent": site, "product_category": product_category}):
		si = frappe.get_doc("Site Item", {"parent": site, "product_category": product_category})
		limits.update({
			'site_item_name': si.name,
			'total_available_quantity': flt(si.balance_quantity)
		})
		cond = """where site = "{}" and branch = "{}" and item = "{}" """.format(site, branch, item)
	elif not site:
		limits.update({
			'site_item_name': None,
			'total_available_quantity': -1
		})
		cond = """where user = "{}" and branch = "{}" and item = "{}" """.format(customer, branch, item)
	else:
		frappe.throw(_("Material {0} not found under Site").format(product_category))

	apply_limit_check = 1
	if site:
		apply_limit_check = frappe.db.get_value("Site Type", frappe.db.get_value("Site", site, "site_type"), "apply_limit_check")

	if cint(apply_limit_check):
		filters = {'site': site, 'branch': branch, 'item': item}
		cbsi = frappe.db.sql("""
			select *
			from `tabCRM Branch Setting Item` cbsi
			where cbsi.item = "{item}"
			and exists(select 1
				from `tabCRM Branch Setting` cbs
				where cbs.branch = "{branch}"
				and cbsi.parent = cbs.name) 
		""".format(**filters), as_dict=True)

		#Added additional selection based on condition to prevent check if selection based on is Lot; Kinley Dorji 2020/11/30
		if selection_based_on == "Lot" or selection_based_on == "Measurement":
			limits.update({
				'limit_type': "Quantity",
				'daily_quantity_limit': 0,
				'daily_quantity_limit_count': 0,
				'weekly_quantity_limit': 0,
				'weekly_quantity_limit_count': 0,
				'monthly_quantity_limit': 0,
				'monthly_quantity_limit_count': 0,
				'yearly_quantity_limit': 0,
				'yearly_quantity_limit_count': 0,
			})
		elif not cbsi:
			frappe.throw(_("Material {0} not found under CRM Branch Setting").format(item))

		ll = frappe.db.sql("""
				select 
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -1 day) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as daily_ordered_quantity,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -1 day) and now() 
							then ifnull(noof_truck_load,0)
						else 0 
					end)),0) as daily_ordered_quantity_count,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -7 day) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as weekly_ordered_quantity,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -7 day) and now() 
							then ifnull(noof_truck_load,0)
						else 0 
					end)),0) as weekly_ordered_quantity_count,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -1 month) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as monthly_ordered_quantity,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -1 month) and now() 
							then ifnull(noof_truck_load,0)
						else 0 
					end)),0) as monthly_ordered_quantity_count,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -1 year) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as yearly_ordered_quantity,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -1 year) and now() 
							then ifnull(noof_truck_load,0)
						else 0 
					end)),0) as yearly_ordered_quantity_count,
					ifnull(sum(ifnull(total_quantity,0)),0) total_ordered_quantity,
					ifnull(sum(ifnull(noof_truck_load,0)),0) total_ordered_quantity_count
				from `tabCustomer Order`
				{}
				and docstatus = 1
		""".format(cond), as_dict=True)

		if not(selection_based_on == "Lot" or selection_based_on == "Measurement"):
			limits.update({'has_limit': frappe._dict({
				'limit_type': cbsi[0].limit_type,
				'daily_quantity_limit': flt(cbsi[0].daily_quantity_limit),
				'daily_ordered_quantity': flt(ll[0].daily_ordered_quantity),
				'daily_quantity_limit_count': flt(cbsi[0].daily_quantity_limit_count),
				'daily_ordered_quantity_count': flt(ll[0].daily_ordered_quantity_count),
				'weekly_quantity_limit': flt(cbsi[0].weekly_quantity_limit),
				'weekly_ordered_quantity': flt(ll[0].weekly_ordered_quantity),
				'weekly_quantity_limit_count': flt(cbsi[0].weekly_quantity_limit_count),
				'weekly_ordered_quantity_count': flt(ll[0].weekly_ordered_quantity_count),
				'monthly_quantity_limit': flt(cbsi[0].monthly_quantity_limit),
				'monthly_ordered_quantity': flt(ll[0].monthly_ordered_quantity),
				'monthly_quantity_limit_count': flt(cbsi[0].monthly_quantity_limit_count),
				'monthly_ordered_quantity_count': flt(ll[0].monthly_ordered_quantity_count),
				'yearly_quantity_limit': flt(cbsi[0].yearly_quantity_limit),
				'yearly_ordered_quantity': flt(ll[0].yearly_ordered_quantity),
				'yearly_quantity_limit_count': flt(cbsi[0].yearly_quantity_limit_count),
				'yearly_ordered_quantity_count': flt(ll[0].yearly_ordered_quantity_count),
				'total_ordered_quantity': flt(ll[0].total_ordered_quantity),
				'total_ordered_quantity_count': flt(ll[0].total_ordered_quantity_count)
			})})
		else:
			limits.update({'has_limit': frappe._dict({
				'daily_ordered_quantity': flt(ll[0].daily_ordered_quantity),
				'daily_ordered_quantity_count': flt(ll[0].daily_ordered_quantity_count),
				'weekly_ordered_quantity': flt(ll[0].weekly_ordered_quantity),
				'weekly_ordered_quantity_count': flt(ll[0].weekly_ordered_quantity_count),
				'monthly_ordered_quantity': flt(ll[0].monthly_ordered_quantity),
				'monthly_ordered_quantity_count': flt(ll[0].monthly_ordered_quantity_count),
				'yearly_ordered_quantity': flt(ll[0].yearly_ordered_quantity),
				'yearly_ordered_quantity_count': flt(ll[0].yearly_ordered_quantity_count),
				'total_ordered_quantity': flt(ll[0].total_ordered_quantity),
				'total_ordered_quantity_count': flt(ll[0].total_ordered_quantity_count)
			})})
	else:
		pass
	return limits

# following method is replaced with the above one to accommodate Phase-II, by SHIV on 2020/11/20
'''
@frappe.whitelist()
def get_limit_details(site, branch, item):
	""" get quantity limit checks from CRM Branch Setting"""
	limits 	= frappe._dict()
	item_sub_group = frappe.db.get_value("Item", item, "item_sub_group")
	if not site:
		frappe.throw(_("Site is mandatory to get quantity limit details"))
	elif not branch:
		frappe.throw(_("Branch is mandatory to get quantity limit details"))
	elif not item:
		frappe.throw(_("Item is mandatory to get quantity limit details"))

	if frappe.db.exists("Site Item", {"parent": site, "item_sub_group": item_sub_group}):
		si = frappe.get_doc("Site Item", {"parent": site, "item_sub_group": item_sub_group})
		limits.update({
			'site_item_name': si.name,
			'total_available_quantity': flt(si.balance_quantity)
		})
	else:
		frappe.throw(_("Material {0} not found under Site").format(item_sub_group))

	st = frappe.get_doc("Site Type", frappe.db.get_value("Site", site, "site_type"))
	if cint(st.apply_limit_check):
		filters = {'site': site, 'branch': branch, 'item': item}
		cbsi = frappe.db.sql("""
			select *
			from `tabCRM Branch Setting Item` cbsi
			where cbsi.item = "{item}"
			and exists(select 1
				from `tabCRM Branch Setting` cbs
				where cbs.branch = "{branch}"
				and cbsi.parent = cbs.name) 
		""".format(**filters), as_dict=True)
		if not cbsi:
			frappe.throw(_("Material {0} not found under CRM Branch Setting").format(item))

		ll = frappe.db.sql("""
				select 
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -1 day) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as daily_ordered_quantity,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -1 day) and now() 
							then ifnull(noof_truck_load,0)
						else 0 
					end)),0) as daily_ordered_quantity_count,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -7 day) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as weekly_ordered_quantity,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -7 day) and now() 
							then ifnull(noof_truck_load,0)
						else 0 
					end)),0) as weekly_ordered_quantity_count,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -1 month) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as monthly_ordered_quantity,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -1 month) and now() 
							then ifnull(noof_truck_load,0)
						else 0 
					end)),0) as monthly_ordered_quantity_count,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -1 year) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as yearly_ordered_quantity,
					ifnull(sum((case 
						when posting_date between date_add(now(), interval -1 year) and now() 
							then ifnull(noof_truck_load,0)
						else 0 
					end)),0) as yearly_ordered_quantity_count,
					ifnull(sum(ifnull(total_quantity,0)),0) total_ordered_quantity,
					ifnull(sum(ifnull(noof_truck_load,0)),0) total_ordered_quantity_count
				from `tabCustomer Order`
				where site = "{site}"
				and branch = "{branch}"
				and item = "{item}"
				and docstatus = 1
		""".format(**filters), as_dict=True)

		limits.update({'has_limit': frappe._dict({
			'limit_type': cbsi[0].limit_type,
			'daily_quantity_limit': flt(cbsi[0].daily_quantity_limit),
			'daily_ordered_quantity': flt(ll[0].daily_ordered_quantity),
			'daily_quantity_limit_count': flt(cbsi[0].daily_quantity_limit_count),
			'daily_ordered_quantity_count': flt(ll[0].daily_ordered_quantity_count),
			'weekly_quantity_limit': flt(cbsi[0].weekly_quantity_limit),
			'weekly_ordered_quantity': flt(ll[0].weekly_ordered_quantity),
			'weekly_quantity_limit_count': flt(cbsi[0].weekly_quantity_limit_count),
			'weekly_ordered_quantity_count': flt(ll[0].weekly_ordered_quantity_count),
			'monthly_quantity_limit': flt(cbsi[0].monthly_quantity_limit),
			'monthly_ordered_quantity': flt(ll[0].monthly_ordered_quantity),
			'monthly_quantity_limit_count': flt(cbsi[0].monthly_quantity_limit_count),
			'monthly_ordered_quantity_count': flt(ll[0].monthly_ordered_quantity_count),
			'yearly_quantity_limit': flt(cbsi[0].yearly_quantity_limit),
			'yearly_ordered_quantity': flt(ll[0].yearly_ordered_quantity),
			'yearly_quantity_limit_count': flt(cbsi[0].yearly_quantity_limit_count),
			'yearly_ordered_quantity_count': flt(ll[0].yearly_ordered_quantity_count),
			'total_ordered_quantity': flt(ll[0].total_ordered_quantity),
			'total_ordered_quantity_count': flt(ll[0].total_ordered_quantity_count)
		})})
	else:
		pass
	return limits
'''

# following method is commented and new code added below by SHIV on 2020/11/12
'''
@frappe.whitelist()
def get_transport_mode(site="",branch=""):
	modes = []
	tl = frappe.db.sql("""
		select
			cbs.has_common_pool,
			cbs.allow_self_owned_transport,
			cbs.allow_other_transport,
			ifnull((select s.allow_private_pool
				from `tabSite` s
				where s.name = "{1}"
				and exists(select 1
				from `tabSite Private Pool` spp
				where spp.parent = s.name)),0) allow_private_pool
		from `tabCRM Branch Setting` cbs
		where cbs.branch = "{0}"
	""".format(branch, site), as_dict=True)

	if tl:
		if tl[0].has_common_pool:
			modes.append("Common Pool")
		if tl[0].allow_self_owned_transport:
			modes.append("Self Owned Transport")
		if tl[0].allow_other_transport:
			modes.append("Others")
		if tl[0].allow_private_pool:
			modes.append("Private Pool")
	return modes
'''

# following method is modified to accommodate Phase-II changes by SHIV on 2020/11/12
@frappe.whitelist()
def get_transport_mode(site="", branch="", product_category=""):
	modes = []
	if product_category != "Boulders and Aggregates":
		tl = frappe.db.sql("""
			select
				cbs.has_common_pool,
				cbs.allow_self_owned_transport,
				cbs.allow_other_transport,
				ifnull((select s.allow_private_pool
					from `tabSite` s
					where s.name = "{}"
					and exists(select 1
					from `tabSite Private Pool` spp
					where spp.parent = s.name)),0) allow_private_pool
			from `tabCRM Branch Setting` cbs, `tabProduct Category` pc
			where cbs.branch = "{}"
			and cbs.product_category = "{}"
			and pc.name = cbs.product_category
			and pc.transport_mode_required = 1
		""".format(site, branch, product_category), as_dict=True)
	else:
		tl = frappe.db.sql("""
			select
				cbs.has_common_pool,
				cbs.allow_self_owned_transport,
				cbs.allow_other_transport,
				ifnull((select s.allow_private_pool
					from `tabSite` s
					where s.name = "{}"
					and exists(select 1
					from `tabSite Private Pool` spp
					where spp.parent = s.name)),0) allow_private_pool
			from `tabCRM Branch Setting` cbs, `tabProduct Category` pc
			where cbs.branch = "{}"
			and cbs.product_category = "{}"
			and pc.name = cbs.product_category
			and pc.transport_mode_required = 0
		""".format(site, branch, product_category), as_dict=True)

	if tl:
		if tl[0].has_common_pool:
			modes.append("Common Pool")
		if tl[0].allow_self_owned_transport:
			modes.append("Self Owned Transport")
		if tl[0].allow_other_transport:
			modes.append("Others")
		if tl[0].allow_private_pool:
			modes.append("Private Pool")
	return modes
'''########## Ver.2020.11.12 Ends, Phase-II by SHIV ##########'''

def cancel_online_payment():
	''' Cancel requests pending for more than 1hr in Online Payment'''
	for i in frappe.db.sql("""select name,status,modified from `tabOnline Payment` where status = 'Pending'
		and (time_to_sec(timediff(now(), modified )) / 3600) > 1""", as_dict=True):
		doc = frappe.get_doc("Online Payment", i.name)
		doc.status = 'Cancelled'
		doc.save(ignore_permissions=True)
	frappe.db.commit()

def notify_customers(msg=None, debug=1):
	tran_id = 1
	staff = ['97517115380','97517839763','97517448509']
	if not msg:
		msg = "NRDCL would like to request all valued customers who have applied for sand through My Resources App to kindly confirm the receipt of the sand delivery through the App ONLY AFTER the sand has been delivered at your construction site, and not before that. Please ensure to verify the truck number mentioned in your delivery confirmation screen in the App. Thank you."
	customers = frappe.db.sql_list("""select distinct u.mobile_no 
			from `tabUser` u 
			where u.account_type = 'CRM' 
			and ifnull(u.enabled,0) = 1 
			and u.mobile_no is not null
			and not exists(select 1
				from bulk_sms b
				where b.id = {}
				and b.mobile_no = u.mobile_no)
			""".format(tran_id))
	
	customers += staff
	counter = 0
	tot_success = 0
	tot_failed  = 0
	for i in customers:
		counter += 1
		if not debug:
			try:
				send_sms(i,msg)
				frappe.db.sql("insert into bulk_sms values({},'{}',NOW())".format(tran_id,i))
				frappe.db.commit()
				tot_success += 1
			except:
				tot_failed += 1
		print counter,i

	print 'Total no.of records: {}'.format(counter)
	print 'Successful         : {}/{}'.format(tot_success,counter)
	print 'Failed             : {}/{}'.format(tot_failed,counter)

# following method created for Timber by SHIV on 2020/11/25
@frappe.whitelist()
def get_product_groups(product_category):
	return frappe.db.sql("""
		select distinct product_group, selection_based_on
		from `tabProduct Category Item`
		where parent = "{}"
		and product_group is not null
		order by product_group
	""".format(product_category), as_dict=True)

# following method created for Timber by SHIV on 2020/11/25
@frappe.whitelist()
def get_product_groups_query(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""
		select distinct product_group, selection_based_on
		from `tabProduct Category Item`
		where parent = "{}"
		and product_group is not null
		order by product_group
	""".format(filters.get("product_category")))

# following method created for by-products by SHIV on 2020/12/30
@frappe.whitelist()
def get_item_types(product_category):
	return frappe.db.sql("""
		select distinct item_sub_group
		from `tabProduct Category Item`
		where parent = "{}"
		order by item_sub_group
	""".format(product_category))

# following method created for by-products by SHIV on 2021/01/22
@frappe.whitelist()
def get_item_types_query(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""
		select distinct item_sub_group
		from `tabProduct Category Item`
		where parent = "{}"
		order by item_sub_group
	""".format(filters.get("product_category")))

# following method for Sawn Timber by Thukten on 2020/12/02
@frappe.whitelist()
def get_sawn_timber(branch, item=None, size=None, length=None):
	if branch:
		if not item:
			item_list = frappe.db.sql("""
							select a.item, a.item_name, a.size, a.length, a.balance_qty
							from `tabStandard Sawn Balance` a
							where a.balance_qty > 0 and a.branch = '{0}'
							and a.creation = (select max(b.creation) 
								from `tabStandard Sawn Balance` b where b.docstatus = 1 and 
								b.item=a.item and b.balance_qty > 0 and b.branch='{0}')
						""".format(branch), as_dict=True)
		else:
			if not size:
				item_list = frappe.db.sql("""
					select a.item, a.item_name, a.size, a.length, a.balance_qty 
					from `tabStandard Sawn Balance` a
					where a.balance_qty > 0 
					and a.branch = '{0}'
					and a.item = '{1}'
					and a.creation= (select max(creation) 
						from `tabStandard Sawn Balance` b 
						where b.docstatus = 1 and b.item=a.item 
						and b.size = a.size
						and b.branch='{0}')
				""".format(branch, item), as_dict=True)
			else:
				if not length:
					item_list = frappe.db.sql("""
						select a.item, a.item_name, a.size, a.length, a.balance_qty
						from `tabStandard Sawn Balance` a
						where a.docstatus = 1 and a.balance_qty > 0 
						and a.branch = '{0}'
						and a.item = '{1}'
						and a.size = '{2}'
						and a.creation = (select max(b.creation) from `tabStandard Sawn Balance` b
                                                	where b.docstatus = 1 and b.item=a.item
                                                	and b.size = a.size
                                                	and b.branch='{0}' and b.length = a.length)
					""".format(branch, item, size), as_dict=True)
				else:
					
					transaction_date = getdate(nowdate())
					item_price = frappe.db.sql("""select a.parent, b.selling_price 
												from `tabSelling Price Branch` a, `tabSelling Price Rate` b 
												where a.parent = b.parent and a.branch = '{0}' 
												and b.particular = '{1}' 
												and exists (select 1 
														from `tabSelling Price` 
														where name = a.parent and '{2}' 
														between from_date and to_date
													) 
												group by a.parent""".format(branch, item, transaction_date), as_dict=True)
					if not item_price:
						item_species = frappe.db.get_value("Item", item, "species")
						if item_species:
							timber_class, timber_type = frappe.db.get_value("Timber Species", item_species, ["timber_class", "timber_type"])
						item_sub_group = frappe.db.get_value("Item", item, "item_sub_group")
						if item_sub_group:
							item_price = frappe.db.sql(""" select a.parent, b.particular, b.timber_type, b.selling_price  
														from `tabSelling Price Branch` a, `tabSelling Price Rate` b 
														where a.parent = b.parent and a.branch = '{0}' 
														and b.particular = '{1}' 
														and b.timber_type = '{2}' 
														and b.item_sub_group = '{4}' 
														and exists (select 1 
																	from `tabSelling Price` 
																	where name = a.parent 
																	and '{3}' between from_date and to_date) 
																	and (b.location is NULL or b.location = ''
																) 
														group by a.parent""".format(branch, timber_class, timber_type, transaction_date, item_sub_group), as_dict=True)	
					if item_price:
						for a in item_price:
							sp = a.selling_price
							price_template = a.parent 

					item_list = frappe.db.sql("""
						select a.name, a.item, a.item_name, a.size, a.length, a.balance_qty, a.unit_cft, '{0}' as selling_price, '{5}' as price_template
						from `tabStandard Sawn Balance` a
						where a.docstatus = 1 and a.balance_qty > 0 
						and a.branch = '{1}'
						and a.item = '{2}'
						and a.size = '{3}'
						and a.length = '{4}'
						order by creation desc limit 1
					""".format(sp, branch, item, size, length, price_template), as_dict=True)
	return item_list

@frappe.whitelist()
def get_sawn_branch():
	items = [str('DUMMY')]
	sawn_items = []
	sawn_items = frappe.db.sql("select distinct item from `tabStandard Sawn Balance`", as_dict=True)
	if sawn_items:
		for d in sawn_items:
			items.append(str(d['item']))
	if items == []:
		bl = []
	else:
		bl = frappe.db.sql("""
				select distinct cbs.branch, 
				(case
					when cbs.has_common_pool = 1 then 'Has Common Pool facility'
					else '<span style = "color:white;padding: 0px 5px;border-radius: 2px; background-color:tomato;">Does not have Common Pool facility</span>'
				end) as has_common_pool_msg
			from 
				`tabCRM Branch Setting` cbs
			inner join `tabCRM Branch Setting Item` cbsi 
				on cbsi.parent = cbs.name
				and cbsi.has_stock = 1
			where cbsi.item_sub_group = 'Sawn'
			and exists(select 1 from `tabStandard Sawn Balance` ssb where ssb.branch = cbs.branch
			and ssb.docstatus = 1
			and ssb.balance_qty > 0
			and ssb.item in {0}
			and ssb.item = cbsi.item
			and ssb.creation = (select b.creation
				from `tabStandard Sawn Balance` b where
			b.item=ssb.item and b.branch=ssb.branch and b.docstatus = 1 group by b.creation desc limit 1)
			 )
		""".format(tuple(items)), as_dict = True)

	return bl

@frappe.whitelist()
def get_product_group_name(type=None):
	if type == "Lot":
		return "Timber Prime Products"
	else:
		return "Sawn Timber"

@frappe.whitelist()
def get_item_name(item_code=None):
	if item_code:
		item_name = frappe.db.get_value("Item",{"item_code": item_code},"item_name")
	return item_name

@frappe.whitelist(allow_guest=True)
def get_faq():
	return frappe.db.sql("select * from `tabFAQ` where isdisplay=1 order by display_order, creation", as_dict=True)

@frappe.whitelist(allow_guest=True)
def get_tor(tor_type=None):
	cond = ""
	if tor_type:
		cond = 'where name = "{}"'.format(tor_type)
	return frappe.db.sql("select * from `tabTOR` {}".format(cond), as_dict=True)


