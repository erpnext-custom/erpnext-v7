// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('User Account', {
	onload: function(frm){
		cur_frm.set_query("financial_institution_branch",function(){
			return {
				filters: {
					"financial_institution": frm.doc.financial_institution
				}
			}
		});
	},
	refresh: function(frm) {
		frm.add_custom_button(__("Change Mobile Number"), function(){
			update_mobile_no(frm);
		}).addClass("btn-warning");
	}
});

var update_mobile_no = function(frm){
        if(in_list(user_roles, "CRM Back Office")){
		frappe.prompt([
			{
				fieldtype: 'Int',
				reqd: true,
				label: 'Mobile Number',
				fieldname: 'mobile_no'
			}],
			function(args){
				validated = true;
				frappe.call({
					method: 'erpnext.crm.doctype.user_account.user_account.change_mobile_no',
					args: {'login_id': frm.doc.name, 'mobile_no': args.mobile_no},
					callback: function(r){
					},
					freeze: true,
					freeze_message: 'Updating mobile number...'
				});
			},
			__('Enter new mobile number'),
			__('Update')
		)
        }
}
