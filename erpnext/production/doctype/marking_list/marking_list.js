// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Marking List', {
	onload: function(frm) {
                if(!frm.doc.posting_date) {
                        frm.set_value("posting_date", get_today())
                }
        },

	refresh: function(frm) {
		cur_frm.set_query("fmu", function() {
			return {
			    "filters": {
				"branch": frm.doc.branch
			    }
			};
		    });
		cur_frm.set_query("block", function() {
			return {
			    "filters": {
				"parent": frm.doc.fmu
			    }
			};
		    });
	}
});



