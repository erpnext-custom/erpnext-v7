from frappe import _

data = {
	'fieldname': 'user',
	'transactions': [
		{
			'label': _('Requests'),
			'items': ['User Request', 'Site Registration', 'Transport Request']
		},
		{
			'label': _('Site Information'),
			'items': ['Site', 'Site Extension', 'Site Status', 'Quantity Extension']
		},
		{
			'label': _('Transport Information'),
			'items': ['Vehicle', 'Vehicle Update', 'Load Request', 'Delivery Confirmation']
		},
		{
			'label': _('Orders & Payments'),
			'items': ['Customer Order', 'Customer Payment']
		}
	]
}
