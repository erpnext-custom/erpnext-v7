from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Accounting Statements"),
			"items": [
				{
					"type": "report",
					"name": "Statement of Trial Balance",
					"doctype": "GL Entry",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Statement of Financial Position",
					"doctype": "GL Entry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Statement of Cash Flow",
					"doctype": "GL Entry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Statement of Comprehensive Income",
					"doctype": "GL Entry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Comparative Statement",
					"doctype": "GL Entry",
					"is_query_report": True,
				},
                                {
					"type": "report",
					"name": "Profitability Analysis",
					"doctype": "GL Entry",
					"is_query_report": True,
				},
				{
                                        "type": "report",
                                        "label": _("Revenue Target & Achievement Report"),
                                        "is_query_report": True,
                                        "name": "Revenue Target",
                                        "doctype": "Revenue Target",
                                },
			]
		},
		{
			"label": _("Project"),
			"icon": "icon-list",
			"items": [
                                {
					"type": "report",
					"is_query_report": True,
					"name": "Project Register",
					"doctype": "Project"
				},
			]
		},
		{
			"label": _("Mechanical Services"),
			"icon": "icon-list",
			"items": [
                                {
					"type": "report",
					"is_query_report": True,
					"name": "Equipment Performance Report",
					"doctype": "Equipment"
				},
                                {
					"type": "report",
					"is_query_report": True,
					"name": "Workshop Progress Report",
					"doctype": "Job Card"
				},
			]
		},
		{
			"label": _("Sales"),
			"icon": "icon-list",
			"items": [
                                {
					"type": "report",
					"is_query_report": True,
					"name": "Sales History Report",
					"doctype": "Sales Invoice"
				},
				{
					"type": "page",
					"name": "sales-analytics",
					"label": "Sales Analytics"
				},
			]
		},
		{
			"label": _("Procurement"),
			"icon": "icon-list",
			"items": [
                                {
					"type": "report",
					"is_query_report": True,
					"name": "Purchase History Report",
					"doctype": "Purchase Invoice"
				},
				{
					"type": "page",
					"name": "purchase-analytics",
					"label": "Purchase Analytics"
				},
			]
		},
		{
			"label": _("Stock/Inventory"),
			"icon": "icon-list",
			"items": [
				{
					"type": "page",
					"name": "stock-analytics",
					"label": "Stock Analytics"
				},
			]
		}
	]


