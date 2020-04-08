// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


frappe.ui.form.on('Site Status', {
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
	},
	site: function(frm){
		get_current_status(frm);
	},
	approval_status: function(frm){
		cur_frm.toggle_reqd("rejection_reason",(frm.doc.approval_status=="Rejected") ? 1:0);	
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

var get_current_status = function(frm){
	frappe.call({
		method: 'frappe.client.get_value',
		args: {
			doctype: 'Site',
			filters: {
				'name': frm.doc.site,
			},
			fieldname: ['enabled'],
		},
		callback: function(r){
			if(r.message){
				cur_frm.set_value("current_status", (r.message.enabled) ? "Active":"Inactive");
			}else{
				cur_frm.set_value("current_status", none);
			}
		}
	});
}
