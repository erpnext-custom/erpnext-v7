from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

##
# Sets the initials of autoname for PO, PR, SO, SI, PI, etc
##
def get_auto_name(dn, naming_series):
	series_seq = 'UNKO'
	if dn.doctype == 'Purchase Order':
		if naming_series == 'CONSUMABLE PO':
                	series_seq = 'POCO'
		elif naming_series == 'FIXED ASSET PO':
	                series_seq = 'POFA'
	        elif naming_series == 'CONSUMABLE SERVICE PO':
	                series_seq = 'POCS'
		elif naming_series == 'WORKS PO':
        	        series_seq = 'POWO'
		else:
			series_seq = 'POPO'
	
	if dn.doctype == 'Sales Order':
        	if naming_series == 'Coal Sales Order':
	                series_seq = 'SOCO'
		elif naming_series == 'Dolomite Sales Order':
	                series_seq = 'SODO'
	        elif naming_series == 'Gypsum Sales Order':
	                series_seq = 'SOGP'
		elif naming_series == 'Lime Stone Sales Order':
	                series_seq = 'SOLS'
		elif naming_series == 'Stone Sales Order':
	                series_seq = 'SOST'
		elif naming_series == 'Bauxite Sales Order':
	                series_seq = 'SOBA'
		elif naming_series == 'Quartzite Sales Order':
	                series_seq = 'SOQZ'
		else:
			series_seq = 'SOSO'
	
	if dn.doctype == 'Purchase Invoice':
		if naming_series == 'CONSUMABLE Invoice':
                	series_seq = 'PICO'
		elif naming_series == 'FIXED ASSET Invoice':
	                series_seq = 'PIFA'
	        elif naming_series == 'CONSUMABLE SERVICE Invoice':
	                series_seq = 'PICS'
		elif naming_series == 'WORKS Invoice':
        	        series_seq = 'PIWO'
		else:
			series_seq = 'PIPI'

	if dn.doctype == 'Sales Invoice':
        	if naming_series == 'Coal Invoice':
	                series_seq = 'SICO'
		elif naming_series == 'Dolomite Invoice':
	                series_seq = 'SIDO'
	        elif naming_series == 'Gypsum Invoice':
	                series_seq = 'SIGP'
		elif naming_series == 'Lime Stone Invoice':
	                series_seq = 'SILS'
		elif naming_series == 'Stone Invoice':
	                series_seq = 'SIST'
		elif naming_series == 'Bauxite Invoice':
	                series_seq = 'SIBA'
		elif naming_series == 'Quartzite Invoice':
	                series_seq = 'SIQZ'
		elif naming_series == 'Credit Invoice':
	                series_seq = 'SICR'
		else:
			series_seq = 'SISI'

	if dn.doctype == 'Stock Entry':
        	if naming_series == 'Capital Inventory GR':
	                series_seq = 'SECIGR'
		elif naming_series == 'Consumable GR':
	                series_seq = 'SECOGR'
	        elif naming_series == 'Capital Inventory GI':
	                series_seq = 'SECIGI'
		elif naming_series == 'Consumable GI':
	                series_seq = 'SECOGI'
		elif naming_series == 'Inventory Transfer':
	                series_seq = 'SEINTX'
		elif naming_series == 'Coal GR':
	                series_seq = 'SECOGR'
		elif naming_series == 'Dolomite GR':
	                series_seq = 'SEDOGR'
		elif naming_series == 'Gypsum GR':
	                series_seq = 'SEGPGR'
		elif naming_series == 'Stone GR':
	                series_seq = 'SESTGR'
		elif naming_series == 'Limestone GR':
	                series_seq = 'SELSGR'
		elif naming_series == 'Bauxite GR':
	                series_seq = 'SEBAGR'
		elif naming_series == 'Quartzite GR':
	                series_seq = 'SEQZGR'
		else:
			series_seq = 'SESESE'

	if dn.doctype == 'Delivery Note':
        	if naming_series == 'Coal Delivery':
	                series_seq = 'DNCO'
		elif naming_series == 'Dolomite Delivery':
	                series_seq = 'DNDO'
	        elif naming_series == 'Gypsum Delivery':
	                series_seq = 'DNGP'
		elif naming_series == 'Limestone Delivery':
	                series_seq = 'DNLS'
		elif naming_series == 'Stone Delivery':
	                series_seq = 'DNST'
		elif naming_series == 'Bauxite Delivery':
	                series_seq = 'DNBA'
		elif naming_series == 'Quartzite Delivery':
	                series_seq = 'DNQZ'
		elif naming_series == 'Return Delivery':
	                series_seq = 'DNRE'
		else:
			series_seq = 'DNDN'

	if dn.doctype == 'Purchase Receipt':
		if naming_series == 'CONSUMABLE GR':
                	series_seq = 'PRCO'
		elif naming_series == 'FIXED ASSET GR':
	                series_seq = 'PRFA'
	        elif naming_series == 'CONSUMABLE SERVICE Entry':
	                series_seq = 'PRCS'
		elif naming_series == 'WORKS Service Entry':
        	        series_seq = 'PRWO'
		elif naming_series == 'Goods Return/Rejection':
        	        series_seq = 'PRGR'
		else:
			series_seq = 'PRPR'

	if dn.doctype == 'Material Request':
		if naming_series == 'CONSUMABLE PR':
                	series_seq = 'MRCO'
		elif naming_series == 'FIXED ASSET PR':
	                series_seq = 'MRFA'
	        elif naming_series == 'CONSUMABLE SERVICE PR':
	                series_seq = 'MRCS'
		elif naming_series == 'WORKS PR':
        	        series_seq = 'MRWO'
		elif naming_series == 'MINES PRODUCT PR':
        	        series_seq = 'MRMP'
		elif naming_series == 'REORDER PR':
        	        series_seq = 'MRRE'
		else:
			series_seq = 'MRMR'

	if dn.doctype == 'Supplier Quotation':
		if naming_series == 'CONSUMABLE':
                	series_seq = 'QTCO'
		elif naming_series == 'FIXED ASSET':
	                series_seq = 'QTFA'
	        elif naming_series == 'CONSUMABLE SERVICE':
	                series_seq = 'QTCS'
		elif naming_series == 'WORKS':
        	        series_seq = 'QTWO'
		else:
			series_seq = 'QTQT'
	
	if dn.doctype == 'Request for Quotation':
		if naming_series == 'RFQ Consumable':
                	series_seq = 'RFQCO'
		elif naming_series == 'RFQ Capital Inventory':
	                series_seq = 'RFQCI'
	        elif naming_series == 'RFQ Miscellaneous Services':
	                series_seq = 'RFQMS'
		elif naming_series == 'RFQ Works':
        	        series_seq = 'RFQWO'
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

	
	return str(series_seq) + ".YYYY.MM"
