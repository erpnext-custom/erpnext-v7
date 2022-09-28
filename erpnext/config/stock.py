from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Stock Transactions"),
			"items": [
				{
					"type": "doctype",
					"name": "Stock Entry",
					"description": _("Record item movement."),
				},
				{
					"type": "doctype",
					"name": "Material Request",
					"description": _("Requests for Materials."),
				},
				{
					"type": "doctype",
					"name": "Delivery Note",
					"description": _("Shipments to customers."),
				},
				{
					"type": "doctype",
					"name": "Purchase Receipt",
					"description": _("Goods received from Suppliers."),
				},
				{
					"type": "doctype",
					"name": "Mining Process",
					"description": _("Capturing the expenses task related to Mines"),
				},
			]
		},
		{
			"label": _("Stock Master"),
			"items": [
				{
					"type": "doctype",
					"name": "Item",
					"label": "Material",
					"description": _("All Products or Services."),
				},
				{
					"type": "doctype",
					"name": "Price List",
					"description": _("Price List master.")
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
					"name": "Item Price",
					"label": _("Material Price"),
					"description": _("Multiple Item prices."),
					"route": "Report/Item Price"
				},
				{
					"type": "doctype",
					"name": "Stock Price Template",
					"label": "Price Templates for Mines Products",
					"description": _("Price Templates for Mines Products"),
				},
				{
					"type": "doctype",
					"name": "Warehouse",
					"description": _("Where items are stored."),
				},
				{
					"type": "doctype",
					"name": "UOM",
					"label": _("Unit of Measure") + " (UOM)",
					"description": _("e.g. Kg, Unit, Nos, m")
				},
				{
					"type": "doctype",
					"name": "Quality Inspection",
					"description": _("Incoming quality inspection.")
				}
			]
		},
		{
			"label": _("Stock Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Stock Ledger Report",
					"doctype": "Stock Ledger Entry",
					"Label": _("Stock Ledger")
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Stock Balance Report",
					"doctype": "Stock Ledger Entry",
					"label": _("Stock Balance")
				},
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Stock Issue Report",
                                        "doctype": "Stock Entry",
                                        "Label": _("Stock Issue Report")
                                },

				{
					"type": "report",
					"is_query_report": True,
					"name": "Stock Projected Quantity",
					"doctype": "Item",
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Stock Ageing Report",
					"doctype": "Item",
					"label": _("Stock Ageing")
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Material Balance History",
					"doctype": "Batch"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Material Shortage Report",
					"doctype": "Bin",
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Requested Materials To Be Transferred",
					"doctype": "Material Request"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Material Price Report",
					"doctype": "Price List",
					"label": _("Material Prices")
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Materialwise Recommended Reorder Level Report",
					"doctype": "Item",
				}
			]
		},
		{
			"label": _("Stock Tools"),
			"icon": "icon-wrench",
			"items": [
				{
					"type": "doctype",
					"name": "Stock Reconciliation",
					"description": _("Upload stock balance via csv.")
				},
				{
					"type": "doctype",
					"name": "Deferred Posting Entry",
					"description": _("Deferred Posting Entry.")
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Deferred Posting Status",
					"doctype": "Deferred Posting Entry",
					"label": _("Deferred Posting Status.")
				},
			]
		}
	]
