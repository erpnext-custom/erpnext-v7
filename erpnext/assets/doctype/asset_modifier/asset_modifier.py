# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.accounts.accounts_custom_functions import get_number_of_days
from erpnext.accounts.accounts_custom_functions import update_jv
from frappe.utils import nowdate, flt, getdate

class AssetModifier(Document):
	def validate(self):
                if self.items:
			total_amount = 0
			for a in self.items:
				total_amount += flt(a.amount)
			self.value = total_amount
                
	#frappe.throw("{0}, {1}, {2}, {3}, {4}".format(asset, value, start_date, credit_account, asset_account))
	def on_submit(self):
                self.change_value()

	def on_cancel(self):
		# Restrict cancelling if journal entry exists
		for t in frappe.get_all("Journal Entry", {"name": self.journal_entry, "docstatus": ["<",2]}, ["name"]):
			frappe.throw(_("You need to cancel Journal Entry {0} first").format(self.journal_entry), title="Invalid Operation")
		self.change_value()
##
# Make GL Entry for the additional cost
##
        def make_gl_entry(self, asset_account, credit_account, value, asset, start_date):
                je = frappe.new_doc("Journal Entry")
                je.flags.ignore_permissions = 1
                je.update({
                        "voucher_type": "Journal Entry",
                        "company": asset.company,
                        "remark": "Value (" + str(value) +" ) added to " + asset.name + " (" + asset.asset_name + ") ",
                        "user_remark": "Value (" + str(value) +" ) added to " + asset.name + " (" + asset.asset_name + ") ",
                        "posting_date": start_date,
                        "branch": asset.branch
                        })
	#credit account update
                je.append("accounts", {
                        "account": credit_account,
                        "credit_in_account_currency": flt(value),
                        "reference_type": "Asset",
                        "reference_name": asset.name,
                        "cost_center": asset.cost_center
                        })

        #debit account update
                je.append("accounts", {
                        "account": asset_account,
                        "debit_in_account_currency": flt(value),
                        "reference_type": "Asset",
                        "reference_name": asset.name,
                        "cost_center": asset.cost_center
                        })
                je.flags.ignore_permissions=1
                je.submit();
		self.db_set("journal_entry", je.name)
	##
# Update the depreciation values for schedules
##
        def update_value(self, sch_name, dep_amount, accu_dep, income, accu_income):
                sch = frappe.get_doc("Depreciation Schedule", sch_name)
                sch.db_set("depreciation_amount",dep_amount)
                sch.db_set("accumulated_depreciation_amount", accu_dep)
                sch.db_set("depreciation_income_tax", income)
                sch.db_set("accumulated_depreciation_income_tax", accu_income)


	#def change_value(self, asset=None, value=None, start_date=None, credit_account=None, asset_account=None):
	def change_value(self):	
		asset= self.asset
                value = self.value
                start_date = self.addition_date
                credit_account = self.credit_account
                asset_account = self.asset_account
	
                if(asset and value and getdate(start_date) <= getdate(nowdate())):
                        asset_obj = frappe.get_doc("Asset", asset)
                        if asset_obj and asset_obj.docstatus == 1:
				value = -1*flt(value) if self.docstatus == 2 else flt(value)
                        #Make GL Entries for additional values and update gross_amount (rate)
                                asset_obj.db_set("additional_value", flt(asset_obj.additional_value) + flt(value))
                                asset_obj.db_set("gross_purchase_amount", flt(flt(asset_obj.gross_purchase_amount) + flt(value)))
				if self.docstatus == 1:
                                	self.make_gl_entry(asset_account, credit_account, value, asset_obj, start_date)
                        #Get dep. schedules which had not yet happened
                                schedules = frappe.db.get_all("Depreciation Schedule", order_by="schedule_date", filters = {"parent": asset_obj.name, "schedule_date": [">=", start_date]},fields={"name", "schedule_date", "journal_entry", "depreciation_amount", "accumulated_depreciation_amount", "depreciation_income_tax","accumulated_depreciation_income_tax"})
                        ##Get total number of dep days for the asset
                                total_days = get_number_of_days(start_date, schedules[-1]['schedule_date'])
                        ##Assign the last dep schedule date for num of days calc
                                last_sch_date = start_date
                                for i in schedules:
                                #Add additional values to the depreciation schedules
                                #Calc num of days for each dep schedule
                                        num_days = get_number_of_days(last_sch_date, i.schedule_date)
                                #Calc num of days till current schedule
                                        num_till_days = get_number_of_days(start_date, i.schedule_date)
                                ##Updated dep amount
                                        dep_amount = flt(i.depreciation_amount) + (flt(value) * num_days / total_days)
                                ##Updated accu dep amount
                                        accu_dep = flt(i.accumulated_depreciation_amount) + (flt(value) * num_till_days / total_days)
                                #Income amount
                                        income = flt(i.depreciation_income_tax) + (flt(value)/(100 * 365.25)) * flt(asset_obj.asset_depreciation_percent) * num_days
                                #Accumulated Income amount
                                        accu_income = flt(i.accumulated_depreciation_income_tax) + (flt(value)/(100 * 365.25)) * flt(asset_obj.asset_depreciation_percent) * num_till_days
					self.update_value(i.name, dep_amount, accu_dep, income, accu_income)

                                        if i.journal_entry:
                                                update_jv(i.journal_entry, dep_amount)

                                ##Update last dep schedule date
                                        last_sch_date = i.schedule_date

                        #Add the reappropriation details for record
                                app_details = frappe.new_doc("Asset Modification Entries")
                                app_details.flags.ignore_permissions=1
                                app_details.asset = asset
                                app_details.value = value
                                app_details.credit_account = credit_account
                                app_details.asset_account = asset_account
                                app_details.addition_date = start_date
                                app_details.posted_on = nowdate()
                                app_details.submit()

                                return "DONE"

                        elif asset_obj.docstatus == 2:
                                return "Cannot add value to CANCELLED assets"
                        else:
                                return "Invalid asset code"

                elif not asset:
                        return "Invalid asset code"

                elif not value:
                        return "Invalid asset value"

                elif start_date > nowdate():
                        return "Effective Date cannot be greater than Today"
		else:
                        return "Sorry, something happened. Please try again"

