'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SSK		                   20/08/2016         Naming Series for Leave Encashment is added.
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint
##
# Sets the initials of autoname for PO, PR, SO, SI, PI, etc
##
def get_auto_name(dn, naming_series=None):
        #msgprint(dn.doctype)
	series_seq = 'UNKO'
	
	if dn.doctype == 'Payment Entry':
                if naming_series == 'Bank Payment Voucher':
                        series_seq = 'PEBP'
                elif naming_series == 'Bank Receipt Voucher':
                        series_seq = 'PEBR'
                elif naming_series == 'Journal Voucher':
                        series_seq = 'PEJV'
                else:
                        series_seq = 'PEPE'

        if dn.doctype == 'Leave Encashment':
                series_seq = str(dn.employee)+"/LE/"
                
	return str(series_seq) + ".YY.MM"
