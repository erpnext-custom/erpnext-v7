frappe.listview_settings['Product Requisition'] = {
        add_fields: ["name", "delivered", "applicant_name", "customer", "docstatus", "posting_date"],
	get_indicator: function(doc) {
               /* if(doc.delivered) {
                        return ["Completed", "orange"];
                }
                else {
                        return ["Pending", "green"];
                } */
        }
};


