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
		}
	]
