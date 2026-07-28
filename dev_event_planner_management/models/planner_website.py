# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
from odoo import api, fields, models


class PlannerEventTypeWebsite(models.Model):
    _name = 'planner.event.type'
    _inherit = ['planner.event.type', 'website.published.mixin']

    website_description = fields.Html(
        string='Website Description', translate=True, sanitize_overridable=True)
    website_tagline = fields.Char(string='Tagline', translate=True)
    cover_image = fields.Image(string='Cover Image', max_width=1920, max_height=1080)

    def _compute_website_url(self):
        super()._compute_website_url()
        for event_type in self:
            event_type.website_url = f'/event-services/{event_type.id}'


class PlannerEventWebsite(models.Model):
    _inherit = 'planner.event'

    is_website_published = fields.Boolean(
        string='Show in Portfolio', copy=False,
        help='Feature this event in the public website portfolio.')
    website_title = fields.Char(
        string='Portfolio Title',
        help='Public name shown in the portfolio — keep it anonymous if needed '
             '(e.g. "Garden Wedding for 150").')
    website_description = fields.Text(string='Portfolio Description', translate=True)
    cover_image = fields.Image(string='Cover Image', max_width=1920, max_height=1080)


class HrEmployeeWebsite(models.Model):
    _inherit = 'hr.employee'

    show_on_planner_website = fields.Boolean(
        string='Show on Event Website',
        groups='hr.group_hr_user',
        help='Feature this team member on the public event planning website.')
    planner_website_role = fields.Char(
        string='Website Role', groups='hr.group_hr_user',
        help='Public role title, e.g. "Senior Wedding Planner".')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
