// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("branch", "cost_center", "cost_center")

frappe.ui.form.on("Production Target",{ 
	refresh:  function(frm){
	},

});

frappe.ui.form.on("Production Target", "refresh", function(frm) {
    cur_frm.set_query("location", function() {
        return {
            "filters": {
                "branch": frm.doc.branch,
                "is_disabled": 0
            }
        };
    });
});

frappe.ui.form.on("Production Target Item", {
	"quarter1": function(frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn)
	},
	"quarter2": function(frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn)
	},
	"quarter3": function(frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn)
	},
	"quarter4": function(frm, cdt, cdn){
		calculate_total(frm, cdt, cdn)
	}
});

frappe.ui.form.on("Disposal Target Item", {
	"quarter1": function(frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn)
	},
	"quarter2": function(frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn)
	},
	"quarter3": function(frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn)
	},
	"quarter4": function(frm, cdt, cdn){
		calculate_total(frm, cdt, cdn)
	}
});

function calculate_total(frm, cdt, cdn) {
	var item = locals[cdt][cdn]
	qty = flt(item.quarter1) + flt(item.quarter2) + flt(item.quarter3) + flt(item.quarter4)
	frappe.model.set_value(cdt, cdn, "quantity", qty);
	cur_frm.refresh_field("quantity")
}


