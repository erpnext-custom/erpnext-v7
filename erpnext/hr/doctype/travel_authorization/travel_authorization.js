// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("employee", "employee_name", "employee_name")
cur_frm.add_fetch("employee", "employee_subgroup", "grade")
cur_frm.add_fetch("employee", "designation", "designation")
cur_frm.add_fetch("employee", "department", "department")
cur_frm.add_fetch("employee", "division", "division")
cur_frm.add_fetch("employee", "branch", "branch")

frappe.ui.form.on('Travel Authorization', {
	refresh: function(frm) {
		//show the document status field and submit button
		if (in_list(user_roles, "Expense Approver") && frappe.session.user == frm.doc.supervisor) {
			frm.toggle_display("document_status", frm.doc.docstatus==0);
			frm.toggle_reqd("document_status", frm.doc.docstatus==0);
		}
		if (frm.doc.docstatus == 1 && !frm.doc.travel_claim) {
			frm.add_custom_button("Create Travel Claim", function() {
				frappe.model.open_mapped_doc({
					method: "erpnext.hr.doctype.travel_authorization.travel_authorization.make_travel_claim",
					frm: cur_frm
				})
			});
		}

		if(frm.doc.docstatus == 1) {
			frm.toggle_display("document_status", 1);
		}
	},
	onload: function(frm) {
		if (!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today());
		}

		frm.set_query("supervisor", function() {
			return {
				query: "erpnext.hr.doctype.leave_application.leave_application.get_approvers",
				filters: {
					employee: frm.doc.employee
				}
			};
		});

		frm.set_query("employee", erpnext.queries.employee);
	},
	"need_advance": function(frm) {
		frm.toggle_reqd("estimated_amount", frm.doc.need_advance==1);
		frm.toggle_reqd("currency", frm.doc.need_advance==1);
		frm.toggle_reqd("advance_amount", frm.doc.need_advance==1);
	},
	"advance_amount": function(frm) {
		if(frm.doc.advance_amount > frm.doc.estimated_amount * 0.9) {
			msgprint("Advance amount cannot be greater than 90% of the estimated amount")
			frm.set_value("advance_amount", 0)
		}
		else {
			if(frm.doc.currency == "BTN") {
				frm.set_value("advance_amount_nu", flt(frm.doc.advance_amount))
			}
			else {
				update_advance_amount(frm)
			}
		}
	},
	"document_status": function(frm) {
		if(frm.doc.document_status == "Rejected") {
			frm.toggle_reqd("purpose")
		}
	},
	"make_traveil_claim": function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.hr.doctype.travel_authorization.travel_authorization.make_travel_claim",
			frm: cur_frm
		})
	},
	"currency": function(frm) {
		if(frm.doc.currency == "BTN") {
			frm.set_value("advance_amount_nu", flt(frm.doc.advance_amount))
		}
		else {
			update_advance_amount(frm)
		}
	}
});

frappe.ui.form.on("Travel Authorization Item", {
	"till_date": function(frm, cdt, cdn) {
		var item = locals[cdt][cdn]
		if (item.till_date >= item.date) {
			frappe.model.set_value(cdt, cdn, "no_days", 1 + cint(frappe.datetime.get_day_diff(item.till_date, item.date)))
		}
		else {
			msgprint("Till Date cannot be earlier than From Date")
			frappe.model.set_value(cdt, cdn, "till_date", "")
		}
	}
});

function update_advance_amount(frm) {
	frappe.call({
		method: "erpnext.hr.doctype.travel_authorization.travel_authorization.get_exchange_rate",
		args: {
			"from_currency": frm.doc.currency,
			"to_currency": "BTN"
		},
		callback: function(r) {
			if(r.message) {
				frm.set_value("advance_amount_nu", flt(frm.doc.advance_amount) * flt(r.message))
				frm.set_value("advance_amount", format_currency(flt(frm.doc.advance_amount), frm.doc.currency))
				frm.set_value("estimated_amount", format_currency(flt(frm.doc.estimated_amount), frm.doc.currency))
			}
		}
	})
}
