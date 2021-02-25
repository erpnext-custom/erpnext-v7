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
		self.make_target_entries()
	def on_submit(self):
                self.update_progress()
		self.validate_dates()
		self.task_dates()
		#self.update_parent()
		self.make_target_entries()

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
		if not self.is_group and not self.reference_budget:
			frappe.msgprint("<b> Budget Not Defined!, Kindly Contact Finance Manager </b>", title = 'No Data')
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
		self.percent_completed_old = 0.0
	
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
			if not a.task_duration:
				frappe.throw("Cannot Schedule Task on Off Days at index {0}".format(a.idx))
			total_duration = self.total_task_duration()
			#a.task_weightage = round(flt(a.task_duration)/flt(total_duration)*self.physical_progress_weightage, 7)
			a.task_weightage = round(flt(a.task_duration)/flt(total_duration) * 100, 7)
			a.one_day_weightage = round(flt(a.task_weightage)/flt(a.task_duration), 7)
			a.one_day_weightage_overall = flt(a.one_day_weightage)/100 * flt(self.physical_progress_weightage)
			a.task_achievement_percent = 0.0	
			a.one_day_achievement = 0.0
			a.task_completion_percent = 0.0
	def total_task_duration(self):
		total_duration = 0.0
		for a in self.get("activity_tasks"):
			total_duration += flt(a.task_duration)
		return total_duration
				
	#def after_insert
	def on_update_after_submit(self):
		if not self.completion_date:
			frappe.throw("Completion Date is Required", title="Missing Input")
		self.physical_progress = round(flt(self.physical_progress), 7)
		self.update_progress()
		if self.percent_completed == 100:
			self.db_set("status", "Completed")
		if self.percent_completed < 100:
			self.db_set("status", "Ongoing")
		self.total_task_duration()
		if not self.is_group:
			self.update_parent()
		self.post_achievement_entries()
		self.make_target_entries()	
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
		self.percent_completed = round(total_achievement, 4)	
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
                self.reference_budget = None
                self.estimated_budget = 0.0
		budget = frappe.db.sql(" select name, actual_total from `tabBudget` where cost_center = '%s' and docstatus = 1" %self.project_name, as_dict =1)
		if budget:
			self.reference_budget = budget[0].name
			self.estimated_budget = budget[0].actual_total
			doc = frappe.db.sql(""" select sum(estimated_budget) as budget from `tabProject` 
			where parent_project = '{0}' group by parent_project""".format(self.parent_project), as_dict = 1)
			
			if doc:
				frappe.db.sql(""" update `tabProject` set estimated_budget = {0} where name = '{1}'
				""".format(doc[0].budget, self.parent_project))
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

	def make_target_entries(self):
		frappe.db.sql(""" delete from `tabTarget Entry Sheet` where project = '%s'""" %self.name)
		#task = self.get_tasks_data()
		target_tot = 0.0
		target_tot_overall = 0.0
		for from_date, to_date in self.get_period_date_ranges():
			old = frappe.db.sql(""" select percent_completed from `tabTarget Entry Sheet` 
					where project = '{0}' and to_date < '{1}' order by to_date desc limit 1
				""".format(self.name, from_date), as_dict = 1)
			old =  old[0].percent_completed if old else 0.0
			for t in self.get("activity_tasks"):
				if getdate(t.start_date) >=  getdate(from_date) and getdate(t.end_date) <= getdate(to_date):
					hol_list = holiday_list(t.start_date, t.end_date, self.holiday_list)
					duration = date_diff(t.end_date, t.start_date) + 1 - flt(hol_list)
					target_tot += round(flt(duration) * flt(t.one_day_weightage), 4)

				if getdate(t.start_date) < getdate(from_date) and getdate(t.end_date) > getdate(to_date):
                                        hol_list = holiday_list(from_date, to_date, self.holiday_list)
                                        duration = date_diff(to_date, from_date) + 1 - flt(hol_list)
                                        target_tot += round(flt(duration) * flt(t.one_day_weightage), 4)	
	
				if getdate(to_date) >= getdate(t.start_date) >=  getdate(from_date) and getdate(t.end_date) > getdate(to_date):
                                        hol_list = holiday_list(t.start_date, to_date, self.holiday_list)
                                        duration = date_diff(to_date, t.start_date) + 1 - flt(hol_list)
                                        target_tot += round(flt(duration) * flt(t.one_day_weightage), 4)

				if getdate(t.start_date) < getdate(from_date) and getdate(from_date) <= getdate(t.end_date) <= getdate(to_date):
					hol_list = holiday_list(from_date, t.end_date, self.holiday_list)
					duration = date_diff(t.end_date, from_date) + 1 - flt(hol_list)
					target_tot += round(flt(duration) * flt(t.one_day_weightage),4)
					
			per = flt(target_tot) - flt(old)
			doc = frappe.get_doc({
				'doctype': 'Target Entry Sheet',
				'project': self.name,
				'project_parent': self.parent_project,
				'entry_type': 'Monthly',
				'from_date': from_date,
				'to_date': to_date,
				'percent_completed': target_tot,
				'percent_completed_overall': round(flt(per)/100 * flt(self.physical_progress_weightage), 9),
				'entry_name': get_period(to_date, 'Monthly') 
					})
			doc.insert()
	def get_tasks_data(self, from_date, to_date):
                task = frappe.db.sql(""" select name, start_date, end_date, one_day_weightage, one_day_weightage_overall  
                        from `tabActivity Tasks` where parent = '{0}' and docstatus <= 1
			and (start_date between '{0}' and '{1}' or end_date between '{0}' and '{1}' or 
				'{0}' between start_date and end_date or '{1}' between start_date and end_date)""".format(self.name, from_date, to_date), as_dict =1)
                return task

	def get_period_date_ranges(self):
                from dateutil.relativedelta import relativedelta
                from_date, to_date = getdate(self.expected_start_date), getdate(self.expected_end_date)
		da = frappe.db.sql(""" select min(start_date) as min_date, max(end_date) as max_date from `tabActivity Tasks` 
			where parent = '{0}'""".format(self.name), as_dict =1)
		if da:
			if from_date < getdate(da[0].min_date):
				from_date = getdate(da[0].min_date)
			if to_date > getdate(da[0].max_date):
				to_date = getdate(da[0].max_date)
                start_date = get_first_day(from_date)
                date_range = 'Monthly'
		#date_range = 'Weekly'
		increment = {
                        "Monthly": 1,
                        "Quarterly": 3,
                        "Half-Yearly": 6,
                        "Yearly": 12
                }.get(date_range,1)

                periodic_daterange = []
                for dummy in range(1, 53, increment):
                        if date_range == "Weekly":
                                period_end_date = start_date + relativedelta(days=6)
                        else:
                                period_end_date = start_date + relativedelta(months=increment, days=-1)

                        if period_end_date > to_date:
                                period_end_date = to_date
                        periodic_daterange.append([start_date, period_end_date])

                        start_date = period_end_date + relativedelta(days=1)
                        from_date = period_end_date + relativedelta(days=1)

                        if period_end_date == to_date:
                                break
                return periodic_daterange

	def post_achievement_entries(self):
		frappe.db.sql(""" delete from `tabAchievement Entry Sheet` where project = '{0}' and posting_date = '{1}'
				""".format(self.name, self.completion_date))
		entry = frappe.db.sql(""" select sum(percent_completed) as per_completed, sum(percent_completed_overall) as overall from `tabAchievement Entry Sheet` where project = '{0}'""".format(self.name), as_dict = 1)
		en = 0.0
		if entry:
			en = entry[0].per_completed
			en_overall = entry[0].overall
		com = flt(self.percent_completed) - flt(en)
		#com_overall  = round(flt(self.physical_progress) - flt(en_overall), 5)
		#if flt(self.percent_completed) - flt(en):
		doc = frappe.get_doc({
			'doctype': 'Achievement Entry Sheet',
			'project': self.name,
			'project_parent': self.parent_project,
			'percent_completed': com,
			'percent_completed_overall': flt(com)/100 * flt(self.physical_progress_weightage),
			'posting_date': self.completion_date
				})
		doc.insert()
		self.db_set('percent_completed_old', round(flt(self.percent_completed), 6))
		self.db_set('physical_progress_old', round(flt(self.physical_progress), 6))
		self.completion_date = None


	def notify_on_change(self):
		pass

def get_period(posting_date, prange):
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        if prange == 'Weekly':
                period = "Week " + str(posting_date.isocalendar()[1]) + " " + str(posting_date.year)
        elif prange == 'Monthly':
                period = str(months[posting_date.month - 1]) + " " + str(posting_date.year)
        elif prange == 'Quarterly':
                period = "Quarter " + str(((posting_date.month-1)//3)+1) +" " + str(posting_date.year)
        else:
                year = get_fiscal_year(posting_date, company=filters.company)
                period = str(year[2])
        return period
	
@frappe.whitelist()
def calculate_durations(hol_list = None, from_date = None, to_date = None):
	holiday = holiday_list(from_date, to_date, hol_list)
	duration = date_diff(to_date, from_date) + 1 - flt(holiday)
	return duration


@frappe.whitelist()
def testing(from_date, to_date):
	frappe.msgprint(" I am called from server")
	return "hi"
	
#returns total holiday between given dates
def holiday_list(from_date, to_date, hol_list):
	holidays = 0.0
	if hol_list:
		holidays = frappe.db.sql("""select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
	where h1.parent = h2.name and h1.holiday_date between %s and %s
	and h2.name = %s""", (from_date, to_date, hol_list))[0][0]
	return holidays

