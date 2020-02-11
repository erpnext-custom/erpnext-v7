from __future__ import unicode_literals
import frappe
import urlparse
from frappe import _
from frappe.utils import cint, flt, now, get_datetime
from erpnext.crm.doctype.site.site import has_pending_transactions
from erpnext.integrations import BFSSecure

#bench execute erpnext.crm_api.init_payment --args "'ORDR200100020','1010','100635222',1"
#@frappe.async.handler
@frappe.whitelist(allow_guest=True)
def init_payment(customer_order, bank_code, bank_account, amount):
	''' start new payment transaction '''
	# TEMPORARILY MADE AMOUNT 1
	amount = 1
	# BFSSecure
	bfs 		= BFSSecure()
	bfs.customer_order = customer_order
	bfs.bank_code	= bank_code
	bfs.bank_account= bank_account
	bfs.amount	= flt(amount)
	response	= None
	error_msg	= None
	status		= None

	# AR Request
	bfs.create_online_payment()
	auth_request 	= bfs.auth_request()	
	if auth_request.error_msg:
		response  = auth_request.response
		error_msg = auth_request.error_msg
		status 	  = auth_request.status
	else:
		account_inquiry = bfs.account_inquiry()
		if account_inquiry.error_msg:
			response  = account_inquiry.response
			error_msg = account_inquiry.error_msg
			status 	  = account_inquiry.status
		else:
			response  = account_inquiry.response
			error_msg = account_inquiry.error_msg
			status 	  = account_inquiry.status
	if error_msg:
		frappe.throw(_(error_msg))
	return bfs.transaction_id

@frappe.whitelist()
def make_payment(transaction_id, otp):
	# BFSSecure
	bfs 		= BFSSecure()
	bfs.transaction_id = transaction_id
	bfs.otp		= otp
	response	= None
	error_msg	= None
	status		= None

	bfs.get_online_payment()
	debit_request = bfs.debit_request()
	if debit_request.error_msg:
		response  = debit_request.response
		error_msg = debit_request.error_msg
		status	  = debit_request.status
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
		select distinct cbs.branch, cbs.has_common_pool
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
def deregister_vehicle(vehicle):
	''' Do not allow to deregister vehicle if user has pending transactions '''
	#if has_pending_transactions(vehicle):
	#	frappe.throw(_("You cannot deregister the site as there are pending transactions"))
	
	v_doc = frappe.get_doc("Vehicle", vehicle)
	if v_doc.vehicle_status != "Active":
		frappe.throw(_("Vechile not allowed to deregister because its {0}".format(v_doc.vehicle_status)))		

	v_doc.db_set('vehicle_status',"Deregistered")

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

