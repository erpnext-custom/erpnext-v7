frappe.listview_settings['Product Requisition'] = {
        add_fields: ["name", "so_reference", "applicant_name", "customer", "docstatus", "posting_date"],
	get_indicator: function(doc) {
                if(doc.so_reference != "") {
                        return ["PR Created", "orange"];
                }
                else {
                        return ["SO Created", "green"];
                }
        }
};


