// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("branch", "cost_center", "cost_center")

frappe.ui.form.on("Production", "refresh", function(frm){
	cur_frm.set_query("branch", function() {
        return {
            "filters": {
                "branch": frm.doc.branch,
                "disabled": 0
            }
        };
    });
	cur_frm.set_query("location", function() {
        	return {
            		"filters": {
                	"branch": frm.doc.branch,
                	"is_disabled": 0
            		}	
        	};
   	 });

	
})

