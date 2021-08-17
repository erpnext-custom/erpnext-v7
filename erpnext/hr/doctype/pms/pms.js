// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('PMS', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1 ){
			frm.add_custom_button(__("Evaluate"),()=>{
				frappe.model.open_mapped_doc({
					method: "erpnext.hr.doctype.pms.pms.create_evaluate",
					frm: cur_frm
				});
			})
		}
	frappe.meta.get_docfield("PMS Item","status",cur_frm.doc.name).hidden = 1
	frappe.meta.get_docfield("PMS Item","final_score",cur_frm.doc.name).hidden = 1
	}
});
