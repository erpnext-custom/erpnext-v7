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
                	series_seq = 'COPO'
		elif naming_series == 'FIXED ASSET PO':
	                series_seq = 'FAPO'
	        elif naming_series == 'CONSUMABLE SERVICE PO':
	                series_seq = 'CSPO'
		elif naming_series == 'WORKS PO':
        	        series_seq = 'WOPO'
		else:
			series_seq = 'POPO'
	
	if dn.doctype == 'Sales Order':
        	if naming_series == 'Coal Sales Order':
	                series_seq = 'COSO'
		elif naming_series == 'Dolomite Sales Order':
	                series_seq = 'DOSO'
	        elif naming_series == 'Gypsum Sales Order':
	                series_seq = 'GPSO'
		elif naming_series == 'Lime Stone Sales Order':
	                series_seq = 'LSSO'
		elif naming_series == 'Stone Sales Order':
	                series_seq = 'STSO'
		elif naming_series == 'Bauxite Sales Order':
	                series_seq = 'BASO'
		elif naming_series == 'Quartzite Sales Order':
	                series_seq = 'QZSO'
		else:
			series_seq = 'SOSO'
	
	if dn.doctype == 'Purchase Invoice':
		if naming_series == 'CONSUMABLE Invoice':
                	series_seq = 'COPI'
		elif naming_series == 'FIXED ASSET Invoice':
	                series_seq = 'FAPI'
	        elif naming_series == 'CONSUMABLE SERVICE Invoice':
	                series_seq = 'CSPI'
		elif naming_series == 'WORKS Invoice':
        	        series_seq = 'WOPI'
		else:
			series_seq = 'PIPI'

	if dn.doctype == 'Sales Invoice':
        	if naming_series == 'Coal Invoice':
	                series_seq = 'COSI'
		elif naming_series == 'Dolomite Invoice':
	                series_seq = 'DOSI'
	        elif naming_series == 'Gypsum Invoice':
	                series_seq = 'GPSI'
		elif naming_series == 'Lime Stone Invoice':
	                series_seq = 'LSSI'
		elif naming_series == 'Stone Invoice':
	                series_seq = 'STSI'
		elif naming_series == 'Bauxite Invoice':
	                series_seq = 'BASI'
		elif naming_series == 'Quartzite Invoice':
	                series_seq = 'QZSI'
		elif naming_series == 'Credit Invoice':
	                series_seq = 'CRSI'
		else:
			series_seq = 'SISI'

	if dn.doctype == 'Stock Entry':
        	if naming_series == 'Capital Inventory GR':
	                series_seq = 'CIGRSE'
		elif naming_series == 'Consumable GR':
	                series_seq = 'COGRSE'
	        elif naming_series == 'Capital Inventory GI':
	                series_seq = 'CIGISE'
		elif naming_series == 'Consumable GI':
	                series_seq = 'COGISE'
		elif naming_series == 'Inventory Transfer':
	                series_seq = 'INTXSE'
		elif naming_series == 'Coal GR':
	                series_seq = 'COGRSE'
		elif naming_series == 'Dolomite GR':
	                series_seq = 'DOGRSE'
		elif naming_series == 'Gypsum GR':
	                series_seq = 'GPGRSE'
		elif naming_series == 'Stone GR':
	                series_seq = 'STGRSE'
		elif naming_series == 'Limestone GR':
	                series_seq = 'LSGRSE'
		elif naming_series == 'Bauxite GR':
	                series_seq = 'BAGRSE'
		elif naming_series == 'Quartzite GR':
	                series_seq = 'QZGRSE'
		else:
			series_seq = 'SESESE'

	if dn.doctype == 'Delivery Note':
        	if naming_series == 'Coal Delivery':
	                series_seq = 'CODN'
		elif naming_series == 'Dolomite Delivery':
	                series_seq = 'DODN'
	        elif naming_series == 'Gypsum Delivery':
	                series_seq = 'GPDN'
		elif naming_series == 'Limestone Delivery':
	                series_seq = 'LSDN'
		elif naming_series == 'Stone Delivery':
	                series_seq = 'STDN'
		elif naming_series == 'Bauxite Delivery':
	                series_seq = 'BADN'
		elif naming_series == 'Quartzite Delivery':
	                series_seq = 'QZDN'
		elif naming_series == 'Return Delivery':
	                series_seq = 'REDN'
		else:
			series_seq = 'DNDN'

	if dn.doctype == 'Purchase Receipt':
		if naming_series == 'CONSUMABLE GR':
                	series_seq = 'COPR'
		elif naming_series == 'FIXED ASSET GR':
	                series_seq = 'FAPR'
	        elif naming_series == 'CONSUMABLE SERVICE Entry':
	                series_seq = 'CSPR'
		elif naming_series == 'WORKS Service Entry':
        	        series_seq = 'WOPR'
		elif naming_series == 'Goods Return/Rejection':
        	        series_seq = 'GRPR'
		else:
			series_seq = 'PRPR'

	if dn.doctype == 'Material Request':
		if naming_series == 'CONSUMABLE PR':
                	series_seq = 'COMR'
		elif naming_series == 'FIXED ASSET PR':
	                series_seq = 'FAMR'
	        elif naming_series == 'CONSUMABLE SERVICE PR':
	                series_seq = 'CSMR'
		elif naming_series == 'WORKS PR':
        	        series_seq = 'WOMR'
		elif naming_series == 'MINES PRODUCT PR':
        	        series_seq = 'MPMR'
		else:
			series_seq = 'MRMR'

	if dn.doctype == 'Supplier Quotation':
		if naming_series == 'CONSUMABLE':
                	series_seq = 'COQT'
		elif naming_series == 'FIXED ASSET':
	                series_seq = 'FAQT'
	        elif naming_series == 'CONSUMABLE SERVICE':
	                series_seq = 'CSQT'
		elif naming_series == 'WORKS':
        	        series_seq = 'WOQT'
		else:
			series_seq = 'QTQT'
	
	if dn.doctype == 'Request for Quotation':
		if naming_series == 'RFQ Consumable':
                	series_seq = 'CORFQ'
		elif naming_series == 'RFQ Capital Inventory':
	                series_seq = 'CIRFQ'
	        elif naming_series == 'RFQ Miscellaneous Services':
	                series_seq = 'MSRFQ'
		elif naming_series == 'RFQ Works':
        	        series_seq = 'WORFQ'
		else:
			series_seq = 'XXRFQ'
	
	if dn.doctype == 'Payment Entry':
                if naming_series == 'Bank Payment Voucher':
                        series_seq = 'BPPE'
                elif naming_series == 'Bank Receipt Voucher':
                        series_seq = 'BRPE'
                elif naming_series == 'Journal Voucher':
                        series_seq = 'JVPE'
                else:
                        series_seq = 'PEPE'

	
	return str(series_seq) + ".YYYY.MM"
