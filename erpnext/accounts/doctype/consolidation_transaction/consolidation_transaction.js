// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Consolidation Transaction', {
	refresh: function(frm) {
		frm.add_custom_button(__("Make Adjustment Entry"),
		()=>{
			console.log(frm.doc.name)
			frappe.model.open_mapped_doc({
			method: "erpnext.accounts.doctype.consolidation_transaction.consolidation_transaction.make_adjustment_entry",
			frm: frm
		});
		})
	},
	make_adjustment_entry:function(frm){
		console.log('here')
		// frappe.model.open_mapped_doc({
		// 	method: "erpnext.projects.doctype.project.project.make_project_advance",
		// 	frm: frm
		// });
	}
});
