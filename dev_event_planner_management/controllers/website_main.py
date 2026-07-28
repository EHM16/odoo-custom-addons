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
from odoo.http import request


class PlannerWebsite(http.Controller):

    @http.route('/event-planning', type='http', auth='public', website=True, sitemap=True)
    def landing(self, **kwargs):
        return request.render(
            'dev_event_planner_management.website_landing',
            self._landing_values())

    def _landing_values(self):
        Event = request.env['planner.event'].sudo()
        done_events = Event.search_count(
            [('stage_id.is_done_stage', '=', True)])
        guests_hosted = sum(Event.search(
            [('stage_id.is_done_stage', '=', True)]).mapped('guest_count_final'))
        return {
            'event_types': request.env['planner.event.type'].sudo().search(
                [('website_published', '=', True)]),
            'portfolio_events': Event.search(
                [('is_website_published', '=', True)], limit=6,
                order='date_start desc'),
            'team': request.env['hr.employee'].sudo().search(
                [('show_on_planner_website', '=', True)], limit=8),
            'stats': {
                'events_delivered': done_events,
                'guests_hosted': guests_hosted,
                'vendor_partners': request.env['res.partner'].sudo().search_count(
                    [('is_event_vendor', '=', True)]),
            },
        }

    @http.route('/event-services', type='http', auth='public', website=True, sitemap=True)
    def services(self, **kwargs):
        return request.render(
            'dev_event_planner_management.website_services', {
                'event_types': request.env['planner.event.type'].sudo().search(
                    [('website_published', '=', True)]),
            })

    @http.route('/event-services/<model("planner.event.type"):event_type>',
                type='http', auth='public', website=True, sitemap=True)
    def service_detail(self, event_type, **kwargs):
        if not event_type.sudo().website_published and not request.env.user.has_group(
                'website.group_website_designer'):
            return request.redirect('/event-services')
        return request.render(
            'dev_event_planner_management.website_service_detail',
            {'event_type': event_type.sudo()})

    @http.route('/event-portfolio', type='http', auth='public', website=True, sitemap=True)
    def portfolio(self, event_type=None, **kwargs):
        domain = [('is_website_published', '=', True)]
        active_type = None
        if event_type:
            try:
                active_type = int(event_type)
                domain.append(('event_type_id', '=', active_type))
            except ValueError:
                pass
        return request.render(
            'dev_event_planner_management.website_portfolio', {
                'events': request.env['planner.event'].sudo().search(
                    domain, order='date_start desc', limit=24),
                'event_types': request.env['planner.event.type'].sudo().search(
                    [('website_published', '=', True)]),
                'active_type': active_type,
            })

    @http.route('/plan-my-event', type='http', auth='public', website=True, sitemap=True)
    def inquiry_form(self, **kwargs):
        return request.render(
            'dev_event_planner_management.website_inquiry_form', {
                'event_types': request.env['planner.event.type'].sudo().search([]),
            })

    @http.route('/plan-my-event/submit', type='http', auth='public', website=True,
                methods=['POST'], csrf=True)
    def inquiry_submit(self, **post):
        if not post.get('name') or not post.get('email'):
            return request.redirect('/plan-my-event')
        if post.get('website_extra'):
            # Honeypot field filled in: a bot. Pretend success, create nothing.
            return request.render(
                'dev_event_planner_management.website_inquiry_thanks',
                {'contact_name': post.get('name')})
        event_type = None
        if post.get('event_type_id'):
            try:
                event_type = request.env['planner.event.type'].sudo().browse(
                    int(post['event_type_id'])).exists()
            except (ValueError, TypeError):
                event_type = None
        description_bits = [
            ('Event type', event_type and event_type.name or '-'),
            ('Preferred date', post.get('event_date') or '-'),
            ('Guests', post.get('guest_count') or '-'),
            ('Budget range', post.get('budget_range') or '-'),
            ('Message', post.get('message') or '-'),
        ]
        lead_values = {
            'name': '%s — %s' % (
                event_type and event_type.name or 'Event Inquiry',
                post.get('name')),
            'type': 'lead',
            'contact_name': post.get('name'),
            'email_from': post.get('email'),
            'phone': post.get('phone'),
            'description': '\n'.join('%s: %s' % bit for bit in description_bits),
            'medium_id': request.env.ref('utm.utm_medium_website').id,
            'event_type_id': event_type.id if event_type else False,
        }
        lead = request.env['crm.lead'].sudo().create(lead_values)
        template = request.env.ref(
            'dev_event_planner_management.mail_template_inquiry_autoresponse',
            raise_if_not_found=False)
        if template:
            template.sudo().send_mail(lead.id, force_send=False)
        return request.render(
            'dev_event_planner_management.website_inquiry_thanks',
            {'contact_name': post.get('name')})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
