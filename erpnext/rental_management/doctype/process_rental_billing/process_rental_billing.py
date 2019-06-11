# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, nowdate, money_in_words
from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba

class ProcessRentalBilling(Document):
	
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
                                and t1.docstatus = 0
                                order by t1.branch, t1.name
                        """.format(self.fiscal_year, self.month), as_dict=True)

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
					if self.month == "01":
						prev_fiscal_year = int(self.fiscal_year) - 1
						prev_month = "12"
					else:
						prev_fiscal_year = self.fiscal_year
						prev_month = "0" + str(int(self.month) - 1)

					customer_code = frappe.db.get_value("Customer", {"customer_id":name}, "customer_code")
					#bill_code = "NHDCL/" + customer_code + "/" + self.fiscal_year + self.month
					yearmonth = str(self.fiscal_year) + str(self.month)
					
					dtls = frappe.db.sql("""
                                                            select tenant_name, block_no, business_activity, flat_no, ministry_agency, location, 
                                                            branch, department, dzongkhag, designation, mobile_no, town_category, building_category, 
                                                            allocated_date, rental_amount 
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
							      		))
						            and t.name = '{1}';
                                                            """.format(bill_date, name, prev_fiscal_year, prev_month), as_dict=True)
					if dtls:
						for d in dtls:
							rb = frappe.get_doc({
								"doctype": "Rental Bill",
								"tenant": name,
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
								"rent_amount": d.rental_amount
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

