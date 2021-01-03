# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, fmt_money, formatdate, getdate, get_datetime, time_diff_in_hours
from frappe.desk.reportview import get_match_cond
from erpnext.custom_utils import check_uncancelled_linked_doc, check_future_date

class Logbook(Document):
	def validate(self):
		self.validate_data()
		check_future_date(self.posting_date)
		self.check_duplicate_entry()
		self.validate_supplier()
		self.check_date_validity()
		self.check_target_hour()
		#self.get_reading_based()
		self.calculate_hours()
		self.calculate_downtime()
		self.validate_hours()

	def validate_data(self):
		is_disabled = frappe.db.get_value("Branch", self.branch, "is_disabled")
		if is_disabled:
			frappe.throw("Cannot use a disabled branch in transaction")

		eqp = frappe.db.get_values("Equipment", self.equipment, ["branch", "is_disabled"], as_dict=1)
		if eqp[0].is_disabled:
			frappe.throw("Cannot use a disabled Equipment in transaction")
		
		if self.branch != eqp[0].branch:
			frappe.throw("Cannot use equipments from other branch")

	def check_duplicate_entry(self):
		lbk = frappe.db.sql("select name as lb from tabLogbook where docstatus = 1 and equipment = %(equipment)s and posting_date = %(posting_date)s and name != %(name)s", {"equipment": self.equipment, "posting_date": self.posting_date, "name": self.name}, as_dict=1)
		if lbk:
			frappe.throw("Only one record per equipment per day is allowed. {0} already exists for {1} on {2}".format(frappe.bold(frappe.get_desk_link("Logbook", lbk[0].lb)), self.equipment, self.posting_date))

	def validate_supplier(self):
		if not self.supplier:
			frappe.throw("Set Supplier in Equipment")

	def check_date_validity(self):
		from_date, to_date = frappe.db.get_value("Equipment Hiring Form", self.equipment_hiring_form, ["start_date", "end_date"])
		if not getdate(from_date) <= getdate(self.posting_date) <= getdate(to_date):
			frappe.throw("Log Date should be between {0} and {1}".format(from_date, to_date))

	def check_target_hour(self):
		if self.equipment_hiring_form:
			self.target_hours = frappe.db.get_value("Equipment Hiring Form", self.equipment_hiring_form, "target_hour")
		if 0 >= self.scheduled_working_hour:
			frappe.throw("Scheduled Working Hour is mandatory")
		if 0 >= self.target_hours:
			frappe.throw("Target Hour is mandatory")
	
	def get_reading_based(self):
		self.reading_based_on = frappe.db.get_value("Equipment Model", self.equipment_model, "reading_based_on")
		if not self.reading_based_on:
			frappe.throw("Set Reading Based On in Equipment Model")

	def calculate_hours(self):
		total_hours = 0
		ot_hours = 0
		for a in self.items:
			a.equipment = self.equipment
			if not a.uom:
				frappe.throw("Reading Unit is mandatory")
			if a.uom == "Trip":
				a.final_reading = 0
				if a.initial_reading and a.initial_reading > 0:
					if 0 >= a.target_trip:
						frappe.throw("Target Trip is mandatory on row {0}".format(a.idx))
					a.hours = flt((a.initial_reading * self.target_hours * 1.00) / a.target_trip, 1)
					total_hours += a.hours
					if a.is_overtime:
						ot_hours += a.hours
				else:
					frappe.throw("Achieved Trip is mandatory")
			elif a.uom == "Hour":
				a.target_trip = 0
				if a.reading_initial and a.reading_final:
					if a.reading_initial > a.reading_final:
						frappe.throw("Final reading should not be smaller than inital")
					a.hours = flt(a.reading_final - a.reading_initial - a.idle_time, 1)
					total_hours += a.hours
					if a.is_overtime:
						ot_hours += a.hours
				else:
					frappe.throw("Initial and Final Readings are mandatory")
			else:
				if a.initial_time and a.final_time:
					start = "{0} {1}".format(str(self.posting_date), str(a.initial_time))
					end = "{0} {1}".format(str(self.posting_date), str(a.final_time))
					if getdate(start) > getdate(end):
						frappe.throw("Final time should not be smaller than inital")
					a.hours = flt(time_diff_in_hours(end, start) - a.idle_time, 1)
					if a.hours <= 0:
						frappe.throw("Difference of time and idle time should be more than 0")  
					total_hours += a.hours
					if a.is_overtime:
						ot_hours += a.hours
				else:
					frappe.throw("Initial and Final Readings are mandatory")
		act_sch = self.scheduled_working_hour + 5
		if total_hours > act_sch:
			frappe.throw("Total hours cannot be more than {0} hours".format(act_sch))


		self.total_hours = flt(total_hours, 1)
		self.total_ot = flt(ot_hours, 1)

	def calculate_downtime(self):
		total = 0
		for a in self.downtimes:
			a.equipment = self.equipment
			if 0 >= a.hours:
				frappe.throw("Downtime hours should be greater than zero") 
			total += a.hours
		self.total_downtime_hours = total

	def validate_hours(self):
		difference = flt(self.total_hours, 1) + flt(self.total_downtime_hours, 1) - flt(self.scheduled_working_hour, 1)
		if difference < 0:
			frappe.throw("Total of work hours ({0}) and downtime hours ({1}) should be more or equal scheduled hours ({2})".format(frappe.bold(self.total_hours), frappe.bold(self.total_downtime_hours), frappe.bold(self.scheduled_working_hour)))
		if difference > 0:
			if flt(self.total_hours) + flt(self.total_downtime_hours) >= 24:
				frappe.throw("Total hours should be less than 24 hours")
			frappe.msgprint("<a style='color:red; font-size:large;'}><b>The total hours exceeds the scheduled working hour by "+str(difference)+" hours</b></a>")

	def on_submit(self):
		pass

	def get_ehf(self):
		if not self.branch:
			frappe.throw("Branch is mandatory")
		if not self.equipment or not self.posting_date:
			frappe.throw("Equipment and Log Date are mandatory")
		ehfs = frappe.db.sql("select name, target_hour from `tabEquipment Hiring Form` where docstatus = 1 and equipment = %(equipment)s and %(logdate)s between start_date and end_date and branch = %(branch)s order by name", {"equipment": self.equipment, "logdate": self.posting_date, "branch": self.branch}, as_dict=1)

		if ehfs:
			self.equipment_hiring_form = ehfs[0]['name']
			self.target_hours = ehfs[0]['target_hour']
		else:
			frappe.throw("No Equipment Hiring Form found!")
