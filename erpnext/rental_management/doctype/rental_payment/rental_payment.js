// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rental Payment', {
	setup: function(frm){
                frm.get_docfield("item").allow_bulk_edit = 1;
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
	"allocated_amount":function(frm, cdt, cdn){
		var total_received = 0;
                frm.doc.item.forEach(function(d) {
                        total_received += d.allocated_amount
                });
		console.log("total Received:" + total_received);
                frm.set_value("amount_received", total_received);
		var net_amount = frm.doc.amount_received - frm.tds_amount;
		frm.set_value("net_amount", net_amount);
	}
});

function get_rental_bills(frm){
	if (frm.doc.branch && frm.doc.ministry_agency){
		return frappe.call({
                        method: "get_rental_bill_list",
                        doc: cur_frm.doc,
                        callback: function(r, rt){
                                if(r.message){
					var amount_received = 0;
                                        console.log(r.message);
					cur_frm.clear_table("item");
                                        r.message.forEach(function(rec) {
						var row = frappe.model.add_child(cur_frm.doc, "Rental Payment Item", "item");
						console.log(rec['tenant']);
						row.tenant = rec['tenant'];
						row.tenant_name = rec['tenant_name'];
						row.customer_code = rec['customer_code'];
						row.rental_bill = rec['bill_no'];
						row.amount = rec['rent_amount'];
						row.allocated_amount = rec['rent_amount'];
						row.fiscal_year = rec['fiscal_year'];
						row.month = rec['month'];
						amount_received = amount_received + rec['rent_amount'];
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


