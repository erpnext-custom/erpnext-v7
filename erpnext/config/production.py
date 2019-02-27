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
					"name": "Adhoc Production",
				},
				{
					"type": "doctype",
					"name": "Item",
					"label": "Material"
				},
				{
					 "type": "doctype",
					 "name": "Departmental Group",
					 "label": "Departmental Group"
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
					"name": "Cost of Production",
				},
				{
					"type": "doctype",
					"name": "Production Target",
				},
				{
					 "type": "doctype",
					 "name": "Transporter Rate",
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
			]
		},
	]
