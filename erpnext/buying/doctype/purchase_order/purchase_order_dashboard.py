from frappe import _

data = {
	'fieldname': 'purchase_order',
	'non_standard_fieldnames': {
                'Payment Entry': 'reference_name',
        },


	'internal_links': {
		'Material Request': ['items', 'material_request'],
		'Supplier Quotation': ['items', 'supplier_quotation'],
		'Project': ['project'],
	},
	'transactions': [
		{
			'label': _('Related'),
			'items': ['Purchase Receipt', 'Purchase Invoice', 'Payment Entry']
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
