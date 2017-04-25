// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Travel Claim', {
	refresh: function(frm) {
	},
	onload: function(frm) {
		cur_frm.set_df_property("supervisor_approval", "hidden", 1)
		cur_frm.set_df_property("hr_approval", "hidden", 1)
		cur_frm.set_df_property("claim_status", "hidden", 1)
		
		if (in_list(user_roles, "Expense Approver") && frappe.session.user == frm.doc.supervisor) {
			cur_frm.set_df_property("supervisor_approval", "hidden", 0)
			cur_frm.set_df_property("claim_status", "hidden", 0)
		}
		if (in_list(user_roles, "HR User"))  {
			cur_frm.set_df_property("hr_approval", "hidden", 0)
			cur_frm.set_df_property("claim_status", "hidden", 0)
		}
	},
	"total_claim_amount": function(frm) {
		frm.set_value("balance_amount", frm.doc.total_claim_amount + frm.doc.extra_claim_amount - frm.doc.advance_amount)
	},
	"extra_claim_amount": function(frm) {
		frm.set_value("balance_amount", frm.doc.total_claim_amount + frm.doc.extra_claim_amount - frm.doc.advance_amount)
	}
});

frappe.ui.form.on("Travel Claim Item", {
	"form_render": function(frm, cdt, cdn) {
		var item = frappe.get_doc(cdt, cdn)
		if (item.halt == 0) {
			var df = frappe.meta.get_docfield("Travel Claim Item","distance", cur_frm.doc.name);
			frappe.model.set_value(cdt, cdn, "distance", "")
			//df.display = 0;
		}	
	
		if(item.currency != "BTN") {
			frappe.model.set_value(cdt, cdn, "amount", format_currency(flt(item.amount), item.currency))
		}
		
	},
	"currency": function(frm, cdt, cdn) {
		do_update(frm, cdt, cdn)
	},
	"dsa": function(frm, cdt, cdn) {
		do_update(frm, cdt, cdn)
	},
	"mileage_rate": function(frm, cdt, cdn) {
		do_update(frm, cdt, cdn)
	},
	"distance": function(frm, cdt, cdn) {
		do_update(frm, cdt, cdn)
	},
	"actual_amount": function(frm, cdt, cdn) {
		var total = 0;
		frm.doc.items.forEach(function(d) { 
			total += d.actual_amount	
		})
		frm.set_value("total_claim_amount", total)
	}
})

function do_update(frm, cdt, cdn) {
	//var item = frappe.get_doc(cdt, cdn)
	var item = locals[cdt][cdn]
	var amount = flt(item.dsa * item.no_days + item.mileage_rate * item.distance)
	if (item.halt == 1) {
		amount = flt(item.dsa * item.no_days)
	}
	if(item.currency != "BTN") {
		frappe.call({
			method: "erpnext.hr.doctype.travel_authorization.travel_authorization.get_exchange_rate",
			args: {
				"from_currency": item.currency,
				"to_currency": "BTN"
			},
			callback: function(r) {
				if(r.message) {
					frappe.model.set_value(cdt, cdn, "actual_amount", flt(r.message) * amount)
				}
			}
		})
	}
	else {
		frappe.model.set_value(cdt, cdn, "actual_amount", amount)
	}
	
	frappe.model.set_value(cdt, cdn, "amount", format_currency(flt(item.dsa * item.no_days + item.mileage_rate * item.distance), item.currency))
	refresh_field("amount")	

}

