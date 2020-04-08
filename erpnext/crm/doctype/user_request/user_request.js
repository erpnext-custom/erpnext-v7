// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("user","full_name","full_name");
cur_frm.add_fetch("user","mobile_no","mobile_no");
cur_frm.add_fetch("user","alternate_mobile_no","alternate_mobile_no");
frappe.ui.form.on('User Request', {
	onload: function(frm){
		cur_frm.set_query("user",function(){
			return {
				filters: {
					"account_type": "CRM"
				}
			}
		});
	},
	refresh: function(frm) {
		custom.apply_default_settings(frm);
		enable_disable(frm);
		get_user_details(frm,'refresh');
	},
	user: function(frm){
		get_user_details(frm,'update');
		get_old_details(frm);
	},
	request_category: function(frm){
		enable_disable(frm);
		get_old_details(frm);
	},
	new_address_type: function(frm){
		get_old_details(frm);
	},
	approval_status: function(frm){
		cur_frm.toggle_reqd("rejection_reason",(frm.doc.approval_status=="Rejected") ? 1 : 0);
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

var enable_disable = function(frm){
	var fields = [{"CID Details": ["cid"]}, 
			{"Address Details": ["address_type", "address_line1", "dzongkhag", "gewog"]},
			{"Contact Details": ["first_name"]}, 
			{"Bank Details": ["financial_institution", "account_number"]}];

	// toggle fields required based on request_category
	$(fields).each(function(i,j){
		var key = Object.keys(j)[0]; 
		$(j[key]).each(function(x,y){
			cur_frm.toggle_reqd("new_"+y,(key==frm.doc.request_category) ? 1 : 0);
		});
	});
}

var get_old_details = function(frm){
	var fields = [{"CID Details": ["cid", "date_of_issue", "date_of_expiry", "cid_file_front", "cid_file_back"]}, 
			{"Address Details": ["address_line1", "address_line2", "dzongkhag", "gewog", "pincode"]},
			{"Contact Details": ["first_name", "last_name", "email_id", "mobile_no", "alternate_mobile_no"]}, 
			{"Bank Details": ["financial_institution", "account_number"]}];

	frappe.call({
		method: "erpnext.crm.doctype.user_request.user_request.get_old_details",
		args: {"user": frm.doc.user || 'x'},
		callback: function(r, rt){
			if(r.message){
				$(fields).each(function(i,j){
					var key = Object.keys(j)[0]; 
					$(j[key]).each(function(x,y){
						if(key==frm.doc.request_category){
							if(key=="Address Details"){
								if(frm.doc.new_address_type){	
									cur_frm.set_value("old_address_type", frm.doc.new_address_type);
									var prefix = ((frm.doc.new_address_type=="Billing Address") ? "billing_" : "perm_");
									cur_frm.set_value("new_"+y, r.message[prefix+y]);
									cur_frm.set_value("old_"+y, r.message[prefix+y]);
								}else{
									cur_frm.set_value("old_address_type", "");
									cur_frm.set_value("new_"+y, "");
									cur_frm.set_value("old_"+y, "");
								}
							}else{
								cur_frm.set_value("new_"+y, r.message[y]);
								cur_frm.set_value("old_"+y, r.message[y]);
							}
						} else {
							cur_frm.set_value("new_"+y, "");
							cur_frm.set_value("old_"+y, "");
						}
					});
				});
			}else{
				$(fields).each(function(i,j){
					var key = Object.keys(j)[0]; 
					$(j[key]).each(function(x,y){
						cur_frm.set_value("new_"+y, "");
						cur_frm.set_value("old_"+y, "");
					});
				});
			}
		},
		freeze: true,
		freeze_message: "Loading..."
	});
}
