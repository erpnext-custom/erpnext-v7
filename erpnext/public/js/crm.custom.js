var custom = {};

custom.apply_default_settings = function(frm){
	if(!in_list(user_roles, "CRM Back Office")){
		//$('.layout-side-section').html("");
		//$('.form-comments').html("");
		/*
		if($('[data-fieldname="user"]').length){
			cur_frm.set_df_property("user", "read_only", 1);
			if(frm.doc.__islocal){
				if(!frm.doc.user){
					frappe.call({
						method: 'frappe.client.get_value',
						args: {
							doctype: 'User Account',
							filters: {
								'name': frappe.session.user,
							},
							fieldname: ['name'],
						},
						callback: function(r){
							if(r.message){
								cur_frm.set_value("user",r.message.name);
							}
						}
					});
				}
			}
		}

		if($('[data-fieldname="site"]').length){
			if(!frm.doc.site){
				frappe.call({
					method: 'frappe.client.get_list',
					args: {
						doctype: 'Site',
						filters: {
							'user': frappe.session.user,
							'enabled': 1
						},
						fields: ['*'],
					},
					callback: function(r){
						if(r.message){
							if(r.message.length==1){
								cur_frm.set_value("site", r.message[0].name);
							}
						}
					}
				});
			}
		}
		*/
		if(frm.doctype=="Site Registration"){
			cur_frm.set_df_property("site_type", "read_only", 1);
		}
	} else {
		if(frm.doctype=="Site Registration"){
			cur_frm.set_df_property("site_type", "read_only", 0);
			cur_frm.toggle_reqd("site_type", 1);
		}
	}
}

custom.update_user_details = function(frm, r, mode){
	var wrapper="";
	var address=[];
	var contact=[];
	var address_box='<div style="background-color: #fafbfc; padding: 0px 15px 10px 15px; margin: 15px 0px; border: 1px solid #d1d8dd; border-radius: 3px; font-size: 12px; ">';
	if(r.message){
		if(frm.doc.docstatus == 0 && mode == 'update'){
			cur_frm.set_value('full_name', r.message.full_name);
			cur_frm.set_value('mobile_no', r.message.mobile_no);
			cur_frm.set_value('alternate_mobile_no', r.message.alternate_mobile_no);
		}
		
		// address details
		if(r.message.billing_address_line1){ address.push(String(r.message.billing_address_line1));}
		if(r.message.billing_address_line2){ address.push(String(r.message.billing_address_line2));}
		if(r.message.billing_dzongkhag){ address.push('<b class="h6">Dzongkhag:</b>'+' '+String(r.message.billing_dzongkhag));}
		if(r.message.billing_gewog){ address.push('<b class="h6">Gewog:</b>'+' '+String(r.message.billing_gewog));}
		if(r.message.billing_pincode){ address.push(String(r.message.billing_pincode));}
		if(address.length > 0){
			wrapper += address_box+'<p class="h5">Present Address</p>'+address.join('<br>')+'</div>';
		}

		// contact details
		if(r.message.first_name){
			if(r.message.last_name){
				contact.push('<b class="h5">'+String(r.message.first_name)+' '+String(r.message.last_name)+'</b>');
			}else{
				contact.push('<b class="h5">'+String(r.message.first_name)+'</b>');
			}
		}else{
			if(r.message.last_name){
				contact.push('<b class="h5">'+String(r.message.last_name)+'</b>');
			}
		}

		if(frm.doc.mobile_no){
			contact.push('<b class="h6"><i class="icon-phone" style="color: green;"></i> Mobile:</b>'+' '+String(frm.doc.mobile_no));
		}else{
			if(r.message.mobile_no){ contact.push('<b class="h6"><i class="icon-phone" style="color: green;"></i> Mobile:</b>'+' '+String(r.message.mobile_no));}
		}

		if(frm.doc.alternate_mobile_no){
			contact.push('<b class="h6"><i class="icon-phone" style="color: green;"></i> Alternate Mobile:</b>'+' '+String(frm.doc.alternate_mobile_no));
		}else{
			if(r.message.alternate_mobile_no){ contact.push('<b class="h6"><i class="icon-phone" style="color: green;"></i> Alternate Mobile:</b>'+' '+String(r.message.alternate_mobile_no));}
		}

		if(r.message.email_id){ contact.push('<b class="h6"><i class="icon-envelope" style="color: green;"></i> Email:</b>'+' '+String(r.message.email_id));}
		if(contact.length > 0){
			wrapper += address_box+'<p class="h5">Contact Details</p>'+contact.join('<br>')+'</div>';
		}

		$(cur_frm.fields_dict.address_list.wrapper).html(wrapper);
	}else{
		if(frm.doc.docstatus == 0 && mode == 'update'){
			cur_frm.set_value('full_name', null);
			cur_frm.set_value('mobile_no', null);
			cur_frm.set_value('alternate_mobile_no', null);
		}
		$(cur_frm.fields_dict.address_list.wrapper).html(wrapper);
	}
}
