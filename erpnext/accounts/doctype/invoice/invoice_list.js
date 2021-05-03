frappe.listview_settings['Invoice'] = {
        add_fields: ["docstatus", "paid"],
        has_indicator_for_draft: 1,
        get_indicator: function(doc) {
                if(doc.paid==0) {
                        return ["Invoice Created", "darkgrey", "paid,=,0"];
                }

                if(doc.paid == 1) {
                                return ["Paid", "green", "paid=,1"];
                        }
                        }
};

