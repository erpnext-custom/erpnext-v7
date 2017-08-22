from frappe import _
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SHIV		                    2017/08/15         Introducting BOQ
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

data = {
	'heatmap': True,
	'heatmap_message': _('This is based on the Time Sheets created against this project'),
	'fieldname': 'project',
	'transactions': [
		{
			'label': _('Project'),
			#'items': ['Task', 'Timesheet', 'Expense Claim', 'Issue']
                        'items': ['Task', 'Timesheet', 'BOQ', 'Issue']
		},
		{
			'label': _('Material'),
			'items': ['Material Request', 'BOM', 'Stock Entry']
		},
		{
			'label': _('Sales'),
			'items': ['Sales Order', 'Delivery Note', 'Sales Invoice']
		},
		{
			'label': _('Purchase'),
			'items': ['Purchase Order', 'Purchase Receipt', 'Purchase Invoice']
		},
	]
}
