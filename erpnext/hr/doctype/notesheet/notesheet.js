// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Notesheet', {
	refresh: function(frm) {
		
	}
});

// function get_full_user_name(frm){
// 	frappe.call({
// 		method: "get_full_user_name",
// 		args: {"user": frappe.session.user },
// 		callback: function(r) {
// 			if(r.message) {
// 				frm.set_value("prepared_by", r.message)
// 			}
// 		}
// 	})
// }