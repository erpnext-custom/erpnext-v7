# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import get_bench_path
import logging
import sys
import smpplib.gsm
import smpplib.client
import smpplib.consts
import time
from datetime import datetime

def SendSMS(sender, receiver, message, debug=0):
	SMSC_HOST = '119.2.115.41'
	SMSC_PORT = '9000'
	SYSTEM_ID = 'nrdcl2'
	SYSTEM_PASS = 'nrdcl@btl'
	USER_TYPE = "bind_transceiver"
	SENDER_ID =  str(sender)
	DESTINATION_NO = str(receiver)
	MESSAGE   = str(message)
	flag	  = 0
	timestamp = datetime.now().strftime("%Y%m%d")

	
	if not sender or not receiver or not message:
		return flag
	elif len(str(receiver)[-8:]) < 8:
		return flag
	elif str(receiver)[-8:][:2] not in ('17','16','77'):
		return flag
	else:
		DESTINATION_NO = "975"+str(DESTINATION_NO)[-8:]

	try:
		# if you want to know what's happening
		if debug:
			log_file = str(get_bench_path())+'/logs/sms_smpp_{0}.log'.format(timestamp)
			logging.basicConfig(filename=log_file, filemode='w', level='DEBUG')
        		logger = logging.getLogger(__name__)
			logger.info("MSISDN: {}".format(DESTINATION_NO))
			logger.info("TRANSACTION_TIME: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

		# Two parts, UCS2, SMS with UDH
		parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(MESSAGE)
		client = smpplib.client.Client(SMSC_HOST, int(SMSC_PORT))

		# Print when obtain message_id
		client.set_message_sent_handler(
			lambda pdu: sys.stdout.write('sent {} {}\n'.format(pdu.sequence, pdu.message_id))
		)
		client.set_message_received_handler(
			lambda pdu: sys.stdout.write('delivered {}\n'.format(pdu.receipted_message_id))
		)

		client.connect()
		if USER_TYPE == "bind_transceiver":
			client.bind_transceiver(system_id=SYSTEM_ID, password=SYSTEM_PASS)
		if USER_TYPE == "bind_tranmitter":
			client.bind_tranmitter(system_id=SYSTEM_ID, password=SYSTEM_PASS)

		for part in parts:
			pdu = client.send_message(
				source_addr_ton=smpplib.consts.SMPP_TON_INTL,
				#source_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
				# Make sure it is a byte string, not unicode:
				source_addr=str(SENDER_ID),
				dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
				#dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
				# Make sure thease two params are byte strings, not unicode:
				destination_addr=str(DESTINATION_NO),
				short_message=part,
				data_coding=encoding_flag,
				esm_class=msg_type_flag,
				registered_delivery=True,
			)
			print(pdu.sequence)
			client.read_pdu()
		client.unbind()
		client.disconnect()
		flag = 1
	except ValueError, e:
		print e
		pass
	except Exception:
		pass

	return flag
