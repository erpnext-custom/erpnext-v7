from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Transactions"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Quotation",
					"label": "Sales Quotation",
					"description": _("Quotes to Leads or Customers."),
				},
				{
                                        "type": "doctype",
                                        "name": "Product Requisition",
                                        "label": "Product Requisition",
                                        "description": _("Customer Requisition For Products"),
                                },

				{
					"type": "doctype",
					"name": "Sales Order",
					"description": _("Confirmed orders from Customers."),
				},
				{
					"type": "doctype",
					"name": "Delivery Note",
					"description": _("Shipments to customers."),
				},
				{
					"type": "doctype",
					"name": "Sales Invoice",
					"description": _("Bills raised to Customers.")
				},
			]
		},
		{
			"label": _("Master Data"),
			"items": [
				{
					"type": "doctype",
					"name": "Customer",
					"description": _("Customer database."),
				},
				{
					"type": "doctype",
					"label": _("Customer Group"),
					"name": "Customer Group",
					"icon": "icon-sitemap",
					"link": "Tree/Customer Group",
					"description": _("Manage Customer Group Tree."),
				},
				{
					"type": "doctype",
					"name":"Terms and Conditions",
					"label": _("Sales Terms and Conditions Template"),
					"description": _("Template of terms or contract.")
				},
				{
					"type": "doctype",
					"name": "Loss Tolerance",
					"description": _("Loss Tolerance Setting"),
				}
			]
		},
		{
			"label": _("Reports"),
			"icon": "icon-list",
			"items": [
				#{
				#	"type": "report",
				#	"is_query_report": True,
				#	"name": "Material-wise Sales History",
				#	"doctype": "Item",
				#	"label": "Materialwise Sales History"
				#},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Quotation Trends",
					"label": "Sales Quotation Trends",
					"doctype": "Quotation"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Sales Order Trends",
					"doctype": "Sales Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Sales History Report",
					"doctype": "Sales Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Ordered Materials To Be Delivered",
					"doctype": "Delivery Note"
				},
				{
					"type": "report",
					"name": "Accounts Receivable",
					"label": "Invoice Receivable",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Stock Price History",
					"doctype": "Stock Price Template",
					"is_query_report": True
				},
				{
					"type": "page",
					"name": "sales-analytics",
					"label": "Sales Analytics"
				},
				{
					"type": "report",
					"name": "Advance Report",
					"doctype": "Payment Entry",
					"is_query_report": True,
				},
			]
		},
		{
			"label": _("Materials and Pricing"),
			"items": [
				{
					"type": "doctype",
					"name": "Item",
					"label": "Materials",
					"description": _("All Products or Services."),
				},
				{
					"type": "doctype",
					"name": "Item Group",
					"icon": "icon-sitemap",
					"label": _("Material Group"),
					"link": "Tree/Item Group",
					"description": _("Tree of Item Groups."),
				},
				{
					"type": "doctype",
					"name": "Item Sub Group",
					"label": _("Material Sub Group"),
					"description": _("Item Sub Groups."),
				},
				{
					"type": "doctype",
					"name": "Material Price",
					"description": _("Multiple Item prices."),
					"route": "Report/Item Price"
				},
				{
					"type" : "doctype",
					"name": "Selling Price",
					"label": _("Selling Price Settings"),
				},
			]
		},

	]
