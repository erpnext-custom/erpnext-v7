frappe.listview_settings['Rental Bill'] = {
        add_fields: ["name","rental_payment","received_amount","docstatus", "posting_date"],
        get_indicator: function(doc) {
                if(doc.rental_payment && doc.received_amount > 0) {
                        return ["Received", "orange"];
                }
                else{
                        return ["Pending","green"];
                }
        }
};
