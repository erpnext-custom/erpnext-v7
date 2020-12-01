from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Projects"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Project",
					"description": _("Project master."),
				},
				{
					"type": "doctype",
					"name": "Task",
					"description": _("Project activity / task."),
				},
                                {
					"type": "doctype",
					"name": "Timesheet",
					"description": _("Timesheet for all tasks."),
				},
                                 {
				 	"type": "doctype",
				 	"name": "BOQ",
				 	"description": _("Bill of Quantities."),
				 },
                                {
					"type": "doctype",
				 	"name": "BOQ Adjustment",
				 	"description": _("Adjustments for Bill of Quantities."),
				 },
                                 {
				 	"type": "doctype",
				 	"name": "MB Entry",
                                         "label": "Measurement Book Entries",
				 	"description": _("Measurement Book Entries."),
				 },
				{
					"type": "report",
					"route": "Gantt/Task",
					"doctype": "Task",
					"name": "Gantt Chart",
					"description": _("Gantt chart of all tasks.")
				},
			]
		},
                {
                        "label": _("Transactions"),
                        "icon": "icon-pencil",
                        "items": [
                                # {
                                #         "type": "doctype",
                                #         "name": "Project Advance",
                                #         "description": _("Project Advances."),
                                # },
                                # {
                                #         "type": "doctype",
                                #         "name": "Project Invoice",
                                #         "description": _("Project Invoices."),
                                # },
                                # {
                                #         "type": "doctype",
                                #         "name": "Project Payment",
                                #         "description": _("Project Payments."),
                                # },
                        ]
                },
		{
                        "label": _("Muster Roll Employee/Operator/Open Air Prisoner"),
                        "icon": "icon-facetime-video",
                        "items": [
                                {
                                        "type": "doctype",
                                        "name": "Muster Roll Employee",
                                        "description": _("Muster Roll Employee Data"),
                                },
                                {
                                        "type": "doctype",
                                        "name": "Operator",
                                        "label": "Operator List",
                                        "description": _("Master Data of Operators"),
                                },
                                {
                                        "type": "doctype",
                                        "name": "Open Air Prisoner",
                                        "label": "OAP List",
                                        "description": _("Open Air Prisoner"),
                                },

				{
					"type": "doctype",
					"name": "MusterRoll Application",
					"label": "Muster Roll Application",
				},
				{
					"type": "doctype",
					"name": "Attendance Tool Others",
					"label": "Attendance Tool",
					"description": _("Attendance Tool for Others"),
				},
				#{
				#	"type": "doctype",
				#	"name": "Upload Attendance Others",
				#	"label": "Upload Bulk Attendance for Muster Roll",
				#	"description": _("Attendance Tool for Others"),
				#},
				{
					"type": "doctype",
					"name": "Project Overtime Tool",
					"label": "Overtime Tool",
					"description": _("Overtime Tool"),
				},
				#{
				#	"type": "doctype",
				#	"name": "Upload Overtime Entries",
				#	"label": "Upload Overtime Entry for Muster Roll",
				#	"description": _("Overtime Tool for Others"),
				#},
				{
					"type": "doctype",
					"name": "Process MR Payment",
					"label": "Process Payment",
					"description": _("Process Payments"),
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Attendance Register",
					"label": "Attendance Register",
					"description": _("Attendance Sheet"),
					"doctype": "Attendance Others"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Overtime Register",
					"label": "Overtime Register",
					"description": _("Overtime Register"),
					"doctype": "Overtime Entry"
				},
				{
                                        "type": "doctype",
                                        "name": "Project Muster Roll Tool",
                                        "label": "Project Muster Roll Tool",
                                        "description": _("MR Transfer tool"),
                                },
			]
		},
		{
			"label": _("Project Tools"),
			"icon": "icon-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Attendance Register",
					"label": "Attendance Register for MR",
					"description": _("Attendance Sheet"),
					"doctype": "Attendance Others"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Overtime Register",
					"label": "Overtime Register for MR",
					"description": _("Overtime Register"),
					"doctype": "Overtime Entry"
				},
				{
					"type": "doctype",
					"name": "Project Sales",
					"label": "Project Sales",
					"description": _("Process Sales of Project Items"),
				},
				{
					"type": "doctype",
					"name": "Project Muster Roll Tool",
					"label": "Assign Muster Roll To Projects",
					"description": _("Project Muster Roll Tool"),
				},
				{
					"type": "doctype",
					"name": "MusterRoll Application",
					"label": "Muster Roll Application",
				},
			]
		},
		{
			"label": _("Reports"),
			"icon": "icon-list",
			"items": [
                                {
					"type": "report",
					"is_query_report": True,
					"name": "Project Register",
					"doctype": "Project"
				},
                                {
					"type": "report",
					"is_query_report": True,
					"name": "Project Work Plan",
					"doctype": "Project"
				},
                                {
					"type": "report",
					"is_query_report": True,
					"name": "Project Manpower",
					"doctype": "Project"
				},
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Project Equipment",
                                        "doctype": "Project"
                                },
                                 {
				 	"type": "report",
				 	"is_query_report": True,
				 	"name": "BOQ Register",
				 	"doctype": "BOQ"
				 },
                                 {
				 	"type": "report",
				 	"is_query_report": True,
				 	"name": "Measurement Book Register",
				 	"doctype": "MB Entry"
				 },
                                 {
				 	"type": "report",
				 	"is_query_report": True,
				 	"name": "Advance Payment Register",
				 	"doctype": "Project Advance"
				 },
                #                 {
				# 	"type": "report",
				# 	"is_query_report": True,
				# 	"name": "Invoice Register",
				# 	"doctype": "Project Invoice"
				# },
                #                 {
				# 	"type": "report",
				# 	"is_query_report": True,
				# 	"name": "Payment Register",
				# 	"doctype": "Project Payment"
				# },
				{
					"type": "report",
					"is_query_report": True,
					"name": "Project wise Stock Tracking",
					"doctype": "Project"
				},
				# {
				# 	"type": "report",
				# 	"is_query_report": True,
				# 	"name": "Items Register",
				# 	"doctype": "Consumable Register Entry"
				# },
			]
		},
	]
