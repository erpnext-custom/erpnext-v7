// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle', {
	refresh: function(frm) {
		check_if_boulder_t(frm)
	}
});
var check_if_boulder_t = function(frm){
	if(cur_frm.doc.is_boulder == 1){
		cur_frm.toggle_reqd("vehicle_capacity",0)
	}
	else{
		cur_frm.toggle_reqd("vehicle_capacity",1)
	}
}
