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
	if dn.doctype == 'Purchase Order':
		if naming_series == 'Consumables':
                	series_seq = 'POCO'
		elif naming_series == 'Fixed Asset':
	                series_seq = 'POFA'
	        elif naming_series == 'Sales Product':
	                series_seq = 'POSA'
		elif naming_series == 'Spareparts':
        	        series_seq = 'POSP'
		elif naming_series == 'Services Miscellaneous':
        	        series_seq = 'POSM'
		elif naming_series == 'Services Works':
        	        series_seq = 'POSW'
		else:
			series_seq = 'POPO'
	
	if dn.doctype == 'Sales Order':
		if naming_series == 'Consumables':
                	series_seq = 'SOCO'
		elif naming_series == 'Fixed Asset':
	                series_seq = 'SOFA'
	        elif naming_series == 'Sales Product':
	                series_seq = 'SOSA'
		elif naming_series == 'Spareparts':
        	        series_seq = 'SOSP'
		elif naming_series == 'Services Miscellaneous':
        	        series_seq = 'SOSM'
		elif naming_series == 'Services Works':
        	        series_seq = 'SOSW'
		else:
			series_seq = 'SOSO'
	
	if dn.doctype == 'Purchase Invoice':
		if naming_series == 'Consumables':
                	series_seq = 'PICO'
		elif naming_series == 'Fixed Asset':
	                series_seq = 'PIFA'
	        elif naming_series == 'Sales Product':
	                series_seq = 'PISA'
		elif naming_series == 'Spareparts':
        	        series_seq = 'PISP'
		elif naming_series == 'Services Miscellaneous':
        	        series_seq = 'PISM'
		elif naming_series == 'Services Works':
        	        series_seq = 'PISW'
		else:
			series_seq = 'PIPI'

	if dn.doctype == 'Sales Invoice':
		if naming_series == 'Consumables':
                	series_seq = 'SICO'
		elif naming_series == 'Fixed Asset':
	                series_seq = 'SIFA'
	        elif naming_series == 'Sales Product':
	                series_seq = 'SISA'
		elif naming_series == 'Spareparts':
        	        series_seq = 'SISP'
		elif naming_series == 'Services Miscellaneous':
        	        series_seq = 'SISM'
		elif naming_series == 'Services Works':
        	        series_seq = 'SISW'
		else:
			series_seq = 'SISI'

	if dn.doctype == 'Stock Entry':
		if naming_series == 'Consumables':
                	series_seq = 'SECO'
		elif naming_series == 'Fixed Asset':
	                series_seq = 'SEFA'
	        elif naming_series == 'Sales Product':
	                series_seq = 'SESA'
		elif naming_series == 'Spareparts':
        	        series_seq = 'SESP'
		elif naming_series == 'Services Miscellaneous':
        	        series_seq = 'SESM'
		elif naming_series == 'Services Works':
        	        series_seq = 'SESW'
		else:
			series_seq = 'SESESE'

	if dn.doctype == 'Delivery Note':
		if naming_series == 'Consumables':
                	series_seq = 'DNCO'
		elif naming_series == 'Fixed Asset':
	                series_seq = 'DNFA'
	        elif naming_series == 'Sales Product':
	                series_seq = 'DNSA'
		elif naming_series == 'Spareparts':
        	        series_seq = 'DNSP'
		elif naming_series == 'Services Miscellaneous':
        	        series_seq = 'DNSM'
		elif naming_series == 'Services Works':
        	        series_seq = 'DNSW'
		else:
			series_seq = 'DNDN'

	if dn.doctype == 'Purchase Receipt':
		if naming_series == 'Consumables':
                	series_seq = 'PRCO'
		elif naming_series == 'Fixed Asset':
	                series_seq = 'PRFA'
	        elif naming_series == 'Sales Product':
	                series_seq = 'PRSA'
		elif naming_series == 'Spareparts':
        	        series_seq = 'PRSP'
		elif naming_series == 'Services Miscellaneous':
        	        series_seq = 'PRSM'
		elif naming_series == 'Services Works':
        	        series_seq = 'PRSW'
		else:
			series_seq = 'PRPR'

	if dn.doctype == 'Material Request':
		if naming_series == 'Consumables':
                	series_seq = 'MRCO'
		elif naming_series == 'Fixed Asset':
	                series_seq = 'MRFA'
	        elif naming_series == 'Sales Product':
	                series_seq = 'MRSA'
		elif naming_series == 'Spareparts':
        	        series_seq = 'MRSP'
		elif naming_series == 'Services Miscellaneous':
        	        series_seq = 'MRSM'
		elif naming_series == 'Services Works':
        	        series_seq = 'MRSW'
		elif naming_series == 'REORDER PR':
        	        series_seq = 'MRRE'
		else:
			series_seq = 'MRMR'

	if dn.doctype == 'Supplier Quotation':
		if naming_series == 'Consumables':
                	series_seq = 'SQCO'
		elif naming_series == 'Fixed Asset':
	                series_seq = 'SQFA'
	        elif naming_series == 'Sales Product':
	                series_seq = 'SQSA'
		elif naming_series == 'Spareparts':
        	        series_seq = 'SQSP'
		elif naming_series == 'Services Miscellaneous':
        	        series_seq = 'SQSM'
		elif naming_series == 'Services Works':
        	        series_seq = 'SQSW'
		else:
			series_seq = 'SQSQ'
	
	if dn.doctype == 'Request for Quotation':
		if naming_series == 'Consumables':
                	series_seq = 'RQCO'
		elif naming_series == 'Fixed Asset':
	                series_seq = 'RQFA'
	        elif naming_series == 'Sales Product':
	                series_seq = 'RQSA'
		elif naming_series == 'Spareparts':
        	        series_seq = 'RQSP'
		elif naming_series == 'Services Miscellaneous':
        	        series_seq = 'RQSM'
		elif naming_series == 'Services Works':
        	        series_seq = 'RQSW'
		else:
			series_seq = 'RFQXX'
	
	if dn.doctype == 'Payment Entry':
                if naming_series == 'Bank Payment Voucher':
                        series_seq = 'PEBP'
                elif naming_series == 'Bank Receipt Voucher':
                        series_seq = 'PEBR'
                elif naming_series == 'Journal Voucher':
                        series_seq = 'PEJV'
                else:
                        series_seq = 'PEPE'

	if dn.doctype == 'Quality Inspection':
		if naming_series == 'Consumables':
                	series_seq = 'QICO'
		elif naming_series == 'Fixed Asset':
	                series_seq = 'QIFA'
	        elif naming_series == 'Sales Product':
	                series_seq = 'QISA'
		elif naming_series == 'Spareparts':
        	        series_seq = 'QISP'
		elif naming_series == 'Services Miscellaneous':
        	        series_seq = 'QISM'
		elif naming_series == 'Services Works':
        	        series_seq = 'QISW'
		else:
			series_seq = 'QIQI'
	
	if dn.doctype == 'Quotation':
		if naming_series == 'Consumables':
                	series_seq = 'QTCO'
		elif naming_series == 'Fixed Asset':
	                series_seq = 'QTFA'
	        elif naming_series == 'Sales Product':
	                series_seq = 'QTSA'
		elif naming_series == 'Spareparts':
        	        series_seq = 'QTSP'
		elif naming_series == 'Services Miscellaneous':
        	        series_seq = 'QTSM'
		elif naming_series == 'Services Works':
        	        series_seq = 'QTSW'
		else:
			series_seq = 'QTQT'

        if dn.doctype == 'Leave Encashment':
                series_seq = str(dn.employee)+"/LE/"
                
	return str(series_seq) + ".YY.MM"
