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
				{
					"type": "doctype",
					"name": "Marking List",
				},
				{
					"type": "doctype",
					"name": "Royalty Payment",
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
					"name": "Adhoc Production",
				},
				{
					"type": "doctype",
					"name": "Timber Class",
				},
				{
					"type": "doctype",
					"name": "Timber Species",
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
					"name": "Production Group",
				},
				{
					"type": "doctype",
					"name": "Production Settings",
				},
				{
					"type": "doctype",
					"name": "Cost of Production",
				},
				{
					"type": "doctype",
					"name": "Adhoc Royalty Setting",
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
                                        "name": "Production Target Report",
                                        "doctype": "Production Target"
                                },


			]
		},
	]
