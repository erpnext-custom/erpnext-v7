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
				{
					 "type": "doctype",
					 "name": "Item Type",
					 "label": "Material Type"
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
				{
					 "type": "doctype",
					 "name": "Production Settings",
				},
				{
					 "type": "doctype",
					 "name": "Production Parameter",
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
		{
			"label": _("Transporter Transactions"),
			"items": [
				{
					"type": "doctype",
					"name": "Transporter Rate",
					"label": "Transportation Rate",
					"description": _("Transportation Rate"),
				},
				{
					"type": "doctype",
					"name": "Transporter Trip Log",
					"label": _("Transporter Trip Log"),
					"description": _("Transporter Trip Log."),
				},
				{
					"type": "doctype",
					"name": "Transporter Payment",
					"description": _("Transporter Payment.")
				},
			]
		},
		{
			"label": _("Coal Raising"),
			"items": [
				{
					"type": "doctype",
					"name": "Tire",
					"label": "Tire",
				},
				{
					"type": "doctype",
					"name": "Coal Raising Master",
					"label": _("Coal Raising Master")
				},
				{
					"type": "doctype",
					"name": "Coal Raising Payment",
					"label": _("Coal Raising Payment")
				}
			]
		},
		{
			"label": _("Coal Raising Report"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Coal Raising Report",
					"label": "Coal Raising Report",
					'doctype':'Production'
				},
			]
		}
	]
