app_name = "textiles_and_garments"
app_title = "Textiles And Garments"
app_publisher = "Aravind"
app_description = "Textiles and Garments"
app_email = "aravindsprint@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/textiles_and_garments/css/textiles_and_garments.css"
# app_include_js = "/assets/textiles_and_garments/js/textiles_and_garments.js"

# include js, css files in header of web template
# web_include_css = "/assets/textiles_and_garments/css/textiles_and_garments.css"
# web_include_js = "/assets/textiles_and_garments/js/textiles_and_garments.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "textiles_and_garments/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Stock Entry": "public/js/stock_entry.js",
    "Purchase Receipt": "public/js/purchase_receipt.js",
    "Sales Invoice": "public/js/sales_invoice.js",
    "Job Card": "public/js/job_card.js",
    "Work Order": "public/js/work_order.js",
    "Payment Entry": "public/js/payment_entry.js",
    "Work Order Payments": "public/js/work_order_payments.js",
    "Serial and Batch Bundle": "public/js/serial_and_batch_bundle.js"
}


# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "textiles_and_garments/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "textiles_and_garments.utils.jinja_methods",
# 	"filters": "textiles_and_garments.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "textiles_and_garments.install.before_install"
# after_install = "textiles_and_garments.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "textiles_and_garments.uninstall.before_uninstall"
# after_uninstall = "textiles_and_garments.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "textiles_and_garments.utils.before_app_install"
# after_app_install = "textiles_and_garments.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "textiles_and_garments.utils.before_app_uninstall"
# after_app_uninstall = "textiles_and_garments.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "textiles_and_garments.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
    "cron": {
        # "*/1 * * * *": [
        #     "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.every_five_minutes",
        # ],
        "30 18 30 * *": [
            "textiles_and_garments.tasks.create_sales_invoice_for_LIC_in_MANONMANI",
            "textiles_and_garments.tasks.create_sales_invoice_for_MIRAAI_in_MANONMANI",
            "textiles_and_garments.tasks.create_sales_invoice_for_VASANTH_in_P_THANGAVELU",
            "textiles_and_garments.tasks.create_sales_invoice_for_RELIANCE_INDUSTRIES_LIMITED_in_P_THANGAVELU",
            "textiles_and_garments.tasks.create_sales_invoice_for_TAMILNADU_GENERATION_AND_DISTRIBUTION_in_P_THANGAVELU",
            "textiles_and_garments.tasks.create_sales_invoice_for_TAMILNADU_GENERATION_AND_DISTRIBUTION_2_in_P_THANGAVELU",
            "textiles_and_garments.tasks.create_sales_invoice_for_LIC_OF_INDIA_in_P_THANGAVELU",

        ],
        # "*/10 * * * *": [
        #     "textiles_and_garments.tasks.create_sales_invoice_for_LIC_in_MANONMANI",
        #     "textiles_and_garments.tasks.create_sales_invoice_for_MIRAAI_in_MANONMANI",
        #     "textiles_and_garments.tasks.create_sales_invoice_for_VASANTH_in_P_THANGAVELU",
        #     "textiles_and_garments.tasks.create_sales_invoice_for_RELIANCE_INDUSTRIES_LIMITED_in_P_THANGAVELU",
        #     "textiles_and_garments.tasks.create_sales_invoice_for_TAMILNADU_GENERATION_AND_DISTRIBUTION_in_P_THANGAVELU",
        #     "textiles_and_garments.tasks.create_sales_invoice_for_TAMILNADU_GENERATION_AND_DISTRIBUTION_2_in_P_THANGAVELU",
        #     "textiles_and_garments.tasks.create_sales_invoice_for_LIC_OF_INDIA_in_P_THANGAVELU",

        # ],
        # "*/10 * * * *": [
        #     "textiles_and_garments.tasks.every_five_minutes",
        # ]
    }
	# "all": [
	# 	"textiles_and_garments.tasks.all"
	# ],
	# "daily": [
	# 	"textiles_and_garments.tasks.daily"
	# ],
	# "hourly": [
	# 	"textiles_and_garments.tasks.hourly"
	# ],
	# "weekly": [
	# 	"textiles_and_garments.tasks.weekly"
	# ],
	# "monthly": [
	# 	"textiles_and_garments.tasks.monthly"
	# ],
    # "all": [
    #     "textiles_and_garments.textiles_and_garments.doctype.dye_chart.dye_chart.every_five_minutes"
    # ]
}

# Testing
# -------

# before_tests = "textiles_and_garments.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "textiles_and_garments.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "textiles_and_garments.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["textiles_and_garments.utils.before_request"]
# after_request = ["textiles_and_garments.utils.after_request"]

# Job Events
# ----------
# before_job = ["textiles_and_garments.utils.before_job"]
# after_job = ["textiles_and_garments.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"textiles_and_garments.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

