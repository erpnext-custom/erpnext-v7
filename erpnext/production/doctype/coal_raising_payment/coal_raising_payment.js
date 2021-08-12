// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch('branch','cost_center','cost_center');
frappe.ui.form.on('Coal Raising Payment', {
	setup: function(frm) {
		if( frm.doc.docstatus != 1 ){
			frm.set_value('from_date',frappe.datetime.month_start())
			frm.set_value('to_date',frappe.datetime.month_end())
		}
	},
	get_coal_raising_details:function(frm){
		if(frm.doc.branch){
			frappe.call({
				method:'get_coal_raising_details',
				doc:cur_frm.doc,
				callback:function(r){
					cur_frm.refresh_field('items')
				}
			})
		}
	},
	refresh:function(frm){
		if(frm.doc.docstatus == 1 ){
			if(frappe.model.can_read("Journal Entry")) {
				cur_frm.add_custom_button('Bank Entries', function() {
					frappe.route_options = {
						"Journal Entry Account.reference_type": frm.doc.doctype,
						"Journal Entry Account.reference_name": frm.doc.name,
					};
					frappe.set_route("List", "Journal Entry");
				}, __("View"));
			}
		}
	}
});

