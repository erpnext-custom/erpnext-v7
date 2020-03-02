from frappe import _

data = {
	'heatmap': True,
	'heatmap_message': _('This is based on the attendance of this Employee'),
	'fieldname': 'employee',
	'transactions': [
		{
			'label': _('Leave and Attendance'),
			'items': [ 'Leave Application', 'Leave Allocation']
		},
		{
			'label': _('Payroll'),
			'items': ['Salary Structure', 'Salary Slip']
		},
		{
			'label': _('Expense'),
			'items': ['Expense Claim']
		},
	#	{
	#		'label': _('Evaluation'),
	#		'items': ['Appraisal']
	#	}
	]
}
