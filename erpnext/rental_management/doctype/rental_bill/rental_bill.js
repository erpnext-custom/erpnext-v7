frappe.ui.form.on('Rental Bill', {
  refresh: function (frm) {
    if(frm.doc.docstatus===1 && frm.doc.gl_entry == 1){
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
  }
});
