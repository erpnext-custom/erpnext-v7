from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Employee Records"),
			"items": [
				{
					"type": "doctype",
					"name": "Employee",
					"description": _("Employee records."),
				},
			]
		}
	]

