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
	},
	refresh: function(frm) {
		//enable_disable(frm);
	},
	has_common_pool: function(frm){
		//enable_disable(frm);
	},
});

var enable_disable = function(frm){
	cur_frm.toggle_reqd("lead_time", frm.doc.has_common_pool);
}

