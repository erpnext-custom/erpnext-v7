// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Product Requisition', {
	refresh: function(frm) {
                if (frm.doc.docstatus == 1 && !frm.doc.sales_order) {
                        frm.add_custom_button("Create Sales Order", function() {
                                frappe.model.open_mapped_doc({
                                        method: "erpnext.selling.doctype.product_requisition.product_requisition.make_sales_order",
                                        frm: cur_frm
                                })
                        });
                }
        }
})
