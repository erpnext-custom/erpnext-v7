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
				}
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
					"name": "Equipment Performance Report",
					"doctype": "Equipment"
				},
                                {
					"type": "report",
					"is_query_report": True,
					"name": "Workshop Progress Report",
					"doctype": "Job Card"
				},
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
				{
					"type": "page",
					"name": "stock-analytics",
					"label": "Stock Analytics"
				},
			]
		}
	]


