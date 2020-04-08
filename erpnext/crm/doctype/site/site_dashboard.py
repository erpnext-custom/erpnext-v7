from frappe import _

data = {
	'fieldname': 'site',
	'transactions': [
		{
			'label': _('Site Information'),
			'items': ['Site Registration', 'Site Extension', 'Site Status', 'Quantity Extension']
		},
		{
			'label': _('Orders & Payments'),
			'items': ['Customer Order', 'Customer Payment', 'Sales Order', 'Payment Entry']
		}
	]
}
