# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
{
    "name": "Event Planning Management for Odoo | Wedding Planner and Catering Software",
    "version": "19.0.1.0",
    "category": "Services",
    "sequence": 1,
    "summary": "Event Planner Management Event Planning Management Event Management Event Planning Software Event Planner Software Wedding Planner Software Catering Management Banquet Event Order BEO Event Agency Management Event Booking Event Budget Management Run of Show Event Vendor Management Event Staffing Guest List Management Event CRM Event Project Management Party Planning Corporate Event Management Event Coordination Wedding Management Event Checklist Event Proposal Venue Management Event Payment Schedule",
    "description": """
Event Planning Management for Odoo turns Odoo into one workspace to plan, coordinate and deliver events, from the first inquiry to the final invoice. One event record fuses the sales pipeline and the planning work, so nothing is re-typed.

This event planning app lets a client send an inquiry from your website, receive an online quote, e-sign it and pay a deposit, and the event books itself: it opens a project with a checklist whose deadlines count back from the event date.

Key Features
* Turn a sales inquiry into a fully planned event in one click, carrying the client, date and type
* Send an online quote the client can e-sign and pay a deposit on, which books the event
* Build a checklist on each booked event with deadlines counted back from the event date
* Source vendors and raise real purchase orders, and re-source when a vendor drops out
* Track estimated, contracted and actual cost from purchase orders and bills, with each event margin
* Assign staff with automatic double-booking blocks, and manage a guest list with RSVP and seating
* Set up installment payment plans from reusable schemes and invoice each one
* Print Banquet Event Orders, run-of-show and budget sheets, and watch revenue and margins on a live dashboard

How It Works
Event planning starts when a client sends an inquiry from your website, which lands as a lead. Turn it into an event in one click, then send a quote the client signs and pays a deposit on. Once signed and paid, the event books itself.

Booking opens an event project and builds its checklist, with each task due a set number of days before the event, such as 30 and 7 days out. You source vendors and raise purchase orders, and the budget tracks estimated, contracted and actual cost.

Closer to the day, staff the event with double-booking blocked, finalise the guest list, and lay out a minute-by-minute run of show. Installments invoice on schedule, daily reminders chase payments and staff, and a dashboard keeps the agency in view.

Who It Is For
It is built for event planning agencies, wedding and party planners, corporate event teams, caterers, and banquet and venue managers.

Benefits
* Book faster by letting clients quote, sign and pay a deposit online
* Never miss a deadline with checklists that count back from the event date
* Protect margin by tracking cost against revenue on every event
* Keep clients in the loop with a self-service portal

Works with Odoo 19 Community and Enterprise, alongside the CRM, Sales, Purchase, Project and Website apps.

Bring inquiry, planning and billing into one event planning system with Odoo.
""",
    "depends": [
        "crm",
        "sale_management",
        "sale_project",
        "purchase",
        "calendar",
        "hr",
        "survey",
        "portal",
        "website",
        "website_crm",
    ],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "security/record_rules.xml",
        "data/ir_sequence_data.xml",
        "data/planner_event_stage_data.xml",
        "data/planner_vendor_category_data.xml",
        "data/planner_budget_category_data.xml",
        "data/planner_payment_scheme_data.xml",
        "data/planner_event_type_data.xml",
        "data/mail_template_data.xml",
        "data/ir_cron_data.xml",
        "report/planner_report_actions.xml",
        "report/planner_report_templates.xml",
        "views/planner_event_views.xml",
        "views/planner_event_stage_views.xml",
        "views/planner_event_type_views.xml",
        "views/planner_event_guest_views.xml",
        "views/planner_event_staff_line_views.xml",
        "views/planner_vendor_views.xml",
        "views/planner_config_views.xml",
        "views/crm_lead_views.xml",
        "views/sale_order_views.xml",
        "views/project_views.xml",
        "views/purchase_order_views.xml",
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
        "views/portal_templates.xml",
        "views/website_templates.xml",
        "wizard/planner_event_quote_wizard_views.xml",
        "wizard/planner_event_reschedule_wizard_views.xml",
        "wizard/planner_event_cancel_wizard_views.xml",
        "wizard/planner_event_duplicate_wizard_views.xml",
        "views/planner_menus.xml",
        "views/planner_dashboard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "dev_event_planner_management/static/src/dashboard/**/*",
        ],
        "web.assets_frontend": [
            "dev_event_planner_management/static/src/website/scss/planner_website.scss",
            "dev_event_planner_management/static/src/website/js/planner_website.js",
        ],
    },
    "demo": [
        "demo/planner_demo.xml",
    ],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    #author and support Details
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'https://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':59.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    "license": "LGPL-3",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
