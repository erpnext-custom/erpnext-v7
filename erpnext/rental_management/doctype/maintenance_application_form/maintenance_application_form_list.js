frappe.listview_settings['Maintenance Application Form'] = {
        add_fields: ["name", "technical_sanction", "docstatus", "posting_date"],
        get_indicator: function(doc) {
                if(doc.technical_sanction) {
                        return ["TS Created", "orange"];
                }
                else {
                        return ["MAF Created", "green"];
                }
        }
};
