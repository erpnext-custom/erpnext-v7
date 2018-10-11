// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("branch", "cost_center", "cost_center")

frappe.ui.form.on("Production Target",{ 
	"refresh":  function(frm){
		console.log(frappe.defaults.get_user_default("year_start_date"))
		 if (frm.doc.fiscal_year){
                        cur_frm.set_value("from_date", frappe.defaults.get_user_default("year_start_date"))
                        cur_frm.set_value("to_date", frappe.defaults.get_user_default("year_end_date"))
                }
	},
	"branch": function(frm) {
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
	},
	"fiscal_year": function(frm) {
		var year_start_date = "01-01-" + frm.doc.fiscal_year;
		var year_end_date = "31-12-" + frm.doc.fiscal_year;
		console.log(year_start_date);
		cur_frm.set_value("from_date", year_start_date);
		cur_frm.set_value("to_date", year_end_date);
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
