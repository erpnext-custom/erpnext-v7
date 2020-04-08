// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transport Request', {
	refresh: function(frm) {
		custom.apply_default_settings(frm);
	},
	onload: function(frm) {

	},
	"owner": function(frm) {
		if(frm.doc.owner == "Self"){
			frappe.model.get_value("User", {"name":frm.doc.user}, "login_id", function(d){
				console.log(frm.doc.user);
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

