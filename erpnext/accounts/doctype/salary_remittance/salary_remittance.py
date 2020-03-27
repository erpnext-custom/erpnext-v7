# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils  import cint,flt, money_in_words

class SalaryRemittance(Document):
	def validate(self):

		self.update_value()

	def update_value(self):

		#frappe.msgprint("aaa")
		for row in self.items:
			if row.original_message:
				#if not row.final_message:
				row.final_message= row.original_message.format(posting_date=self.posting_date, month=self.month, fiscal_year=self.fiscal_year, salary_component= row.salary_component, bank=row.bank, amount="{0:,.2f}".format(row.amount)+" ("+money_in_words(row.amount)[4:]+") ", cheque=row.cheque_no, cheque_date=row.cheque_date)
				#row.final_message= row.original_message




@frappe.whitelist()
def get_dtls(month, fiscal_year):
	month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(month) + 1
	month = str(month) if cint(month) > 9 else str("0" + str(month))

	data=[]
	li = frappe.db.sql( """
		select sd.salary_component, sd.institution_name, 
		case 
		when sd.salary_component = 'PF' then 2*sum(sd.amount) 
		else sum(sd.amount) end as amount,
			 t.message
			from `tabSalary Detail` sd, `tabSalary Slip` ss, `tabSalary Remittance Template`  t
			where ss.name = sd.parent and t.salary_component = sd.salary_component
			and sd.parenttype = 'Salary Slip'
			and sd.docstatus =1
			and ss.month ='{0}'
			and ss.fiscal_year = '{1}'
			group by sd.salary_component, sd.institution_name
			order by sd.salary_component """.format (month, fiscal_year), as_dict=True)

	rest = frappe.db.sql("""select  'Salary Remittance' as salary_component, ss.bank_name as institution_name,
		                  sum(
		                       case
			                      when sd.parentfield = 'deductions' then -1*ifnull(sd.amount,0)
                                  else ifnull(sd.amount,0)
		                        end
		                        ) as amount, t.message
			from `tabSalary Detail` as sd, `tabSalary Slip` as ss, `tabSalary Remittance Template`  t
			where t.salary_component = 'Salary Remittance'
			and ss.month = '{0}'
			and ss.fiscal_year = '{1}'
			and ss.docstatus = 1
			and sd.parent = ss.name
			group by ss.bank_name;""".format (month, fiscal_year), as_dict=True)

	#frappe.msgprint(rest)
	
	data.extend(rest)
	data.extend(li)	
	return data



#def get_message():
	#query = "select message from `tabSalary Remittance Template`"
