frappe.provide("erpnext.financial_statements");

erpnext.project_statements = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1
		},
		{
			"fieldname": "periodicity",
			"label": __("Periodicity"),
			"fieldtype": "Select",
			"options": [
				{ "value": "Monthly", "label": __("Monthly") },
				{ "value": "Quarterly", "label": __("Quarterly") },
				{ "value": "Half-Yearly", "label": __("Half-Yearly") },
				{ "value": "Yearly", "label": __("Yearly") }
			],
			"default": "Monthly",
			"reqd": 1
		}
	],
	"formatter": function(row, cell, value, columnDef, dataContext, default_formatter) {
		if (columnDef.df.fieldname=="account") {
			value = dataContext.account_name;

			columnDef.df.link_onclick =
				"erpnext.financial_statements.open_general_ledger(" + JSON.stringify(dataContext) + ")";
			columnDef.df.is_tree = true;
		}

		value = default_formatter(row, cell, value, columnDef, dataContext);

		if (!dataContext.parent_account) {
			var $value = $(value).css("font-weight", "bold");
			if (dataContext.warn_if_negative && dataContext[columnDef.df.fieldname] < 0) {
				$value.addClass("text-danger");
			}

			value = $value.wrap("<p></p>").parent().html();
		}

		return value;
	},
	"open_documents": function(data) {
		console.log(data);
	},
	"tree": true,
	"name_field": "account",
	"parent_field": "parent_account",
	"initial_depth": 3,
	onload: function(report) {
		// dropdown for links to other financial statements
		report.page.add_inner_button(__("Financial Position"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Statement of Financial Position', {company: filters.company});
		}, 'Financial Statements');
		report.page.add_inner_button(__("Comprehensive Income"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Statement of Comprehensive Income', {company: filters.company});
		}, 'Financial Statements');
		report.page.add_inner_button(__("Cash Flow Statement"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Statement of Cash Flow', {company: filters.company});
		}, 'Financial Statements');
	}
};
