// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rental Bill Cancelation Tool', {
	refresh: function(frm) {

	},
	"get_rental_bill_vouchers": function(frm){
		get_rental_vouchers(frm);
	}
});

function get_rental_vouchers(frm){
	if (frm.doc.fiscal_year && frm.doc.month){
		return frappe.call({
                        method: "get_rental_vouchers",
                        doc: cur_frm.doc,
                        callback: function(r, rt){
                                if(r.message){
					console.log(r.message);
					cur_frm.clear_table("items");
                                        r.message.forEach(function(rec) {
                                        	var row = frappe.model.add_child(cur_frm.doc, "Rental Bill Cancelation Item", "items");
                                                row.posting_date = rec['posting_date'];
                                                row.voucher_no = rec['voucher_no'];
                                                row.amount = rec['debit'];
                                        });	
				}else{
					cur_frm.clear_table("items");	
				}
				cur_frm.refresh();
			}
		});
	}
}

