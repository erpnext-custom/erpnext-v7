from frappe import _

data = {
	'fieldname': 'purchase_order',
	'non_standard_fieldnames': {
		'Payment Entry': 'so_reference',
	},
	'internal_links': {
		'Material Request': ['items', 'material_request'],
		'Supplier Quotation': ['items', 'supplier_quotation'],
		'Project': ['project'],
	},
	'transactions': [
		{
			'label': _('Related'),
			'items': ['Payment Entry', 'Purchase Receipt', 'Purchase Invoice']
		},
		{
			'label': _('Reference'),
			'items': ['Material Request', 'Supplier Quotation', 'Project']
		},
		{
			'label': _('Sub-contracting'),
			'items': ['Stock Entry']
		},
	]
}
