# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, fmt_money, formatdate, getdate, get_datetime
from frappe.desk.reportview import get_match_cond
from erpnext.custom_utils import check_uncancelled_linked_doc, check_future_date

class Logbook(Document):
	def validate(self):
		check_future_date(self.posting_date)
		self.check_duplicate_entry()
		self.validate_supplier()
		self.check_date_validity()
		self.check_target_hour()
		#self.get_reading_based()
		self.calculate_hours()
		self.calculate_downtime()
		self.validate_hours()

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
		if 0 >= self.scheduled_working_hour:
			frappe.throw("Scheduled Working Hour is mandatory")
	
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
			if a.uom != self.reading_based_on:
				frappe.msgprint("Reading Unit is different from defined unit")
			if a.uom == "Trip":
				a.final_reading = 0
				if a.initial_reading and a.initial_reading > 0:
					if 0 >= a.target_trip:
						frappe.throw("Target Trip is mandatory on row {0}".format(a.idx))
					a.hours = (a.initial_reading * self.scheduled_working_hour) / a.target_trip
					total_hours += a.hours
					if a.is_overtime:
						ot_hours += a.hours
				else:
					frappe.throw("Achieved Trip is mandatory")
			else:
				a.target_trip = 0
				if a.initial_reading and a.final_reading:
					if a.initial_reading > a.final_reading:
						frappe.throw("Final reading should not be smaller than inital")
					a.hours = a.final_reading - a.initial_reading
					total_hours += a.hours
					if a.is_overtime:
						ot_hours += a.hours
				else:
					frappe.throw("Initial and Final Readings are mandatory")
		if total_hours > 24:
			frappe.throw("Total hours cannot be more than 24 hours")


		self.total_hours = total_hours
		self.total_ot = ot_hours

	def calculate_downtime(self):
		total = 0
		for a in self.downtimes:
			a.equipment = self.equipment
			if 0 >= a.hours:
				frappe.throw("Downtime hours should be greater than zero") 
			total += a.hours
		self.total_downtime_hours = total

	def validate_hours(self):
		difference = flt(self.total_hours) + flt(self.total_downtime_hours) - flt(self.scheduled_working_hour)
		if difference < 0:
			frappe.throw("Total of work hours ({0}) and downtime hours ({1}) should be more or equal scheduled hours ({2})".format(frappe.bold(self.total_hours), frappe.bold(self.total_downtime_hours), frappe.bold(self.scheduled_working_hour)))
		if difference > 0:
			if flt(self.total_hours) + flt(self.total_downtime_hours) >= 24:
				frappe.throw("Total hours should be less than 24 hours")
			frappe.msgprint("<a style='color:red; font-size:large;'}><b>The total hours exceeds the scheduled working hour by "+str(difference)+" hours</b></a>")

	def on_submit(self):
		pass


