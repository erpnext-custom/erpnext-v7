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
				{
					"type": "doctype",
					"name": "Expense Head",
					"label": "Define Expense Heads",
				},
				{
					"type": "doctype",
					"name": "Downtime Reason",
					"label": "Define Downtime Reasons",
				},
				{
					"type": "doctype",
					"name": "Offence",
					"label": "Define Offence",
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
			"label": _("Transporter Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Trip Log",
					"doctype": "Transporter Trip Log"
				},
			]
		},
		{
			"label": _("EME Reports"),
			"icon": "icon-star",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Daily EME Expenses",
					"doctype": "Logbook"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Daily EME Working Hour",
					"doctype": "Logbook"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Expense and Performance Summary",
					"doctype": "Logbook"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "EME Payment Report",
					"doctype": "EME Payment"
				}
			]
		},
		{
			"label": _("EME Transactions"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Equipment Hiring Form",
					"label": "Equipment Hiring Form",
				},
				{
					"type": "doctype",
					"name": "Logbook",
					"label": "Logbooks",
				},
				{
					"type": "doctype",
					"name": "EME Payment",
					"label": "EME Payment",
				},
				{
					"type": "doctype",
					"name": "Incident",
					"label": "Report Incident",
				}
			]
		},
	]
