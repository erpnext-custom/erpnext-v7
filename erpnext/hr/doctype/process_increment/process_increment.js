// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.cscript.display_activity_log = function(msg) {
	if(!cur_frm.ss_html)
		cur_frm.ss_html = $a(cur_frm.fields_dict['activity_log'].wrapper,'div');
	if(msg) {
		cur_frm.ss_html.innerHTML =
			'<div class="padding"><h4>'+__("Activity Log:")+'</h4>'+msg+'</div>';
	} else {
		cur_frm.ss_html.innerHTML = "";
	}
}

//Create Increment
//-----------------------
cur_frm.cscript.create_increment = function(doc, cdt, cdn) {
	cur_frm.cscript.display_activity_log("");
	var callback = function(r, rt){
		if (r.message)
			cur_frm.cscript.display_activity_log(r.message);
	}
	return $c('runserverobj', args={'method':'create_increment','docs':doc},callback);
}

//Remove Increment
//-----------------------
cur_frm.cscript.remove_increment = function(doc, cdt, cdn) {
	cur_frm.cscript.display_activity_log("");
	var callback = function(r, rt){
		if (r.message)
			cur_frm.cscript.display_activity_log(r.message);
	}
	return $c('runserverobj', args={'method':'remove_increment','docs':doc},callback);
}

//Submit Increment
//-----------------------
cur_frm.cscript.submit_increment = function(doc, cdt, cdn) {
	cur_frm.cscript.display_activity_log("");

	frappe.confirm(__("Do you really want to Submit all Salary Increment for month {0} and year {1}", [doc.month, doc.fiscal_year]), function() {
		// clear all in locals
		if(locals["Salary Increment"]) {
			$.each(locals["Salary Increment"], function(name, d) {
				frappe.model.remove_from_locals("Salary Increment", name);
			});
		}

		var callback = function(r, rt){
			if (r.message)
				cur_frm.cscript.display_activity_log(r.message);
		}

		return $c('runserverobj', args={'method':'submit_increment','docs':doc},callback);
	});
}

frappe.ui.form.on('Process Increment', {
	refresh: function(frm) {
		frm.disable_save();
	}
});
