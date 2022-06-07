from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Finance & Accounts"),
			"items": [
				#{
				#	"type": "report",
				#	"name": "Statement of Trial Balance",
				#	"doctype": "GL Entry",
				#	"is_query_report": True,
				#},
				#{
				#	"type": "report",
				#	"name": "Statement of Financial Position",
				#	"doctype": "GL Entry",
				#	"is_query_report": True
				#},
				#{
				#	"type": "report",
				#	"name": "Statement of Cash Flow",
				#	"doctype": "GL Entry",
				#	"is_query_report": True
				#},
				#{
				#	"type": "report",
				#	"name": "Statement of Comprehensive Income",
				#	"doctype": "GL Entry",
				#	"is_query_report": True
				#},
				#{
				#	"type": "report",
				#	"name": "Comparative Statement",
				#	"doctype": "GL Entry",
				#	"is_query_report": True,
				#},
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
				#  {
                                #        "type": "report",
                                #        "name": "Budget Consumption Report",
                                #        "is_query_report": True,
                                #        "doctype": "GL Entry"
                                #}
				{
                                        "type": "page",
                                        "name": "accounts-management",
                                        "label": "Accounts Management"
                                }
			]
		},
		{
			"label": _("Project(Physical Progress)"),
			"icon": "icon-list",
			"items": [
                 {
                                        "type": "page",
                                        "name": "design-management",
                                        "label": "Design Management"
                                },
				{
                                        "type": "page",
                                        "name": "project-management",
                                        "label": "Project Management"
                                },
				# {
                #                         "type": "page",
                #                         "name": "design-management",
                #                         "label": "Design Management"
                #                 },
								{
                                        "type": "page",
                                        "name": "dessung-project",
                                        "label": "Priority Progress"
                                },
								# 	{
                                #         "type": "page",
                                #         "name": "target",
                                #         "label": "target test"
                                # },
			]
		},
		{
			"label": _("Mechanical Services"),
			"icon": "icon-list",
			"items": [
                                #{
				#	"type": "report",
				#	"is_query_report": True,
				#	"name": "Equipment Expense Report",
				#	"doctype": "Equipment"
				#},
				{
                                        "type": "page",
                                        "name": "mechanical-services",
                                        "label": "Mechanical Services Management"
                                },
			]
		},
		{
			"label": _("Material Management"),
			"icon": "icon-list",
			"items": [
                                #{
				#	"type": "report",
				#	"is_query_report": True,
				#	"name": "Purchase History Report",
				#	"doctype": "Purchase Invoice"
				#},
				#{
				#	"type": "page",
				#	"name": "purchase-analytics",
				#	"label": "Purchase Analytics"
				#},
				#{
                                #        "type": "report",
                                #        "is_query_report": True,
                                #        "name": "MR Status Report",
                                #        "doctype": "Buying"
                                #},
				{
                                        "type": "page",
                                        "name": "material-management",
                                        "label": "Material Management"
                                },

			]
		},
		{
			"label": _ ("Human Resource"),
			"icon": "icon-list",
			"items": [
				#{	
				#	"type": "report",
				#	"is_query_report": False,
				#	"name": "Employee Information",
				#	"doctype": "Employee"
				#},
				{
                                        "type": "page",
                                        "name": "human-resource",
                                        "label": "Human Resource Management"
                                }
			]	
		},
		 {
                        "label": _("Asset Management"),
                        "icon": "icon-list",
                        "items": [
                                #{
                                #        "type":"report",
                                #        "is_query_report": True,
                                #        "name": "Asset Register",
                                #        "doctype": "Asset"
                                #},
                                #{
                                #        "type": "report",
                                #        "is_query_report": True,
                                #        "name": "Equipment Register",
                                #        "doctype": "Asset"
                                #},
                                #{
                                #        "type": "report",
                                #        "is_query_report": True,
                                #        "name": "Employee Asset Report",
                                #        "doctype": "Asset"
                                #},
                                #{
                                #        "type": "report",
                                #        "is_query_report": True,
                                #        "name": "Others' Asset Report",
                                #        "doctype":"Asset Others"
                                #},
				{
                                        "type": "page",
                                        "name": "asset-management",
                                        "label": "Asset Management"
                                }
				#{
				#	"type": "report",
				#	"is_query_report": True,
				#	"name": "Asset Balance Report",
				#	"doctype": "Asset Received Entries"
				#}

                        ]
                },

	]


