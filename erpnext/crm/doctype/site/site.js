// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site', {
	setup: function(frm){
		frm.get_field('items').grid.editable_fields = [
			{fieldname: 'item_sub_group', columns: 2},
			{fieldname: 'overall_expected_quantity', columns: 2},
			{fieldname: 'uom', columns: 1},
			{fieldname: 'branch', columns: 3},
			{fieldname: 'transport_mode', columns: 2},
		];
		frm.get_field('private_pool').grid.editable_fields = [
			{fieldname: 'vehicle', columns: 2},
			{fieldname: 'vehicle_capacity', columns: 2},
			{fieldname: 'drivers_name', columns: 3},
			{fieldname: 'contact_no', columns: 2},
		];
		frm.get_field('distance').grid.editable_fields = [
			{fieldname: 'branch', columns: 6},
			{fieldname: 'item_sub_group', columns: 2},
			{fieldname: 'distance', columns: 2},
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
		frm.fields_dict['private_pool'].grid.get_field('vehicle').get_query = function(){
			return{
				filters: {
					'vehicle_status': "Active",
				}
			}
		};
	},
	refresh: function(frm) {
	}
});

