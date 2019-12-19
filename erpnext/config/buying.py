from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Buying Transaction"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Material Request",
					"description": _("Request for purchase."),
				},
				{
					"type": "doctype",
					"name": "Request for Quotation",
					"description": _("Request for quotation."),
				},
				{
					"type": "doctype",
					"name": "Supplier Quotation",
					"label": "Vendor Quotation",
					"description": _("Quotations received from Suppliers."),
				},
				{
					"type": "doctype",
					"name": "Purchase Order",
					"description": _("Purchase Orders given to Suppliers."),
				},
				{
					"type": "doctype",
					"name": "Purchase Receipt",
					"description": _("Goods received from Suppliers."),
				},
				{
					"type": "doctype",
					"name": "Quality Inspection",
					"description": _("Quality Inspection"),
				},
				{
					"type": "doctype",
					"name": "Purchase Invoice",
					"description": _("Bills raised by Suppliers.")
				}
			]
		},
		{
			"label": _("Buying - Master"),
			"items": [
				{
					"type": "doctype",
					"name": "Supplier",
					"label": "Vendor",
					"description": _("Supplier database."),
				},
				{
					"type": "doctype",
					"name": "Supplier Type",
					"label": "Vendor Type",
					"description": _("Supplier Type master.")
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
					"label": _("Purchase Terms and Conditions Template"),
					"description": _("Template of terms or contract.")
				}
			]
		},
		{
			"label": _("Buying - Reports"),
			"icon": "icon-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Material Request Pending for Purchase Order",
					"doctype": "Material Request"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Material Request Pending for Supplier Quotation",
					"doctype": "Material Request"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Material Purchase History",
					"doctype": "Item"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Vendor Addresses",
					"doctype": "Supplier"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Purchase History Report",
					"doctype": "Purchase Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Order Trends",
					"doctype": "Purchase Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Order Materials To Be Received",
					"doctype": "Purchase Receipt"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Receipt Trends",
					"doctype": "Purchase Receipt"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Penalty Report",
					"doctype": "Purchase Invoice"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Asset Issue Report",
					"doctype": "Asset Issue Details"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Asset Balance Report",
					"doctype": "Asset Received Entries"
				},
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Comparative Statement(Quotation)",
                                        "doctype": "Purchase Order"
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
					"name": "Item Price",
					"label": "Material Price",
					"description": _("Multiple Item prices."),
					"route": "Report/Item Price"
				},
				{
					"type": "doctype",
					"name": "Asset Issue Details",
					"description": _("Record to whom the assets are issued"),
				}
			]
		}
	]
