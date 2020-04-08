frappe.listview_settings['Delivery Confirmation'] = {
        add_fields: ["confirmation_status"],
        get_indicator: function(doc) {
                if(doc.confirmation_status==="In Transit") {
                        return [__("In Transit"), "green", "status,=,In Transit"];
                } else {
                        return [__("Received"), "orange", "status,=,Received"];
                }
        }
};
