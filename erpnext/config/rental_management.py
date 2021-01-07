from frappe import _

def get_data():
	return [
		{
			"label": _("Master Data"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Town Category",
				},
				{
					"type": "doctype",
					"name": "Locations",
				},
				{
					"type": "doctype",
					"name": "Building Classification",
				},
				{
					"type": "doctype",
					"name": "Building Category",
				},
				{
					"type": "doctype",
					"name": "Block No",
				},
				{
					"type": "doctype",
					"name": "Flat No",
				},
				{
					"type": "doctype",
					"name": "Floor Area",
				},
				{
					"type": "doctype",
					"name": "Ministry and Agency",
				},
				{
					"type": "doctype",
					"name": "Tenant Department",
				},
				{
					"type": "doctype",
					"name": "Tenant Section",
				},
				
			]
		},
		{
			"label": _("Settings"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Rental Setting",
				},
				{
					"type": "doctype",
					"name": "Rental Account Setting",
				},
				{
					"type": "doctype",
					"name": "Rate",
				},
			]
		},
		{
			"label": _("Tenant Transactions"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Tenant Information",
				},
				{
					"type": "doctype",
					"name": "Process Rental Billing",
				},
				{
					"type": "doctype",
					"name": "Rental Bill",
				},
				{
					"type": "doctype",
					"name": "Rental Payment",
				},
				{
					"type": "doctype",
					"name": "Rental Advance Adjustment"
				}
				
			]
		},
		 {
                        "label": _("Real Estate Management Services"),
                        "icon": "icon-star",
                        "items": [
                                {
                                        "type": "doctype",
                                        "name": "Maintenance Application Form",
                                },
                                {
                                        "type": "doctype",
                                        "name": "Technical Sanction",
                                },
                                {
                                        "type": "doctype",
                                        "name": "Rate Analysis",
                                },
                                {
                                        "type": "doctype",
                                        "name": "Service",
                                },
				{
					"type": "doctype",
					"name": "Upload Service List",
					"description": "Upload Bulk Service List"
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
                                        "name": "Rental Register",
                                        "doctype": "Rental Information",
                                        "Label": _("Rental Register")
                                },
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Tenant Information",
                                        "doctype": "Tenant Information",
                                        "Label": _("Tenant Information")
                                },
								{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Monthly Rental Collection and Dues",
                                        "doctype": "Rental Payment",
                                        "Label": _("Rental Payment")
                                },

				{
                                        "type": "report",
                                        "name": "Accounts Receivable",
                                        "doctype": "Sales Invoice",
                                        "is_query_report": True
                                },
			]
		},
		   {
                        "label": _("Tools"),
                        "icon": "icon-list",
                        "items": [
                                 {
                                        "type": "doctype",
                                        "name": "Tenant Updation Tool",
                                },
								{
									"type": "doctype",
									"name": "Draft ID"
								},
                                 {
                                        "type": "doctype",
                                        "name": "Rental Bill Cancelation Tool",
					"label": "Bill Cancellation Tool"
                                }

                        ]
                },
	]
