# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
2.0		  SHIV		                    11/08/2017         Default "Project Tasks" is replaced by custom
                                                                         "Activity Tasks"
2.0		  SHIV		                    02/09/2017         make_advance_payment method is created.
2.0		  SHIV		                    05/09/2017         make_project_payment method is created.
2.0               SHIV                              03/11/2017         set_status method is created.
2.0               SHIV                              07/06/2018         * Allowing role "Project Committee" to change
                                                                         Branch and Cost Center.
                                                                         Method: validate_branch_change
2.0.190402        SHIV                              2019/04/02         * Refined                                                                         
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe

from frappe import _

from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
import datetime

from frappe.model.naming import make_autoname
from erpnext.custom_utils import get_branch_cc

from frappe.utils import add_days, getdate, formatdate, today, get_first_day, date_diff, add_years, flt
from erpnext.accounts.utils import get_fiscal_year



class Project(Document):
        def autoname(self):
               	self.name = self.project_name

	def validate(self):
		self.name = self.project_name
		self.check_required_data()
		self.validate_dates()
		self.task_dates()
		self.physical_progress_weightage = round(flt(self.mandays)/flt(self.overall_mandays) * 100, 3)
		#self.calculations()
		#self.update_parent()
		self.get_budget()
	
	def on_submit(self):
                self.update_progress()
		self.validate_dates()
		self.task_dates()
		#self.update_parent()

	def check_required_data(self):
		if not self.expected_start_date or not self.expected_end_date:
			frappe.throw("<b> Expected Start/End Date Is Required </b> ", title = 'Missing Input')
		if not self.overall_mandays:
			frappe.throw("<b> Mandays for Academy Is Required </b> ", title = 'Missing Input')
		if not self.mandays:
			frappe.throw("<b> Mandays for Activity Is Required </b>", title = 'Missing Input')
		if not self.physical_progress_weightage:
			frappe.throw("<b> Activity Weightage Is required </b>", title = 'Missing Input')
		if not self.is_group and not self.project_category:
			frappe.throw("<b> Activity Category Is Required </b>", title = 'Missing Input')
		if not self.is_group and not self.project_sub_category:
			frappe.throw("<b> Activity Sub Category Is Required </b>", title = 'Missing Input')
		if not self.is_group and not self.parent_project:
			frappe.throw("<b> Academy(Parent Activity) Is Required </b>", title = 'Missing Input')
		if not self.holiday_list:
			frappe.throw("<b> Holiday List Is Missing </b>", title = 'Missing Input')
		#if not self.is_group and not self.reference_budget:
		#frappe.throw("<b> Budget Not Defined!, Kindly Contact Finance Manager </b>", title = 'No Data')
		if flt(self.mandays) > flt(self.overall_mandays):
			frappe.throw("<b> Activity Mandays Cannot be greather than Academy Mandays </b>", title = 'Invalid Input')

	def validate_dates(self):
		total_days = 0.0
		if self.expected_start_date and self.expected_end_date:
			if getdate(self.expected_start_date) > getdate(self.expected_end_date):
				frappe.throw("Start Date Cannot be before End Date")
			holiday  = holiday_list(self.expected_start_date, self.expected_end_date, self.holiday_list)
			self.total_duration = date_diff(self.expected_end_date, self.expected_start_date) + 1 - flt(holiday)
			self.man_power_required = round(flt(self.mandays)/flt(self.total_duration))
		self.physical_progress = 0.0
		self.percent_completed = 0.0

	
	def task_dates(self):
		total_duration = 0.0		
		for a in self.get("activity_tasks"):
			if getdate(a.start_date) > getdate(a.end_date):
				frappe.throw("Task Start Date Cannot be Greater than End Date at Index {0}".format(a.idx))
			if flt(a.task_completion_percent) > 100:
				frappe.throw(" Percent Cannot exceed 100%")

			if flt(a.task_completion_percent) < 0:
				frappe.throw("Percent Cannot be less than 0%")

			if getdate(a.start_date) < getdate(self.expected_start_date):
				frappe.throw("Task Start Date Cannot be before Activity Start Date at Index {0}".format(a.idx))

			if getdate(a.end_date) > getdate(self.expected_end_date):
				frappe.throw("Task End Date Cannot Exceed the Activity End Date at Index {0}".format(a.idx))
			
			holiday  = holiday_list(a.start_date, a.end_date, self.holiday_list)	
			a.task_duration = date_diff(a.end_date, a.start_date) + 1 - flt(holiday)	
			total_duration = self.total_task_duration()
			#a.task_weightage = round(flt(a.task_duration)/flt(total_duration)*self.physical_progress_weightage, 7)
			a.task_weightage = round(flt(a.task_duration)/flt(total_duration) * 100, 7)
			a.one_day_weightage = round(flt(a.task_weightage)/flt(a.task_duration), 7)
			a.task_achievement_percent = 0.0	
			a.one_day_achievement = 0.0
	def total_task_duration(self):
		total_duration = 0.0
		for a in self.get("activity_tasks"):
			total_duration += flt(a.task_duration)
		return total_duration
				
	#def after_insert
	def on_update_after_submit(self):
		self.physical_progress = round(flt(self.physical_progress), 7)
		self.update_progress()
		if self.percent_completed == 100:
			self.db_set("status", "Completed")
		if self.percent_completed < 100:
			self.db_set("status", "Ongoing")
		te = self.total_task_duration()
		if not self.is_group:
			self.update_parent()
		
	def update_progress(self):
                total_achievement = 0.0
                for a in self.get("activity_tasks"):
			if a.task_completion_percent > 100:
				frappe.throw("Task Completion Percent Cannot Exceed 100 % at Sl. <b> {0} </b>".format(a.idx))
			'''if flt(a.get_db_value('task_completion_percent')) < flt(a.task_completion_percent):
				frappe.throw("Task Progress Percent Cannot be less than {0} at SL. {1}".format(a.get_db_value('task_completion_percent'), a.idx))
			'''
			a.task_achievement_percent = round(flt(a.task_completion_percent)/100 * flt(a.task_weightage), 7)
                        a.one_day_achievement = round(flt(a.task_achievement_percent)/flt(a.task_duration), 7)
                        total_achievement += flt(a.task_achievement_percent)
                #self.physical_progress = round(total_achievement, 3)
		#self.physical_progress = round(flt(total_achievement)/100 * flt(self.physical_progress_weightage), 3)
		self.percent_completed = round(total_achievement, 3)	
		#self.percent_completed = round(flt(self.physical_progress)/flt(self.physical_progress_weightage)*100, 3)
		self.physical_progress = round(flt(self.percent_completed)/100 * flt(self.physical_progress_weightage), 3)	
		self.update_parent()



	def update_parent(self):
		progress = frappe.db.sql(""" select sum(ifnull(physical_progress, 0)) as val from `tabProject` where parent_project = '{0}' 
			and is_group = 0 and docstatus <=1""".format(self.parent_project), as_dict = 1)
		if progress:
			doc = frappe.get_doc("Project", self.parent_project)
			doc.db_set("physical_progress", flt(progress[0].val))
			doc.db_set("percent_completed", round(flt(doc.physical_progress)/flt(doc.physical_progress_weightage) * 100, 4)) 
		#progress = flt(progress[0].val)
		#completed = round(flt(doc.physical_progress)/flt(doc.physical_progress_weightage), 4)
		#frappe.db.sql(""" update `tabProject` set physical_progress = {0}, percent_completed = {1} where name = '{2}' and is_group = 1 and docstatus <= 1""".format(progress, completed, self.parent_project))

	def get_budget(self):
                budget = frappe.db.sql(" select name, actual_total from `tabBudget` where cost_center = '{0}' and docstatus = 1".format(self.project_name), as_dict =1)
		if budget:
			self.reference_budget = budget[0].name
			self.estimated_budget = budget[0].actual_total
		
	#on_change
        def update_task_group(self):
                group_list = frappe.db.sql("""
                                        select t1.name, t1.task, t1.idx, t1.is_group,
                                                (select ifnull(min(t2.idx),9999)
                                                 from  `tabActivity Tasks` as t2
                                                 where t2.parent  = t1.parent
                                                 and   t2.is_group = t1.is_group
                                                 and   t2.idx > t1.idx
                                                ) as max_idx
                                        from `tabActivity Tasks` as t1
                                        where t1.parent = "{0}"
                                        and   t1.is_group = 1
                                        order by t1.idx
                                """.format(self.name), as_dict=1)
                for a in group_list:
                        frappe.db.sql(""" update `tabActivity Tasks` set task_group = '{0}' where idx> {1} and idx < {2} and parent = '{3}' and name != '{4}'""".format(a.name, a.idx, a.max_idx, self.name, a.name))

                if not group_list:
                        frappe.db.sql(""" update `tabActivity Tasks` set task_group = '' where parent = '{0}'""".format(self.name))
                        #self.calculations()    
                frappe.db.commit()

	def calculations(self):
                total_days = 0.0
                mandays = self.mandays
                contributed = 0.0
                for a in self.get("activity_tasks"):
                        if a.task_group:

                                doc = frappe.get_doc("Activity Tasks", a.task_group)
                                task_doc= frappe.db.sql(""" select sum(ifnull(task_duration, 0)) as task from `tabActivity Tasks` where parent = '{0}' and docstatus <=1 and task_group = '{1}' group by task_group, parent""".format(self.name, a.task_group), as_dict = 1)
                                if task_doc:
                                        a.task_weightage = flt(a.task_duration)/flt(task_doc[0].task)*flt(doc.task_weightage)
                        else:
                                a.task_weightage = round(flt(a.task_duration)/flt(self.mandays), 7)
                        a.one_day_weightage = round(flt(a.task_weightage)/flt(a.task_duration), 7)

                        if not a.is_group:
                                contributed += round(flt(a.task_achievement_percent), 7)
                self.physical_progress = round(contributed, 7)
                self.percent_completed = round(flt(self.physical_progress)/flt(self.physical_progress_weightage), 5) * 100
	
	def make_group(self):
                self.task_dates()
                group_list = frappe.db.sql("""
                                        select t1.name, t1.task, t1.idx, t1.is_group,
                                                (select ifnull(min(t2.idx),9999)
                                                 from  `tabActivity Tasks` as t2
                                                 where t2.parent  = t1.parent
                                                 and   t2.is_group = t1.is_group
                                                 and   t2.idx > t1.idx
                                                ) as max_idx
                                        from `tabActivity Tasks` as t1
                                        where t1.parent = "{0}"
                                        and   t1.is_group = 1
                                        order by t1.idx
                                """.format(self.name), as_dict=1)
                for a in group_list:
                        frappe.db.sql(""" update `tabActivity Tasks` set task_group = '{0}' where {1} < idx < {2} and parent = '{3}'""".format(a.name, a.idx, a.max_idx, self.name), debug =1)

@frappe.whitelist()
def calculate_durations(hol_list = None, from_date = None, to_date = None):
	holiday = holiday_list(from_date, to_date, hol_list)
	duration = date_diff(to_date, from_date) + 1 - flt(holiday)
	return duration
	
	
#returns total holiday between given dates
def holiday_list(from_date, to_date, hol_list):
	holidays = 0.0
	if hol_list:
		holidays = frappe.db.sql("""select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
	where h1.parent = h2.name and h1.holiday_date between %s and %s
	and h2.name = %s""", (from_date, to_date, hol_list))[0][0]
	return holidays

