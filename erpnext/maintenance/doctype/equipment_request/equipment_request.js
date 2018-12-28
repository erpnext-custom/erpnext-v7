// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Request', {
	onload: function(frm) {
		frm.set_indicator_formatter('equipment_type',
			function(doc) { return doc.approved ? "green" : "orange" })
	},
	refresh: function(frm) {
		if (frm.doc.docstatus == 1 && frm.doc.percent_completed < 100) {
                        frm.add_custom_button("Create Equipment Hiring Form", function() {
                                frappe.model.open_mapped_doc({
                                        method: "erpnext.maintenance.doctype.equipment_request.equipment_request.make_hire_form",
                                        frm: cur_frm
                                })
                        });
                }
	}
});

frappe.ui.form.on('Equipment Request Item', {
	from_date: function(doc, cdt, cdn) {
		calculate_hour(doc, cdt, cdn)
	},
	to_date: function(doc, cdt, cdn) {
		calculate_hour(doc, cdt, cdn)
	},
})

function calculate_hour(doc, cdt, cdn) {
	obj = locals[cdt][cdn]	
	if(obj.from_date && obj.to_date) {
		if(obj.from_date > obj.to_date) {
			msgprint("From Date has to be small than To Date")
			frappe.model.set_value(cdt, cdn, "to_date", "")
		}
		else {
			frappe.model.set_value(cdt, cdn, "total_hours", (frappe.datetime.get_day_diff(obj.to_date, obj.from_date) + 1) * 8)
		}
	}
}

