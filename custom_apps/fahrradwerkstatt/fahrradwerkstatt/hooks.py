# -*- coding: utf-8 -*-
# Fahrradwerkstatt App für ERPNext - Hooks-Datei
# 
# Erstellt: 04.05.2025
# Änderungen:
# - Initiale Erstellung der hooks.py für die Integration der App in ERPNext
#
# Diese Datei definiert Hooks, die ERPNext nutzt, um die App zu integrieren.

from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "fahrradwerkstatt"
app_title = "Fahrradwerkstatt"
app_publisher = "Fahrradwerkstatt Team"
app_description = "ERPNext-Anwendung für Fahrradwerkstätten"
app_icon = "octicon octicon-gear"
app_color = "#4CB5F5"
app_email = "info@fahrradwerkstatt.de"
app_license = "MIT"

# DocTypes
# --------
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "Customer-bicycle_owner"
                ]
            ]
        ]
    }
]

# Includes in <head>
# ------------------
# include js, css files in header of desk.html
app_include_css = "/assets/fahrradwerkstatt/css/fahrradwerkstatt.css"
app_include_js = "/assets/fahrradwerkstatt/js/fahrradwerkstatt.js"

# include js, css files in header of web template
web_include_css = "/assets/fahrradwerkstatt/css/fahrradwerkstatt-web.css"
web_include_js = "/assets/fahrradwerkstatt/js/fahrradwerkstatt-web.js"

# Home Pages
# ----------
# application home page (will override Website Settings)
home_page = "fahrradwerkstatt-home"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "fahrradwerkstatt.utils.get_home_page"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

notification_config = "fahrradwerkstatt.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
    "Bicycle": "fahrradwerkstatt.permissions.get_bicycle_permission_query_conditions",
    "Bicycle Repair": "fahrradwerkstatt.permissions.get_bicycle_repair_permission_query_conditions"
}

has_permission = {
    "Bicycle": "fahrradwerkstatt.permissions.has_bicycle_permission",
    "Bicycle Repair": "fahrradwerkstatt.permissions.has_bicycle_repair_permission"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Invoice": {
        "on_submit": "fahrradwerkstatt.bicycle_management.on_sales_invoice_submit",
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "fahrradwerkstatt.tasks.daily"
    ],
    "weekly": [
        "fahrradwerkstatt.tasks.weekly"
    ],
    "monthly": [
        "fahrradwerkstatt.tasks.monthly"
    ]
}

# Testing
# -------
# before_tests = "fahrradwerkstatt.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#     "frappe.desk.doctype.event.event.get_events": "fahrradwerkstatt.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#     "Task": "fahrradwerkstatt.task.get_dashboard_data"
# }