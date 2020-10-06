frappe.listview_settings['Rental Bill'] = {
        add_fields: ["name","rental_payment","received_amount","docstatus", "posting_date", "receivable_amount"],
        get_indicator: function(doc) {
                if(doc.rental_payment && doc.received_amount > 0) {
                        return ["Received", "orange"];
                }
		else if(doc.receivable_amount < 1 || doc.receivable_amount == ""){
			return ["Adjusted", "blue"];
		}
                else if(doc.receivable_amount > 0){
                        return ["Pending","green"];
                }
        }
};
