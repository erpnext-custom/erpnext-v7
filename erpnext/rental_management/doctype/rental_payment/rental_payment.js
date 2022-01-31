// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rental Payment', {
	setup: function(frm){
                frm.get_docfield("item").allow_bulk_edit = 1;
        },
	onload: function(frm){
		frm.set_query("bank_account", function() {
		var account_types = ["Bank", "Cash"]
			return {
				filters: {
					account_type:  ["in", account_types],
				}
			}
		})
		
		frm.set_query("debit_account", function() {
		var root_types = ["Liability"]
			return {
				filters: {
					root_type:  ["in", root_types],
				}
			}
		})
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
		frappe.call({
			method: "erpnext.rental_management.doctype.rental_payment.rental_payment.get_tds_account",
			callback: function(r) {
				if(r.message) {
					console.log(r.message);
					frm.set_value("tds_account", r.message);
					cur_frm.refresh_field("tds_account");
				}
			}
        });
	},
	"discount_percent": function(frm){
		
	},
	"rent_write_off": function(frm){
		if (frm.doc.rent_write_off == 1){
			frappe.model.get_value('Rental Account Setting', { 'name': 'Rental Account Setting' }, 'rent_write_off_account',
			function (r) {
				cur_frm.set_value("rent_write_off_account", r.rent_write_off_account);
			});
		}else{
			frm.set_value("rent_write_off_account", "");
			cur_frm.refresh_field("rent_write_off_account");
		}
	}
});

frappe.ui.form.on("Rental Payment Item", {
	"tenant": function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		if(frm.doc.fiscal_year && frm.doc.month){
			get_rental_bills_tenant_wise(frm, row);
		}
	},
	"sa_amount": function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		if(!row.total_amount_received){
			frappe.model.set_value(row.doctype, row.name, "total_amount_received", row.sa_amount);
		}
	},
	"penalty": function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		if(!row.total_amount_received){
			frappe.model.set_value(row.doctype, row.name, "total_amount_received", row.penalty);
		}
	}
});

function get_rental_bills_tenant_wise(frm, row){
	return frappe.call({
		method: "get_rental_bill_list",
		doc: cur_frm.doc,
		args: {'tenant': row.tenant},
		callback: function(r, rt){
				if(r.message){
					frappe.model.set_value(row.doctype, row.name, "bill_amount", r.message[0]['receivable_amount']);
					frappe.model.set_value(row.doctype, row.name, "rent_received", r.message[0]['rent_amount']);
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
}

function get_rental_bills(frm){
	if (frm.doc.branch || frm.doc.ministry_agency){
		return frappe.call({
					method: "get_rental_bill_list",
					doc: cur_frm.doc,
					callback: function(r, rt){
							var bill_amount = 0.00
							if(r.message){
								cur_frm.set_value('rent_received', r.message);
								cur_frm.set_value('total_bill_amount', r.message);
								cur_frm.set_value('total_amount_received', r.message);
							}
							cur_frm.refresh_fields();
						},
						freeze: true,
						freeze_message: "Fetching Transaction Details.... Please Wait",
					});     
			}else{
				frappe.msgprint("To retrieve rentall bill you must provide atleast Branch and Ministry or Agency");
			}
}
