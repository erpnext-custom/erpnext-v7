#Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate
from frappe import utils
utils.now()
utils.today()


def execute(filters=None):
        columns = get_columns(filters)
	data = get_data(filters)
        return columns, data

def get_data(filters):
	#today = frappe.utils.nowdate()
	#frappe.msgprint("{0}".format(today))
	query =  """select distinct
			mr.name as mr_name, date(mr.creation) as mr_cra, date(mr.transaction_date) as tr, mr.workflow_state as mr_status,
			mr.owner as ownm, 1, mr.material_request_type as mr_typ,
			po.name as po_name, date(po.creation) as po_cra, date(po.transaction_date) as tr, po.status as po_status,
            po.owner as ownp, po.modified_by as mop,
			pr.name as pr_name, date(pr.creation) as pr_cra, date(pr.posting_date) as pr_mod1, pr.status as pr_status,
			pr.owner as onrr, pr.modified_by as mor,
			pi.name as pi_name, date(pi.creation) as pi_cra, date(pi.posting_date) as pi_modi,
			case
			when pi.is_return = 1 then "Return"
			when pi.is_return =  0 and pi.outstanding_amount > 0 and pi.docstatus = 1 and datediff(pi.due_date, curdate())<0 then "Overdue"
			when  pi.is_return =  0 and pi.outstanding_amount > 0 and pi.docstatus = 1 and datediff(pi.due_date, curdate()) >= 0 then "Unpaid"
			when pi.is_return = 0 and pi.outstanding_amount = 0 and pi.docstatus = 1 then "Paid"
			when pi.docstatus = 0 then "Draft"
			when pi.docstatus = 2 then "Cancelled"
			end as pi_status,
			pi.owner as owni, pi.modified_by as moii
			from `tabMaterial Request` mr
			left join  `tabPurchase Order Item` poi
			on  poi.material_request = mr.name
			left join `tabPurchase Order` po
			on po.name = poi.parent
			left join
			`tabPurchase Receipt Item` pri on
			pri.purchase_order = po.name
			left join
			`tabPurchase Receipt` pr  on pr.name = pri.parent
			left join
			`tabPurchase Invoice Item` pii on
			pii.purchase_receipt = pr.name
			left join `tabPurchase Invoice` pi
			on pi.name = pii.parent"""
	return frappe.db.sql(query)

def get_columns(filters):
        cols = [
                ("MR Name") + ":Link/Material Request:120",
		        ("MR Create Date") + ":Date:120",
                ("MR Submit Date") + ":Date:120",
                ("Mr Status") + ":Data:120",
		        ("MR Owner") + ":Link/User:140",
		        ("Forward To Procurment") + ":Data:120",
                ("MR Type") + ":Data:120",
                ("PO Name") + ":Link/Purchase Order:120",
                ("PO Create Date") + ":Date:120",
		        ("PO Submit Date") + ":Date:120",
                ("PO Status") + ":Data:120",
		        ("PO Owner") + ":Link/User:140",
                ("PO Updated By") + ":Link/User:140",
                ("PR Name") + ":Link/Purchase Receipt:120",
                ("PR Create Date") + ":Date:120",
                ("PR Submit Date") + ":Date:120",
                ("PR Status") + ":Data:120",
		        ("PR Owner") + ":Link/User:140",
                ("PR Updated By") + ":Link/User:140",
                ("PI Name") + ":Link/Purchase Invoice:120",
                ("PI Create Date") + ":Date:120",
                ("PI Posting Date") + ":Date:120",
                ("PI Status") + ":Data:120",
		        ("PI Owner") + ":Link/User:140",
                ("PI updated By") + ":Link/User:140",

        ]
        return cols
