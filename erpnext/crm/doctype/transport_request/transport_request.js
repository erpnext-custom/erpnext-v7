// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transport Request', {
	refresh: function(frm) {
		custom.apply_default_settings(frm);
	},
	onload: function(frm) {
		cur_frm.set_query("vehicle_capacity",function(){
			return {
				"filters": [
					["is_crm_item", "=", "1"]
				]
			}
		});
	},
	"vehicle_owner": function(frm) {
		if(frm.doc.vehicle_owner == "Self"){
			frappe.model.get_value("User", {"name":frm.doc.user}, "login_id", function(d){
				frm.set_value("owner_cid", d.login_id);
			});
		}
	}
});

/*cur_frm.fields_dict['items'].grid.get_field('crm_branch').get_query = function(doc, cdt, cdn) {
        return {
                filters:[
                        ['CRM Branch Setting', 'has_common_pool', '=', 1]
                ]
        }
} */

