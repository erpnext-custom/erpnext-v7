frappe.listview_settings['Rental Bill'] = {
        add_fields: ["name", "received_amount", "discount_amount", "docstatus", "tds_amount", "adjusted_amount", "receivable_amount"],
        get_indicator: function (doc) {
                if (doc.receivable_amount == (doc.received_amount + doc.discount_amount + doc.tds_amount)) {
                        return ["Received", "green"];
                }
                else if (doc.receivable_amount == doc.adjusted_amount) {
                        return ["Adjusted", "blue"];
                }
                else if (doc.receivable_amount > (doc.received_amount + doc.discount_amount + doc.tds_amount) && doc.received_amount > 0) {
                        return ["Partial Received", "yellow"];
                }
                else{
                        return ["Not Received", "orange"];
                }
        }
};
