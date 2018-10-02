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
				{
					"type": "doctype",
					"name": "Cost of Production",
				},
			]
		},
	]
