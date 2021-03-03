// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Issue List', {
	validate: function(frm) {
	frappe.prompt([{
    		label: 'Comment(Add if you have any comments)',
    		fieldname: 'remarks',
    		fieldtype: 'Small Text'
	}], 
		
		function(values){
		cur_frm.set_value("remarks", values.remarks)
		return frappe.call({
			method: "get_series",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.reload_doc();
			}
		});	
		},
        )}
		//cur_frm.set_value("test", values.test);
    		//console.log(values.date);
});
