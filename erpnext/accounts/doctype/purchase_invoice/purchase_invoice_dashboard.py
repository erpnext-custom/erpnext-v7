from frappe import _

data = {
	'fieldname': 'purchase_invoice',
	'non_standard_fieldnames': {
		'Delivery Note': 'against_sales_invoice',
		'Journal Entry': 'reference_name',
		'Payment Entry': 'reference_name',
		'Payment Request': 'reference_name',
		'Landed Cost Voucher': 'receipt_document',
		'Purchase Invoice': 'return_against'
	},
	'internal_links': {
		'Purchase Order': ['items', 'purchase_order'],
		'Purchase Receipt': ['items', 'purchase_receipt'],
	},
	'transactions': [
		{
			'label': _('Payment'),
			'items': ['Payment Entry', 'Payment Request', 'Journal Entry']
		},
		{
			'label': _('Reference'),
			'items': ['Purchase Order', 'Purchase Receipt', 'Asset', 'Landed Cost Voucher']
		},
		{
			'label': _('Returns'),
			'items': ['Purchase Invoice']
		},
	]
}
