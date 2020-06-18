// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Section', {
	refresh: function(frm) {

	}
});

cur_frm.fields_dict['d_name'].get_query = function(doc, dt, dn) {
       return {
               filters:{"dpt_name": doc.dpt_name}
       }
}

cur_frm.fields_dict['s_name'].get_query = function(doc, dt, dn) {
       return {
               filters:{"d_name": doc.d_name}
       }
}

/*cur_frm.fields_dict.cost_center.get_query = function(doc) {
	return{
		filters:{
			'is_group': 0,
			'is_disabled': 0,
		}
	}
}*/
