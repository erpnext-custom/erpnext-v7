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
			"label": _("Muster Roll Management"),
			"icon": "icon-facetime-video",
			"items": [
				{
					"type": "doctype",
					"name": "Muster Roll Employee",
					"description": _("Muster Roll Employee Data"),
				},
				{
					"type": "doctype",
					"name": "Muster Roll Attendance",
					"description": _("Muster Roll Attendance Toll"),
				},
				{
					"type": "doctype",
					"name": "MR Attendance",
					"description": _("Muster Roll Attendance"),
				},
				{
					"type": "doctype",
					"name": "Project Overtime Tool",
					"label": "Project Overtime Tool",
					"description": _("Overtime Tool for MR and GEP"),
				},
				{
					"type": "doctype",
					"name": "Project Muster Roll Tool",
					"label": "Assign Muster Roll To Projects",
					"description": _("Project Muster Roll Tool"),
				},
				{
					"type": "doctype",
					"name": "Process MR Payment",
					"description": _("Process Payments for Project Muster Roll"),
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "MR Attendance Sheet",
					"description": _("MR Attendance Sheet"),
					"doctype": "MR Attendance"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "MR Overtime Register",
					"description": _("MR Attendance Sheet"),
					"doctype": "Overtime Entry"
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
			]
		},
	]
