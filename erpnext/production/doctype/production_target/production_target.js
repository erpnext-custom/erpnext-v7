// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("branch", "cost_center", "cost_center")
cur_frm.add_fetch("fiscal_year","year_start_date","from_date");
cur_frm.add_fetch("fiscal_year","year_end_date","to_date");
frappe.ui.form.on("Production Target",{ 
	refresh:  function(frm){
		/*
		console.log(frappe.defaults.get_user_default("year_end_date"))
		 if (frm.doc.fiscal_year){
                        cur_frm.set_value("from_date", frappe.defaults.get_user_default("year_start_date"))
                        cur_frm.set_value("to_date", frappe.defaults.get_user_default("year_start_date"))
                }
		*/
	},
	/*"branch": function(frm) {
		return frappe.call({
			method: "erpnext.custom_utils.get_branch_cc",
			args: {
				"branch": frm.doc.branch
			},
			callback: function(r){
				cur_frm.set_value("cost_center", r.message)
				cur_frm.refresh_fields()
			}
		});
	},*/
	fiscal_year: function(frm) {
		/*
		var year_start_date = "01-01-" + frm.doc.fiscal_year;
		var year_end_date = "31-12-" + frm.doc.fiscal_year;
		console.log(year_start_date);
		console.log(year_end_date);
		cur_frm.set_value("from_date", year_start_date);
		cur_frm.set_value("to_date", "31-11-2018");
		*/
	}

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

function calculate_total(frm, cdt, cdn) {
	var item = locals[cdt][cdn]
	//if(item.quarter1 && item.queater2 && item.queater3 && item.queater4){
		qty = item.quarter1 + item.quarter2 + item.quarter3 + item.quarter4
		frappe.model.set_value(cdt, cdn, "quantity", qty);
//	}
	cur_frm.refresh_field("quantity")
}
