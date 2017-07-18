from frappe import _
def get_data():
	return [
		{
			"label": _("Maintenance Transaction"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Break Down Report",
					"description": _("Break Down Reports"),
				},
				{
					"type": "doctype",
					"name": "Job Card",
					"description": _("Create Job Card"),
				},
			]
		},
		{
			"label": _("Maintenance Master"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Equipment",
					"description": _("Equipment Details"),
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
			]
		},
		{
			"label": _("Fleet Transaction"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Equipment Model",
					"description": _("Equipment Model Details"),
				},
			]
		},
		{
			"label": _("HSD Transaction"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Equipment Model",
					"description": _("Equipment Model Details"),
				},
			]
		},
		{
			"label": _("Reports"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Equipment Model",
					"description": _("Equipment Model Details"),
				},
			]
		},
	]
