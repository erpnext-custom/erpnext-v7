# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, nowdate, money_in_words
from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba
from erpnext.accounts.general_ledger import make_gl_entries
from frappe.utils.data import get_first_day, get_last_day, add_days
from erpnext.controllers.accounts_controller import AccountsController

class ProcessRentalBilling(AccountsController):
	
	def get_tenant_list(self, process_type=None):
		self.check_mandatory()
		rental_bill_date = self.fiscal_year + "-" + self.month + "-" + "01"
		if process_type == "create":
			tenant_list = frappe.db.sql("""
                               select t1.name
                               from `tabTenant Information` t1
                               where t1.status = "Allocated" and t1.docstatus = "1"
                               and t1.allocated_date < now()
                               and t1.allocated_date <= '{2}'
                               and not exists(select 1
                                              from `tabRental Bill` as t2
                                              where t2.tenant = t1.name
                                              and t2.docstatus != 2 
                                              and t2.fiscal_year = '{0}'
                                              and t2.month = '{1}'
                                              )
                               order by t1.ministry_agency, t1.department
			""".format(self.fiscal_year, self.month, rental_bill_date), as_dict=True)

		else:
			tenant_list = frappe.db.sql("""
                                select t1.name
                                from `tabRental Bill` as t1
                                where t1.fiscal_year = '{0}'
                                and t1.month = '{1}'
				and t1.branch = '{2}'
                                and t1.docstatus = 0
                                order by t1.branch, t1.name
                        """.format(self.fiscal_year, self.month, self.branch), as_dict=True)

		return tenant_list	

	def check_mandatory(self):
		for f in ['month', 'fiscal_year']:
			if not self.get(f):
				frappe.throw(_("Please set {0}").format(f))

	
	def process_rental(self, process_type=None, name=None):
		self.check_permission('write')
		msg=""

		if name:
			try:
				if process_type == "create":
					bill_date = self.fiscal_year+"-"+self.month+"-"+"01"
					posting_date = get_last_day(bill_date) 
					if self.month == "01":
						prev_fiscal_year = int(self.fiscal_year) - 1
						prev_month = "12"
					else:
						prev_fiscal_year = self.fiscal_year
						if int(self.month) <= 10:	
							a = 0
							b = int(self.month) - 1
							prev_month = str(a) + str(b)
						else:
							prev_month = str(int(self.month) - 1)
					#customer_code = frappe.db.get_value("Customer", {"customer_id":name}, "customer_code")
					#bill_code = "NHDCL/" + customer_code + "/" + self.fiscal_year + self.month
					yearmonth = str(self.fiscal_year) + str(self.month)

					query = """
                                                            select tenant_name, customer_code, block_no, business_activity, flat_no, 
                                                            ministry_agency, location, branch, department, dzongkhag, designation, 
                                                            mobile_no, town_category, building_category, allocated_date, 
							    (Case 
								WHEN building_category = 'Pilot Housing' Then original_monthly_instalment  
								Else rental_amount 
							    End) as rental_amount
                                                            from `tabTenant Information` t 
                                                            inner join `tabTenant Rental Charges` r 
                                                            on t.name = r.parent 
                                                            where '{0}' between r.from_date and r.to_date 
						       	    and (exists(select 1
								           from `tabRental Bill` as t2
							                   where t2.tenant = t.name
							                   and t2.docstatus != 2 
							                   and t2.fiscal_year = '{2}'
							                   and t2.month = '{3}'
									) 
								or not exists(select 1
	                                                                   from `tabRental Bill` as t3
						                           where t3.tenant = '{1}'
									   and t3.docstatus != 2	
							      		))
						            and t.name = '{1}';
                                                            """.format(bill_date, name, prev_fiscal_year, prev_month)
					dtls = frappe.db.sql(query, as_dict=True)

					if dtls:
						for d in dtls:
							cost_center = frappe.db.get_value("Branch", d.branch, "cost_center") 
							company = frappe.db.get_value("Branch", d.branch, "company") 
							rb = frappe.get_doc({
								"doctype": "Rental Bill",
								"tenant": name,
								"customer_code": d.customer_code,
								"posting_date": posting_date,
								"tenant_name": d.tenant_name,
								"block_no": d.block_no,
								"total_in_words": "",
								"fiscal_year": self.fiscal_year,
								"month": self.month,
								"flat_no": d.flat_no,
								"ministry_agency": d. ministry_agency,
								"location": d.location,
								"branch": d.branch,
								"department": d.department,
								"dzongkhag": d.dzongkhag,
								"designation": d.designation,
								"mobile": d.mobile_no,
								"town_category": d.town_category,
								"building_category": d.building_category,
								"allocation_date": d.allocated_date,
								"yearmonth": yearmonth,
								"fiscal_year" : self.fiscal_year,
								"month": self.month,
								"rent_amount": d.rental_amount,
								"cost_center": cost_center,
								"company": company
							})
							rb.insert()
						msg = "Rental Bill Created Successfully for {0} amount Nu. {1}".format(d.tenant_name, d.rental_amount)
					else:
						msg = '<span style="color:red;"> FAILED. Previous month rentall bill might not have process or <br/> rental charges might be missing in tenant information</span>'
				else:
					if process_type == "remove":
						rb = frappe.get_doc("Rental Bill", name)
                                                rb_list = frappe.db.sql("delete from `tabRental Bill` where name='{0}'".format(name))
                                                frappe.db.commit()
                                                msg = "Rental Bill Removed Successfully"
                                        else:
                                                rb = frappe.get_doc("Rental Bill", name)
                                                rb.submit()
                                                msg = "Rental Bill Submitted Successfully"

				format_string = 'href="#Form/Rental Bill/{0}"'.format(name)
				return '<tr><td><a {0}>{1}</a></td><td><a {0}>{2}</a></td></tr>'.format(format_string, name, msg)

			except Exception, e:
				return '<div style="color:red;"> Error: Tenant CID :{1} - {0}</div>'.format(str(e), name)

	def post_gl_entry(self):
		bill_date = str(self.fiscal_year) + "-" + str(self.month) + "-" + "01"
		self.posting_date = get_last_day(bill_date)
		gl_entries = []
		cost_center = frappe.db.get_value("Branch", self.branch, "cost_center")
		business_activity = frappe.db.get_single_value("Rental Setting", "business_activity")
		revenue_claim_account = frappe.db.get_single_value("Rental Account Setting", "revenue_claim_account")
		total_debit = total_credit = 0.00
		bills = frappe.db.sql("""
	                      select sum(rent_amount) as rental_amount 
                              from `tabRental Bill` 
                              where branch = '{0}' 
                              and fiscal_year = '{1}' 
                              and month = '{2}'
			      and docstatus = 1
			      and gl_entry = 0
		           """.format(self.branch, self.fiscal_year, self.month), as_dict=True)	
		if bills[0]['rental_amount'] > 0:
			x = "RB" + str(self.fiscal_year)[2:4] + str(self.month)
			voucher_nos = frappe.db.sql("select voucher_no from `tabGL Entry` Where voucher_no like '{0}%' order by voucher_no desc limit 1".format(x), as_dict=1)
			if voucher_nos:
				for a in voucher_nos:
					start_id = len(x)
					y = cint(a.voucher_no[start_id:]) + 1
					if y < 10:
						no = str("0") + str(y)
					else:
						no = str(y)
				voucher_no = x + no
			else:
				voucher_no = x + str("01")
				
			for b in bills:
				total_debit = b.rental_amount
				gl_entries.append(
					self.get_gl_dict({
					    "account": revenue_claim_account,
					    "debit": b.rental_amount,
					    "debit_in_account_currency": b.rental_amount,
					    "voucher_no": voucher_no,
					    "voucher_type": "Rental Bill",
					    "cost_center": cost_center,
					    #'party': b.customer_code,
					    #'party_type': 'Customer',
					    "company": self.company,
					    "remarks": "Monthly Rental Bill for Year " + str(self.fiscal_year) + " Month " + str(self.month),
					    "business_activity": business_activity
					})
				  )
			
			credit_bills = frappe.db.sql("""
				      select sum(rent_amount) as rental_amount, building_category 
				      from `tabRental Bill` 
				      where branch = '{0}' 
				      and fiscal_year = '{1}' 
				      and month = '{2}'
				      and docstatus = 1
				      and gl_entry = 0
				      group by building_category 
				   """.format(self.branch, self.fiscal_year, self.month), as_dict=True)	
					  
			if credit_bills:
				
				total_credit = 0
				for c in credit_bills:
					if c.building_category == "Pilot Housing":
						total_pilot_credit = 0.0
						pilot_housing_data = frappe.db.sql("""
									select sum(p.amount) as p_amount, p.account as p_account
									from `tabTenant Information` t inner join
									`tabPilot Housing Account` p on t.name = p.parent
									where t.building_category = 'Pilot Housing' 
									and exists(select 1
                                                                           	from `tabRental Bill` as t2
                                                                           	where t2.tenant = t.name
										and t2.branch = '{0}'
                                                                           	and t2.docstatus = 1 
                                                                           	and t2.fiscal_year = '{1}'
                                                                           	and t2.month = '{2}'
                                                                           	)
									group by p.account 
									""".format(self.branch, self.fiscal_year, self.month), as_dict=True)
						for p in pilot_housing_data:
							total_pilot_credit += p.p_amount
							gl_entries.append(
								self.get_gl_dict({
									"account": p.p_account,
									"credit": p.p_amount,
									"credit_in_account_currency": p.p_amount,
									"voucher_no": voucher_no,
									"voucher_type": "Rental Bill",
									"cost_center": cost_center,
									"company": self.company,
									"remarks": "Rental Bill for " + str(c.building_category) +" Year "+ str(self.fiscal_year) + " Month " +str(self.month),
									"business_activity": business_activity
									})
							    )
						if total_pilot_credit == c.rental_amount:
							total_credit += c.rental_amount
						else:
							frappe.throw("Rental Bill Amount {0} for Pilot Housing and Tenant Account Amount {1} is not equal".format(total_pilot_credit, c.rental_amount))
					else:
						total_credit = total_credit + c.rental_amount
						credit_account = frappe.db.get_value("Rental Account Setting Item",{"building_category":c.building_category}, "account")
						gl_entries.append(
							self.get_gl_dict({
								"account": credit_account,
								"credit": c.rental_amount,
								"credit_in_account_currency": c.rental_amount,
								"voucher_no": voucher_no,
								"voucher_type": "Rental Bill",
								"cost_center": cost_center,
								"company": self.company,
								"remarks": "Rental Bill for " + str(c.building_category) +" Year "+ str(self.fiscal_year) + " Month " +str(self.month),
								"business_activity": business_activity
								})
						    )
			if total_credit and total_debit:	
				#frappe.msgprint("{0}".format(gl_entries))
				make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)	
				frappe.db.sql("update `tabRental Bill` set gl_entry = 1, gl_reference = '{3}'  where branch='{0}' and fiscal_year='{1}' and month = '{2}' and docstatus=1".format(self.branch, self.fiscal_year, self.month, voucher_no))
				msg = "<b>Rental Bills Successfully posted to account and updated</b>"
			else:
				msg = "Failed to post to account as Total Credit: {0} is not equal to Total Debit: {1} ".format(total_credit, total_debit)
			return "<div>{0}</div>".format(msg)
		else:
			msg = "Rental Bills might have already been posted to accounts or still not yet created for the <b> Year {0} and Month {1} </b>".format(self.fiscal_year, self.month)

		return "<div>{0}</div>".format(msg)
