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
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe

from frappe.utils import flt, getdate, get_url, today
from frappe import _

from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
import datetime

# Autonaming is changed, SHIV on 23/10/2017
from frappe.model.naming import make_autoname
from erpnext.custom_utils import get_branch_cc

class Project(Document):
        def autoname(self):
                cur_year  = str(today())[0:4]
                cur_month = str(today())[5:7]
                serialno  = make_autoname("PRJ.####")
                self.name = serialno[0:3] + cur_year + cur_month + serialno[3:]
                
	def get_feed(self):
		return '{0}: {1}'.format(_(self.status), self.project_name)

	def onload(self):
		"""Load project tasks for quick view"""
		# ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
		# Following code commented by SHIV on 11/08/2017
		'''
		if not self.get('__unsaved') and not self.get("tasks"):
			self.load_tasks()
		'''

                # Following code added by SHIV on 11/08/2017 
		if not self.get('__unsaved') and not self.get("activity_tasks"):
			self.load_activity_tasks()
			self.load_additional_tasks()
			self.load_boq()
			self.load_advance()
			self.load_invoice()

                # Following code is commented and the subsequent is added by SHIV on 20/09/2017
                """
		self.set_onload('activity_summary', frappe.db.sql('''select activity_type,
			sum(hours) as total_hours
			from `tabTimesheet Detail` where project=%s and docstatus < 2 group by activity_type
			order by total_hours desc''', self.name, as_dict=True))

                """
                
		self.set_onload('activity_summary', frappe.db.sql('''select description activity_type,
			sum(days) as total_days
			from `tabTimesheet Detail` where project=%s and docstatus < 2 group by description
			order by total_days desc''', self.name, as_dict=True))
                # +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++

        # Commented by SHIV on 2019/01/30, it seems is calling onload twice
        '''
	def __setup__(self):
		self.onload()
        '''
        
	def validate(self):
		self.validate_dates()
		self.validate_branch_cc()

		# ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
		# Follwoing 2 lines are commented by SHIV on 2017/08/11
		'''
		self.sync_tasks()
		self.tasks = []
		'''
		# set_status method created by SHIV on 03/11/2017
		self.set_status()
		
		# Following code added by SHIV on 2017/08/11
		self.validate_target_quantity()
		self.validate_work_quantity()
		self.validate_imprest()
		if self.status in ('Planning','Ongoing'):
                        self.sync_activity_tasks()
                        self.sync_additional_tasks()
		self.activity_tasks = []
		self.additional_tasks = []
		self.project_advance_item = []
		self.project_boq_item = []
		self.project_invoice_item = []

		# Following method added by SHIV on 03/11/2017
		self.validate_branch_change()
		# +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++
		self.send_welcome_email()

	def validate_branch_cc(self):
		if self.cost_center != get_branch_cc(self.branch):
			frappe.throw("Project\'s branch and cost center doesn't belong to each other")

	def on_update(self):
                # ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
                # Following 2 lines commented by SHIV on 2017/08/11
                '''
		self.load_tasks()
		self.sync_tasks()
                '''
		# Following 2 lines added by SHIV on 2017/08/11
		self.load_activity_tasks()
		self.load_additional_tasks()
		if self.status in ('Planning','Ongoing'):
                        self.sync_activity_tasks()
                        self.sync_additional_tasks()
		self.update_task_progress()
		self.update_project_progress()
		self.update_group_tasks()
		# Following method created by SHIV on 07/06/2018
		self.update_branch_change()
		# +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++

        def validate_branch_change(self):
                if self.branch != self.get_db_value("branch"):
                        for doctype in ["Project Advance", "Project Invoice"]:
                                for t in frappe.get_all(doctype, ["name"], {"project": self.name, "docstatus":("<",2)}):
                                        msg = '<b>Reference# <a href="#Form/{0}/{1}">{0}: {1}</a></b>'.format(doctype, t.name)
                                        frappe.throw(_("Change of branch not permitted.<br>{0}").format(msg),title="Dependencies found")

        def update_branch_change(self):
                for doctype in ["MB Entry", "BOQ Adjustment", "BOQ", "Timesheet", "Task"]:
                        for t in frappe.get_all(doctype, ["name"], {"project": self.name}):
                                doc = frappe.get_doc(doctype, t.name)
                                if self.branch != doc.branch:
                                        doc.branch      = self.branch
                                        doc.cost_center = self.cost_center
                                        doc.save(ignore_permissions = True)
                                        

        def set_status(self):
                self.docstatus = {
                      "Planning": 0,
                      "Ongoing": 0,
                      "Completed": 1,
                      "Cancelled": 2
                }[str(self.status) or "Planning"]

        def validate_imprest(self):
                if flt(self.imprest_limit) < 0:
                        frappe.throw(_("Imprest Limit cannot be a negative value."),title="Invalid Value")
                        
                if flt(self.imprest_limit) < flt(self.imprest_received):
                        frappe.throw(_("Imprest Limit cannot be less than already received amount."),title="Invalid Value")

                self.imprest_receivable = flt(self.imprest_limit) - flt(self.imprest_received)

        
        # ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
        def validate_target_quantity(self):
                for task in self.activity_tasks:
                        prev_value = frappe.db.get_value("Task", task.task_id, "target_quantity")
                        
                        if flt(task.target_quantity) < flt(task.target_quantity_complete):
                                frappe.throw(_("<b>WORK PLAN</b><br/> Row# {0} : `Target Value` cannot be less than `Achieved Value`.").format(task.idx))

                        if flt(task.target_quantity) != flt(prev_value) and flt(prev_value) > 0:
                                msg = ""
                                ts_list = frappe.db.sql("""
                                                select name
                                                from `tabTimesheet`
                                                where project = "{0}"
                                                and task = '{1}'
                                                and docstatus < 2
                                        """.format(self.name, task.task_id), as_dict=1)

                                if len(ts_list):
                                        for item in ts_list:
                                                msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
                                        
                                        frappe.throw("Row# {0} : Cannot change `Target Quantity/Value` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))
                                        
                for task in self.additional_tasks:
                        prev_value = frappe.db.get_value("Task", task.task_id, "target_quantity")
                        
                        if flt(task.target_quantity) < flt(task.target_quantity_complete):
                                frappe.throw(_("<b>WORK PLAN</b><br/> Row# {0} : `Target Value` cannot be less than `Achieved Value`.").format(task.idx))

                        if flt(task.target_quantity) != flt(prev_value) and flt(prev_value) > 0:
                                msg = ""
                                ts_list = frappe.db.sql("""
                                                select name
                                                from `tabTimesheet`
                                                where project = "{0}"
                                                and task = '{1}'
                                                and docstatus < 2
                                        """.format(self.name, task.task_id), as_dict=1)

                                if len(ts_list):
                                        for item in ts_list:
                                                msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
                                        
                                        frappe.throw("Row# {0} : Cannot change `Target Quantity/Value` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))
                                        
        def validate_work_quantity(self):
                for task in self.activity_tasks:
                        prev_value = frappe.db.get_value("Task", task.task_id, "work_quantity")
                        
                        if flt(task.work_quantity) < flt(task.work_quantity_complete):
                                frappe.throw(_("<b>WORK PLAN</b><br/> Row# {0} : `Target Work Quantity` cannot be less than `Already Achieved Wrok Quantity`.").format(task.idx))

                        if flt(task.work_quantity) != flt(prev_value) and flt(prev_value) > 0:
                                msg = ""
                                ts_list = frappe.db.sql("""
                                                select name
                                                from `tabTimesheet`
                                                where project = "{0}"
                                                and task = '{1}'
                                                and docstatus < 2
                                        """.format(self.name, task.task_id), as_dict=1)

                                if len(ts_list):
                                        for item in ts_list:
                                                msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
                                        
                                        frappe.throw("Row# {0} : Cannot change `Target Work Quantity` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))
        
                for task in self.additional_tasks:
                        prev_value = frappe.db.get_value("Task", task.task_id, "work_quantity")
                        
                        if flt(task.work_quantity) < flt(task.work_quantity_complete):
                                frappe.throw(_("<b>WORK PLAN</b><br/> Row# {0} : `Target Work Quantity` cannot be less than `Already Achieved Wrok Quantity`.").format(task.idx))

                        if flt(task.work_quantity) != flt(prev_value) and flt(prev_value) > 0:
                                msg = ""
                                ts_list = frappe.db.sql("""
                                                select name
                                                from `tabTimesheet`
                                                where project = "{0}"
                                                and task = '{1}'
                                                and docstatus < 2
                                        """.format(self.name, task.task_id), as_dict=1)

                                if len(ts_list):
                                        for item in ts_list:
                                                msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
                                        
                                        frappe.throw("Row# {0} : Cannot change `Target Work Quantity` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))
                                        
        def update_task_progress(self):
                task_list = frappe.db.sql("""
                                select name
                                from `tabTask`
                                where project = "{0}"
                                """.format(self.name), as_dict=1)

                if task_list:
                        for task in task_list:
                                values = frappe.db.sql("""
                                                select sum(ifnull(target_quantity_complete,0)) as target_quantity_complete,
                                                        sum(ifnull(work_quantity_complete,0)) as work_quantity_complete
                                                from `tabTimesheet`
                                                where task = '{0}'
                                                and   docstatus < 2
                                                """.format(task.name), as_dict=1)[0]
                        
                                frappe.db.sql("""
                                        update `tabTask`
                                        set target_quantity_complete = {0},
                                                work_quantity_complete = {1},
                                                status = case
                                                                when {0} >= target_quantity then 'Closed'
                                                                else status
                                                         end
                                        where name = '{2}'
                                """.format(flt(values.target_quantity_complete), flt(values.work_quantity_complete), task.name))

        def update_project_progress(self):
                # Following code added by SHIV on 2017/08/16
		total = frappe.db.sql("""
                                select
                                        sum(
                                                case
                                                when additional_task = 0 and status in ('Closed', 'Cancelled') then 1
                                                else 0
                                                end
                                        ) as completed_count,
                                        sum(
                                                case
                                                when additional_task = 0 then 1
                                                else 0
                                                end
                                        ) as count,
                                        sum(
                                                case
                                                when additional_task = 1 and status in ('Closed', 'Cancelled') then 1
                                                else 0
                                                end
                                        ) as add_completed_count,
                                        sum(
                                                case
                                                when additional_task = 1 then 1
                                                else 0
                                                end
                                        ) as add_count,
                                        sum(
                                                case
                                                when additional_task = 0 then ifnull(work_quantity,0)
                                                else 0
                                                end
                                        ) as tot_work_quantity,
                                        sum(
                                                case
                                                when additional_task = 1 then ifnull(work_quantity,0)
                                                else 0
                                                end
                                        ) as tot_add_work_quantity,
                                        sum(
                                                case
                                                when additional_task = 0 then ifnull(work_quantity_complete,0)
                                                else 0
                                                end
                                        ) as tot_work_quantity_complete,
                                        sum(
                                                case
                                                when additional_task = 1 then ifnull(work_quantity_complete,0)
                                                else 0
                                                end
                                        ) as tot_add_work_quantity_complete
                                from tabTask
                                where project=%s
                                and is_group=0
                        """, self.name, as_dict=1)[0]

                # Following code commented by SHIV on 09/11/2017
                self.percent_complete           = 0.0
                self.add_percent_complete       = 0.0
                self.tot_wq_percent             = 0.0
                self.tot_wq_percent_complete    = 0.0
                self.tot_add_wq_percent         = 0.0
                self.tot_add_wq_percent_complete= 0.0

                if total.count:
                        self.percent_complete   = flt(flt(total.completed_count) / total.count * 100, 2)
                        self.tot_wq_percent     = flt(total.tot_work_quantity,2)
                        self.tot_wq_percent_complete = flt(total.tot_work_quantity_complete,2)

                if total.add_count:
                        self.add_percent_complete = flt(flt(total.add_completed_count) / total.add_count * 100, 2)
                        self.tot_add_wq_percent = flt(total.tot_add_work_quantity,2)
                        self.tot_add_wq_percent_complete = flt(total.tot_add_work_quantity_complete,2)
                # +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++                

        def update_group_tasks(self):
                # Activity Tasks
                group_list = frappe.db.sql("""
                                        select t1.name, t1.task_idx, t1.subject, t1.is_group,
                                                (select ifnull(min(t2.task_idx),9999)
                                                 from  `tabTask` as t2
                                                 where t2.project  = t1.project
                                                 and   t2.is_group = t1.is_group
                                                 and   t2.task_idx > t1.task_idx
                                                ) as max_idx
                                        from `tabTask` as t1
                                        where t1.project = "{0}"
                                        and   t1.is_group = 1
                                        and   t1.additional_task = 0
                                        order by t1.task_idx
                                """.format(self.name), as_dict=1)
                
                for item in group_list:
                        values = frappe.db.sql("""
                                        select min(exp_start_date) as min_start_date,
                                                max(exp_end_date) as max_end_date,
                                                sum(ifnull(work_quantity,0)) as tot_work_quantity,
                                                sum(ifnull(work_quantity_complete,0)) as tot_work_quantity_complete
                                         from   `tabTask`
                                         where  project = "{0}"
                                         and    task_idx > {1}
                                         and    task_idx < {2}
                                         and    additional_task = 0
                                """.format(self.name, item.task_idx, item.max_idx), as_dict=1)[0]

                        frappe.db.sql("""
                                        update `tabTask`
                                        set
                                                grp_exp_start_date = '{0}',
                                                grp_exp_end_date = '{1}',
                                                grp_work_quantity = {4},
                                                grp_work_quantity_complete = {5}
                                        where project = "{2}"
                                        and name = '{3}'
                                """.format(values.min_start_date, values.max_end_date, self.name, item.name, flt(values.tot_work_quantity), flt(values.tot_work_quantity_complete)))

                # Additional Tasks
                group_list = frappe.db.sql("""
                                        select t1.name, t1.task_idx, t1.subject, t1.is_group,
                                                (select ifnull(min(t2.task_idx),9999)
                                                 from  `tabTask` as t2
                                                 where t2.project  = t1.project
                                                 and   t2.is_group = t1.is_group
                                                 and   t2.task_idx > t1.task_idx
                                                ) as max_idx
                                        from `tabTask` as t1
                                        where t1.project = "{0}"
                                        and   t1.is_group = 1
                                        and   t1.additional_task = 1
                                        order by t1.task_idx
                                """.format(self.name), as_dict=1)
                
                for item in group_list:
                        values = frappe.db.sql("""
                                        select min(exp_start_date) as min_start_date,
                                                max(exp_end_date) as max_end_date,
                                                sum(ifnull(work_quantity,0)) as tot_work_quantity,
                                                sum(ifnull(work_quantity_complete,0)) as tot_work_quantity_complete
                                         from   `tabTask`
                                         where  project = "{0}"
                                         and    task_idx > {1}
                                         and    task_idx < {2}
                                         and    additional_task = 1
                                """.format(self.name, item.task_idx, item.max_idx), as_dict=1)[0]

                        frappe.db.sql("""
                                        update `tabTask`
                                        set
                                                grp_exp_start_date = '{0}',
                                                grp_exp_end_date = '{1}',
                                                grp_work_quantity = {4},
                                                grp_work_quantity_complete = {5}
                                        where project = "{2}"
                                        and name = '{3}'
                                """.format(values.min_start_date, values.max_end_date, self.name, item.name, flt(values.tot_work_quantity), flt(values.tot_work_quantity_complete)))                        
        # +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++
        
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

        # ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
        # Follwoing code added by SSK on 2017/08/11
        def load_boq(self):
                """Load `project_advance_item` from the database"""
                self.project_boq_item = []
                tot_tot_amt = 0.0
                tot_rcd_amt = 0.0
                tot_bal_amt = 0.0
                boq_list    = self.get_project_boq()
                
                for item in boq_list:
                        self.append("project_boq_item",{
                                "boq_name": item.name,
                                "boq_date": item.boq_date.strftime("%d-%m-%Y"),
                                "amount": flt(item.total_amount),
                                "price_adjustment": flt(item.price_adjustment),
                                "total_amount": flt(item.total_amount)+flt(item.price_adjustment),
                                "received_amount": flt(item.received_amount),
                                "balance_amount": flt(item.balance_amount)
                        })
                        tot_tot_amt += flt(item.total_amount)+flt(item.price_adjustment)
                        tot_rcd_amt += flt(item.received_amount)
                        tot_bal_amt += flt(item.balance_amount)

                if flt(tot_tot_amt) > 0 and len(boq_list) > 1:
                        self.append("project_boq_item",{
                                "boq_date": "TOTAL",
                                "total_amount": flt(tot_tot_amt),
                                "received_amount": flt(tot_rcd_amt),
                                "balance_amount": flt(tot_bal_amt)
                        })
                        
        def load_advance(self):
                """Load `project_advance_item` from the database"""
                self.project_advance_item = []
                tot_rcd_amt = 0.0
                tot_adj_amt = 0.0
                tot_bal_amt = 0.0
                advance_list= self.get_project_advance()
                
                for item in advance_list:
                        #datetime.datetime.strptime(str(item.advance_date),"%Y-%m-%d").strftime("%d-%m-%Y")
                        self.append("project_advance_item",{
                                "advance_name": item.name,
                                "advance_date": item.advance_date.strftime("%d-%m-%Y"),
                                "received_amount": flt(item.received_amount),
                                "adjustment_amount": flt(item.adjustment_amount),
                                "balance_amount": flt(item.balance_amount)
                        })
                        tot_rcd_amt += flt(item.received_amount)
                        tot_adj_amt += flt(item.adjustment_amount)
                        tot_bal_amt += flt(item.balance_amount)

                if flt(tot_rcd_amt) > 0 and len(advance_list) > 1:
                        self.append("project_advance_item",{
                                "advance_date": "TOTAL",
                                "received_amount": tot_rcd_amt,
                                "adjustment_amount": tot_adj_amt,
                                "balance_amount": tot_bal_amt
                        })
                        

        def load_invoice(self):
                """Load `project_invoice_item` from the database"""
                self.project_invoice_item = []
                tot_tot_amt = 0.0
                tot_rcd_amt = 0.0
                tot_bal_amt = 0.0
                invoice_list= self.get_project_invoice()
                
                for item in invoice_list:
                        self.append("project_invoice_item",{
                                "invoice_name": item.name,
                                "invoice_date": item.invoice_date.strftime("%d-%m-%Y"),
                                "boq": item.boq,
                                "gross_invoice_amount": flt(item.gross_invoice_amount),
                                "price_adjustment_amount": flt(item.price_adjustment_amount),
                                "net_invoice_amount": flt(item.net_invoice_amount),
                                "total_received_amount": flt(item.total_received_amount),
                                "total_balance_amount": flt(item.total_balance_amount)
                        })
                        tot_tot_amt += flt(item.net_invoice_amount)
                        tot_rcd_amt += flt(item.total_received_amount)
                        tot_bal_amt += flt(item.total_balance_amount)

                if flt(tot_tot_amt) > 0 and len(invoice_list) > 1:
                        self.append("project_invoice_item",{
                                "invoice_date": "TOTAL",
                                "net_invoice_amount": flt(tot_tot_amt),
                                "total_received_amount": flt(tot_rcd_amt),
                                "total_balance_amount": flt(tot_bal_amt)
                        })
                        
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
                                "work_quantity_complete": task.work_quantity_complete,
                                "target_uom": task.target_uom,
                                "target_quantity": task.target_quantity,
                                "target_quantity_complete": task.target_quantity_complete,
				"task_id": task.name,
                                "grp_exp_start_date": task.grp_exp_start_date,
                                "grp_exp_end_date": task.grp_exp_end_date,
                                "grp_work_quantity": task.grp_work_quantity,
                                "grp_work_quantity_complete": task.grp_work_quantity_complete
			})

	def load_additional_tasks(self):
                #frappe.msgprint(_("load_activity_task is called from onload"))
		"""Load `additional_tasks` from the database"""
		self.additional_tasks = []
		for task in self.get_additional_tasks():
			self.append("additional_tasks", {
                                "activity": task.activity,
				"task": task.subject,
                                "is_group": task.is_group,
				"status": task.status,
				"start_date": task.exp_start_date,
				"end_date": task.exp_end_date,
				"description": task.description,
                                "work_quantity": task.work_quantity,
                                "work_quantity_complete": task.work_quantity_complete,
                                "target_uom": task.target_uom,
                                "target_quantity": task.target_quantity,
                                "target_quantity_complete": task.target_quantity_complete,
				"task_id": task.name,
                                "grp_exp_start_date": task.grp_exp_start_date,
                                "grp_exp_end_date": task.grp_exp_end_date,
                                "grp_work_quantity": task.grp_work_quantity,
                                "grp_work_quantity_complete": task.grp_work_quantity_complete
			})			

	def get_activity_tasks(self):
		return frappe.get_all("Task", "*", {"project": self.name, "additional_task": 0}, order_by="task_idx, exp_start_date")

	def get_additional_tasks(self):
		return frappe.get_all("Task", "*", {"project": self.name, "additional_task": 1}, order_by="task_idx, exp_start_date")	

	def get_project_advance(self):
                return frappe.get_all("Project Advance", "*", {"project": self.name, "docstatus": 1}, order_by="advance_date")

	def get_project_boq(self):
                return frappe.get_all("BOQ", "*", {"project": self.name, "docstatus": 1}, order_by="boq_date")

	def get_project_invoice(self):
                return frappe.get_all("Project Invoice", "*", {"project": self.name, "docstatus": 1}, order_by="invoice_date")        
        
        # +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++
			
	def get_tasks(self):
		return frappe.get_all("Task", "*", {"project": self.name}, order_by="exp_start_date asc")

	def validate_dates(self):
		if self.expected_start_date and self.expected_end_date:
			if getdate(self.expected_end_date) < getdate(self.expected_start_date):
				frappe.throw(_("Expected End Date can not be less than Expected Start Date"))
				
		# ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
		# Following code added by SHIV on 20/09/2017
                for task in self.activity_tasks:
                        prev_start_date = getdate(frappe.db.get_value("Task", task.task_id, "exp_start_date"))
                        prev_end_date = getdate(frappe.db.get_value("Task", task.task_id, "exp_end_date"))

                        if (prev_start_date and getdate(task.start_date)) and (getdate(task.start_date) != prev_start_date):
                                msg = ""
                                ts_list = frappe.db.sql("""
                                                select name
                                                from `tabTimesheet`
                                                where project = "{0}"
                                                and task = '{1}'
                                                and docstatus < 2
                                        """.format(self.name, task.task_id), as_dict=1)

                                if len(ts_list):
                                        for item in ts_list:
                                                msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
                                        
                                        frappe.throw("Row# {0} : Cannot change `Start Date` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))

                        if (prev_end_date and getdate(task.end_date)) and (getdate(task.end_date) != prev_end_date):
                                msg = ""
                                ts_list = frappe.db.sql("""
                                                select name
                                                from `tabTimesheet`
                                                where project = "{0}"
                                                and task = '{1}'
                                                and docstatus < 2
                                        """.format(self.name, task.task_id), as_dict=1)

                                if len(ts_list):
                                        for item in ts_list:
                                                msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
                                        
                                        frappe.throw("Row# {0} : Cannot change `End Date` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))

                for task in self.additional_tasks:
                        prev_start_date = getdate(frappe.db.get_value("Task", task.task_id, "exp_start_date"))
                        prev_end_date = getdate(frappe.db.get_value("Task", task.task_id, "exp_end_date"))

                        if (prev_start_date and getdate(task.start_date)) and (getdate(task.start_date) != prev_start_date):
                                msg = ""
                                ts_list = frappe.db.sql("""
                                                select name
                                                from `tabTimesheet`
                                                where project = "{0}"
                                                and task = '{1}'
                                                and docstatus < 2
                                        """.format(self.name, task.task_id), as_dict=1)

                                if len(ts_list):
                                        for item in ts_list:
                                                msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
                                        
                                        frappe.throw("Row# {0} : Cannot change `Start Date` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))

                        if (prev_end_date and getdate(task.end_date)) and (getdate(task.end_date) != prev_end_date):
                                msg = ""
                                ts_list = frappe.db.sql("""
                                                select name
                                                from `tabTimesheet`
                                                where project = "{0}"
                                                and task = '{1}'
                                                and docstatus < 2
                                        """.format(self.name, task.task_id), as_dict=1)

                                if len(ts_list):
                                        for item in ts_list:
                                                msg += 'Reference: <a href="#Form/Timesheet/{0}">{0}</a><br/>'.format(item.name,item.name)
                                        
                                        frappe.throw("Row# {0} : Cannot change `End Date` for Tasks already having active Timesheets. <br/>{1}".format(task.idx, msg))                                        
                                        
                # +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++

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
		
        # ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
        # Following function is created
	def sync_activity_tasks(self):
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
                                "work_quantity_complete": t.work_quantity_complete,
                                "target_uom": t.target_uom,
                                "target_quantity": t.target_quantity,
				"status": t.status,
				"exp_start_date": t.start_date,
				"exp_end_date": t.end_date,
				"description": t.description,
                                "target_quantity_complete": t.target_quantity_complete,
                                "task_idx": task_idx,
                                "grp_exp_start_date": t.grp_exp_start_date,
                                "grp_exp_end_date": t.grp_exp_end_date,
                                "grp_work_quantity": t.grp_work_quantity,
                                "grp_work_quantity_complete": t.grp_work_quantity_complete,
                                "additional_task": 0
			})

			task.flags.ignore_links = True
			task.flags.from_project = True
			task.flags.ignore_feed = True
			task.save(ignore_permissions = True)
			task_names.append(task.name)

		# delete
		for t in frappe.get_all("Task", ["name"], {"project": self.name, "name": ("not in", task_names), "additional_task": 0}):
			frappe.delete_doc("Task", t.name)

		self.update_percent_complete()
		self.update_costing()

	def sync_additional_tasks(self):
		"""sync tasks and remove table"""
		if self.flags.dont_sync_tasks: return

		task_names = []
		task_idx = 0
		for t in self.additional_tasks:
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
                                "work_quantity_complete": t.work_quantity_complete,
                                "target_uom": t.target_uom,
                                "target_quantity": t.target_quantity,
				"status": t.status,
				"exp_start_date": t.start_date,
				"exp_end_date": t.end_date,
				"description": t.description,
                                "target_quantity_complete": t.target_quantity_complete,
                                "task_idx": task_idx,
                                "grp_exp_start_date": t.grp_exp_start_date,
                                "grp_exp_end_date": t.grp_exp_end_date,
                                "grp_work_quantity": t.grp_work_quantity,
                                "grp_work_quantity_complete": t.grp_work_quantity_complete,
                                "additional_task": 1
			})

			task.flags.ignore_links = True
			task.flags.from_project = True
			task.flags.ignore_feed = True
			task.save(ignore_permissions = True)
			task_names.append(task.name)

		# delete
		for t in frappe.get_all("Task", ["name"], {"project": self.name, "name": ("not in", task_names), "additional_task": 1}):
			frappe.delete_doc("Task", t.name)

		self.update_percent_complete()
		self.update_costing()		
        # +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++
		
	def update_project(self):
		#self.update_percent_complete()
                self.update_project_progress()
		self.update_costing()
		self.flags.dont_sync_tasks = True
		self.save(ignore_permissions = True)

	def update_percent_complete(self):
                # ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
                # Following code commented by SHIV on 2017/08/16
                '''
		total = frappe.db.sql("""select count(*) from tabTask where project=%s""", self.name)[0][0]
		if total:
			completed = frappe.db.sql("""select count(*) from tabTask where
				project=%s and status in ('Closed', 'Cancelled')""", self.name)[0][0]

			self.percent_complete = flt(flt(completed) / total * 100, 2)
                '''
                pass
                        
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

		self.total_costing_amount = flt(from_time_sheet.costing_amount)
		self.total_billing_amount = flt(from_time_sheet.billing_amount)
		self.actual_time = flt(from_time_sheet.time)

		self.total_expense_claim = flt(from_expense_claim.total_sanctioned_amount)

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

# ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
# Following method is created by SHIV on 02/09/2017
@frappe.whitelist()
def make_project_advance(source_name, target_doc=None):
        def update_master(source_doc, target_doc, source_partent):
                target_doc.customer = source_doc.customer
        
        doclist = get_mapped_doc("Project", source_name, {
                "Project": {
                                "doctype": "Project Advance",
                                "field_map":{
                                        "name": "project",
                                        "customer": "customer"
                                },
                                "postprocess": update_master
                        }
        }, target_doc)
        return doclist
# +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++
