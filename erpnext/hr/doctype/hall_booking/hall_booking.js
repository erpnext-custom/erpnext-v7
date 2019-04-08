// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.ui.form.on('Hall Booking', {
	refresh: function(frm) {
		if(!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today())
		}
	},
	"rate": function(frm) {
		calculate_amount(frm);
	},
	"from_date": function(frm) {
		calculate_amount(frm);
	},
	"to_date": function(frm) {
		calculate_amount(frm);	
	}
});


function calculate_amount(frm) {
	if(frm.doc.to_date && frm.doc.from_date){
		var date1 = new Date(frm.doc.from_date);
		var date2 = new Date(frm.doc.to_date);
		if(date1 > date2){
			frappe.msgprint("To date Cannot be before From Date ");
		}
	
		var timeDiff = Math.abs(date2.getTime() - date1.getTime());
		var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 
		cur_frm.set_value("no_of_days", diffDays + 1);
		if(frm.doc.rate){
			cur_frm.set_value("amount", frm.doc.no_of_days * frm.doc.rate);
		}
	}
}
