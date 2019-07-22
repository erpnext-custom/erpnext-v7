from frappe import _
def get_data():
	return [
		{
			"label": _("Master Data"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Equipment",
					"description": _("Equipment Details"),
				},
				{
					"type": "doctype",
					"name": "Equipment Category",
					"description": _("Equipment Category Details"),
				},
				{
					"type": "doctype",
					"name": "Equipment Type",
					"description": _("Equipment Type Details"),
				},
				{
					"type": "doctype",
					"name": "Equipment Model",
					"description": _("Equipment Model Details"),
				},
				{
					"type": "doctype",
					"name": "Fuelbook",
					"description": _("Fuelbook Types"),
				},
			]
		},
		{
			"label": _("Settings and Tools"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Mechanical Settings",
				},
				{
					"type": "doctype",
					"name": "HSD Adjustment",
					"description": _("Create Payment"),
				},
				{
					"type": "doctype",
					"name": "Equipment Modifier Tool",
					"description": _("Equipment Modifier Tool"),
				},
			]
		},
		{
			"label": _("POL Transaction"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "POL",
					"label": "Receive POL",
					"description": _("Receive POL"),
				},
				{
					"type": "doctype",
					"name": "Issue POL",
					"label": "Issue POL",
					"description": _("Issue POL"),
				},
				{
					"type": "doctype",
					"name": "Equipment POL Transfer",
				},
				{
					"type": "doctype",
					"name": "HSD Payment",
					"description": _("Create Payment"),
				},
			]
		},
		{
			"label": _("POL Reports"),
			"icon": "icon-star",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "POL Ledger",
					"doctype": "POL Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "POL Issue Report",
					"doctype": "Consumed POL"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "POL Balance Report",
					"doctype": "POL"
				},
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "POL Receive Report",
                                        "doctype": "POL"
                                },

			]
		},
	]
