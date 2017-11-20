// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Deposit Work', {
	refresh: function(frm) {
	},
});

cur_frm.add_fetch("cost_center", "branch", "branch")

frappe.ui.form.on("Deposit Work", "onload", function(frm){
    cur_frm.set_query("cost_center", function(){
        return {
            "filters": [
                ["is_disabled", "!=", "1"],
                ["is_group", "!=", "1"],
            ]
        }
    });
});
