// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.ui.form.on('Job Card', {
	refresh: function(frm) {
		if (frm.doc.jv && frappe.model.can_read("Journal Entry")) {
			cur_frm.add_custom_button(__('Bank Entries'), function() {
				frappe.route_options = {
					"Journal Entry Account.reference_type": me.frm.doc.doctype,
					"Journal Entry Account.reference_name": me.frm.doc.name,
				};
				frappe.set_route("List", "Journal Entry");
			}, __("View"));
		}
	
		if (frm.doc.outstanding_amount > 0 && frm.doc.owned_by == "Others" && frappe.model.can_write("Journal Entry")) {
			//cur_frm.toggle_display("receive_payment", 1)
			/*cur_frm.add_custom_button(__('Payment'), function() {
				cur_frm.cscript.receive_payment()
			}, __("Receive"));*/
			frm.add_custom_button("Receive Payment", function() {
				frappe.model.open_mapped_doc({
					method: "erpnext.maintenance.doctype.job_card.job_card.make_payment_entry",
					frm: cur_frm
				})
			}, __("Receive"));
		}
		else {
			cur_frm.toggle_display("receive_payment", 0)
		}
		
		cur_frm.toggle_display("owned_by", 0)

	},
	"receive_payment": function(frm) {
		if(frm.doc.paid == 0) {
			return frappe.call({
				method: "erpnext.maintenance.doctype.job_card.job_card.make_bank_entry",
				args: {
					"frm": cur_frm.doc.name,
				},
				callback: function(r) {
				}
			});
		}
		cur_frm.refresh_field("paid")
		cur_frm.refresh_field("receive_payment")
		cur_frm.refresh()
	},
	"get_items": function(frm) {
		//get_entries_from_min(frm.doc.stock_entry)
		//load_accounts(frm.doc.company)
		return frappe.call({
			method: "get_job_items",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("items");
				frm.refresh_fields();
			}
		});
	}
});

cur_frm.add_fetch("mechanic", "employee_name", "employee_name")

//Job Card Item  Details
frappe.ui.form.on("Job Card Item", {
	"start_time": function(frm, cdt, cdn) {
		calculate_datetime(frm, cdt, cdn)
	},
	"end_time": function(frm, cdt, cdn) {
		calculate_datetime(frm, cdt, cdn)
	},
	"job": function(frm, cdt, cdn) {
		var item = locals[cdt][cdn]
		
		if(item.job) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: item.which,
					fieldname: ["item_name", "cost"],
					filters: {
						name: item.job
					}
				},
				callback: function(r) {
					frappe.model.set_value(cdt, cdn, "job_name", r.message.item_name)
					frappe.model.set_value(cdt, cdn, "amount", r.message.cost)
					cur_frm.refresh_field("job_name")
					cur_frm.refresh_field("amount")
				}
			})
		}
	}
})

function calculate_datetime(frm, cdt, cdn) {
	var item = locals[cdt][cdn]
	if(item.start_time && item.end_time && item.end_time >= item.start_time) {
		frappe.model.set_value(cdt, cdn,"total_time", frappe.datetime.get_hour_diff(item.end_time, item.start_time))
	}
	cur_frm.refresh_field("total_time")
}

//Job Card Mechanic Details
frappe.ui.form.on("Mechanic Assigned", {
	"start_time": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"end_time": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	}
})

function calculate_time(frm, cdt, cdn) {
	var item = locals[cdt][cdn]
	if(item.start_time && item.end_time && item.end_time >= item.start_time) {
		frappe.model.set_value(cdt, cdn,"total_time", frappe.datetime.get_hour_diff(item.end_time, item.start_time))
	}
	cur_frm.refresh_field("total_time")
}

frappe.ui.form.on("Job Card", "refresh", function(frm) {
/*    cur_frm.set_query("stock_entry", function() {
        return {
            "filters": {
		"docstatus": 1,
		"purpose": "Material Issue",
		"job_card": frm.doc.name
            }
        };
    }); */
})
	
function get_entries_from_min(form) {
	frappe.call({
		method: "erpnext.maintenance.doctype.job_card.job_card.get_min_items",
		async: false,
		args: {
			"name": form,
		},
		callback: function(r) {
			if(r.message) {
				var total_amount = 0;
				r.message.forEach(function(logbook) {
				        var row = frappe.model.add_child(cur_frm.doc, "Job Card Item", "items");
					row.which = "Item"
					row.job = logbook['item_code']
					row.job_name = logbook['item_name']
					row.amount = logbook['amount']
				})
				cur_frm.refresh_field("items")
			}
		}
	})
}

cur_frm.cscript.receive_payment = function(){
	var doc = cur_frm.doc;
	frappe.ui.form.is_saving = true;
	frappe.call({
		method: "erpnext.maintenance.doctype.job_card.job_card.make_bank_entry",
		args: {
			"frm": cur_frm.doc.name,
		},
		callback: function(r){
			cur_frm.reload_doc();
		},
		always: function() {
			frappe.ui.form.is_saving = false;
		}
	});
}
