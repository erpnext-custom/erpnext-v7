# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests, json
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, get_datetime, get_url, nowdate, now_datetime, money_in_words
from erpnext.custom_utils import check_future_date

class UtilityBill(Document):
    def validate(self):
        check_future_date(self.posting_date)
        self.calculate_tds_net()
        
        if self.docstatus == 1:
            self.utility_payment()

    def on_submit(self):
        self.make_direct_payment()
    
    def on_cancel(self):
        frappe.throw("Not allowed to cancel the Utility Bill Payments")
    
    def calculate_tds_net(self):
        total_amount = total_tds = net_amount = 0.00
        for a in self.item:
            total_amount += a.invoice_amount
            total_tds += a.tds_amount
            net_amount += a.net_amount
        self.total_bill_amount = total_amount
        self.total_tds_amount = total_tds
        self.net_payable_amount = net_amount
        
        if not self.net_payable_amount:
            frappe.throw("Net Payable amount should be greater than zero")
    
    def utility_payment(self):
        for d in self.item:
            if d.outstanding_amount > 0 and not d.payment_status_code:
                api_name, service_id, service_type, consumer_field = frappe.db.get_value("Utility Service Type", d.utility_service_type, ["payment_api", "service_id", "service_type", "unique_key_field"])
                api_details = frappe.get_doc("API Detail", api_name)
                url = api_details.api_link
                api_param = {}
                for a in api_details.item:
                    if a.pre_defined_value:
                        api_param[a.param] = str(a.defined_value)
                    elif a.param == "serviceid":
                        api_param[a.param] = str(service_id)
                    elif a.param == "servicetype":
                        api_param[a.param] = str(service_type)
                    elif a.param == "FrmAcctNum":
                        api_param[a.param] = str(self.bank_account)
                    elif a.param == "Amt":
                        api_param[a.param] = str(d.outstanding_amount)
                    elif a.param == "pi":
                        api_param[a.param] = "RN" + str(service_id) + str(self.name)
                api_param[consumer_field] = str(d.consumer_code)
                
                payload = json.dumps(api_param)
                d.request = str(payload)
                headers = {
                'Content-Type': 'application/json'
                }               
                response = requests.request("POST", url, headers=headers, data=payload)
                details = response.json()
                d.response = str(details)
                res_status = details['statusCode']
                d.payment_status_code = res_status
                if res_status == "00":
                    d.payment_response_msg = details['ResultMessage']
                    d.payment_journal_no = details['jrnlno']
                    d.payment_status = "Success"
                else:
                    d.payment_response_msg = details['ErrorMessage']
                    d.payment_status = "Failed"

    def get_utility_services(self):
        data = []
        data = frappe.db.sql("""
                      SELECT 
                        i.utility_service_type, i.customer_identification, 
                        i.consumer_code, i.party,
                        i.service_id, i.service_type
                      FROM `tabUtility Services` u 
                      INNER JOIN `tabUtility Services Item` i
                      ON u.name = i.parent
                      WHERE i.disabled = 0
                        and u.name = '{}'
                       """.format(self.utility_services), as_dict=True)
        # and r.docstatus = 1
        self.set('item', [])
        for d in data:
            row = self.append('item', {})
            api_name, service_id, service_type, consumer_field, expense_account = frappe.db.get_value("Utility Service Type", d.utility_service_type, ["fetch_outstanding_api", "service_id", "service_type", "unique_key_field","expense_account"])
            api_details = frappe.get_doc("API Detail", api_name)
            url = api_details.api_link
            api_param = {}
            for a in api_details.item:
                if a.pre_defined_value:
                    api_param[a.param] = a.defined_value
                elif a.param == "SERVICEID":
                    api_param[a.param] = service_id
                elif a.param == "SERVICETYPE":
                    api_param[a.param] = service_type
            api_param[consumer_field.upper()] = d.consumer_code
            
            payload = json.dumps(api_param)
            headers = {
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            details = response.json()
            res_status = details['statusCode']
            row.payment_status = "Pending"
            if res_status == "00":
                row.invoice_amount = details['ResultMessage']
                row.outstanding_amount = details['ResultMessage']
                row.response_msg = "Success"
                row.net_amount = details['ResultMessage']
            elif res_status == "01":
                row.response_msg = details['ErrorMessage']
            row.debit_account = expense_account
            row.outstanding_datetime = now_datetime()
            row.fetch_status_code = res_status
            row.create_direct_payment = 1
            row.update(d)

    def make_direct_payment(self):
        doc = frappe.new_doc("Direct Payment")
        doc.branch = self.branch
        doc.cost_center = self.cost_center
        doc.posting_date = self.posting_date
        doc.payment_type = "Payment"
        doc.tds_percent = self.tds_percent
        doc.tds_account = self.tds_account
        doc.credit_account = self.expense_account
        doc.business_activity = self.business_activity
        doc.remarks = "Utility Bill Payment " + str(self.name)
        if self.item:
            count_child = 0
            for a in self.item:
                if a.create_direct_payment:
                    if a.invoice_amount > 0 and a.payment_status == "Success":
                        doc.append("item", {
                                "party_type": "Supplier",
                                "party": a.party,
                                "account": a.debit_account,
                                "amount": a.invoice_amount,
                                "invoice_no": a.invoice_no,
                                "invoice_date": a.invoice_date,
                                "tds_applicable": a.tds_applicable,
                                "taxable_amount": a.invoice_amount,
                                "tds_amount": a.tds_amount,
                                "net_amount": a.net_amount,
                            })
                        count_child +=1
            if count_child > 0:
                doc.submit()
            if doc.name:
                self.db_set("direct_payment", doc.name)
                frappe.msgprint("Direct Payment created and submitted for this Utility Bill")