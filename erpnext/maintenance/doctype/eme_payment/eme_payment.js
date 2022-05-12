// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("branch", "cost_center", "cost_center")
cur_frm.add_fetch("branch", "expense_bank_account", "bank_account")

frappe.ui.form.on('EME Payment', {
        setup: function (frm) {
                frm.get_docfield("items").allow_bulk_edit = 1;
        },
        refresh: function (frm) {
                if (frm.doc.docstatus === 1) {
                        frm.add_custom_button("Pay Arrear", function() {
                                frappe.model.open_mapped_doc({
                                        method: "erpnext.maintenance.doctype.eme_payment.eme_payment.make_arrear_payment",
                                        frm: cur_frm
                                });
                        }).addClass("btn-success");
                }
                if (frm.doc.docstatus === 1) {
                        frm.add_custom_button(__('Accounting Ledger'), function () {
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
                frm.add_custom_button(__('EME Bill Report'), function () {
                        frappe.route_options = {
                                name: frm.doc.name
                        };
                        frappe.set_route("query-report", "EME Bill Report");
                }, __("View"));
                frm.add_custom_button(__('EME Payment Details'), function () {
                        frappe.route_options = {
                                name: frm.doc.name
                        };
                        frappe.set_route("query-report", "EME Payment Details");
                }, __("View"));
                cur_frm.page.set_inner_btn_group_as_primary(__('View'));
        },

        onload: function (frm) {
                if (!frm.doc.posting_date) {
                        cur_frm.set_value("posting_date", get_today())
                }
        },

        get_logbooks: function (frm) {
                return frappe.call({
                        method: "get_logbooks",
                        doc: frm.doc,
                        callback: function (r, rt) {
                                frm.refresh_fields();
                        },
                        freeze: true,
                        freeze_message: "Fetching Logbooks....."
                });
        },

        tds_percent: function (frm) {
                calculate_totals(frm)
        }
});

function calculate_totals(frm) {
        cur_frm.call({
                method: "calculate_totals",
                doc: frm.doc,
                callback: function (r, rt) {
                        frm.refresh_fields();
                },
        });
}

