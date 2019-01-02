// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("branch", "cost_center", "cost_center")

frappe.ui.form.on('Marking List', {
	setup: function(frm) {
		frm.get_field('items').grid.editable_fields = [
			{fieldname: 'species', columns: 2},
			{fieldname: 'timber_class', columns: 2},
			{fieldname: 'dbh_range', columns: 2},
			{fieldname: 'qty_m3', columns: 2},
			{fieldname: 'qty_cft', columns: 2},
			{fieldname: 'timber_type', columns: 2},
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
	},
	
});

frappe.ui.form.on('Marking List Details', {
	"l_volume": function(frm, cdt, cdn) {
		calculate(frm, cdt, cdn)
	},
	
	"no_of_trees": function(frm, cdt, cdn) {
		calculate(frm, cdt, cdn)
	},
	
	"dbh_range": function(frm, cdt, cdn) {
                frappe.model.set_value(cdt, cdn, "l_volume", '');
                //cur_frm.refresh_field("l_volume");
                //cur_frm.refresh_fields();
        },
})

function calculate(frm, cdt, cdn) {
	var local = locals[cdt][cdn];
	var total_volume = flt(local.l_volume)*flt(local.no_of_trees);
	frappe.model.set_value(cdt, cdn, "qty_m3", total_volume);
}




