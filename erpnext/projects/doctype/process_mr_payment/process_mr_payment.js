// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Process MR Payment', {
	onload: function(frm) {
		if(!frm.doc.from_date) {
			frm.set_value("from_date", frappe.datetime.month_start(get_today()))	
		}
		if(!frm.doc.to_date) {
			frm.set_value("to_date", frappe.datetime.month_end(get_today()))	
		}
	},
	load_records: function(frm) {
		if(frm.doc.from_date && frm.doc.from_date < frm.doc.to_date) {
			get_records(frm.doc.from_date, frm.doc.to_date, frm.doc.project)
		}
		else if(frm.doc.from_date && frm.doc.from_date > frm.doc.to_date) {
			msgprint("To Date should be smaller than From Date")
			frm.set_value("to_date", "")
		}
	}
});

function get_records(from_date, to_date, project) {
	frappe.call({
		method: "erpnext.projects.doctype.process_mr_payment.process_mr_payment.get_records",
		args: {
			"from_date": from_date,
			"to_date": to_date,
			"project": project,
		},
		callback: function(r) {
			if(r.message) {
				var total_overall_amount = 0;
				cur_frm.clear_table("items");
				r.message.forEach(function(mr) {
					if(mr['number_of_days'] > 0 || mr['number_of_hours'] > 0) {
						var row = frappe.model.add_child(cur_frm.doc, "MR Payment Item", "items");
						row.mr_employee = mr['name']
						row.person_name = mr['person_name']
						row.id_card = mr['id_card']
						row.number_of_days = mr['number_of_days']
						row.daily_rate = mr['rate_per_day']
						row.number_of_hours = mr['number_of_hours']
						row.hourly_rate = mr['rate_per_hour']
						row.total_ot_amount = row.number_of_hours * row.hourly_rate
						row.total_wage = row.daily_rate * row.number_of_days
						row.total_amount = row.total_ot_amount + row.total_wage
						refresh_field("items");

						total_overall_amount += row.total_amount 
					}
				});

				cur_frm.set_value("total_overall_amount", total_overall_amount)
				cur_frm.refresh_field("total_overall_amount")
				cur_frm.refresh_field("items");
			}
		}
	})
}
