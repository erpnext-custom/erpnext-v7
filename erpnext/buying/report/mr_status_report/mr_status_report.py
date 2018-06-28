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
    conditions, filters = get_conditions(filters)
    query = frappe.db.sql("""select distinct
			mr.name as mr_name, mr.creation_date as mr_cra,
			case when mr.workflow_state != 'Draft' then mr.transaction_date else '' end as tr, mr.workflow_state as mr_status,
			mr.owner as ownm, case when mr.workflow_state = 'Approved' and mr.material_request_type = "Purchase"  then
			mr.transaction_date else '' end as ftp, mr.material_request_type as mr_typ,
			po.name as po_name, po.creation as po_cra, case when po.docstatus = !0  then po.transaction_date else '' end as tr1,
			po.status as po_status,
                        po.owner as ownp, po.modified_by as mop,
			pr.name as pr_name, pr.creation as pr_cra, case when pr.status != 'Draft' then pr.posting_date else '' end as pr_mod1, pr.status as pr_status,
			pr.owner as onrr, pr.modified_by as mor,
			pi.name as pi_name, pi.creation as pi_cra, case when pi.docstatus != 0 then pi.posting_date else '' end as pi_modi,
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
			left join  `tabPurchase Order Item` poi on poi.material_request = mr.name
            left join `tabPurchase Order` po on po.name = poi.parent
            left join `tabPurchase Receipt Item` pri on pri.purchase_order = po.name
            left join `tabPurchase Receipt` pr on pr.name = pri.parent
            left join `tabPurchase Invoice Item` pii on pii.purchase_receipt = pr.name
            left join `tabPurchase Invoice` pi on pi.name = pii.parent
			where {0}""".format(conditions))
    #frappe.msgprint("{0}".format(query))
    return query
def get_conditions(filters):
	conditions = ""
	if filters.get("month"):
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
			"Dec"].index(filters["month"]) + 1
		filters["month"] = month
		frappe.msgprint(month)
		conditions += " month(mr.creation_date) = {0}".format(filters["month"])

	if filters.get("fiscal_year"): conditions += " and year(mr.creation) = {0}".format(filters.get("fiscal_year"))

	conditions += " and mr.workflow_state  != 'Cancelled'"
	conditions += " and case when po.docstatus IS NOT NULL then po.docstatus != 2 else 1 =1 end"
	conditions += " and case when pr.status IS NOT NULL then pr.status != 'Cancelled' else 1 =1 end"
	conditions += " and case when pi.docstatus IS NOT NULL then pi.docstatus != 2 else 1 =1 end"

	#and ifnull(1 =1, pi.docstatus != 2)"
	return conditions, filters

def get_columns(filters):
        cols = [
                ("MR Name") + ":Link/Material Request:120",
		        ("MR Create Date") + ":Date:100",
                ("MR Submit Date") + ":Date:110",
                ("Mr Status") + ":Data:100",
		        ("MR Owner") + ":Link/User:140",
		        ("Forward To Procurment") + ":Data:100",
                ("MR Type") + ":Data:120",
                ("PO Name") + ":Link/Purchase Order:120",
                ("PO Create Date") + ":Date:100",
		        ("PO Submit Date") + ":Date:100",
                ("PO Status") + ":Data:100",
		        ("PO Owner") + ":Link/User:140",
                ("PO Updated By") + ":Link/User:140",
                ("PR Name") + ":Link/Purchase Receipt:120",
                ("PR Create Date") + ":Date:100",
                ("PR Submit Date") + ":Date:100",
                ("PR Status") + ":Data:100",
		        ("PR Owner") + ":Link/User:140",
                ("PR Updated By") + ":Link/User:140",
                ("PI Name") + ":Link/Purchase Invoice:120",
                ("PI Create Date") + ":Date:100",
                ("PI Posting Date") + ":Date:100",
                ("PI Status") + ":Data:100",
		        ("PI Owner") + ":Link/User:140",
                ("PI updated By") + ":Link/User:140",

        ]
        return cols
