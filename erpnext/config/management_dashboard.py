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
                                #{
				#	"type": "report",
				#	"name": "Profitability Analysis",
				#	"doctype": "GL Entry",
				#	"is_query_report": True,
				#},
				#{
                                #        "type": "report",
                                #        "label": _("Revenue Target & Achievement Report"),
                                #        "is_query_report": True,
                                #        "name": "Revenue Target",
                                #        "doctype": "Revenue Target",
                                #},
				  {
                                        "type": "report",
                                        "name": "Budget Consumption Report",
                                        "is_query_report": True,
                                        "doctype": "GL Entry"
                                }
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
					"name": "Equipment Expense Report",
					"doctype": "Equipment"
				}
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
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "MR Status Report",
                                        "doctype": "Buying"
                                }
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
				{
					"type":"report",
					"is_query_report": True,
					"name": "Stock Ledger Report",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Stock Balance Report",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Stock Ageing Report",
					"doctype": "Item"
				},
				{	
					"type": "report",
					"is_query_report": True,
					"name": "Material Shortage Report",
					"doctype":"Bin"
				},
 
			]
		},
		{
			"label": _ ("Human Resource"),
			"icon": "icon-list",
			"items": [
				{	
					"type": "report",
					"is_query_report": False,
					"name": "Employee Information",
					"doctype": "Employee"
				},
			]	
		},
	]


