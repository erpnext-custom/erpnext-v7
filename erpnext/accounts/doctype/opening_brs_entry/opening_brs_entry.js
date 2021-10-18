// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Opening BRS Entry', {
	refresh: function(frm) {
	},
});

cur_frm.fields_dict['details'].grid.get_field('bank_account').get_query = function(frm, cdt, cdn) {
	return {
		filters: {
			"account_type":[ 'in', ['Bank', 'Cash']]
		}
	}
}