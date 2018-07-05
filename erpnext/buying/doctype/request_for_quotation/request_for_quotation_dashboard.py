from frappe import _

data = {
	'docstatus': 1,
	'fieldname': 'request_for_quotation',
        'internal_links': {
            'Material Request': ['items', 'material_request']
        },
	'transactions': [
		{
			'label': _('Related'),
			'items': ['Material Request', 'Supplier Quotation']
		},
	]
}
