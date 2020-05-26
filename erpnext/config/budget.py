from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Budget"),
			"items": [
				{
					"type": "doctype",
					"name": "Budget",
					"description": _("Define budget for a financial year.")
				},
#				{
#					"type": "doctype",
#					"name": "Revenue Target",
#				},
			]
		},
                {
			"label": _("Tools"),
			"items": [
				{
					"type": "doctype",
					"name": "Supplementary Budget",
					"description": "Supplementary Budget",
					"hide_count": True
				},
				{
					"type": "doctype",
					"name": "Budget Reappropiation",
					"label": "Budget Reappropiation Tool"
				},
			]
		},
                {
			"label": _("Reports"),
			"items": [
				{
					"type": "report",
					"name": "Budget Consumption Report",
					"is_query_report": True,
					"doctype": "GL Entry"
				},
				{
                    "type": "report",
                    "name": "Budget Consumption Breakdown Report",
                    "is_query_report": True,
                    "doctype": "Consumed Budget"
                },
				{
					"type": "report",
					"is_query_report": True,
					"name": "Supplementary Budget Report",
					"doctype": "Supplementary Details"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Budget Reappropriation Report",
					"doctype": "Reappropriation Details"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Committed Budget Report",
					"doctype": "Committed Budget"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Budget Proposal",
					"doctype": "Budget"
				}
				#{
				#	"type": "report",
				#	"label": _("Revenue Achievement"),
				#	"is_query_report": True,
				#	"name": "Revenue Target",
				#	"doctype": "Revenue Target",
				#},
				#{
				#	"type": "report",
				#	"is_query_report": True,
				#	"name": "Revenue Target Proposal",
				#	"doctype": "Revenue Target"
				#},
			]
		},
	]
