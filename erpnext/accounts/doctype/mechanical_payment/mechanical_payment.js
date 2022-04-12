// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("branch", "revenue_bank_account", "income_account")

frappe.ui.form.on('Mechanical Payment', {
	onload: function(frm) {
		cur_frm.set_query("income_account", function(){
			return {
				"filters": [
					["is_group", "=", "0"],
					
				]
			}
		});
		cur_frm.set_query("tds_account", function(){
			return {
				"filters": [
					["is_group", "=", "0"],
					
				]
			}
		});	
	},
	refresh: function(frm) {
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
		cur_frm.refresh_fields();
	},

	"receivable_amount": function(frm) {
		calculate_totals(frm)
	},

	"tds_amount": function(frm) {
		calculate_totals(frm)
		frm.toggle_reqd("tds_account", frm.doc.tds_amount)
	},
	"tds_rate": function(frm) {
		set_tds_account(frm);
		calculate_totals(frm);
		if(frm.doc.tds_rate < 1 || frm.doc.tds_rate == ""){
			cur_frm.set_value("tds_account", "");
			cur_frm.set_value("tds_amount", 0.00);
		}
		cur_frm.set_df_property("tds_account", "reqd", (frm.doc.tds_rate > 0)? 1:0);
	},
	get_series: function(frm) {
		return frappe.call({
			method: "get_series",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.reload_doc();
			}
		});
	},

	get_transactions: function(frm) {
		//load_accounts(frm.doc.company)
		return frappe.call({
			method: "get_transactions",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("items");
				frm.refresh_fields();
			},
			freeze: true,
			freeze_message: "Fetching Transactions......Please Wait"
		});
	},

	"receivable_amount": function(frm) {
		if(frm.doc.receivable_amount > frm.doc.actual_amount) {
			cur_frm.set_value("receivable_amount", frm.doc.actual_amount)
			msgprint("Receivable Amount cannot be greater than the Total Payable Amount")
		}
		else {
			var total = frm.doc.receivable_amount
			frm.doc.items.forEach(function(d) {
				var allocated = 0
				if (total > 0 && total >= d.outstanding_amount ) {
					allocated = d.outstanding_amount
				}
				else if(total > 0 && total < d.outstanding_amount) {
					allocated = total
				}
				else {
					allocated = 0
				}
			
				d.allocated_amount = allocated
				total-=allocated
			})
			cur_frm.refresh_field("items")
		}
	},
	"items_on_form_rendered": function(frm, grid_row, cdt, cdn) {
		var row = cur_frm.open_grid_row();
		row.grid_form.fields_dict.reference_type.set_value(frm.doc.payment_for)
		row.grid_form.fields_dict.reference_type.refresh()
	},
	"payment_for": function(frm) {
		if(cur_frm.doc.payment_for == "Transporter Payment"){
			cur_frm.toggle_reqd("transporter",1);
		}
		else{
			cur_frm.toggle_reqd("transporter",0);
		}
		if(frm.doc.payment_for == "Transporter Payment"){
			frappe.model.get_value('Production Account Settings',{'company':frm.doc.company},'transportation_account', function(d){
				frm.set_value("transportation_account", d.transportation_account);
			});
			frappe.model.get_value('Branch',{'branch':frm.doc.branch},'expense_bank_account', function(d){
				frm.set_value("expense_account", d.expense_bank_account);
			});
			
		}
		calculate_totals(frm);
		frm.refresh_fields();
	},
	"other_deduction": function(frm) {
	   	calculate_totals(frm);
	},
	"get_delivery_note": function(frm) {
                get_delivery_notes(frm);
        },
});

function set_tds_account(frm) {
	frappe.call({
		method: "erpnext.accounts.doctype.mechanical_payment.mechanical_payment.get_tds_account",
		args: {
			percent: frm.doc.tds_rate
		},
		callback: function(r) {
			if(r.message) {
				frm.set_value("tds_account", r.message);
				cur_frm.refresh_field("tds_account");
			}
		}
	})
}

function get_delivery_notes(frm){
        if (frm.doc.transporter || frm.doc.vehicle){
                return frappe.call({
                        method: "get_delivery_note_list",
                        doc: cur_frm.doc,
                        callback: function(r, rt){
                                if(r.message){
					console.log(r.message);
                                        var total_amount = 0;
                                        console.log(r.message);
                                        cur_frm.clear_table("transporter_payment_item");
                                        r.message.forEach(function(rec) {
                                                var row = frappe.model.add_child(cur_frm.doc, "Transporter Payment Item", "transporter_payment_item");
                                                row.delivery_note = rec['delivery_note'];
                                                row.vehicle = rec['vehicle'];
                                                row.amount = rec['amount'];
                                                total_amount += rec['amount'];
                                        });
                                        cur_frm.set_value("total_amount", total_amount);
                                }else{
                                      cur_frm.clear_table("transporter_payment_item");
                                      frappe.msgprint("No Delivery Note for the above selected vehicle or transporter");
                                }
                                cur_frm.refresh();
                        },
                });
        }else{
                frappe.msgprint("To retrieve Delivery Note, Please Provide Transporter or Vehicle no");
        }
}

function calculat(frm) {
	if(frm.doc.payment_for == "Transporter Payment"){
		var net_amount = frm.doc.total_amount - (frm.doc.tds_amount + frm.doc.other_deduction);
		frm.set_value("net_amount", net_amount);
	}
	else{
		if (frm.doc.receivable_amount) {
			frm.set_value("net_amount", frm.doc.receivable_amount - frm.doc.tds_amount)
			cur_frm.refresh_field("net_amount")
		}
	}
	console.log("net_amount:" + net_amount);
}

cur_frm.fields_dict['items'].grid.get_field('reference_name').get_query = function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
		filters: {
			"docstatus": 1,
			"branch": frm.branch,
			"customer": frm.customer,
			"outstanding_amount": [">", 0]
		}
	}
}

function calculate_totals(frm) {
		if(frm.doc.tds_rate > 0){
			if (in_list(["Job Card"], frm.doc.payment_for)) {
				frm.set_value("tds_amount", parseFloat(frm.doc.tds_rate) * parseFloat(frm.doc.payable_amount) / 100 );
			}else if(in_list(["Transporter Payment", "Maintenance Payment"], frm.doc.payment_for)){
				frm.set_value("tds_amount", parseFloat(frm.doc.tds_rate) * parseFloat(frm.doc.total_amount) / 100 );
			}
		}else{
			frm.set_value("tds_amount", 0.00);
		}
        if(frm.doc.payment_for == "Transporter Payment"){
                var net_amount = frm.doc.total_amount - (frm.doc.tds_amount + frm.doc.other_deduction);
                frm.set_value("net_amount", net_amount);
        }
        else{
                if (frm.doc.receivable_amount) {
                        frm.set_value("net_amount", frm.doc.receivable_amount - frm.doc.tds_amount)
                        cur_frm.refresh_field("net_amount")
                }
        }
        console.log("net_amount:" + net_amount);
}

frappe.ui.form.on("Transporter Payment Item", {
		"delivery_note": function(frm, cdt, cdn){
			var items = frm.doc.transporter_payment_item;
			var total = 0;
			for(var i = 0; i < items.length ; i++){
           			total += parseFloat(items[i].amount);
      			}
      			frm.set_value('total_amount', total);
			calculate_totals(frm);
		}
})

frappe.ui.form.on("Mechanical Payment Item", {
	"reference_name": function(frm, cdt, cdn) {
		var item = locals[cdt][cdn]
		rec_amount = flt(frm.doc.receivable_amount)
		act_amount = flt(frm.doc.actual_amount)
		if (item.reference_name) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: item.reference_type,
					fieldname: ["outstanding_amount"],
					filters: {
						name: item.reference_name
					}
				},
				callback: function(r) {
					frappe.model.set_value(cdt, cdn, "outstanding_amount", r.message.outstanding_amount)
					frappe.model.set_value(cdt, cdn, "allocated_amount", r.message.outstanding_amount)
					cur_frm.refresh_field("outstanding_amount")
					cur_frm.refresh_field("allocated_amount")

					cur_frm.set_value("actual_amount", act_amount + flt(r.message.outstanding_amount))
					cur_frm.refresh_field("actual_amount")
					cur_frm.set_value("receivable_amount", rec_amount + flt(r.message.outstanding_amount))
					cur_frm.refresh_field("receivable_amount")
				}
			})
		}
	},
	
	"before_items_remove": function(frm, cdt, cdn) {
		doc = locals[cdt][cdn]
		amount = flt(frm.doc.receivable_amount) 
		ac_amount = flt(frm.doc.actual_amount) - flt(doc.outstanding_amount)
		cur_frm.set_value("actual_amount", ac_amount)
		cur_frm.refresh_field("actual_amount")
		cur_frm.trigger("receivable_amount")
	}
})
