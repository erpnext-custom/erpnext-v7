from frappe import _

data = {
	'fieldname': 'asset_code',
	'non_standard_fieldnames': {
		'Asset Movement': 'asset',
	},
	'transactions': [
		{
			'label': _('Equipment'),
			'items': ['Equipment']
		},
		{
			'label': _('Asset Movement'),
			'items': ['Asset Movement', 'Bulk Asset Transfer']
		},
	]
}
