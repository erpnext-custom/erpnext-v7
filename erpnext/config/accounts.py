from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Accounts"),
			"items": [
				{
					"type": "doctype",
					"name": "Journal Entry",
					"description": _("Accounting journal entries.")
				},
				{
					"type": "doctype",
					"name": "Payment Entry",
					"description": _("Bank/Cash transactions against party or for internal transfer")
				},
				{
					"type": "doctype",
					"name": "Sales Invoice",
					"description": _("Bills raised to Customers.")
				},
				{
					"type": "doctype",
					"name": "Purchase Invoice",
					"description": _("Bills raised by Suppliers.")
				},
				{
					"type": "doctype",
					"name": "Direct Payment",
					"description": _("Direct Payment")
				},
				{
					"type": "doctype",
					"name": "Period Closing Voucher",
					"description": _("Close Balance Sheet and book Profit or Loss.")
				},
				{
					"type": "doctype",
					"name": "Transporter Payment",
				},
				{
					"type": "doctype",
					"name": "TDS Remittance",
					"description": _("TDS Remittance")
				},
				{
					"type": "doctype",
					"name": "Overtime Payment",
					"description": _("Employee Overtime Payment")
				},
				{
					"type": "doctype",
					"name": "EME Payment",
					"description": _("EME Payment")
				},
			]
		},
		{
			"label": _("Company"),
			"items": [
				{
					"type": "doctype",
					"name": "Company",
					"description": _("Company (not Customer or Supplier) master.")
				},
				{
					"type": "doctype",
					"name": "Account",
					"icon": "icon-sitemap",
					"label": _("Chart of Accounts"),
					"route": "Tree/Account",
					"description": _("Tree of financial accounts."),
				},
				{
					"type": "doctype",
					"name": "Customer",
                                        "label": _("Customer Master"),
					"description": _("Customer database.")
				},
				{
					"type": "doctype",
					"name": "Supplier",
                                        "label": _("Supplier Master"),
					"description": _("Supplier database.")
				},
				{
					"type": "doctype",
					"name": "Vehicle",
                                        "label": _("Vehicle Master"),
				},
				{
					"type": "doctype",	
					"name": "Financial Institution",
					"label": _("Financial Institution"),			
				},
				{
                                        "type": "doctype",
                                        "name": "COP",
					"label": "Cost Distribution", 
                                        "description": _("Cop Cost Percent")
                                },
				{	
                                        "type": "doctype",
                                        "name": "Activity",
					"label": "Activity",
                                        "description": _("List of Activities")
                                }
			]
		},
		{
			"label": _("Asset Management"),
			"items": [
				{
					"type": "doctype",
					"name": "Asset",
				},
				{
					"type": "doctype",
					"name": "Asset Modifier Tool",
					"description": "Asset Addition Tool",
					"label": "Asset Addition Tool",
					"hide_count": True
				},
				{
					"type": "doctype",
					"name": "Asset Category",
				},
				#{
				#	"type": "report",
				#	"name": "Asset Depreciation Ledger",
				#	"doctype": "Asset",
				#	"is_query_report": True,
				#},
				{
					"type": "report",
					"name": "Asset Depreciations and Balances",
					"doctype": "Asset",
					"is_query_report": True,
				},
				{
					"type": "doctype",
					"name": "Asset Movement",
					"description": _("Transfer an asset from one warehouse to another")
				},
				{
					"type": "report",
					"name": "Asset Register",
					"doctype": "Asset",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Property Plant and Equipment",
					"doctype": "GL Entry",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Employee Asset Report",
					"doctype": "Asset",
					"is_query_report": True,
				},
			]
		},
		{
			"label": _("Taxes and Registers"),
			"items": [
				{
					"type": "report",
					"name": "Sales Register",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Purchase Register",
					"doctype": "Purchase Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Cheque Register",
					"doctype": "Journal Entry",
					"is_query_report": True
				},
				{
					"type": "doctype",
					"name": "Cheque Lot",
					"label": "Create Cheque Lot",
					"description": "Creation of Cheque Lot",
					"hide_count": True
				},
				{
					"type": "report",
					"name": "TDS Certificate",
					"label": "Generate TDS Certificate",
					"doctype": "Purchase Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "TDS Challen",
					"label": "Generate TDS Challan",
					"doctype": "Purchase Invoice",
					"is_query_report": True
				},
				{
					"type": "doctype",
					"name": "RRCO Receipt Tool",
					"description": "Enter RRCO Receipts in Bulk",
					"hide_count": True
				}
			]
		},
                {
                        "label": _("Imprest Management"),
                        "icon": "icon-cog",
                        "items": [
                                {
                                        "type": "doctype",
                                        "name": "Imprest Type",
                                        "description": _("Imprest Types.")
                                },
                                {
                                        "type": "doctype",
                                        "name": "Imprest Receipt",
                                        "label": "Receipt Entry",
                                        "description": _("Imprest Receipt Entry.")
                                },
                                {
                                        "type": "doctype",
                                        "name": "Imprest Recoup",
                                        "label": "Recoup Entry",
                                        "description": _("Imprest Recoup Entry.")
                                },
                                {
                                        "type": "report",
                                        "label": _("Imprest Register"),
                                        "is_query_report": True,
                                        "name": "Register Imprest",
                                        "doctype": "Imprest Receipt"
                                },
                        ]
                },
		  {
                        "label": _("Tools"),
                        "items": [
                                {
                                        "type": "doctype",
                                        "name": "Salary Remittance",
                                },
                                {
                                        "type": "doctype",
                                        "name": "Fixed Deposit",
                                },
				{
					"type": "doctype",
					"name": "RRCO Receipt Modifier",
				},
                        ]
                },
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
					"name": "Statement of Changes in Equity",
					"doctype": "GL Entry",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Comparative Statement",
					"doctype": "GL Entry",
					"is_query_report": True,
				}
			]
		},
		{
			"label": _("General Reports"),
			"items": [
				{
					"type": "report",
					"name":"General Ledger",
					"doctype": "GL Entry",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Accounts Receivable",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Accounts Payable",
					"doctype": "Purchase Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Party Wise Ledger",
					"doctype": "GL Entry",
					"is_query_report": True,
				},
				{
                                        "type": "report",
                                        "name": "Direct Payment Report",
                                        "doctype": "Direct Payment",
                                        "is_query_report": True,
                                },
				{
					 "type": "report",
					 "name": "Transporter Payment Report",
					 "doctype": "Transporter Payment",
					 "is_query_report": True,														      }
			]
		},
		{
			"label": _("Banking and Payments"),
			"items": [
                		{
					"type": "doctype",
					"name": "Upload BRS Entries",
                    			"label": _("Upload BRS Data"),
					"description": _("Upload bank payment dates.")
				},
                		{
					"type": "doctype",
					"name": "Bank Reconciliation",
                    			"label": _("Update Bank Transaction Dates"),
					"description": _("Update bank payment dates with journals.")
				},
                		{
					"type": "report",
					"name": "Bank Reconciliation Statement",
                			"is_query_report": True,
					"doctype": "Journal Entry"
				},
                		{
					"type": "report",
					"name": "Bank Clearance Summary",
                    			"is_query_report": True,
					"doctype": "Journal Entry"
				},
			]
		},
		{
			"label": _("Budget and Cost Center"),
			"items": [
				{
					"type": "doctype",
					"name": "Cost Center",
					"icon": "icon-sitemap",
					"label": _("Chart of Cost Centers"),
					"route": "Tree/Cost Center",
					"description": _("Tree of financial Cost Centers."),
				},
				{
					"type": "doctype",
					"name": "Budget",
					"description": _("Define budget for a financial year.")
				},
				{
                                        "type": "doctype",
                                        "name": "Revenue Target",
                                },
				{
					"type": "report",
					"name": "Budget Consumption Report",
					"is_query_report": True,
					"doctype": "GL Entry"
				},
				{
					"type": "doctype",
					"name": "Supplementary Budget",
					"description": "Supplementary Budget",
					"hide_count": True
				},
				{
					"type": "doctype",
					"name": "Budget Reappropiation",
					"description": "Budget Reappropriation",
					"hide_count": True
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
                                        "label": _("Revenue Achievement"),
                                        "is_query_report": True,
                                        "name": "Revenue Target",
                                        "doctype": "Revenue Target",
                                },
				{
					"type": "report",
					"is_query_report": True,
					"name": "Committed Budget Report",
					"doctype": "Committed Budget"
				}
			]
		},
		{
                        "label": _("Account Setup"),
                        "icon": "icon-cog",
                        "items": [
                                {
                                        "type": "doctype",
                                        "name": "Accounts Settings",
                                        "description": _("Default settings for accounting transactions.")
                                },
                                {
                                        "type": "doctype",
                                        "name": "HR Accounts Settings",
                                        "description": _("HR Account Settings")
                                },
                                {
                                        "type": "doctype",
                                        "name": "Production Account Settings",
                                        "description": _("Account setting for production module")
                                },
                        ]
                },

		{
			"label": _("Setup"),
			"icon": "icon-cog",
			"items": [
				{
					"type": "doctype",
					"name": "Accounts Settings",
					"description": _("Default settings for accounting transactions.")
				},
				{
					"type": "doctype",
					"name": "Fiscal Year",
					"description": _("Financial / accounting year.")
				},
				{
					"type": "doctype",
					"name": "Currency",
					"description": _("Enable / disable currencies.")
				},
				{
					"type": "doctype",
					"name": "Currency Exchange",
					"description": _("Currency exchange rate master.")
				},
				{
					"type": "doctype",
					"name":"Mode of Payment",
					"description": _("e.g. Bank, Cash, Credit Card")
				},
			]
		},
		{
			"label": _("Analytics"),
			"items": [
				{
					"type": "report",
					"name": "Gross Profit",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Purchase Invoice Trends",
					"is_query_report": True,
					"doctype": "Purchase Invoice"
				},
				{
					"type": "report",
					"name": "Sales Invoice Trends",
					"is_query_report": True,
					"doctype": "Sales Invoice"
				},
				{
                                        "type": "report",
                                        "name": "COP Computation Report",
					"label": _("COP Details"),
                                        "is_query_report": True,
                                        "doctype": "Account"
                                },
				{
                                        "type": "report",
                                        "name": "COP",
					"label": _("Final COP"),
                                        "is_query_report": True,
                                        "doctype": "Account"
                                }
			]
		},
		{
			"label": _("ePayment"),
			# "icon": "icon-table",
			"items": [
       			{
					"type": "doctype",
					"name": "Bank Payment Settings",
					"label": _("Bank Payment Settings"),
					# "hide_count": True
				},
				{
					"type": "doctype",
					"name": "Bank Payment",
					"label": _("Bank Payment"),
					# "hide_count": True
				},
    {
					"type": "doctype",
					"name": "Utility Bill",
					"label": _("Utility Bill Payment"),
				},
				{
					"type": "doctype",
					"name": "Utility Services",
					"label": _("Utility Services"),
				},
				{
					"type": "doctype",
					"name": "Utility Service Type",
					"label": _("Utility Service Type"),
				},
				{
					"type": "doctype",
					"name": "API Detail",
					"label": _("API Detail"),
				},
				{
					"type": "report",
					"name": "e-Payment Report",
					"is_query_report": True,
					"doctype": "Bank Payment"
				},
			]
		},
		{
			"label": _("Other Reports"),
			"icon": "icon-table",
			"items": [
				{
					"type": "report",
					"name": "Payment Period Based On Invoice Date",
					"is_query_report": True,
					"doctype": "Journal Entry"
				},
				{
					"type": "report",
					"name": "Sales Partners Commission",
					"is_query_report": True,
					"doctype": "Sales Invoice"
				},
				{
					"type": "report",
					"name": "Item-wise Sales Register",
					"is_query_report": True,
					"doctype": "Sales Invoice",
					"label":"Materialwise Sales Register"
				},
				{
					"type": "report",
					"name": "Item-wise Purchase Register",
					"is_query_report": True,
					"doctype": "Purchase Invoice",
					"label":"Materialwise Purchase Register"
				},
				{
					"type": "report",
					"name": "Accounts Receivable Summary",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Accounts Payable Summary",
					"doctype": "Purchase Invoice",
					"is_query_report": True
				},
				{
                                        "type": "report",
                                        "name": "Fixed Deposit Report",
                                        "doctype": "Fixed Deposit",
                                        "is_query_report": True
                                },
				{
					"type": "report",
					"is_query_report": True,
					"name": "Customer Credit Balance",
					"doctype": "Customer"
				},
				{
				    	"type": "report",
					"is_query_report": True,
					"name": "Overtime Report",
					"doctype": "Overtime Application"
				}

			]
		},
		{
			"label": _("DHI Consolidation"),
			# "icon": "icon-table",
			"items": [
       			{
					"type": "doctype",
					"name": "DHI Setting",
					"label": _("DHI Setting"),
					# "hide_count": True
				},
				{
					"type": "doctype",
					"name": "DHI GCOA",
					"label": _("Group Chart Of Account"),
					# "hide_count": True
				},
				{
					"type": "doctype",
					"name": "DHI Company",
					"label": "DHI Owned Company",
					# "hide_count": True
				},
				{
					"type": "doctype",
					"name": "Consolidation Transaction",
					"label": _("Consolidation Transaction"),
					"hide_count": True
				},
				{
					"type": "doctype",
					"name": "DHI GCOA Mapper",
					"label": "GCOA Mapper To COA",
					# "hide_count": True
				},
				
			]
		},
		{
			"label":_("Consolidation Report"),
			"items":[
				{
					"type": "report",
					"name": "Consolidation Report",
					"doctype": "DHI GCOA Mapper",
					"is_query_report": True
				},
    			{
					"type": "report",
					"name": "DHI GCOA Mapper Report",
					"doctype": "DHI GCOA Mapper",
					"is_query_report": True
				},
       			{
					"type": "report",
					"name": "GCOA Wise Report",
					"doctype": "DHI GCOA Mapper",
					"is_query_report": True
				}
			]
		}
	]
