// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fixed Deposit', {
	refresh: function(frm){
	},
	"principal": function(frm)
	{
		cal_amount(frm)
	},
	"rate": function(frm)
	{
		cal_amount(frm)
	},
	"start_date": function(frm)
	{
		cal_date(frm)
	},
	"days": function(frm)
	{
		cal_date(frm)
		cal_amount(frm)
	}
});

function cal_amount(frm){
	var interest_amount = frm.doc.principal*(parseFloat(frm.doc.rate)/100.00)/365*parseFloat(frm.doc.days)
    	var amount = frm.doc.principal + parseFloat(interest_amount)
	cur_frm.set_value("i_amount", interest_amount)
	cur_frm.set_value("total_amount", amount)
	console.log(interest_amount, amount)
}

function cal_date(frm) {
		if(frm.doc.days === 0){
			var to_date = frappe.datetime.add_days(frm.doc.start_date, parseInt(frm.doc.days));
		}
		else {
		  	var to_date = frappe.datetime.add_days(frm.doc.start_date, parseInt(frm.doc.days)-1);
		}
		cur_frm.set_value("end_date", to_date)
	}
