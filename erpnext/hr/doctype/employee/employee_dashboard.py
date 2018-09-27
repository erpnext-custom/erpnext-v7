from frappe import _

data = {
	'heatmap': True,
	'heatmap_message': _('This is based on the attendance of this Employee'),
	'fieldname': 'employee',
	'transactions': [
		{
			'label': _('Leave and Attendance'),
			'items': ['Attendance', 'Leave Application', 'Leave Allocation']
		},
		{
			'label': _('Payroll'),
			'items': ['Salary Structure', 'Salary Slip', 'Salary Increment', 'Timesheet']
		},
		{
			'label': _('Expense'),
			'items': ['Travel Claim', 'Leave Encashment', 'Overtime Application']
		},
		{
			'label': _('Yearly Components'),
			'items': ['Leave Travel Concession', 'PBVA', 'Bonus']
		},
	]
}
