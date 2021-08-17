# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    if filters.get("dispatch_type") == "Incoming":
        columns, data = get_columns(filters), get_data(filters)
    else:
        columns, data = get_outgoing_coulmns(filters), get_outgoing_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
            _("Dispatch Name") + ":Link/Dispatch:100", 
            _("Dispatch Type") + ":Data:100", 
            _("Agency From") + ":Data:200",
            _("Date") + "::100",
            _("Dispatch No.") + ":Data:200",
            _("Subject") + "::200",
            _("Address") + "::400",
            _("Remarks") + "::400"
    ]
    return columns

def get_data(filters):
    data = frappe.db.sql(
        """
        select 
            name, dispatch_type, agency_from, date, dispatch_no, subject, address, remarks
        from `tabDispatch` where docstatus = 1 and dispatch_type = "Incoming" order by date desc
        """
    )
    return data


def get_outgoing_coulmns(filters):
    columns =[
        _("Dispatch Name") + ":Link/Dispatch:100", 
        _("Dispath Type") + "::100",
        _("Date") + "::100",
        _("Subject") + "::100",
        _("Dispatch Format") + "::200",
        _("Dispatch Serial No.") + "::100",
        _("Dispatch No.") + "::200",
        _("Old Dispatch No") + "::150",
        _("To Whom") + "::100",
        _("Place") + "::200",
        _("Remarks") + "::400"
    ]
    return columns

def get_outgoing_data(filters):
    data = frappe.db.sql(
        """
        select 
            name, dispatch_type, date, subject, dispatch_format, dispatch_serial_no, dispatch_no, old_dispatch_no, to_whom, place, remarks
        from `tabDispatch` where docstatus = 1 and dispatch_type = "Out-Going" order by date desc
        """
    )
    return data