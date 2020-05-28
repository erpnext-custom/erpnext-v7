from __future__ import unicode_literals
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
		and now() between sp.from_date and sp.to_date
		and spb.parent  = sp.name
		and spb.branch  = cbs.branch
		and spr.parent  = sp.name
		and spr.price_based_on = 'Item'
		and spr.particular = i.name
	""".format(filters.get("item_sub_group")))

	if not bl:
		frappe.throw(_("No material source found"))
	return bl

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
		and now() between sp.from_date and sp.to_date
		and spb.parent  = sp.name
		and spb.branch  = cbs.branch
		and spr.parent  = sp.name
		and spr.price_based_on = 'Item'
		and spr.particular = i.name
	""".format(item_sub_group), as_dict=True)

	if not bl:
		frappe.throw(_("No material source found"))
	return bl

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
			and now() between sp.from_date and sp.to_date
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
				where now() between sp.from_date and sp.to_date
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
		and now() between sp.from_date and sp.to_date
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
				where now() between sp.from_date and sp.to_date
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
			on now() between sp.from_date and sp.to_date
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
		where now() between sp.from_date and sp.to_date  
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
		where now() between sp.from_date and sp.to_date  
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
		where now() between sp.from_date and sp.to_date  
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
		where now() between sp.from_date and sp.to_date  
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
		where now() between sp.from_date and sp.to_date  
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

@frappe.whitelist()
def get_vehicles(user, site=None, transport_mode=None):
	cond = ""

	if transport_mode:
		if transport_mode == "Self Owned Transport":
			if not user:
				frappe.throw(_("Please select a customer first"))
			cond = """and v.user = "{}" """.format(user)

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
                return frappe.db.sql("""select vehicle, requesting_date_time, token from `tabLoad Request`
                                        where load_status = 'Queued'
                                        and crm_branch = '{0}'
                                        and vehicle_capacity = '{1}'
                                        order by requesting_date_time, token limit 1
                                """.format(filters.get("branch"), filters.get("total_quantity"), key=frappe.db.escape(searchfield),
                                 match_condition=get_match_cond(doctype)), {
                                'txt': "%%%s%%" % frappe.db.escape(txt)
                        })

	if transport_mode in ["Self Owned Transport", "Private Pool"]:
		cond = " and v.user = '{0}'".format(user_id) if transport_mode == "Self Owned Transport" else ""
			
                return frappe.db.sql("""select name, drivers_name, contact_no from `tabVehicle` v
                                        where v.vehicle_status = 'Active'
					{0}
					and exists(
						select 1 from `tabCustomer Order Vehicle` c 
						where c.parent = '{1}' 
						and c.vehicle = v.name  
					)
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


@frappe.whitelist()
def get_limit_details_old(site, branch, item):
	''' get quantity limit checks from CRM Branch Setting'''
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
						when now() between date_add(now(), interval -1 day) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as daily_ordered_quantity,
					ifnull(sum((case 
						when now() between date_add(now(), interval -7 day) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as weekly_ordered_quantity,
					ifnull(sum((case 
						when now() between date_add(now(), interval -1 month) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as monthly_ordered_quantity,
					ifnull(sum((case 
						when now() between date_add(now(), interval -1 year) and now() 
							then ifnull(total_quantity,0)
						else 0 
					end)),0) as yearly_ordered_quantity,
					ifnull(sum(ifnull(total_quantity,0)),0) total_ordered_quantity
				from `tabCustomer Order`
				where site = "{site}"
				and branch = "{branch}"
				and item = "{item}"
				and docstatus = 1
				and now() between date_add(now(), interval -1 year) and now()
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

@frappe.whitelist()
def get_limit_details(site, branch, item):
	''' get quantity limit checks from CRM Branch Setting'''
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
