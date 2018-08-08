# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SHIV		                   18/07/2018         1) Option to select doctype introduced.
                                                                      2) Date format changed
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class ChequePrintTemplate(Document):
	pass

@frappe.whitelist()
def create_or_update_cheque_print_format(template_name, doctype_name=''):
        party = ""
        amount = ""
        if not doctype_name:
                frappe.throw(_("Please select a valid doctype."))
                
	if not frappe.db.exists("Print Format", template_name):
		cheque_print = frappe.new_doc("Print Format")
		cheque_print.update({
			"doc_type": doctype_name,
			"standard": "No",
			"custom_format": 1,
			"print_format_type": "Server",
			"name": template_name
		})
	else:
		cheque_print = frappe.get_doc("Print Format", template_name)
	
	doc = frappe.get_doc("Cheque Print Template", template_name)

	date_formats = {
                'DD-MM-YYYY': 'dd-MM-YYYY',
                'YYYY-MM-DD': 'YYYY-MM-dd',
                'DDMMYYYY': 'ddMMYYYY'
        }[doc.date_formats]

        if doc.doctype_name == "Payment Entry":
                party = "doc.party"
        elif doc.doctype_name == "HSD Payment":
                party = "doc.supplier"
        else:
                party = "doc.pay_to_recd_from"

	cheque_print.html = """
<div style="position: relative; top:{starting_position_from_top_edge}cm; font-size:15px;">
	<div style="width:{cheque_width}cm;height:{cheque_height}cm;">
		<span style="top:{acc_pay_dist_from_top_edge}cm; left:{acc_pay_dist_from_left_edge}cm;
			border-bottom: solid 1px;border-top:solid 1px; position: absolute;">
				<!-- {message_to_show} -->
		</span>
		<span style="top:{date_dist_from_top_edge}cm; left:{date_dist_from_left_edge}cm;
			position: absolute; letter-spacing:{date_letter_spacing}cm">
			<!-- {{ doc.reference_date or '' }} -->
			{{%- if doc.doctype == 'Payment Entry' -%}}
                                {{{{frappe.utils.formatdate(doc.reference_date,'{date_formats}') if doc.reference_date else '' }}}}
                        {{%- else -%}}
                                {{{{frappe.utils.formatdate(doc.cheque_date,'{date_formats}') if doc.cheque_date else '' }}}}
                        {{%- endif -%}}
		</span>
		<span style="top:{acc_no_dist_from_top_edge}cm;left:{acc_no_dist_from_left_edge}cm;
			position: absolute;">
			{{{{ doc.account_no or '' }}}}
		</span>
		<span style="top:{payer_name_from_top_edge}cm;left: {payer_name_from_left_edge}cm;
			position: absolute;">
			<!-- {{ doc.party }} -->
			{{{{ {party} }}}}
		</span>
		<span style="top:{amt_in_words_from_top_edge}cm; left:{amt_in_words_from_left_edge}cm;
			position: absolute; display: block; width: {amt_in_word_width}cm;
			line-height:{amt_in_words_line_spacing}cm; word-wrap: break-word;">
				<!-- {{frappe.utils.money_in_words(doc.base_paid_amount or doc.base_received_amount)}} -->
				{{%- if doc.doctype == 'Payment Entry' -%}}
                                        {{{{frappe.utils.money_in_words(doc.base_paid_amount or doc.base_received_amount)[3:]}}}}
                                {{%- elif doc.doctype == 'Imprest Recoup' -%}}
                                        {{{{frappe.utils.money_in_words(doc.purchase_amount)[3:]}}}}
                                {{%- elif doc.doctype == 'HSD Payment' -%}}
                                        {{{{frappe.utils.money_in_words(doc.amount)[3:]}}}}
				{{%- else -%}}
                                        {{% set total_amount = [0] %}}
                                        {{%- for row in doc.accounts -%}}
                                                {{%- if frappe.db.get_value("Account", row.account, "account_type") == 'Bank' -%}}
                                                        {{%- if total_amount.append(total_amount.pop() + row.credit_in_account_currency) -%}}{{%- endif -%}}
                                                {{%- endif -%}}
                                        {{%- endfor -%}}
                                        {{{{frappe.utils.money_in_words(total_amount[0])[3:]}}}}
				{{%- endif -%}}
		</span>
		<span style="top:{amt_in_figures_from_top_edge}cm;left: {amt_in_figures_from_left_edge}cm;
			position: absolute;">
			<!-- {{doc.get_formatted("base_paid_amount") or doc.get_formatted("base_received_amount")}} -->
			{{%- if doc.doctype == 'Payment Entry' -%}}
                                <!-- {{{{doc.get_formatted("base_paid_amount") or doc.get_formatted("base_received_amount")}}}} -->
                                {{{{ '{{0:,.2f}}'.format(doc.base_paid_amount) if doc.base_paid_amount else '{{0:,.2f}}'.format(doc.base_received_amount) }}}}
                        {{%- elif doc.doctype == 'Imprest Recoup' -%}}
                                {{{{ '{{0:,.2f}}'.format(doc.purchase_amount) }}}}
                        {{%- elif doc.doctype == 'HSD Payment' -%}}
                                {{{{ '{{0:,.2f}}'.format(doc.amount) }}}}
                        {{%- else -%}}
                                {{{{ '{{0:,.2f}}'.format(total_amount[0]) }}}}
                        {{%- endif -%}}
		</span>
		<span style="top:{signatory_from_top_edge}cm;left: {signatory_from_left_edge}cm;
			position: absolute;">
			<!-- {{{{doc.company}}}} -->
		</span>
	</div>
</div>""".format(
		starting_position_from_top_edge= doc.starting_position_from_top_edge \
			if doc.cheque_size == "A4" else 0.0,
		cheque_width= doc.cheque_width, cheque_height= doc.cheque_height,
		acc_pay_dist_from_top_edge= doc.acc_pay_dist_from_top_edge,
		acc_pay_dist_from_left_edge= doc.acc_pay_dist_from_left_edge,
		message_to_show= doc.message_to_show if doc.message_to_show else _("Account Pay Only"),
		date_dist_from_top_edge= doc.date_dist_from_top_edge,
		date_dist_from_left_edge= doc.date_dist_from_left_edge,
		acc_no_dist_from_top_edge= doc.acc_no_dist_from_top_edge,
		acc_no_dist_from_left_edge= doc.acc_no_dist_from_left_edge,
		payer_name_from_top_edge= doc.payer_name_from_top_edge,
		payer_name_from_left_edge= doc.payer_name_from_left_edge,
		amt_in_words_from_top_edge= doc.amt_in_words_from_top_edge,
		amt_in_words_from_left_edge= doc.amt_in_words_from_left_edge,
		amt_in_word_width= doc.amt_in_word_width,
		amt_in_words_line_spacing= doc.amt_in_words_line_spacing,
		amt_in_figures_from_top_edge= doc.amt_in_figures_from_top_edge,
		amt_in_figures_from_left_edge= doc.amt_in_figures_from_left_edge,
		signatory_from_top_edge= doc.signatory_from_top_edge,
		signatory_from_left_edge= doc.signatory_from_left_edge,
                party= party,
                date_formats= date_formats,
                date_letter_spacing= doc.date_letter_spacing
	)
	# +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++

	cheque_print.save(ignore_permissions=True)
	
	frappe.db.set_value("Cheque Print Template", template_name, "has_print_format", 1)
		
	return cheque_print
