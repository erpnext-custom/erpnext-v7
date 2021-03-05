// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("branch","cost_center","cost_center");
cur_frm.add_fetch("branch","expense_bank_account","bank_account");
frappe.ui.form.on('Overtime Payment', {
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
	"branch": function(frm) {
		frappe.model.get_value("HR Accounts Settings", {"name":"HR Accounts Settings"}, "overtime_account", 
			function(d) {
				cur_frm.set_value("debit_account", d.overtime_account);
			});
	},
	get_ot_application: function(frm) {
		get_application(frm);
	}
});

function get_application(frm){
	if (frm.doc.branch && frm.doc.from_date && frm.doc.to_date){
		return frappe.call({
			method: "get_ot_application",
			doc: cur_frm.doc,
			callback: function(r, rt){					
				if(r.message){
					cur_frm.clear_table("item");
					var total_amount = 0.00;
					r.message.forEach(function(rec) {
						console.log(r.message);
						var row = frappe.model.add_child(cur_frm.doc, "Overtime Payment Item", "item");
						row.employee = rec['employee'];
						row.employee_name = rec['employee_name'];	
						row.hourly_rate = rec['rate'];	
						row.total_hour = rec['total_hours'];
						row.total_amount = rec['total_amount'];
						row.reference = rec['reference'];
						total_amount += parseFloat(rec['total_amount']);
					});
					cur_frm.set_value("total_amount", total_amount);
					cur_frm.set_value("payable_amount", total_amount);
				}			
			cur_frm.refresh();
			},
        });     
	}else{
		frappe.msgprint("To get the Overtime Application, please provide the branch and dates");
	}
}
