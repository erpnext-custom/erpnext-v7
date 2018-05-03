from frappe import _

data = {
	'fieldname': 'equipment_request',
	'internal_links': {
		'Equipment Hiring Form': ['approved_items', 'equipment_request'],
	},
	'transactions': [
		{
			'label': _('Linked Documents'),
			'items': ['Equipment Hiring Form']
		},
	]
}
