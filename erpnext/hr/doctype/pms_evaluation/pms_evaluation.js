// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('PMS Evaluation', {
	refresh: function(frm) {
		make_field_read_only(frm)
	}
});
var make_field_read_only = (frm)=>{
	frappe.meta.get_docfield("PMS Item","output",cur_frm.doc.name).read_only = 1
	frappe.meta.get_docfield("PMS Item","success_indicator",cur_frm.doc.name).read_only = 1
	frappe.meta.get_docfield("PMS Item","weightage",cur_frm.doc.name).read_only = 1
	frappe.meta.get_docfield("PMS Item","unit",cur_frm.doc.name).read_only = 1
	frappe.meta.get_docfield("PMS Item","base",cur_frm.doc.name).read_only = 1
	frappe.meta.get_docfield("PMS Item","budget_amount",cur_frm.doc.name).read_only = 1
	frappe.meta.get_docfield("PMS Item","target_date",cur_frm.doc.name).read_only = 1
	frappe.meta.get_docfield("PMS Item","target_num",cur_frm.doc.name).read_only = 1
	frappe.meta.get_docfield("PMS Item","target_per",cur_frm.doc.name).read_only = 1
	frappe.meta.get_docfield("PMS Item","actual_achievement",cur_frm.doc.name).read_only = 1
}
