// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Division', {
	refresh: function(frm) {

	},

	branch: function(frm){
	}
});


/*cur_frm.fields_dict['dpt_name'].get_query = function(doc, dt, dn) {
       return {
               filters:{"branch1": doc.branch}
       }
}*/

cur_frm.fields_dict.cost_center.get_query = function(doc) {
	return{
		filters:{
			'is_group': 0,
			'is_disabled': 0,
		}
	}
}
