from frappe import _

data = {
	'fieldname': 'sales_order',
	'non_standard_fieldnames': {
		'Delivery Note': 'against_sales_order',
		'Payment Entry': 'so_reference',
	},
	'internal_links': {
		'Quotation': ['items', 'prevdoc_docname']
	},
	'transactions': [
		{
			'label': _('Fulfillment'),
			'items': ['Payment Entry', 'Sales Invoice', 'Delivery Note']
		},
		{
			'label': _('Purchasing'),
			'items': ['Material Request', 'Purchase Order']
		},
		{
			'label': _('Projects'),
			'items': ['Project']
		},
		{
			'label': _('Manufacturing'),
			'items': ['Production Order']
		},
		{
			'label': _('Reference'),
			'items': ['Quotation']
		},
	]
}
