from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint, nowdate, getdate, formatdate

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
def get_branch_source(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	""" get list of `CRM Branch`s based on `Item Sub Group` 
	    used under:
		1. Site Registration
	"""
	if not filters.get("item_sub_group"):
		frappe.throw(_("Please select a material first"))

	bl = frappe.db.sql("""
		select distinct cbs.branch, 
			has_common_pool,
			(case
				when cbs.has_common_pool = 1 then 'Has Common Pool facility'
				else '<span style = "color:white;padding: 0px 5px;border-radius: 2px; background-color:tomato;">Does not have Common Pool facility</span>'
			end) as has_common_pool_msg
		from `tabCRM Branch Setting` cbs, `tabCRM Branch Setting Item` cbsi
		where cbsi.item_sub_group = "{0}"
		and cbsi.has_stock = 1
		and cbs.name = cbsi.parent
	""".format(filters.get("item_sub_group")))

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
					and sd.item 	= cbsi.item
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
	columns   = ["cbs.branch", "cbs.has_common_pool"]
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
def get_vehicles(user):
	vl = frappe.db.sql("""
		select 
			name vehicle,
			drivers_name,
			contact_no,
			vehicle_capacity
		from `tabVehicle`
		where user = "{user}"
		and docstatus = 1
		and vehicle_status = "Active"
	""".format(user=user), as_dict=True)
	if not vl:
		for i in frappe.db.get_all("Transport Request",{"user": user, "docstatus": 0, "self_arranged": 1}):
			frappe.throw(_("Your request for vehicle registration (Request ID#{0}) is awaiting approval").format(i.name))

		frappe.throw(_("Please register a vehicle first"))
	return vl

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
        if not filters.get("customer_order"):
                frappe.throw("Select Customer Order First")
        from erpnext.controllers.queries import get_match_cond
        user_id, transport_mode = frappe.db.get_value("Customer Order", filters.get("customer_order"), ["user","transport_mode"])
        if transport_mode == "Common Pool":
                return frappe.db.sql("""select vehicle, requesting_date_time, transporter, token from `tabLoad Request`
                                        where load_status = 'Queued'
                                        and crm_branch = '{1}'
					and docstatus = 1
                                        and exists(
                                                select 1 from `tabVehicle` where docstatus = 1 and vehicle_status = 'Active'
                                        )
                                        order by requesting_date_time, token limit 1
                                """.format(filters.get("posting_date"), filters.get("branch"), key=frappe.db.escape(searchfield),
                                 match_condition=get_match_cond(doctype)), {
                                'txt': "%%%s%%" % frappe.db.escape(txt)
                        })
        else:
                return frappe.db.sql("""select name, drivers_name, contact_no from `tabVehicle`
                                        where user = '{0}' 
                                        and docstatus = 1 
                                        and vehicle_status = 'Active'
					and self_arranged = 1
                                """.format(user_id, key=frappe.db.escape(searchfield),
                                 match_condition=get_match_cond(doctype)), {
                                'txt': "%%%s%%" % frappe.db.escape(txt)
                        })

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
