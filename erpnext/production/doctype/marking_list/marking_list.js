// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("branch", "cost_center", "cost_center")

frappe.ui.form.on('Marking List', {
	setup: function(frm) {
		frm.get_field('items').grid.editable_fields = [
			{fieldname: 'species', columns: 4},
			{fieldname: 'diameter', columns: 2},
			{fieldname: 'qty', columns: 3},
		]
		frm.get_field('aggregate_items').grid.editable_fields = [
			{fieldname: 'timber_class', columns: 3},
			{fieldname: 'timber_type', columns: 3},
			{fieldname: 'qty_cft', columns: 3},
		]
	},
	onload: function(frm) {
                if(!frm.doc.posting_date) {
                        frm.set_value("posting_date", get_today())
                }
        },

	refresh: function(frm) {
		cur_frm.toggle_display("block", frm.doc.docstatus == 0)
	
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



