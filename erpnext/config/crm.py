from frappe import _

def get_data():
	#return [{"label": "","items":[]}]
	
	return [
		{
			"label": _("Master Data"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Site Type",
					"description": _("Site Type."),
				},
				{
					"type": "doctype",
					"name": "Construction Type",
					"description": _("Construction Type."),
				},
				{
					"type": "doctype",
					"name": "CRM Branch Setting",
					"description": _("CRM Branch Setting."),
				},
				{
					"type": "doctype",
					"name": "Vehicle Capacity",
					"description": _("Vehicle Load Capacity"),
				},
			]
		},
		{
			"label": _("SMS"),
			"icon": "icon-wrench",
			"items": [
				{
					"type": "doctype",
					"name": "SMS Center",
					"description":_("Send mass SMS to your contacts"),
				},
				{
					"type": "doctype",
					"name": "SMS Log",
					"description":_("Logs for maintaining sms delivery status"),
				},
				{
					"type": "doctype",
					"name": "SMS Settings",
					"description": _("Setup SMS gateway settings")
				}
			]
		},
		{
			"label": _("User Information"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "User Request",
					"description": _("User Requests."),
				},
				{
					"type": "doctype",
					"name": "User Account",
					"description": _("User Accounts."),
				},
				{
					"type": "doctype",
					"name": "Feedback",
					"description": _("Feedbacks."),
				},
			]
		},
		{
			"label": _("Site Information"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Site",
					"description": _("Site."),
				},
				{
					"type": "doctype",
					"name": "Site Registration",
					"description": _("Site Registration."),
				},
				{
					"type": "doctype",
					"name": "Site Extension",
					"description": _("Site Extension."),
				},
				{
					"type": "doctype",
					"name": "Site Status",
					"description": _("Activate/Deactivate site."),
				},
				{
					"type": "doctype",
					"name": "Quantity Extension",
					"description": _("Quantity Extension."),
				},
			]
		},
		{
			"label": _("Transporter Information"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Transporter",
					"description": _("Transporters"),
				},
				{
					"type": "doctype",
					"name": "Transport Request",
					"description": _("Transport Request"),
				},
				{
					"type": "doctype",
					"name": "Vehicle",
					"description": _("Vehicle Records"),
				},
				{
					"type": "doctype",
					"name": "Vehicle Update",
					"label": "Update Vehicle Details",
					"description": _("Vehicle Update"),
				},
				{
					"type": "doctype",
					"name": "Change Status",
					"label": "Change Queue and Delivery Confirmation Status",
					"description": _("Change Queue and Confirmation Status"),
				},
				{
					"type": "doctype",
					"name": "Change Vehicle Status",
					"description": _("Change Vehicle Status"),
				},
				{
					"type": "doctype",
					"name": "Load Request",
					"description": _("Transporter Requesting for load"),
				},
				{
					"type": "doctype",
					"name": "Delivery Confirmation",
					"description": _("Delivery Note"),
				}
			]
		},
		{
			"label": _("Orders & Payments"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Customer Order",
					"label": "Customer Orders",
					"description": _("Customer Order"),
				},
				{
					"type": "doctype",
					"name": "Customer Payment",
					"label": "Customer Payments",
					"description": _("Customer Payments"),
				},
			]
		},
		{
			"label": _("Help"),
			"items": [
				{
					"type": "help",
					"label": _("Lead to Quotation"),
					"youtube_id": "TxYX4r4JAKA"
				},
				{
					"type": "help",
					"label": _("Newsletters"),
					"youtube_id": "muLKsCrrDRo"
				},
			]
		},
	]

"""	return [
		{
			"label": _("Sales Pipeline"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Lead",
					"description": _("Database of potential customers."),
				},
				{
					"type": "doctype",
					"name": "Opportunity",
					"description": _("Potential opportunities for selling."),
				},
				{
					"type": "doctype",
					"name": "Customer",
					"description": _("Customer database."),
				},
				{
					"type": "doctype",
					"name": "Contact",
					"description": _("All Contacts."),
				},
			]
		},
		{
			"label": _("Reports"),
			"icon": "icon-list",
			"items": [
				{
					"type": "page",
					"name": "sales-funnel",
					"label": _("Sales Funnel"),
					"icon": "icon-bar-chart",
				},
				{
					"type": "report",
					"name": "Minutes to First Response for Opportunity",
					"doctype": "Opportunity",
					"is_query_report": True
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Lead Details",
					"doctype": "Lead"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Customer Addresses and Contacts",
					"doctype": "Contact"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Inactive Customers",
					"doctype": "Sales Order"
				},
			]
		},
		{
			"label": _("Communication"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Communication",
					"description": _("Record of all communications of type email, phone, chat, visit, etc."),
				},
			]
		},
		{
			"label": _("Setup"),
			"icon": "icon-cog",
			"items": [
				{
					"type": "doctype",
					"name": "Campaign",
					"description": _("Sales campaigns."),
				},
				{
					"type": "doctype",
					"label": _("Customer Group"),
					"name": "Customer Group",
					"icon": "icon-sitemap",
					"link": "Tree/Customer Group",
					"description": _("Manage Customer Group Tree."),
				},
				{
					"type": "doctype",
					"label": _("Territory"),
					"name": "Territory",
					"icon": "icon-sitemap",
					"link": "Tree/Territory",
					"description": _("Manage Territory Tree."),
				},
				{
					"type": "doctype",
					"label": _("Sales Person"),
					"name": "Sales Person",
					"icon": "icon-sitemap",
					"link": "Tree/Sales Person",
					"description": _("Manage Sales Person Tree."),
				},
			]
		},
		{
			"label": _("SMS"),
			"icon": "icon-wrench",
			"items": [
				{
					"type": "doctype",
					"name": "SMS Center",
					"description":_("Send mass SMS to your contacts"),
				},
				{
					"type": "doctype",
					"name": "SMS Log",
					"description":_("Logs for maintaining sms delivery status"),
				},
				{
					"type": "doctype",
					"name": "SMS Settings",
					"description": _("Setup SMS gateway settings")
				}
			]
		},
		{
			"label": _("Help"),
			"items": [
				{
					"type": "help",
					"label": _("Lead to Quotation"),
					"youtube_id": "TxYX4r4JAKA"
				},
				{
					"type": "help",
					"label": _("Newsletters"),
					"youtube_id": "muLKsCrrDRo"
				},
			]
		},
	]
"""
