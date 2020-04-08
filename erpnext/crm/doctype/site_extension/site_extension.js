// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Extension', {
	onload: function(frm){
		cur_frm.set_query("user",function(){
			return {
				"filters": [
					["account_type", "=", "CRM"]
				]
			}
		});

		cur_frm.set_query("site", function(){
			return {
				"filters": [
					["user", "=", frm.doc.user],
					["enabled", "=", "1"],
				]
			}
		});
	},
	refresh: function(frm) {
		custom.apply_default_settings(frm);
		get_user_details(frm,'refresh');
	},
	user: function(frm){
		get_user_details(frm,'update');
		if(!frm.doc.user){
			cur_frm.set_value("site", null);
		}
	},
	site: function(frm){
		get_site_details(frm);
	},
	approval_status: function(frm){
		cur_frm.toggle_reqd("rejection_reason", (frm.doc.approval_status == "Rejected") ? 1:0);
	}
});

var get_user_details = function(frm, mode){
	if(frm.doc.user){
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'User Account',
				filters: {
					'name': frm.doc.user
				},
				fieldname: '*'
			},
			callback: function(r){
				custom.update_user_details(frm, r, mode);
			}
		});
	} else {
		custom.update_user_details(frm, {}, mode);
	}
}

var get_site_details = function(frm){
	if(frm.doc.site){
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Site',
				filters: {
					'name': frm.doc.site,
				},
				fieldname: ['construction_start_date', 'construction_end_date', 'extension_till_date'],
			},
			callback: function(r){
				if(r.message){
					cur_frm.set_value("construction_start_date", r.message.construction_start_date);
					cur_frm.set_value("construction_end_date", r.message.extension_till_date || r.message.construction_end_date);
				} else {
					cur_frm.set_value("construction_start_date", null);
					cur_frm.set_value("construction_end_date", null);
				}
			}
		});	
	}else{
		cur_frm.set_value("construction_start_date", null);
		cur_frm.set_value("construction_end_date", null);
	}
}
