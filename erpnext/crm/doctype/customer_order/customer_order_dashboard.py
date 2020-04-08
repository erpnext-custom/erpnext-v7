from frappe import _

data = {
	'fieldname': 'customer_order',
	'transactions': [
		{
			'label': _('Order Details'),
			'items': ['Sales Order' ]
		},
		{
			'label': _('Payment Details'),
			'items': ['Customer Payment', 'Online Payment', 'Payment Entry']
		}
	]
}
