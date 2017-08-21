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
					"name": "Equipment Accessories",
					"description": _("Equipment Accessories Details"),
				},
				{
					"type": "doctype",
					"name": "POL Type",
					"description": _("POL Types"),
				},
				{
					"type": "doctype",
					"name": "Service",
					"description": _("Services"),
				},
			]
		},
		{
			"label": _("Fleet Transaction"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Equipment Hiring Form",
					"description": _("Equipment Hiring Form"),
				},
				{
					"type": "doctype",
					"name": "Vehicle Logbook",
					"description": _("Vehicle Logbook"),
				},
				{
					"type": "doctype",
					"name": "Hire Charge Invoice",
					"description": _("Hire Charge Invoice"),
				},
				{
					"type": "doctype",
					"name": "Equipment Hiring Extension",
					"description": _("Equipment Hiring Extension"),
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
			]
		},
		{
			"label": _("Maintenance Reports"),
			"icon": "icon-star",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Job Card Imprest Report",
					"doctype": "Job Card"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Work Progress Report",
					"doctype": "Job Card"
				},
			]
		},
		{
			"label": _("Fleet Reports"),
			"icon": "icon-star",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Equipment Hire Report",
					"doctype": "Hire Charge Invoice"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "POL Consumption Report",
					"doctype": "Consumed POL"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "POL Balance Report",
					"doctype": "POL"
				},
			]
		},
	]
