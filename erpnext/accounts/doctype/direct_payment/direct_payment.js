// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.ui.form.on('Direct Payment', {
	reload: function(frm) {
		cur_frm.set_query("debit_account", function(){
			return {
				"filters": [
					["is_group", "=", "0"],					
				]
			}
		});
		cur_frm.set_query("credit_account", function(){
			return {
				"filters": [
					["is_group", "=", "0"],					
				]
			}
		});
	},
	refresh: function(frm) {
		if(!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today())
		}
		
		if (frm.doc.party_type == "Customer"){
			cur_frm.set_query("party", function() {
				return {
					"filters": {
						"inter_company": 1
					}
				}
			 });
		}
	if(frm.doc.docstatus===1){
		frm.add_custom_button(__('Accounting Ledger'), function(){
			frappe.route_options = {
				voucher_no: frm.doc.name,
				from_date: frm.doc.posting_date,
				to_date: frm.doc.posting_date,
				company: frm.doc.company,
				group_by_voucher: false
			};
			frappe.set_route("query-report", "General Ledger");
		}, __("View"));
	}
	},
	"party_type": function(frm){
		//frm.set_value("party","");	
	},
        "payment_type": function(frm){
		/*
                if (frm.doc.party_type == "Customer"){
                        cur_frm.set_query("party", function() {
                                return {
                                        "filters": {
                                                "inter_company": 1
                                        }
                                }
                         });
                } */

                if(frm.doc.payment_type == "Receive"){
                        frappe.model.get_value('Branch', {'name': frm.doc.branch}, 'revenue_bank_account',
                        function(d) {
                            cur_frm.set_value("debit_account",d.revenue_bank_account);
                            cur_frm.set_value("credit_account","");
                        });
                }
                if(frm.doc.payment_type == "Payment"){
                        frappe.model.get_value('Branch', {'name': frm.doc.branch}, 'expense_bank_account',
                          function(d) {
                            cur_frm.set_value("credit_account",d.expense_bank_account);
                            cur_frm.set_value("debit_account","");
                        });
                }
                calculate_tds(frm);
        },
	"amount": function(frm) {
		frm.set_value("taxable_amount", parseFloat(frm.doc.amount))
		calculate_tds(frm);
	},
	"tds_percent": function(frm) {
		calculate_tds(frm);
		var net_amt = 0.00, tds_amt = 0.00;
		if(frm.doc.tds_percent < 1 || frm.doc.tds_percent == ""){
			cur_frm.set_value("tds_account", "");
			cur_frm.set_value("tds_amount", 0.00);
			if(!frm.doc.single_party_multiple_payments){
				frm.doc.item.forEach(function(d) {
					d.tds_amount = 0.00;
					d.net_amount = d.amount;
				});
			}
			else{
				frm.doc.multiple_account.forEach(function(d) {
					net_amt += d.amount;
				});
			}
		}else{
			if(!frm.doc.single_party_multiple_payments){
				frm.doc.item.forEach(function(d) {
					d.tds_amount = parseFloat(frm.doc.tds_percent) * parseFloat(d.taxable_amount) / 100;
					d.net_amount = parseFloat(d.taxable_amount) - parseFloat(d.tds_amount);
					tds_amt += d.tds_amount;
					net_amt += d.net_amount;
				});
			}
			else{
				frm.doc.multiple_account.forEach(function(d) {
					net_amt += d.amount;
				});
				tds_amt = parseFloat(frm.doc.tds_percent) * parseFloat(d.net_amt) / 100;
			}
		}
		frm.set_value("tds_amount", tds_amt);
		frm.set_value("net_amount", net_amt);
		cur_frm.set_df_property("tds_account", "reqd", (frm.doc.tds_percent > 0)? 1:0);
	},
	"taxable_amount": function(frm) {
		calculate_tds(frm);
	},
	"tds_amount": function(frm){
		frm.set_value("net_amount", parseFloat(frm.doc.amount) - parseFloat(frm.doc.tds_amount))
	},
	"branch": function(frm) {
		/*frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Cost Center", 
				fieldname:"name",
				filters: {
					branch: frm.doc.branch
				}
			},
			callback: function(r) {
				if(r.message.name) {
					cur_frm.set_value("cost_center", r.message.name)
				}				
			}
		}); */

		frappe.model.get_value('Branch', {'name': frm.doc.branch}, 'cost_center',
                          function(d) {
                            cur_frm.set_value("cost_center",d.cost_center);
                        });

		if(frm.doc.payment_type == "Receive"){
			frappe.model.get_value('Branch', {'name': frm.doc.branch}, 'revenue_bank_account',
			  function(d) {
			    cur_frm.set_value("debit_account",d.revenue_bank_account);
			});
		}
		if(frm.doc.payment_type == "Payment"){
			frappe.model.get_value('Branch', {'name': frm.doc.branch}, 'expense_bank_account',
			  function(d) {
			    cur_frm.set_value("credit_account",d.expense_bank_account);
			});
		}
	},
	"party": function(frm) {
		frm.set_value("pay_to_recd_from", frm.doc.party);
	}	
});

function roundOff(num) {    
    return +(Math.round(num + "e+2")  + "e-2");
}

function calculate_tds(frm) {
	frappe.call({
		method: "erpnext.accounts.doctype.direct_payment.direct_payment.get_tds_account",
		args: {
			percent: frm.doc.tds_percent,
			payment_type: frm.doc.payment_type
		},
		callback: function(r) {
			if(r.message) {
				frm.set_value("tds_account", r.message);
				cur_frm.refresh_field("tds_account");
			}
		}
	})
}

frappe.ui.form.on("Direct Payment", "onload", function(frm){
	cur_frm.set_query("select_cheque_lot", function(){
		return 	{
			"filters":[
				["status", "!=", "Used"],
				["docstatus", "=", "1"],
//				["branch", "=", frm.doc.branch]
			]
		}
	});
});

frappe.ui.form.on("Direct Payment", "select_cheque_lot", function(frm){
	if(frm.doc.select_cheque_lot) {
		frappe.call({
			method: "erpnext.accounts.doctype.cheque_lot.cheque_lot.get_cheque_no_and_date",
			args: {
				'name': frm.doc.select_cheque_lot
			},
			callback: function(r){
				if(r.message) {
					cur_frm.set_value("cheque_no", r.message[0].reference_no);
					cur_frm.set_value("cheque_date", r.message[1].reference_date);
				}
			}
		});	
	}
});

frappe.ui.form.on("Direct Payment Item", {
        "party_type": function(frm, cdt, cdn){
		frappe.model.set_value(cdt, cdn, "party", "");
		},
	"amount": function(frm, cdt, cdn){
		item = locals[cdt][cdn]
		frappe.model.set_value(cdt, cdn, "taxable_amount", item.amount);
		calculate_total(frm, cdt, cdn);
		},
	"taxable_amount": function(frm, cdt, cdn){
		calculate_total(frm, cdt, cdn);
		},
	"tds_amount": function(frm, cdt, cdn){
		calculate_total(frm, cdt, cdn);
	},
});

function calculate_total(frm, cdt, cdn){
	item = locals[cdt][cdn]
	if(frm.doc.tds_percent > 0){
		frappe.model.set_value(cdt, cdn, "tds_amount", parseFloat(frm.doc.tds_percent) * parseFloat(item.taxable_amount) / 100 );
	}
	frappe.model.set_value(cdt, cdn, "net_amount", parseFloat(item.amount) - parseFloat(item.tds_amount));
	var gross_amount=0, total_taxable_amount=0, total_net_amount=0, total_tds_amount=0;
	frm.doc.item.forEach(function(d) {
		gross_amount += d.amount;
		total_net_amount += d.net_amount;
		total_taxable_amount += d.taxable_amount;
		total_tds_amount += d.tds_amount;
	});
	frm.set_value("amount", gross_amount);
	frm.set_value("taxable_amount", total_taxable_amount);
	frm.set_value("net_amount", total_net_amount);
	frm.set_value("tds_amount", total_tds_amount);
	
}

/* ePayment Begins */
var create_custom_buttons = function(frm){
	var items = frm.doc.item || [];
	var status = ["Failed", "Upload Failed", "Cancelled"];
	var process_payment = 0;

	if(frm.doc.docstatus == 1 && frm.doc.payment_type == "Payment" && !frm.doc.utility_bill/*&& !frm.doc.cheque_no*/){
		items.forEach(function(r,i){
			if(r.party_type == 'Supplier' && r.party && (!r.bank_payment || r.payment_status == 'Failed'|| r.payment_status == 'Payment Failed')){
				process_payment += 1;
			}
		});

		// if(!frm.doc.bank_payment || status.includes(frm.doc.status) ){
		if(process_payment){
			frm.page.set_primary_action(__('Process Payment'), () => {
				frappe.model.open_mapped_doc({
					method: "erpnext.accounts.doctype.direct_payment.direct_payment.make_bank_payment",
					frm: cur_frm
				})
			});
		}
	}
}
/* ePayment Ends */