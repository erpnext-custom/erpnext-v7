from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Selling - Transactions"),
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
				{
					"type": "doctype",
					"name": "Mines Quality Record",
					"description": _("Mines Quality Record Details")
				},
				{
					"type": "doctype",
					"name": "Consolidated Invoice",
					"description": _("Consolidated Invoices Details")
				}
			]
		},
		{
			"label": _("Selling Master"),
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
					"name": "Contact",
					"description": _("All Contacts."),
				},
				{
					"type": "doctype",
					"name": "Address",
					"description": _("All Addresses."),
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
			"label": _("Selling Reports"),
			"icon": "icon-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Mines Delivery Overview",
					"doctype": "Delivery Note"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Material-wise Sales History",
					"doctype": "Item",
					"label": "Materialwise Sales History"
				},
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
					"name": "Transportation Report",
					"doctype": "Delivery Note"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Mines Product Quality Report",
					"doctype": "Mines Quality Record"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Ordered Materials To Be Delivered",
					"doctype": "Delivery Note"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Sales Compensation Report",
					"doctype": "Sales Invoice"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Delivered Items To Be Billed",
					"doctype": "Sales Invoice"	 										                                },
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Customer Summary Report",
                                        "doctype": "Sales Invoice"                                                                                                                      }	
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
			]
		},

	]
