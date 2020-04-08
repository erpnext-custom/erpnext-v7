
import logging
import sys

import smpplib.gsm
import smpplib.client
import smpplib.consts

def send_sms(*args):
    try:
        # if you want to know what's happening

        logging.basicConfig(filename='sms_smpp.log', filemode='w', level='DEBUG')

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
                source_addr=SENDER_ID,

                dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
                #dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
                # Make sure thease two params are byte strings, not unicode:
                destination_addr=DESTINATION_NO,
                short_message=part,

                data_coding=encoding_flag,
                esm_class=msg_type_flag,
                registered_delivery=True,
            )
            print(pdu.sequence)

        client.unbind()
        client.disconnect()

    except ValueError:
        pass

SMSC_HOST = '119.2.115.41'
SMSC_PORT = '9000'
#SYSTEM_ID = 'vas1'
#SYSTEM_PASS = 'vasbtl18'
SYSTEM_ID = 'nrdcl2'
SYSTEM_PASS = 'nrdcl@btl'
USER_TYPE = "bind_transceiver"
SENDER_ID = "NRDCL"
DESTINATION_NO = "97517115380"
MESSAGE = "from "+SYSTEM_ID
send_sms()

