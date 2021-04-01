// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rental Payment', {
	setup: function(frm){
                frm.get_docfield("item").allow_bulk_edit = 1;
        },
	onload: function(frm){
		frm.set_query("credit_account", function() {
		var account_types = ["Bank", "Cash"]
			return {
				filters: {
					account_type:  ["in", account_types],
				}
				}																	})
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

	},
	"tenant":function(frm){
		if(frm.doc.tenant){
			cur_frm.add_fetch("tenant", "branch", "branch");
			cur_frm.add_fetch("tenant", "building_category", "building_category");
			cur_frm.add_fetch("tenant", "ministry_agency","ministry_agency");
			cur_frm.add_fetch("tenant", "department", "department");
			cur_frm.add_fetch("tenant", "location", "location");
		}else{
			cur_frm.set_value("building_category","");
			cur_frm.set_value("ministry_agency","");
			cur_frm.set_value("department", "");
			cur_frm.set_value("location", "");
		}
	},
	"individual_payment":function(frm){
		if(frm.doc.individual_payment==1){
			cur_frm.add_fetch("tenant","branch","branch");
			cur_frm.add_fetch("tenant", "building_category", "building_category");
			cur_frm.add_fetch("tenant", "ministry_agency","ministry_agency");
			cur_frm.add_fetch("tenant", "department", "department");
			cur_frm.add_fetch("tenant", "location", "location");
		}else{
			cur_frm.set_value("building_category","");
			cur_frm.set_value("department","");
			cur_frm.set_value("location","");
		}	
	},
	"get_rental_bills":function(frm){
		get_rental_bills(frm);
	},
	"tds_amount":function(frm){
		frm.set_value("net_amount", frm.doc.amount_received - frm.doc.tds_amount);
		frappe.call({
			method: "erpnext.rental_management.doctype.rental_payment.rental_payment.get_tds_account",
			callback: function(r) {
				if(r.message) {
					frm.set_value("tds_account", r.message);
					cur_frm.refresh_field("tds_account");
				}
			}
        	});

	} 
});

frappe.ui.form.on("Rental Payment Item", {
	"tenant": function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		console.log("called from individual row");
		get_rental_bills_tenant_wise(frm, row);
	},
	"amount_received": function(frm, cdt, cdn){
		var child = locals[cdt][cdn];
		console.log("Amount Received: " + child.amount_received)
		if(child.amount_received < child.amount){
			frappe.model.set_value(cdt, cdn, "allocated_amount", child.amount_received);
		}
		else{
			frappe.model.set_value(cdt, cdn, "allocated_amount", child.amount);
		}
		var sum_received = 0;
                frm.doc.item.forEach(function(d) {
                        sum_received += d.amount_received;
                });
		
                frm.set_value("amount_received", sum_received);
		var net_amount = frm.doc.amount_received - frm.tds_amount;
		frm.set_value("net_amount", net_amount);
	}
});

function get_rental_bills_tenant_wise(frm, row){
	if(!frm.doc.month){
		msgprint("Please set Month");
		return 0;
	}
	if(!frm.doc.fiscal_year){
		msgprint("Please set Fiscal Year");
		return 0;
	}
	if (!row.bulk_update){
		return frappe.call({
			method: "get_rental_bill_list",
			doc: cur_frm.doc,
			args: {'tenant': row.tenant},
			callback: function(r, rt){
					if(r.message){
						frappe.model.set_value(row.doctype, row.name, "actual_rent_amount", r.message[0]['rent_amount']);
						frappe.model.set_value(row.doctype, row.name, "amount", r.message[0]['receivable_amount']);
						frappe.model.set_value(row.doctype, row.name, "amount_received", r.message[0]['rent_amount']);
						frappe.model.set_value(row.doctype, row.name, "allocated_amount", r.message[0]['rent_amount']);
						frappe.model.set_value(row.doctype, row.name, "cid", r.message[0]['cid']);
						frappe.model.set_value(row.doctype, row.name, "customer_code", r.message[0]['customer_code']);
						frappe.model.set_value(row.doctype, row.name, "rental_bill", r.message[0]['bill_no']);
						frappe.model.set_value(row.doctype, row.name, "fiscal_year", r.message[0]['fiscal_year']);
						frappe.model.set_value(row.doctype, row.name, "month", r.message[0]['month']);
						frappe.model.set_value(row.doctype, row.name, "ministry_agency", r.message[0]['ministry_agency']);
						frappe.model.set_value(row.doctype, row.name, "department", r.message[0]['department']);
					} 
			}
		});
	} else {
		frappe.msgprint("To retrieve rentall bill you must provide atleast Branch and Ministry or Agency");
	}
}


function get_rental_bills(frm){
	if (frm.doc.branch || frm.doc.ministry_agency){
		return frappe.call({
                        method: "get_rental_bill_list",
						doc: cur_frm.doc,
                        callback: function(r, rt){
                                if(r.message){
					var amount_received = 0;
					cur_frm.clear_table("item");
                                        r.message.forEach(function(rec) {
						var row = frappe.model.add_child(cur_frm.doc, "Rental Payment Item", "item");
						row.tenant = rec['tenant'];
						row.tenant_name = rec['tenant_name'];
						row.cid = rec['cid'];
						row.customer_code = rec['customer_code'];
						row.rental_bill = rec['bill_no'];
						row.actual_rent_amount = rec['rent_amount'];
						row.amount = rec['receivable_amount'];
						row.fiscal_year = rec['fiscal_year'];
						row.month = rec['month'];
						row.ministry_agency = rec['ministry_agency'];
						row.department = rec['department'];
                                                row.amount_received = rec['receivable_amount'];
                                                row.allocated_amount = rec['receivable_amount'];
						row.bulk_update = 1;
						amount_received += rec['receivable_amount'];
                                        });
					cur_frm.set_value("amount_received", amount_received);
					cur_frm.set_value("net_amount", cur_frm.doc.amount_received - cur_frm.doc.tds_amount);
                                }else{
				      cur_frm.clear_table("item");
				      frappe.msgprint("No Rental Bills for the above selections");
				}
				cur_frm.refresh();
                        },
                });     
	}else{
		frappe.msgprint("To retrieve rentall bill you must provide atleast Branch and Ministry or Agency");
	}
}


