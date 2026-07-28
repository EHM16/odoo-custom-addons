# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class PlannerCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'event_count' in counters:
            PlannerEvent = request.env['planner.event']
            values['event_count'] = (
                PlannerEvent.search_count([])
                if PlannerEvent.has_access('read') else 0)
        return values

    @http.route(['/my/events', '/my/events/page/<int:page>'],
                type='http', auth='user', website=True)
    def portal_my_events(self, page=1, **kwargs):
        PlannerEvent = request.env['planner.event']
        domain = []
        event_count = PlannerEvent.search_count(domain)
        pager = portal_pager(
            url='/my/events', total=event_count, page=page, step=10)
        events = PlannerEvent.search(
            domain, order='date_start desc', limit=10, offset=pager['offset'])
        return request.render(
            'dev_event_planner_management.portal_my_events', {
                'page_name': 'planner_events',
                # The record rule filtered the search; render sudo so related
                # records (stage, venue) the portal user cannot read still
                # display instead of raising AccessError.
                'events': events.sudo(),
                'pager': pager,
            })

    @http.route('/my/events/<int:event_id>', type='http', auth='user', website=True)
    def portal_event_detail(self, event_id, access_token=None, **kwargs):
        try:
            event_sudo = self._document_check_access(
                'planner.event', event_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render(
            'dev_event_planner_management.portal_event_page', {
                'page_name': 'planner_events',
                'event': event_sudo,
            })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
