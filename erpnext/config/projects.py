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
					"type": "report",
					"route": "Gantt/Task",
					"doctype": "Task",
					"name": "Gantt Chart",
					"description": _("Gantt chart of all tasks.")
				},
			]
		},
		{
			"label": _("Manpower Management"),
			"icon": "icon-facetime-video",
			"items": [
				{
					"type": "doctype",
					"name": "Muster Roll Employee",
					"description": _("Muster Roll Employee Data"),
				},
				{
					"type": "doctype",
					"name": "Attendance Tool Others",
					"label": "Attendance Tool for GEP & MR",
					"description": _("Attendance Tool for Others"),
				},
				{
					"type": "doctype",
					"name": "Project Overtime Tool",
					"label": "Overtime Tool for GEP & MR",
					"description": _("Overtime Tool for MR and GEP"),
				},
				{
					"type": "doctype",
					"name": "Process MR Payment",
					"label": "Process Payment for GEP & MR",
					"description": _("Process Payments for Project Muster Roll"),
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
					"label": "Attendance Register for GEP & MR",
					"description": _("Attendance Sheet"),
					"doctype": "Attendance Others"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Overtime Register",
					"label": "Overtime Register for GEP & MR",
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
			]
		},
		{
			"label": _("Reports"),
			"icon": "icon-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Project wise Stock Tracking",
					"doctype": "Project"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Items Register",
					"doctype": "Consumable Register Entry"
				},
			]
		},
	]
