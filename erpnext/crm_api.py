from __future__ import unicode_literals
import frappe
import urlparse
from frappe import _
from frappe.utils import cint, flt, now, get_datetime
from erpnext.crm.doctype.site.site import has_pending_transactions
from erpnext.integrations import BFSSecure, SendSMS
from frappe.custom_utils import cancel_draft_doc

#bench execute erpnext.crm_api.init_payment --args "'ORDR200100020','1010','100635222',1"
@frappe.whitelist()
def init_payment(customer_order=None, bank_code=None, bank_account=None, amount=0):
	''' start new payment transaction '''
	# TEMPORARILY MADE AMOUNT 1
	if not customer_order:
		frappe.throw(_("Invalid Order"))
	elif not bank_code:
		frappe.throw(_("Invalid Remitter Bank"))
	elif not bank_account:
		frappe.throw(_("Invalid Remitter Account No"))
	elif not flt(amount):
		frappe.throw(_("Invalid Amount"))
	#amount = 1

	# LOG
	print '#'*60
	print '#','METHOD	   :','init_payment'
	print '#','CUSTOMER_ORDER   :',customer_order
	print '#','BANK_CODE        :',bank_code
	print '#','BANK_ACCOUNT     :',bank_account
	print '#','AMOUNT           :',flt(amount)
	print '#'*60

	# BFSSecure
	bfs 		= BFSSecure()
	response	= None
	error_msg	= None
	status		= None

	req 		= bfs.auth_request(customer_order, bank_code, bank_account, amount)	
	if req.error_msg:
		response  = req.response
		error_msg = req.error_msg
		status 	  = req.status
	else:
		req = bfs.account_inquiry()
		if req.error_msg:
			response  = req.response
			error_msg = req.error_msg
			status 	  = req.status
		else:
			response  = req.response
			error_msg = req.error_msg
			status 	  = req.status
	print
	print '#','ONLINE_PAYMENT   :',bfs.order_no
	print '#','TRANSACTION_ID   :',bfs.transaction_id
	print '#','TRANSACTION_TIME :',bfs.transaction_time
	print
	if error_msg:
		frappe.throw(_(error_msg))
	return ({'transaction_id': bfs.transaction_id})

@frappe.whitelist()
def make_payment(customer_order=None, otp=None):
	''' make debit request '''
	if not customer_order:
		frappe.throw(_("Invalid Order"))
	elif not otp:
		frappe.throw(_("Invalid OTP"))
		
	# LOG
	print '#'*60
	print '#','METHOD	   :','make_payment'
	print '#','CUSTOMER_ORDER   :',customer_order
	print '#'*60

	# BFSSecure
	bfs 		= BFSSecure()
	response	= None
	error_msg	= None
	status		= None

	req = bfs.debit_request(customer_order, otp)
	if req.error_msg:
		response  = req.response
		error_msg = req.error_msg
		status	  = req.status
	else:
		pass

	if error_msg:
		frappe.throw(_(error_msg))
	return({
		'transaction_id': bfs.order_no,
		'transaction_time': bfs.transaction_time_fmt,
		'amount': flt(bfs.amount),
	})

@frappe.whitelist()
def check_payment(customer_order):
	''' check payment status '''
	# BFSSecure
	bfs 		= BFSSecure()
	response	= None
	error_msg	= None
	status		= None

	req = bfs.auth_status(customer_order)
	if req.error_msg:
		response  = req.response
		error_msg = req.error_msg
		status	  = req.status
	else:
		pass

	if error_msg:
		frappe.throw(_(error_msg))

@frappe.whitelist()
def branch_source(item_sub_group):
	""" get list of branches based on material """
	if not item_sub_group:
		frappe.throw(_("Please select a material first"))

	bl = frappe.db.sql("""
		select distinct cbs.branch, cbs.has_common_pool, cbs.allow_self_owned_transport, cbs.allow_other_transport
		from `tabCRM Branch Setting` cbs, `tabCRM Branch Setting Item` cbsi
		where cbsi.item_sub_group = "{0}"
		and cbs.name = cbsi.parent
	""".format(item_sub_group), as_dict=True)

	if not bl:
		frappe.throw(_("No material source found"))
	return bl

@frappe.whitelist()
def set_site_status(site, status):
	''' Do not allow change of site status if user has pending transactions '''
	if not cint(status) and has_pending_transactions(site):
		frappe.throw(_("You cannot disable the site as there are pending transactions"))

	# create and submit Site Status 
	doc = frappe.get_doc({
		"doctype": "Site Status",
		"approval_status": "Approved",
		"user": frappe.session.user,
		"site": site,
		"change_status": "Activate" if cint(status) else "Deactivate",
		"remarks": "Self"
	})
	doc.save(ignore_permissions = True)
	doc.submit()

@frappe.whitelist()
def deregister_vehicle(vehicle, user):
	''' Do not allow to deregister vehicle if user has pending transactions '''
	#if has_pending_transactions(vehicle):
	#	frappe.throw(_("You cannot deregister the site as there are pending transactions"))
	
	v_doc = frappe.get_doc("Vehicle", vehicle)
	if v_doc.vehicle_status not in ["Active","Approved"]:
		frappe.throw(_("Vechile not allowed to deregister because its {0}".format(v_doc.vehicle_status)))
	else:
		# Update Vehicle Status	
		v_doc.db_set('vehicle_status',"Deregistered")
		# Update Transport Request
		frappe.db.sql("update `tabTransport Request` set approval_status = 'Deregistered' where vehicle_no = '{0}' and approval_status = 'Approved' and user = '{1}'".format(vehicle, user))
		frappe.msgprint("Vehicle deregistration successful")

@frappe.whitelist()
def delivery_confirmation(delivery_note, user, remarks=None):
	if not delivery_note or not user:
		frappe.throw("Delivery Note no or User ID is missing")
	import datetime
	received_datetime =  datetime.datetime.now()
	
	frappe.db.sql("update `tabDelivery Confirmation` set confirmation_status = 'Received', received_date_time = '{0}', remarks = '{1}' where  delivery_note = '{2}' and user = '{3}'".format(received_datetime, remarks, delivery_note, user))
	frappe.db.sql("update `tabLoad Request` set load_status = 'Delivered'  where delivery_note = '{0}'".format(delivery_note))


@frappe.whitelist()
def cancel_load_request(user, vehicle):
	if not user or not vehicle:
		frappe.throw("Either User ID or Vehicle No is missing")
	frappe.db.sql("update `tabLoad Request` set docstatus = 2, load_status = 'Cancelled' where user = '{0}' and vehicle = '{1}' and load_status = 'Queued'".format(user, vehicle))


@frappe.whitelist(allow_guest=True)
def success(**args):
	frappe.respond_as_web_page(_("Payment is Successful"),
		_("This is just a test URL without any batteries included."),
	)

	return

@frappe.whitelist(allow_guest=True)
def cancel(**args):
	frappe.respond_as_web_page(_("Payment is Cancelled"),
		_("This is just a test URL without any batteries included."),
	)

	return

@frappe.whitelist(allow_guest=True)
def failure(**args):
	frappe.respond_as_web_page(_("Payment Failed"),
		_("This is just a test URL without any batteries included."),
	)

	return

@frappe.whitelist()
def webpay(**args):
	import requests
	url = "http://uatbfssecure.rma.org.bt:8080/BFSSecure/makePayment?bfs_benfTxnTime=20200122151200&bfs_txnCurrency=BTN&bfs_paymentDesc=TestPayment&bfs_benfId=BE10000103&bfs_remitterEmail=sivasankar.k2003%40gmail.com&bfs_version=1.0&bfs_checkSum=01D8CB6FA42C8A2C5239873989C907502FD45379C44D0D2B8F18860D13FFBBD3C2E9C7613956ADBA0FF284F0FAE041BBB66BD6F98D8A50B735A5EA8B42A290720D514671C8E4FF275F3F1041CF29BA9275A772E3147CC6B5DC80A6C16CC65FF464070927344E7EC96AFE03F6FB8D614AE189BC22E506AD4EBEDF3C053B82E60D48B408EDB6AA6C00D68E8F347E6EE32F23F1483706141E4CBE1A8D4218B206122CBE0FEF1A957EE0FF18F3A77949B24C8F796083FA77EF71A196CCC6FE3BF2173FBECD56965C217194865FC4106BC81586E09810720711B6FA39130D778B8D466F62D9D9FBB6C595F64BD70BDE939EAAF4FE289C068764B0E2F3A54C0370&bfs_benfBankCode=01&bfs_txnAmount=1.00&bfs_orderNo=20200123175903&bfs_msgType=AR"
	#frappe.local.response["type"] = "redirect"
	#frappe.local.response["location"] = url
	#with requests.Session() as s:
	#	res = s.post(url)
	return url
	

@frappe.whitelist(allow_guest=True)
def sendsms(**args):
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
	SYSTEM_ID = 'nrdcl2'
	SYSTEM_PASS = 'nrdcl@btl'
	#SYSTEM_ID = 'vas1'
	#SYSTEM_PASS = 'vasbtl18'
	USER_TYPE = "bind_transceiver"
	SENDER_ID = "BTL_TEST" if not args.get('sender') else args.get('sender')
	DESTINATION_NO = args.get('mobileno')
	#DESTINATION_NO = "97517115380"
	MESSAGE = "from "+SYSTEM_ID
	send_sms()

	return args

@frappe.whitelist(allow_guest=True)
def make_payment_request(**args):
	"""Make payment request"""

	args = frappe._dict(args)

	# print from GET request
	#frappe.msgprint(_("{0}").format(args))

	# print from POST request
	#frappe.msgprint(_("{0}").format(args.data))
	return args.data

	#data = frappe._dict()
	#data.success = "True"
	#return data	

	''' WORKS GOOD
	frappe.respond_as_web_page(_("Something went wrong"),
		_("Looks like something went wrong during the transaction. Since we haven't confirmed the payment."),
	)

	return
	'''

	''' REDIRECTION WORKS PERFECTLY
	frappe.local.response["type"] = "redirect"
	frappe.local.response["location"] = "/"
	'''

	'''
	ref_doc = frappe.get_doc(args.dt, args.dn)

	gateway_account = get_gateway_details(args) or frappe._dict()

	grand_total = get_amount(ref_doc, args.dt)

	existing_payment_request = frappe.db.get_value("Payment Request",
		{"reference_doctype": args.dt, "reference_name": args.dn, "docstatus": ["!=", 2]})

	if existing_payment_request:
		pr = frappe.get_doc("Payment Request", existing_payment_request)

	else:
		pr = frappe.new_doc("Payment Request")
		pr.update({
			"payment_gateway_account": gateway_account.get("name"),
			"payment_gateway": gateway_account.get("payment_gateway"),
			"payment_account": gateway_account.get("payment_account"),
			"currency": ref_doc.currency,
			"grand_total": grand_total,
			"email_to": args.recipient_id or "",
			"subject": "Payment Request for %s"%args.dn,
			"message": gateway_account.get("message") or get_dummy_message(args.use_dummy_message),
			"reference_doctype": args.dt,
			"reference_name": args.dn
		})

		if args.return_doc:
			return pr

		if args.mute_email:
			pr.flags.mute_email = True

		if args.submit_doc:
			pr.insert(ignore_permissions=True)
			pr.submit()

	if hasattr(ref_doc, "order_type") and getattr(ref_doc, "order_type") == "Shopping Cart":
		generate_payment_request(pr.name)
		frappe.db.commit()

	if not args.cart:
		return pr
	'''

@frappe.whitelist()
def cancel_customer_order(customer_order):
	cancel_draft_doc('Customer Order', customer_order)

