from frappe import _

def get_data():
	return [
		{
			"label": _("Transaction"),
			"items": [
                {
					"type": "doctype",
					"name": "Production",
				},
			]
		},
		{
			"label": _("Master Data"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Location",
				},
				{
					"type": "doctype",
					"name": "Item",
					"label": "Material"
				},
			]
		},
		{
			"label": _("Settings"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Cost of Production",
				},
				{
					"type": "doctype",
					"name": "Production Target",
				},
			]
		},
		{
                        "label": _("Reports"),
                        "icon": "icon-list",
                        "items": [
                                {
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Production Report",
                                        "doctype": "Production"
                                },
                                {
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Production Progress Report",
                                        "doctype": "Production"
                                },
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Disposal Progress Report",
                                        "doctype": "Production"
                                },
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Production Target Report",
                                        "doctype": "Production Target"
                                },
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Sales Report",
                                        "label": "Sales Report",
                                        "doctype": "Sales Order"
                                }


			]
		},
	]
