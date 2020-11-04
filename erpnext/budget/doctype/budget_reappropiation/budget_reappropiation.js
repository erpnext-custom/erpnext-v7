// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Budget Reappropiation', {
	refresh: function(frm) {

	}
});

//cost center
//-----------------------
cur_frm.fields_dict.to_cost_center.get_query = function(doc) {
	return{
		filters:{
			'is_group': 0,
			'is_disabled': 0,
		}
	}
}

//cost center
//-----------------------
cur_frm.fields_dict.from_cost_center.get_query = function(doc) {
	return{
		filters:{
			'is_group': 0,
			'is_disabled': 0,
		}
	}
}


frappe.ui.form.on("Budget Reappropiation Detail", "amount", function(frm, cdt, cdn) {

    calculate_value(frm, cdt, cdn);
});

function calculate_value(frm, cdt, cdn) {
        var re_amount = 0;
        frm.doc.items.forEach(function(d) {
                if(d.amount) {

                        re_amount += d.amount
                }

        })
        frm.set_value("total_amount", re_amount);
        cur_frm.refresh_field("total_amount");

}


