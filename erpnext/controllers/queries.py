# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import get_match_cond
from frappe.model.db_query import DatabaseQuery
from frappe.utils import nowdate
from erpnext.custom_utils import get_branch_cc

def get_filters_cond(doctype, filters, conditions):
	if filters:
		flt = filters
		if isinstance(filters, dict):
			filters = filters.items()
			flt = []
			for f in filters:
				if isinstance(f[1], basestring) and f[1][0] == '!':
					flt.append([doctype, f[0], '!=', f[1][1:]])
				else:
					flt.append([doctype, f[0], '=', f[1]])

		query = DatabaseQuery(doctype)
		query.filters = flt
		query.conditions = conditions
		query.build_filter_conditions(flt, conditions)

		cond = ' and ' + ' and '.join(query.conditions)
	else:
		cond = ''
	return cond

 # searches for active employees
def employee_query(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select name, employee_name, designation, branch from `tabEmployee`
		where status = 'Active'
			and docstatus < 2
			and ({key} like %(txt)s
				or employee_name like %(txt)s)
			{mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, employee_name), locate(%(_txt)s, employee_name), 99999),
			idx desc,
			name, employee_name
		limit %(start)s, %(page_len)s""".format(**{
			'key': searchfield,
			'mcond': get_match_cond(doctype)
		}), {
			'txt': "%%%s%%" % txt,
			'_txt': txt.replace("%", ""),
			'start': start,
			'page_len': page_len
		})

 # searches for leads which are not converted
def lead_query(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select name, lead_name, company_name from `tabLead`
		where docstatus < 2
			and ifnull(status, '') != 'Converted'
			and ({key} like %(txt)s
				or lead_name like %(txt)s
				or company_name like %(txt)s)
			{mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, lead_name), locate(%(_txt)s, lead_name), 99999),
			if(locate(%(_txt)s, company_name), locate(%(_txt)s, company_name), 99999),
			idx desc,
			name, lead_name
		limit %(start)s, %(page_len)s""".format(**{
			'key': searchfield,
			'mcond':get_match_cond(doctype)
		}), {
			'txt': "%%%s%%" % txt,
			'_txt': txt.replace("%", ""),
			'start': start,
			'page_len': page_len
		})

 # searches for customer
def customer_query(doctype, txt, searchfield, start, page_len, filters):
	cust_master_name = frappe.defaults.get_user_default("cust_master_name")

	if cust_master_name == "Customer Name":
		fields = ["name", "customer_group", "territory"]
	else:
		fields = ["name", "customer_name", "customer_group", "territory"]
		
	meta = frappe.get_meta("Customer")
	fields = fields + [f for f in meta.get_search_fields() if not f in fields]

	fields = ", ".join(fields)

	return frappe.db.sql("""select {fields} from `tabCustomer`
		where docstatus < 2
			and ({key} like %(txt)s
				or customer_name like %(txt)s) and disabled=0
			{mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, customer_name), locate(%(_txt)s, customer_name), 99999),
			idx desc,
			name, customer_name
		limit %(start)s, %(page_len)s""".format(**{
			"fields": fields,
			"key": searchfield,
			"mcond": get_match_cond(doctype)
		}), {
			'txt': "%%%s%%" % txt,
			'_txt': txt.replace("%", ""),
			'start': start,
			'page_len': page_len
		})


#filtering family members based on sws membership
@frappe.whitelist()
def filter_sws_member_item(doctype, txt, searchfield, start, page_len, filters):
        # frappe.throw("here")
        data = []
        if not filters.get("employee"):
            frappe.throw("Please select employee first.")
        return frappe.db.sql("""
        select a.name as name, a.full_name as full_name from `tabSWS Membership Item` a, `tabSWS Membership` b where a.parent = b.name
        and b.employee = '{0}' and a.status != 'Claimed' and b.docstatus = 1
        """.format(filters.get("employee")))

#Added by Kinley DOrji to filter CRM customers in lot allotment
@frappe.whitelist()
def get_crm_users(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select name, full_name from `tabUser` where account_type = 'CRM' and enabled = 1
			and ({key} like %(txt)s
				or full_name like %(txt)s)
			{mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, full_name), locate(%(_txt)s, username), 99999),
			idx desc,
			name, full_name
		limit %(start)s, %(page_len)s""".format(**{
			'key': searchfield,
			'mcond': get_match_cond(doctype)
		}), {
			'txt': "%%%s%%" % txt,
			'_txt': txt.replace("%", ""),
			'start': start,
			'page_len': page_len
		})
#Added by Kinley Dorji to filter items based on the product category selected
@frappe.whitelist()
def get_pc_items(doctype, txt, searchfield, start, page_len, filters):
	if filters.get("product_category") == None or filters.get("product_category")=="":
		frappe.throw("Please select product category first")
	else:
		item_list = frappe.db.sql("""
			select name, item_name from `tabItem` where item_sub_group in (select item_sub_group from `tabProduct Category Item` where parent = '{}');
		""".format(filters.get("product_category")))
	return item_list

#Added by Kinley DOrji to filter Sawn Item in Customer Order 2020/12/08
@frappe.whitelist()
def get_sawn_items(doctype, txt, searchfield, start, page_len, filters):
	if filters.get("branch"):
		if not filters.get("item"):
			item_list = frappe.db.sql("""
							select a.item, a.item_name, a.size, a.length, a.balance_qty
							from `tabStandard Sawn Balance` a
							where a.balance_qty > 0 and a.branch = '{0}'
							and a.creation = (select max(b.creation) 
								from `tabStandard Sawn Balance` b where
								b.item=a.item and b.balance_qty > 0 and b.branch='{0}')
						""".format(filters.get("branch")))
		else:
			if not filters.get("size"):
				item_list = frappe.db.sql("""
					select a.size 
					from `tabStandard Sawn Balance` a
					where a.balance_qty > 0 
					and a.branch = '{0}'
					and a.item = '{1}'
					and a.creation= (select max(creation) from `tabStandard Sawn Balance` b
						where b.item=a.item
						and b.size = a.size
						and b.branch='{0}')
				""".format(filters.get("branch"), filters.get("item")))
			else:
				if not filters.get("length"):
					item_list = frappe.db.sql("""
						select a.length
						from `tabStandard Sawn Balance` a
						where a.balance_qty > 0 
						and a.branch = '{0}'
						and a.item = '{1}'
						and a.size = '{2}'
						and a.creation = (select max(b.creation) from `tabStandard Sawn Balance` b
                                                	where b.item=a.item
                                                	and b.size = a.size
                                                	and b.branch='{0}' and b.length = a.length)
					""".format(filters.get("branch"), filters.get("item"), filters.get("size")))
				else:	
					transaction_date = getdate(nowdate())
					item_price = frappe.db.sql("""select a.parent, b.selling_price from `tabSelling Price Branch` a, `tabSelling Price Rate` b where a.parent = b.parent and a.branch = '{0}' and b.particular = '{1}' and exists (select 1 from `tabSelling Price` where name = a.parent and '{2}' between from_date and to_date) group by a.parent""".format(filters.get("branch"), filtrs.get("item"), filters.get("transaction_date")), as_dict=True)
					if not item_price:
						item_species = frappe.db.get_value("Item", filters.get("item"), "species")
						if item_species:
							timber_class, timber_type = frappe.db.get_value("Timber Species", item_species, ["timber_class", "timber_type"])
						item_sub_group = frappe.db.get_value("Item", filters.get("item"), "item_sub_group")
						if item_sub_group:
							item_price = frappe.db.sql(""" select a.parent, b.particular, b.timber_type, b.selling_price  from `tabSelling Price Branch` a, `tabSelling Price Rate` b where a.parent = b.parent and a.branch = '{0}' and b.particular = '{1}' and b.timber_type = '{2}' and b.item_sub_group = '{4}' and exists (select 1 from `tabSelling Price` where name = a.parent and '{3}' between from_date and to_date) and (b.location is NULL or b.location = '') group by a.parent""".format(filters.get("branch"), timber_class, timber_type, transaction_date, item_sub_group), as_dict=True)	
					if item_price:
						for a in item_price:
							sp = a.selling_price
							price_template = a.parent 

					item_list = frappe.db.sql("""
						select '{5}' as price_template
						from `tabStandard Sawn Balance` a
						where a.balance_qty > 0 
						and a.branch = '{1}'
						and a.item = '{2}'
						and a.size = '{3}'
						and a.length = '{4}'
						order by creation desc limit 1
					""".format(sp, filters.get("branch"), filters.get("item"), filters.get("size"), filters.get("length"), price_template))
	return item_list
	# return frappe.db.sql("""select name, full_name from `tabUser` where account_type = 'CRM' and enabled = 1
	# 		and ({key} like %(txt)s
	# 			or full_name like %(txt)s)
	# 		{mcond}
	# 	order by
	# 		if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
	# 		if(locate(%(_txt)s, full_name), locate(%(_txt)s, username), 99999),
	# 		idx desc,
	# 		name, full_name
	# 	limit %(start)s, %(page_len)s""".format(**{
	# 		'key': searchfield,
	# 		'mcond': get_match_cond(doctype)
	# 	}), {
	# 		'txt': "%%%s%%" % txt,
	# 		'_txt': txt.replace("%", ""),
	# 		'start': start,
	# 		'page_len': page_len
	# 	})


@frappe.whitelist()
def filter_lot_list(doctype, txt, searchfield, start, page_len, filters):
        if not filters.get("branch") and not filters.get("item"):
                frappe.throw("Select Branch and Item First")
        from erpnext.controllers.queries import get_match_cond
        return frappe.db.sql("""select lot_no, item_sub_group, branch, item_name from `tabLot List` ll
                                where branch = '{0}' 
                                and docstatus = 1 
                                and item = '{1}' 
                                and (sales_order is NULL or sales_order = "")
                     		and (ll.stock_entry is NULL or ll.stock_entry = "")
				and (ll.production is NULL or ll.production = "")
                        """.format(filters.get("branch"), filters.get("item"), key=frappe.db.escape(searchfield),
                         match_condition=get_match_cond(doctype)), {
                        'txt': "%%%s%%" % frappe.db.escape(txt)
                })

@frappe.whitelist()
def filter_lots(doctype, txt, searchfield, start, page_len, filters):
        if not filters.get("branch") and not filters.get("item"):
                frappe.throw("Select Branch and Item First")
        from erpnext.controllers.queries import get_match_cond
        return frappe.db.sql("""select lot_no, lld.item_sub_group, branch, lld.item_name from `tabLot List` ll, `tabLot List Details` lld
                                where ll.name = lld.parent
								and branch = '{0}' 
                                and ll.docstatus = 1 
                                and lld.item = '{1}' 
                                and (sales_order is NULL or sales_order = "")
                                and (production is NULL or production = "")
                        """.format(filters.get("branch"), filters.get("item"), key=frappe.db.escape(searchfield),
                         match_condition=get_match_cond(doctype)), {
                        'txt': "%%%s%%" % frappe.db.escape(txt)
                })


# searches for supplier
def supplier_query(doctype, txt, searchfield, start, page_len, filters):
	supp_master_name = frappe.defaults.get_user_default("supp_master_name")
	if supp_master_name == "Supplier Name":
		fields = ["name", "supplier_type"]
	else:
		fields = ["name", "supplier_name", "supplier_type"]
	fields = ", ".join(fields)

	return frappe.db.sql("""select {field} from `tabSupplier`
		where docstatus < 2
			and ({key} like %(txt)s
				or supplier_name like %(txt)s) and disabled=0
			{mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, supplier_name), locate(%(_txt)s, supplier_name), 99999),
			idx desc,
			name, supplier_name
		limit %(start)s, %(page_len)s """.format(**{
			'field': fields,
			'key': searchfield,
			'mcond':get_match_cond(doctype)
		}), {
			'txt': "%%%s%%" % txt,
			'_txt': txt.replace("%", ""),
			'start': start,
			'page_len': page_len
		})

def tax_account_query(doctype, txt, searchfield, start, page_len, filters):
	tax_accounts = frappe.db.sql("""select name, parent_account	from tabAccount
		where tabAccount.docstatus!=2
			and account_type in (%s)
			and is_group = 0
			and company = %s
			and `%s` LIKE %s
		order by idx desc, name
		limit %s, %s""" %
		(", ".join(['%s']*len(filters.get("account_type"))), "%s", searchfield, "%s", "%s", "%s"),
		tuple(filters.get("account_type") + [filters.get("company"), "%%%s%%" % txt,
			start, page_len]))
	if not tax_accounts:
		tax_accounts = frappe.db.sql("""select name, parent_account	from tabAccount
			where tabAccount.docstatus!=2 and is_group = 0
				and company = %s and `%s` LIKE %s limit %s, %s"""
			% ("%s", searchfield, "%s", "%s", "%s"),
			(filters.get("company"), "%%%s%%" % txt, start, page_len))

	return tax_accounts

def item_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	conditions = []

	return frappe.db.sql("""select tabItem.name, tabItem.item_group, tabItem.item_sub_group, tabItem.image,
		if(length(tabItem.item_name) > 40,
			concat(substr(tabItem.item_name, 1, 40), "..."), item_name) as item_name,
		if(length(tabItem.description) > 40, \
			concat(substr(tabItem.description, 1, 40), "..."), description) as decription
		from tabItem
		where tabItem.docstatus < 2
			and tabItem.has_variants=0
			and tabItem.disabled=0
			and (tabItem.end_of_life > %(today)s or ifnull(tabItem.end_of_life, '0000-00-00')='0000-00-00')
			and (tabItem.`{key}` LIKE %(txt)s
				or tabItem.item_group LIKE %(txt)s
				or tabItem.item_sub_group LIKE %(txt)s
				or tabItem.item_name LIKE %(txt)s
				or tabItem.description LIKE %(txt)s)
			{fcond} {mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, item_name), locate(%(_txt)s, item_name), 99999),
			idx desc,
			name, item_name
		limit %(start)s, %(page_len)s """.format(key=searchfield,
			fcond=get_filters_cond(doctype, filters, conditions).replace('%', '%%'),
			mcond=get_match_cond(doctype).replace('%', '%%')),
			{
				"today": nowdate(),
				"txt": "%%%s%%" % txt,
				"_txt": txt.replace("%", ""),
				"start": start,
				"page_len": page_len
			}, as_dict=as_dict)

def bom(doctype, txt, searchfield, start, page_len, filters):
	conditions = []

	return frappe.db.sql("""select tabBOM.name, tabBOM.item
		from tabBOM
		where tabBOM.docstatus=1
			and tabBOM.is_active=1
			and tabBOM.`{key}` like %(txt)s
			{fcond} {mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			idx desc, name
		limit %(start)s, %(page_len)s """.format(
			fcond=get_filters_cond(doctype, filters, conditions),
			mcond=get_match_cond(doctype),
			key=frappe.db.escape(searchfield)),
		{
			'txt': "%%%s%%" % frappe.db.escape(txt),
			'_txt': txt.replace("%", ""),
			'start': start,
			'page_len': page_len
		})

def get_project_name(doctype, txt, searchfield, start, page_len, filters):
	cond = ''
	if filters.get('customer'):
		cond = '(`tabProject`.customer = "' + filters['customer'] + '" or ifnull(`tabProject`.customer,"")="") and'

	return frappe.db.sql("""select `tabProject`.name from `tabProject`
		where `tabProject`.status not in ("Completed", "Cancelled")
			and {cond} `tabProject`.name like %(txt)s {match_cond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			idx desc,
			`tabProject`.name asc
		limit {start}, {page_len}""".format(
			cond=cond,
			match_cond=get_match_cond(doctype),
			start=start,
			page_len=page_len), {
				"txt": "%{0}%".format(txt),
				"_txt": txt.replace('%', '')
			})

def get_delivery_notes_to_be_billed(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select `tabDelivery Note`.name, `tabDelivery Note`.customer_name
		from `tabDelivery Note`
		where `tabDelivery Note`.`%(key)s` like %(txt)s and
			`tabDelivery Note`.docstatus = 1 and status not in ("Stopped", "Closed") %(fcond)s
			and (`tabDelivery Note`.per_billed < 100 or `tabDelivery Note`.grand_total = 0)
			%(mcond)s order by `tabDelivery Note`.`%(key)s` asc
			limit %(start)s, %(page_len)s""" % {
				"key": searchfield,
				"fcond": get_filters_cond(doctype, filters, []),
				"mcond": get_match_cond(doctype),
				"start": "%(start)s", "page_len": "%(page_len)s", "txt": "%(txt)s"
			}, { "start": start, "page_len": page_len, "txt": ("%%%s%%" % txt) })

def get_batch_no(doctype, txt, searchfield, start, page_len, filters):
	cond = ""
	if filters.get("posting_date"):
		cond = "and (ifnull(batch.expiry_date, '')='' or batch.expiry_date >= %(posting_date)s)"

	batch_nos = None
	args = {
		'item_code': filters.get("item_code"),
		'warehouse': filters.get("warehouse"),
		'posting_date': filters.get('posting_date'),
		'txt': "%{0}%".format(txt),
		"start": start,
		"page_len": page_len
	}

	if args.get('warehouse'):
		batch_nos = frappe.db.sql("""select sle.batch_no, round(sum(sle.actual_qty),2), sle.stock_uom, batch.expiry_date
				from `tabStock Ledger Entry` sle
				    INNER JOIN `tabBatch` batch on sle.batch_no = batch.name
				where
					sle.item_code = %(item_code)s
					and sle.warehouse = %(warehouse)s
					and sle.batch_no like %(txt)s
					and batch.docstatus < 2
					{0}
					{match_conditions}
				group by batch_no having sum(sle.actual_qty) > 0
				order by batch.expiry_date, sle.batch_no desc
				limit %(start)s, %(page_len)s""".format(cond, match_conditions=get_match_cond(doctype)), args)

	if batch_nos:
		return batch_nos
	else:
		return frappe.db.sql("""select name, expiry_date from `tabBatch` batch
			where item = %(item_code)s
			and name like %(txt)s
			and docstatus < 2
			{0}
			{match_conditions}
			order by expiry_date, name desc
			limit %(start)s, %(page_len)s""".format(cond, match_conditions=get_match_cond(doctype)), args)

def get_account_list(doctype, txt, searchfield, start, page_len, filters):
	filter_list = []

	if isinstance(filters, dict):
		for key, val in filters.items():
			if isinstance(val, (list, tuple)):
				filter_list.append([doctype, key, val[0], val[1]])
			else:
				filter_list.append([doctype, key, "=", val])
	elif isinstance(filters, list):
		filter_list.extend(filters)

	if "is_group" not in [d[1] for d in filter_list]:
		filter_list.append(["Account", "is_group", "=", "0"])

	if searchfield and txt:
		filter_list.append([doctype, searchfield, "like", "%%%s%%" % txt])

	return frappe.desk.reportview.execute("Account", filters = filter_list,
		fields = ["name", "parent_account"],
		limit_start=start, limit_page_length=page_len, as_list=True)

@frappe.whitelist()
def get_income_account(doctype, txt, searchfield, start, page_len, filters):
	from erpnext.controllers.queries import get_match_cond

	# income account can be any Credit account,
	# but can also be a Asset account with account_type='Income Account' in special circumstances.
	# Hence the first condition is an "OR"
	if not filters: filters = {}

	condition = ""
	if filters.get("company"):
		condition += "and tabAccount.company = %(company)s"

	return frappe.db.sql("""select tabAccount.name from `tabAccount`
			where (tabAccount.report_type = "Profit and Loss"
					or tabAccount.account_type in ("Income Account", "Temporary"))
				and tabAccount.is_group=0
				and tabAccount.`{key}` LIKE %(txt)s
				{condition} {match_condition}
			order by idx desc, name"""
			.format(condition=condition, match_condition=get_match_cond(doctype), key=searchfield), {
				'txt': "%%%s%%" % frappe.db.escape(txt),
				'company': filters.get("company", "")
			})


@frappe.whitelist()
def get_expense_account(doctype, txt, searchfield, start, page_len, filters):
	from erpnext.controllers.queries import get_match_cond

	if not filters: filters = {}

	condition = ""
	if filters.get("company"):
		condition += "and tabAccount.company = %(company)s"

	return frappe.db.sql("""select tabAccount.name from `tabAccount`
		where (tabAccount.report_type = "Profit and Loss"
				or tabAccount.account_type in ("Expense Account", "Fixed Asset", "Temporary"))
			and tabAccount.is_group=0
			and tabAccount.docstatus!=2
			and tabAccount.{key} LIKE %(txt)s
			{condition} {match_condition}"""
		.format(condition=condition, key=frappe.db.escape(searchfield),
			match_condition=get_match_cond(doctype)), {
			'company': filters.get("company", ""),
			'txt': "%%%s%%" % frappe.db.escape(txt)
		})


@frappe.whitelist()
def get_item(doctype, txt, searchfield, start, page_len, filters):
        if not filters.get("item_sub_group"):
                frappe.throw("Select Item Sub Group First")
        return frappe.db.sql("select name from `tabItem` where item_sub_group = %s and disabled != 0", filters.get("item_sub_group"))

@frappe.whitelist()
def get_item_uom(doctype, txt, searchfield, start, page_len, filters):
        if not filters.get("item_code"):
                frappe.throw("Select Item Code")
        return frappe.db.sql("select a.name from tabUOM a, `tabUOM Conversion Detail` b where a.name = b.uom and b.parent = %s", filters.get("item_code"))

@frappe.whitelist()
def filter_branch_wh(doctype, txt, searchfield, start, page_len, filters):
        if not filters.get("branch"):
                frappe.throw("Select Branch First")
	return frappe.db.sql("select a.parent from `tabWarehouse Branch` a, tabWarehouse b where a.parent = b.name and a.branch = %s and b.disabled = 0", filters.get("branch"))

@frappe.whitelist()
def filter_location_rng(doctype, txt, searchfield, start, page_len, filters):
        if not filters.get("location"):
                frappe.throw("Select Location First")
	return frappe.db.sql("select a.parent from `tabRange Location` a, tabRange b where a.parent = b.name and a.location = '{0}' and a.branch = '{1}' and b.is_disabled = 0".format(filters.get("location"),filters.get("branch")))

@frappe.whitelist()
def filter_branch_rng(doctype, txt, searchfield, start, page_len, filters):
        if not filters.get("branch"):
                frappe.throw("Select Branch First")
	return frappe.db.sql("select distinct a.parent from `tabRange Location` a, tabRange b where a.parent = b.name and a.branch = '{0}' and b.is_disabled = 0".format(filters.get("branch")))

@frappe.whitelist()
def filter_range_location(doctype, txt, searchfield, start, page_len, filters):
        if not filters.get("range"):
                frappe.throw("Select Range First")
	return frappe.db.sql("select a.location from `tabRange Location` a, tabRange b where a.parent = b.name and b.name= '{0}' and b.is_disabled = 0".format(filters.get("range")))

@frappe.whitelist()
def filter_branch_cost_center(doctype, txt, searchfield, start, page_len, filters):
        if not filters.get("branch"):
                frappe.throw("Select Branch First")
	return frappe.db.sql("select cost_center from `tabBranch` where name = %s", filters.get("branch"))

@frappe.whitelist()
def get_cop_list(doctype, txt, searchfield, start, page_len, filters):
        if not filters.get("branch") or not filters.get("item_code") or not filters.get("posting_date"):
                frappe.throw("Select Item Code or Branch or Posting Date")
	item_sub_group = frappe.db.get_value("Item", filters.get("item_code"), "item_sub_group")
	if not item_sub_group:
		frappe.db.sql("No Item Sub Group Assigned")
	return frappe.db.sql("select a.parent, b.item_sub_group, b.cop_amount from `tabCOP Branch` a, `tabCOP Rate Item` b where a.parent = b.parent and a.branch = %s and b.item_sub_group = %s and exists (select 1 from `tabCost of Production` where name = a.parent and %s between from_date and to_date)", (filters.get("branch"), str(item_sub_group), filters.get("posting_date")))

#added the query to select custom selling price

def price_template_list(doctype,txt, searchfield, start, page_len, filters):
	if not filters.get("branch") or not filters.get("item_code") or not filters.get("transaction_date"):
                frappe.throw("Select Item Code or Branch or Posting Date")
	item_price=""
	if filters.get("location"):
        	item_price = frappe.db.sql(""" select a.parent, b.particular, b.selling_price from `tabSelling Price Branch` a, `tabSelling Price Rate` b where a.parent = b.parent and a.branch = '{0}' and b.location = '{1}' and b.particular = '{2}' and exists (select 1 from `tabSelling Price` where name = a.parent and '{3}' between from_date and to_date) group by a.parent""".format(filters.get("branch"), filters.get("location"), filters.get("item_code"), filters.get("transaction_date")))
	if not item_price:
		item_price = frappe.db.sql(""" select a.parent, b.particular, b.selling_price from `tabSelling Price Branch` a, `tabSelling Price Rate` b where a.parent = b.parent and a.branch = '{0}' and b.particular = '{1}' and exists (select 1 from `tabSelling Price` where name = a.parent and '{2}' between from_date and to_date) group by a.parent""".format(filters.get("branch"), filters.get("item_code"), filters.get("transaction_date")))
        
	if not item_price:
                item_species = frappe.db.get_value("Item", filters.get("item_code"), "species")
		if not item_species:
			return item_price
		else:
			timber_class, timber_type = frappe.db.get_value("Timber Species", item_species, ["timber_class", "timber_type"])
                #frappe.msgprint("{0}".format(item_species))
		item_sub_group = frappe.db.get_value("Item", filters.get("item_code"), "item_sub_group")
		if filters.get("location"): 
                	item_price = frappe.db.sql(""" select a.parent, b.particular, b.timber_type, b.selling_price  from `tabSelling Price Branch` a, `tabSelling Price Rate` b where a.parent = b.parent and a.branch = '{0}' and b.location = '{1}' and b.particular = '{2}' and b.timber_type = '{3}' and b.item_sub_group = '{5}' and exists (select 1 from `tabSelling Price` where name = a.parent and '{4}' between from_date and to_date) group by a.parent""".format(filters.get("branch"), filters.get("location"), timber_class, timber_type, filters.get("transaction_date"), item_sub_group))
		if not item_price:
                	item_price = frappe.db.sql(""" select a.parent, b.particular, b.timber_type, b.selling_price  from `tabSelling Price Branch` a, `tabSelling Price Rate` b where a.parent = b.parent and a.branch = '{0}' and b.particular = '{1}' and b.timber_type = '{2}' and b.item_sub_group = '{4}' and exists (select 1 from `tabSelling Price` where name = a.parent and '{3}' between from_date and to_date) and (b.location is NULL or b.location = '') group by a.parent""".format(filters.get("branch"), timber_class, timber_type, filters.get("transaction_date"), item_sub_group))
		
        if not item_price:
                frappe.throw("Rate for Item: <b> '{0}' </b> Is Not Defined In Selling Price List, Please Define The Rate".format(filters.get('item_code')))
	return item_price

''' ########## Ver.2020.11.03 Begins ########## '''
# following method created by SHIV on 2020/11/03
@frappe.whitelist()
def get_measurements(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	app_list = []
	cond = ""
	if not filters.get("item_sub_group"):
		frappe.throw(_("Please select Material Sub Group first."))
	
	if filters.get("item_code"):
		cond = """and exists(select 1
				from `tabItem` i
				where i.name = '{}'
				and (i.material_measurement is null or i.material_measurement = mm.name)
			)""".format(filters.get("item_code"))

	li = frappe.db.sql("""select isgm.material_measurement
		from `tabItem Sub Group Measurement` isgm, `tabMaterial Measurement` mm 
		where isgm.parent = '{}' 
		and mm.name = isgm.material_measurement
		{}
		order by mm.measurement
	""".format(filters.get("item_sub_group"), cond))

	return li
''' ########## Ver.2020.11.03 Ends ########## '''
