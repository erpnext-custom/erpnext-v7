// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('CRM Branch Setting', {
	setup: function(frm){
		frm.get_field('items').grid.editable_fields = [
			{fieldname: 'item', columns: 3},
			{fieldname: 'item_sub_group', columns: 2},
			{fieldname: 'uom', columns: 1},
			{fieldname: 'has_stock', columns: 2},
			{fieldname: 'has_limit', columns: 2},
		];
	},
	onload: function(frm){
		frm.fields_dict['items'].grid.get_field('item_sub_group').get_query = function(){
			return{
				filters: {
					'is_crm_item': 1,
				}
			}
		};
		cur_frm.fields_dict.default_warehouse.get_query = function(){
			return {
				"query": "erpnext.crm_utils.get_branch_warehouse",
				filters: {'branch': frm.doc.branch}
			}
		};
		frm.fields_dict['items'].grid.get_field('item').get_query = function() {
			return {
				query: "erpnext.crm.doctype.crm_branch_setting.crm_branch_setting.get_items",
				filters:{"product_category": frm.doc.product_category}       
			}
		}
	},
	refresh: function(frm) {
		enable_disable(frm);
		set_transport_mode(frm);
	},
	has_common_pool: function(frm){
		enable_disable(frm);
	},
	branch: function(frm){
		cur_frm.set_value("default_warehouse", null);
	},
	product_category: function(frm){
		set_transport_mode(frm);
	}
});

var enable_disable = function(frm){
	cur_frm.toggle_reqd("lead_time", frm.doc.has_common_pool);
}

var set_transport_mode = function(frm){
	if(frm.doc.product_category){
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Product Category',
				filters: {
					'name': frm.doc.product_category
				},
				fieldname: '*'
			},
			callback: function(r){
				if(r.message){
					cur_frm.toggle_display("sb_transport_settings", r.message.transport_mode_required);
				}
			}
		});
	} else {
		cur_frm.toggle_display("sb_transport_settings", 0);
	}
}