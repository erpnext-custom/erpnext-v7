# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SHIV		                    2017/08/11         Default "Project Tasks" is replaced by custom
                                                                         "Activity Tasks"
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe

from frappe.utils import flt, getdate, get_url
from frappe import _

from frappe.model.document import Document

class Project(Document):
	def get_feed(self):
		return '{0}: {1}'.format(_(self.status), self.project_name)

	def onload(self):
		"""Load project tasks for quick view"""
		# ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
		# Following code commented by SHIV on 2017/08/11
		'''
		if not self.get('__unsaved') and not self.get("tasks"):
			self.load_tasks()
		'''
		# +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++

                # ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
                # Following code added by SHIV on 2017/08/11
		if not self.get('__unsaved') and not self.get("activity_tasks"):
			self.load_activity_tasks()			
                # +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
                
		self.set_onload('activity_summary', frappe.db.sql('''select activity_type,
			sum(hours) as total_hours
			from `tabTimesheet Detail` where project=%s and docstatus < 2 group by activity_type
			order by total_hours desc''', self.name, as_dict=True))


	def __setup__(self):
		self.onload()

	def load_tasks(self):
		"""Load `tasks` from the database"""
		self.tasks = []
		for task in self.get_tasks():
			self.append("tasks", {
				"title": task.subject,
				"status": task.status,
				"start_date": task.exp_start_date,
				"end_date": task.exp_end_date,
				"description": task.description,
				"task_id": task.name
			})

        # ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
        # Follwoing code added by SSK on 2017/08/11
	def load_activity_tasks(self):
                #frappe.msgprint(_("load_activity_task is called from onload"))
		"""Load `activity_tasks` from the database"""
		self.activity_tasks = []
		for task in self.get_activity_tasks():
			self.append("activity_tasks", {
                                "activity": task.activity,
				"task": task.subject,
                                "is_group": task.is_group,
				"status": task.status,
				"start_date": task.exp_start_date,
				"end_date": task.exp_end_date,
				"description": task.description,
                                "work_quantity": task.work_quantity,
                                "target_uom": task.target_uom,
                                "target_quantity": task.target_quantity,
                                "target_quantity_complete": task.target_quantity_complete,
				"task_id": task.name
			})

	def get_activity_tasks(self):
		return frappe.get_all("Task", "*", {"project": self.name}, order_by="task_idx, exp_start_date")
	
        # +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
			
	def get_tasks(self):
		return frappe.get_all("Task", "*", {"project": self.name}, order_by="exp_start_date asc")

	def validate(self):
		self.validate_dates()

		# ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
		# Follwoing 2 lines are commented by SHIV on 2017/08/11
		'''
		self.sync_tasks()
		self.tasks = []
		'''
		# +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++

		# ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
		# Following 2 Lines added by SHIV on 2017/08/11
		self.sync_activity_tasks()
		self.activity_tasks = []
		# +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
		self.send_welcome_email()

	def validate_dates(self):
		if self.expected_start_date and self.expected_end_date:
			if getdate(self.expected_end_date) < getdate(self.expected_start_date):
				frappe.throw(_("Expected End Date can not be less than Expected Start Date"))

	def sync_tasks(self):
		"""sync tasks and remove table"""
		if self.flags.dont_sync_tasks: return

		task_names = []
		for t in self.tasks:
			if t.task_id:
				task = frappe.get_doc("Task", t.task_id)
			else:
				task = frappe.new_doc("Task")
				task.project = self.name

			task.update({
				"subject": t.title,
				"status": t.status,
				"exp_start_date": t.start_date,
				"exp_end_date": t.end_date,
				"description": t.description,
			})

			task.flags.ignore_links = True
			task.flags.from_project = True
			task.flags.ignore_feed = True
			task.save(ignore_permissions = True)
			task_names.append(task.name)

		# delete
		for t in frappe.get_all("Task", ["name"], {"project": self.name, "name": ("not in", task_names)}):
			frappe.delete_doc("Task", t.name)

		self.update_percent_complete()
		self.update_costing()
		
        # ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
        # Following function is created
	def sync_activity_tasks(self):
                #frappe.msgprint(_("sync_activity_tasks is called...."))
		"""sync tasks and remove table"""
		if self.flags.dont_sync_tasks: return

		task_names = []
		task_idx = 0
		for t in self.activity_tasks:
                        task_idx += 1

                        if not t.target_uom:
                                t.target_uom = 'Percent'
                                if not t.target_quantity:
                                        t.target_quantity = 100
                        
			if t.task_id:
				task = frappe.get_doc("Task", t.task_id)
			else:
				task = frappe.new_doc("Task")
				task.project = self.name

			task.update({
                                "activity": t.activity,
				"subject": t.task,
                                "is_group": t.is_group,
                                "work_quantity": t.work_quantity,
                                "target_uom": t.target_uom,
                                "target_quantity": t.target_quantity,
				"status": t.status,
				"exp_start_date": t.start_date,
				"exp_end_date": t.end_date,
				"description": t.description,
                                "target_quantity_complete": t.target_quantity_complete,
                                "task_idx": task_idx
			})

			task.flags.ignore_links = True
			task.flags.from_project = True
			task.flags.ignore_feed = True
			task.save(ignore_permissions = True)
			task_names.append(task.name)

		# delete
		for t in frappe.get_all("Task", ["name"], {"project": self.name, "name": ("not in", task_names)}):
			frappe.delete_doc("Task", t.name)

		self.update_percent_complete()
		self.update_costing()
        # +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
		
	def update_project(self):
		self.update_percent_complete()
		self.update_costing()
		self.flags.dont_sync_tasks = True
		self.save(ignore_permissions = True)

	def update_percent_complete(self):
                # ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
                # Following code commented by SHIV on 2017/08/16
                '''
		total = frappe.db.sql("""select count(*) from tabTask where project=%s""", self.name)[0][0]
		if total:
			completed = frappe.db.sql("""select count(*) from tabTask where
				project=%s and status in ('Closed', 'Cancelled')""", self.name)[0][0]

			self.percent_complete = flt(flt(completed) / total * 100, 2)
                '''

                # Following code added by SHIV on 2017/08/16
		total = frappe.db.sql("""select count(*) as counts,
                        sum(work_quantity) as tot_work_quantity
                        from tabTask where project=%s""", self.name, as_dict=1)[0]

		if total.counts:
			completed = frappe.db.sql("""select count(*) from tabTask where
				project=%s and status in ('Closed', 'Cancelled')""", self.name)[0][0]

			self.percent_complete = flt(flt(completed) / total.counts * 100, 2)

                if total.tot_work_quantity:
                        self.tot_wq_percent = flt(total.tot_work_quantity,2)
                # +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
                        
	def update_costing(self):
		from_time_sheet = frappe.db.sql("""select
			sum(costing_amount) as costing_amount,
			sum(billing_amount) as billing_amount,
			min(from_time) as start_date,
			max(to_time) as end_date,
			sum(hours) as time
			from `tabTimesheet Detail` where project = %s and docstatus = 1""", self.name, as_dict=1)[0]

		from_expense_claim = frappe.db.sql("""select
			sum(total_sanctioned_amount) as total_sanctioned_amount
			from `tabExpense Claim` where project = %s and approval_status='Approved'
			and docstatus = 1""",
			self.name, as_dict=1)[0]

		self.actual_start_date = from_time_sheet.start_date
		self.actual_end_date = from_time_sheet.end_date

		self.total_costing_amount = from_time_sheet.costing_amount
		self.total_billing_amount = from_time_sheet.billing_amount
		self.actual_time = from_time_sheet.time

		self.total_expense_claim = from_expense_claim.total_sanctioned_amount

		self.gross_margin = flt(self.total_billing_amount) - flt(self.total_costing_amount)

		if self.total_billing_amount:
			self.per_gross_margin = (self.gross_margin / flt(self.total_billing_amount)) *100

	def update_purchase_costing(self):
		total_purchase_cost = frappe.db.sql("""select sum(base_net_amount)
			from `tabPurchase Invoice Item` where project = %s and docstatus=1""", self.name)

		self.total_purchase_cost = total_purchase_cost and total_purchase_cost[0][0] or 0

	def send_welcome_email(self):
		url = get_url("/project/?name={0}".format(self.name))
		messages = (
		_("You have been invited to collaborate on the project: {0}".format(self.name)),
		url,
		_("Join")
		)

		content = """
		<p>{0}.</p>
		<p><a href="{1}">{2}</a></p>
		"""

		for user in self.users:
			if user.welcome_email_sent==0:
				frappe.sendmail(user.user, subject=_("Project Collaboration Invitation"), content=content.format(*messages))
				user.welcome_email_sent=1

	def on_update(self):
                # ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
                # Following 2 lines commented by SHIV on 2017/08/11
                '''
		self.load_tasks()
		self.sync_tasks()
                '''
		# Following 2 lines added by SHIV on 2017/08/11
		self.load_activity_tasks()
		self.sync_activity_tasks()		
		# +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++

def get_timeline_data(doctype, name):
	'''Return timeline for attendance'''
	return dict(frappe.db.sql('''select unix_timestamp(from_time), count(*)
		from `tabTimesheet Detail` where project=%s
			and from_time > date_sub(curdate(), interval 1 year)
			and docstatus < 2
			group by date(from_time)''', name))

def get_project_list(doctype, txt, filters, limit_start, limit_page_length=20):
	return frappe.db.sql('''select distinct project.*
		from tabProject project, `tabProject User` project_user
		where
			(project_user.user = %(user)s
			and project_user.parent = project.name)
			or project.owner = %(user)s
			order by project.modified desc
			limit {0}, {1}
		'''.format(limit_start, limit_page_length),
			{'user':frappe.session.user},
			as_dict=True,
			update={'doctype':'Project'})

def get_list_context(context=None):
	return {
		"show_sidebar": True,
		"show_search": True,
		'no_breadcrumbs': True,
		"title": _("Projects"),
		"get_list": get_project_list,
		"row_template": "templates/includes/projects/project_row.html"
	}

def get_users_for_project(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select name, concat_ws(' ', first_name, middle_name, last_name)
		from `tabUser`
		where enabled=1
		and name not in ("Guest", "Administrator")
		order by
		name asc""")

@frappe.whitelist()
def get_cost_center_name(project):
	return frappe.db.get_value("Project", project, "cost_center")
