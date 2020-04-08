// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Quantity Extension', {
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
		frm.fields_dict['items'].grid.get_field('item_sub_group').get_query = function(){
			return{
				filters: {
					'is_crm_item': 1,
				}
			}
		};
	},
	refresh: function(frm) {
		custom.apply_default_settings(frm);
		get_user_details(frm,'refresh');
	},
	user: function(frm){
		get_user_details(frm,'update');
	},
	site: function(frm){
		load_items(frm);
	},
	approval_status: function(frm){
		cur_frm.toggle_reqd("rejection_reason", (frm.doc.approval_status=="Rejected") ? 1:0);
	}
});

frappe.ui.form.on('Quantity Extension Item',{
	additional_quantity: function(frm, cdt, cdn){
		update_quantity(frm, cdt, cdn);
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

var update_quantity = function(frm, cdt, cdn){
	var row = locals[cdt][cdn];

	final_quantity = flt(row.initial_quantity) + flt(row.additional_quantity);
        frappe.model.set_value(cdt, cdn, "final_quantity", final_quantity);
}

var load_items = function(frm){
	frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: 'Site Item',
			filters: {
				'parent': frm.doc.site,
			},
			fields: ['*'],
		},
		callback: function(r){
			if(r.message){
				cur_frm.clear_table("items");
				r.message.forEach(function(i){
					var row = frappe.model.add_child(frm.doc, "Quantity Extension Item", "items");
					row.site_item_name	= i['name'];
					row.item_sub_group	= i['item_sub_group'];
					row.uom			= i['uom'];
					row.initial_quantity	= flt(i['overall_expected_quantity']); 
					row.branch		= i['branch'];	
					row.transport_mode	= i['transport_mode'];
				});
				cur_frm.refresh();
			}
		}
	});
}
