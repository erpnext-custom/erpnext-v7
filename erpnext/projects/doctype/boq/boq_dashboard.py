from frappe import _

data = {
	'fieldname': 'boq',
	'transactions': [
		{
			'label': _('BOQ'),
                        'items': ['BOQ Adjustment', 'BOQ Addition', 'BOQ Substitution']
		},
                {
			'label': _('Transactions'),
			'items': ['Subcontract','MB Entry']
		},
	]
}
