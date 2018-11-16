// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Records" ,"end_date",  function(frm) {
	        if (frm.doc.end_date < frm.doc.start_date) {
                	msgprint(__("End Date should be greater than Start Date"));
                	validated = false;
        }
});

/*cur_frm.cscript.start_date = function(doc) {
        cur_frm.call({
                method: "erpnext.hr.hr_custom_functions.get_date_diff",
                args: {
                    start_date: (typeof doc.start_date === 'undefined') ? null : doc.start_date,
                    end_date: (typeof doc.end_date === 'undefined') ? null : doc.end_date
                },
                callback: function(r) {
                    cur_frm.set_value("duration", r.message.toString() + " days");
                }
        });
}
*/
cur_frm.cscript.end_date = function(doc) {
        cur_frm.call({
                method: "erpnext.hr.hr_custom_functions.get_date_diff",
                args: {
                        start_date: doc.start_date,
                        end_date: doc.end_date
                },
                callback: function(r) {
                        cur_frm.set_value("duration", r.message.toString() + " days");
                }
        });
}
