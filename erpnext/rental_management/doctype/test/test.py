# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, getdate
from frappe.model.document import Document

class Test(Document):
	def validate(self):
		'''from dateutil.relativedelta import relativedelta
                import calendar, datetime
		year = self.fiscal_year
		month = self.month
		ysd = frappe.db.get_value("Fiscal Year", year, "year_start_date")
		if cint(month) <= 6:
			ysd = ysd + relativedelta(6)

		if ysd:
			diff_mnt = cint(month)-cint(ysd.month)
			if diff_mnt<0:
				diff_mnt = 12-int(ysd.month)+cint(month)
			msd = ysd + relativedelta(months=diff_mnt) # month start date
			month_days = cint(calendar.monthrange(cint(msd.year) ,cint(month))[1]) # days in month
			med = datetime.date(msd.year, cint(month), month_days) # month end date
			return frappe._dict({
				'year': msd.year,
				'month_start_date': msd,
				'month_end_date': med,
				'month_days': month_days
			})
		else:
			frappe.throw(_("Fiscal Year {0} not found").format(year))
		doc = frappe.db.sql(" select name from `tabFiscal Year` where '{0}' between year_start_date and year_end_date".format(self.transaction_date))
		
		c = doc and doc[0][0]'''
		acc_froze_monthly = frappe.db.get_value("Accounts Settings", None, "froze_acc_monthly")
		frappe.msgprint("{0}".format(acc_froze_monthly))
                if acc_froze_monthly:
                        frozen_accounts_modifier = frappe.db.get_value("Accounts Settings", None, "frozen_accounts_modifier")
                        if getdate(self.transaction_date).month != getdate(frappe.utils.nowdate()).month \
                                        and not frozen_accounts_modifier in frappe.get_roles():
                                frappe.throw(("You are not authorized to add or update entries for {0} as month is already closed").format(getdate(self.transaction_date).month))
