# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
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
			mr.name as mr_name, date(mr.creation) as mr_cra, date(mr.modified) as mr_modi, 
			mr.material_request_type as mr_typ, case mr.docstatus when 0 then 'Draft' else 'Submitted' end as mrs,
			po.name as po_name, date(po.creation) as po_cra, date(po.modified) as po_mod1, case po.docstatus when 0 then 'Draft' else 'Submitted' end as pos,
			pr.name as pr_name, date(pr.creation) as pr_cra, date(pr.modified) as pr_mod1, case pr.docstatus when 0 then 'Draft' else 'Submitted' end as prs,
			pi.name as pi_name, date(pi.creation) as pi_cra, date(pi.modified) as pi_modi, case pi.docstatus when 0 then 'Draft' else 'Submitted' end as pis
			from `tabMaterial Request` mr
			left join `tabPurchase Order Item` poi
			on poi.material_request = mr.name and mr.docstatus < 2
			left join `tabPurchase Order` po
			on po.name = poi.parent and po.docstatus < 2
			left join
			`tabPurchase Receipt Item` pri on
			pri.purchase_order = po.name
			left join
			`tabPurchase Receipt` pr  on pr.name = pri.parent and pr.docstatus < 2
			left join 
			`tabPurchase Invoice Item` pii on
			pii.purchase_receipt = pr.name
			left join `tabPurchase Invoice` pi
			on pi.name = pii.parent and pi.docstatus < 2"""
	return frappe.db.sql(query)

def get_columns(filters):
        cols = [
                ("MR Name") + ":Link/Material Request:120",
                ("MR Created Date") + ":Date:120",
                ("MR Last Modified") + ":Date:120",
                ("MR Type") + ":Data:120",
                ("MR Status") + ":Data:120",
                ("PO Name") + ":Link/Purchase Order:120",
                ("PO Created Date") + ":Date:120",
                ("PO Last Modified") + ":Date:120",
                ("PO Status") + ":Data:120",
                ("PR Name") + ":Link/Purchase Receipt:120",
                ("PR Created Date") + ":Date:120",
                ("PR Last Modified") + ":Date:120",
                ("PR Status") + ":Data:120",
                ("PI Name") + ":Link/Purchase Invoice:120",
                ("PI Created Date") + ":Date:120",
                ("PI Modified") + ":Date:120",
                ("PI Status") + ":Data:120"

        ]
        return cols                  


