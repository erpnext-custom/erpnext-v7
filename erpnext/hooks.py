from __future__ import unicode_literals
from frappe import _
from . import __version__ as app_version

app_name = "erpnext"
app_title = "ERPNext"
app_publisher = "Frappe Technologies Pvt. Ltd."
app_description = """ERP made simple"""
app_icon = "icon-th"
app_color = "#e74c3c"
app_email = "erpnext@dhi.bt"
app_license = "GNU General Public License (v3)"
source_link = "https://github.com/frappe/erpnext"

error_report_email = "erpnext@dhi.bt"

app_include_js = "assets/js/erpnext.min.js"
app_include_css = "assets/css/erpnext.css"
web_include_js = "assets/js/erpnext-web.min.js"
web_include_css = "assets/erpnext/css/website.css"

# setup wizard
setup_wizard_requires = "assets/erpnext/js/setup_wizard.js"
setup_wizard_complete = "erpnext.setup.setup_wizard.setup_wizard.setup_complete"

before_install = "erpnext.setup.install.check_setup_wizard_not_completed"
after_install = "erpnext.setup.install.after_install"

boot_session = "erpnext.startup.boot.boot_session"
notification_config = "erpnext.startup.notifications.get_notification_config"

on_session_creation = "erpnext.shopping_cart.utils.set_cart_count"
on_logout = "erpnext.shopping_cart.utils.clear_cart_count"

#remember_selected = ['Company', 'Cost Center', 'Project']
remember_selected = ['Company']
treeviews = ['Account', 'Cost Center', 'Warehouse', 'Item Group', 'Customer Group', 'Sales Person', 'Territory', "BOM"]

# website
update_website_context = "erpnext.shopping_cart.utils.update_website_context"
my_account_context = "erpnext.shopping_cart.utils.update_my_account_context"

email_append_to = ["Job Applicant", "Opportunity", "Issue"]

calendars = ["Task", "Production Order", "Leave Application", "Sales Order", "Holiday List"]

fixtures = []
#fixtures = ["Web Form", "Custom Field", "Property Setter"]

website_generators = ["Item Group", "Item", "Sales Partner", "Job Opening"]

website_context = {
	"favicon": 	"/assets/erpnext/images/favicon.ico",
	"splash_image": "/assets/erpnext/images/loading_icon.gif"
}

website_route_rules = [
	{"from_route": "/orders", "to_route": "Sales Order"},
	{"from_route": "/orders/<path:name>", "to_route": "order",
		"defaults": {
			"doctype": "Sales Order",
			"parents": [{"title": _("Orders"), "name": "orders"}]
		}
	},
	{"from_route": "/invoices", "to_route": "Sales Invoice"},
	{"from_route": "/invoices/<path:name>", "to_route": "order",
		"defaults": {
			"doctype": "Sales Invoice",
			"parents": [{"title": _("Invoices"), "name": "invoices"}]
		}
	},
	{"from_route": "/shipments", "to_route": "Delivery Note"},
	{"from_route": "/shipments/<path:name>", "to_route": "order",
		"defaults": {
			"doctype": "Delivery Note",
			"parents": [{"title": _("Shipments"), "name": "shipments"}]
		}
	},
	{"from_route": "/rfq", "to_route": "Request for Quotation"},
	{"from_route": "/rfq/<path:name>", "to_route": "rfq",
		"defaults": {
			"doctype": "Request for Quotation",
			"parents": [{"title": _("Request for Quotation"), "name": "rfq"}]
		}
	},
	{"from_route": "/addresses", "to_route": "Address"},
	{"from_route": "/addresses/<path:name>", "to_route": "addresses",
		"defaults": {
			"doctype": "Address",
			"parents": [{"title": _("Addresses"), "name": "addresses"}]
		}
	},
	{"from_route": "/jobs", "to_route": "Job Opening"},
]

portal_menu_items = [
	{"title": _("Projects"), "route": "/project", "reference_doctype": "Project"},
	{"title": _("Request for Quotations"), "route": "/rfq", "reference_doctype": "Request for Quotation"},
	{"title": _("Orders"), "route": "/orders", "reference_doctype": "Sales Order"},
	{"title": _("Invoices"), "route": "/invoices", "reference_doctype": "Sales Invoice"},
	{"title": _("Shipments"), "route": "/shipments", "reference_doctype": "Delivery Note"},
	{"title": _("Issues"), "route": "/issues", "reference_doctype": "Issue", "show_always": True},
	{"title": _("Addresses"), "route": "/addresses", "reference_doctype": "Address"},
	{"title": _("Announcements"), "route": "/announcement", "reference_doctype": "Announcement"},
	{"title": _("Courses"), "route": "/course", "reference_doctype": "Course"},
	{"title": _("Assessment Schedule"), "route": "/assessment", "reference_doctype": "Assessment"},
	{"title": _("Fees"), "route": "/fees", "reference_doctype": "Fees"}
]

has_website_permission = {
	"Sales Order": "erpnext.controllers.website_list_for_contact.has_website_permission",
	"Sales Invoice": "erpnext.controllers.website_list_for_contact.has_website_permission",
	"Delivery Note": "erpnext.controllers.website_list_for_contact.has_website_permission",
	"Issue": "erpnext.support.doctype.issue.issue.has_website_permission",
	"Address": "erpnext.utilities.doctype.address.address.has_website_permission",
	"Discussion": "erpnext.schools.web_form.discussion.discussion.has_website_permission"
}

permission_query_conditions = {
	"Contact": "erpnext.utilities.address_and_contact.get_permission_query_conditions_for_contact",
	"Address": "erpnext.utilities.address_and_contact.get_permission_query_conditions_for_address",
 
}

has_permission = {
	"Contact": "erpnext.utilities.address_and_contact.has_permission",
	"Address": "erpnext.utilities.address_and_contact.has_permission"
}

dump_report_map = "erpnext.startup.report_data_map.data_map"

before_tests = "erpnext.setup.utils.before_tests"

"""standard_queries = {
	"Customer": "erpnext.selling.doctype.customer.customer.get_customer_list"
}"""

doc_events = {
	"Stock Entry": {
		"on_submit": "erpnext.stock.doctype.material_request.material_request.update_completed_and_requested_qty",
		"on_cancel": "erpnext.stock.doctype.material_request.material_request.update_completed_and_requested_qty"
	},
	"User": {
		"validate": "erpnext.hr.doctype.employee.employee.validate_employee_role",
		"on_update": "erpnext.hr.doctype.employee.employee.update_user_permissions",
		"on_update": "erpnext.utilities.doctype.contact.contact.update_contact"
	},
	("Sales Taxes and Charges Template", 'Price List'): {
		"on_update": "erpnext.shopping_cart.doctype.shopping_cart_settings.shopping_cart_settings.validate_cart_settings"
	},
	"Address": {
		"validate": "erpnext.shopping_cart.cart.set_customer_in_address"
	},

	# bubble transaction notification on master
	('Opportunity', 'Quotation', 'Sales Order', 'Delivery Note', 'Sales Invoice',
		'Supplier Quotation', 'Purchase Order', 'Purchase Receipt',
		'Purchase Invoice', 'Project', 'Issue'): {
			'on_change': 'erpnext.accounts.party_status.notify_status'
		},

	"Website Settings": {
		"validate": "erpnext.portal.doctype.products_settings.products_settings.home_page_is_products"
	},
	"Payment Entry": {
		"on_submit": "erpnext.accounts.doctype.payment_request.payment_request.make_status_as_paid"
	}
}

scheduler_events = {
    "cron": {
		"0 0 * * *": [
      		"erpnext.buying.doctype.purchase_order.purchase_order.notify_due_date",
		]
	},
	"hourly": [
		"erpnext.controllers.recurring_document.create_recurring_documents",
		"erpnext.stock.doctype.item.item.sync_item_code",
		"erpnext.assets.doctype.asset.asset.sync_cc_branch",
		#"erpnext.maintenance.doctype.equipment.equipment.sync_branch_asset",
		"erpnext.selling.doctype.customer.customer.check_cc_branch",
		# "erpnext.accounts.report.gcoa_wise_report.gcoa_wise_report.create_transaction",
		#"erpnext.hr.doctype.leave_application.leave_application.check_cancelled_leaves"    # Ver 2.0.190225 Commented by SHIV on 25/02/2019
	],
	"daily": [
		#"erpnext.stock.reorder_item.reorder_item",
		"erpnext.setup.doctype.email_digest.email_digest.send",
		"erpnext.support.doctype.issue.issue.auto_close_tickets",
		"erpnext.accounts.doctype.fiscal_year.fiscal_year.auto_create_fiscal_year",
		"erpnext.hr.doctype.employee.employee.send_birthday_reminders",
		"erpnext.projects.doctype.task.task.set_tasks_as_overdue",
		"erpnext.assets.doctype.asset.depreciation.post_depreciation_entries",
		"erpnext.hr.doctype.officiating_employee.officiating_employee.check_off_exp",
		"erpnext.maintenance.maintenance_utils.check_hire_end",
		#"erpnext.hr.hr_custom_functions.post_earned_leaves",
		#"erpnext.hr.hr_custom_functions.post_casual_leaves",
		"erpnext.hr.hr_custom_functions.post_leave_credits",
		"erpnext.custom_functions.check_pending_approvers",
		# "erpnext.buying.doctype.purchase_order.purchase_order.notify_due_date",
	],
	"daily_long":[
		"erpnext.accounts.report.gcoa_wise_report.gcoa_wise_report.create_transaction",
     ],
}

default_mail_footer = """<div style="text-align: center;">
	<a style="color: #8d99a6;">
		Sent via <b>ERPNext</b> 
	</a>
</div>"""

get_translated_dict = {
	("doctype", "Global Defaults"): "frappe.geo.country_info.get_translated_dict"
}

bot_parsers = [
	'erpnext.utilities.bot.FindItemBot',
]

get_site_info = 'erpnext.utilities.get_site_info'

