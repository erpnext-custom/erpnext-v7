// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("construction_type", "is_building", "is_building");
frappe.ui.form.on('Site Registration', {
	setup: function(frm){
		frm.get_field('items').grid.editable_fields = [
			{fieldname: 'expected_quantity', columns: 2},
			{fieldname: 'uom', columns: 1},
			{fieldname: 'branch', columns: 3},
			{fieldname: 'transport_mode', columns: 2},
			{fieldname: 'remarks', columns: 2},
		];
		frm.get_field('distance').grid.editable_fields = [
			{fieldname: 'branch', columns: 6},
			{fieldname: 'item_sub_group', columns: 2},
			{fieldname: 'distance', columns: 2},
		];
	},
	onload: function(frm){
		cur_frm.set_query("user",function(){
			return {
				"filters": [
					["account_type", "=", "CRM"]
				]
			}
		});
		cur_frm.set_query("construction_type",function(){
			return {
				"filters": [
					["is_crm_item", "=", 1]
				]
			}
		});

		cur_frm.set_query("product_category",function(){
			return {
				"filters": [
					["is_crm_item", "=", 1],
					["site_required", "=", 1]
				]
			}
		});

		frm.fields_dict['items'].grid.get_field('product_category').get_query = function(){
			return{
				filters: {
					'is_crm_item': 1,
				}
			}
		};
	},
	user: function(frm){
		get_user_details(frm,'update');
	},
	refresh: function(frm) {
		custom.apply_default_settings(frm);
		enable_disable(frm);
		get_user_details(frm,'refresh');
	},
	approval_status: function(frm){
		cur_frm.toggle_reqd("rejection_reason", (frm.doc.approval_status=="Rejected") ? 1:0);
	},
	transport_mode: function(frm){
		cur_frm.toggle_reqd("distance", (frm.doc.transport_mode == "Common Pool") ? 1:0);
	},
	get_distance: function(frm){
		update_distance_table(frm);
	}
});

frappe.ui.form.on('Site Registration Item', {
	// Following code is commented by SHIV on 2020/11/09 as the item_sub_group is replaced with product_category for Phase-II
	//item_sub_group: function(frm, cdt, cdn){
	//	frappe.model.set_value(cdt, cdn, "branch", null);	
	//},
	product_category: function(frm, cdt, cdn){
		frappe.model.set_value(cdt, cdn, "branch", null);	
	}
});

/*########## Ver.2020.11.09 Begins, Phase-II  ##########*/
// following code is replaced by the next following code by SHIV on 2020/11/09
/*
frappe.ui.form.on("Site Registration", "refresh", function(frm) {
	frm.fields_dict['items'].grid.get_field('branch').get_query = function(doc, cdt, cdn) {
		doc = locals[cdt][cdn];
		return {
			"query": "erpnext.crm_utils.get_branch_source_query",
			filters: {'item_sub_group': doc.item_sub_group}
		}
	}
});
*/

// following code is created as a replacement for the above  code by SHIV on 2020/11/09
frappe.ui.form.on("Site Registration", "refresh", function(frm) {
	frm.fields_dict['items'].grid.get_field('product_category').get_query = function(doc, cdt, cdn) {
		doc = locals[cdt][cdn];
		return {
			filters: {'name': frm.doc.product_category}
		}
	}

	frm.fields_dict['items'].grid.get_field('branch').get_query = function(doc, cdt, cdn) {
		doc = locals[cdt][cdn];
		return {
			"query": "erpnext.crm_utils.get_branch_source_query",
			filters: {'product_category': doc.product_category}
		}
	}
});
/*########## Ver.2020.11.09 Ends ##########*/

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
	frm.toggle_reqd(["customer_type", "customer_group", "territory"],in_list(user_roles, "CRM Back Office"));
	frm.toggle_display("sb_distance",in_list(user_roles, "CRM Back Office"));
	frm.refresh_field("distance");
}

var update_distance_table = function(frm){
	if(in_list(user_roles, "CRM Back Office") && frm.doc.docstatus == 0){
		cur_frm.clear_table("distance");
		frappe.call({
			method: "erpnext.crm.doctype.site_registration.site_registration.get_distance",
			args: {"site": frm.doc.name},
			callback: function(r, rt) {
				if(r.message){
					r.message.forEach(function(v){
						var row = frappe.model.add_child(frm.doc, "Site Registration Distance", "distance");
						row.branch 		= v['branch'];
						row.item_sub_group	= v['item_sub_group'];
						//row.item		= v['item'];
						//row.item_name 	= v['item_name'];
						row.distance		= 0;
					});
				}
				frm.refresh_field("distance");
				//cur_frm.refresh();
			}
		});
	}

}
