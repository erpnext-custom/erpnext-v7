from frappe import _

data = {
	'fieldname': 'asset_code',
	'non_standard_fieldnames': {
		'Asset Movement': 'asset',
		'Sales Invoice': 'asset',
	},
	'transactions': [
		{
			'label': _('Related Data'),
			'items': ['Equipment', 'Sales Invoice']
		},
		{
			'label': _('Asset Movement'),
			'items': ['Asset Movement', 'Bulk Asset Transfer']
		},
	]
}
