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
from odoo.tools import consteq


class PlannerStaffController(http.Controller):

    def _get_shift(self, line_id, token):
        line = request.env['planner.event.staff.line'].sudo().browse(line_id)
        if not line.exists() or not token or not consteq(
                line.access_token or '', token):
            return None
        return line

    @http.route('/planner/shift/<int:line_id>/<string:answer>/<string:token>',
                type='http', auth='public', website=True)
    def shift_ask(self, line_id, answer, token, **kwargs):
        """Mail scanners and prefetchers follow GET links: this page only
        shows the shift and a POST button — the state change happens in
        shift_answer below."""
        line = self._get_shift(line_id, token)
        if line is None or answer not in ('accept', 'decline'):
            return request.render(
                'dev_event_planner_management.shift_answer_page',
                {'status': 'invalid'})
        if line.state not in ('requested', 'confirmed', 'declined'):
            return request.render(
                'dev_event_planner_management.shift_answer_page',
                {'status': 'closed', 'line': line})
        return request.render(
            'dev_event_planner_management.shift_answer_page', {
                'status': 'ask',
                'line': line,
                'answer': answer,
                'token': token,
            })

    @http.route('/planner/shift/<int:line_id>/<string:answer>/<string:token>/confirm',
                type='http', auth='public', website=True, methods=['POST'])
    def shift_answer(self, line_id, answer, token, **kwargs):
        line = self._get_shift(line_id, token)
        if line is None or answer not in ('accept', 'decline'):
            return request.render(
                'dev_event_planner_management.shift_answer_page',
                {'status': 'invalid'})
        if line.state not in ('requested', 'confirmed', 'declined'):
            return request.render(
                'dev_event_planner_management.shift_answer_page',
                {'status': 'closed', 'line': line})
        try:
            if answer == 'accept':
                line.action_confirm()
                status = 'accepted'
            else:
                line.action_decline()
                status = 'declined'
        except Exception:
            # Typically the always-blocking staff overlap constraint
            status = 'conflict'
        if status in ('accepted', 'declined'):
            line.event_id.sudo().message_post(body=request.env._(
                '%(employee)s %(answer)s the %(role)s shift via email link.',
                employee=line.employee_id.name, answer=status, role=line.role))
        return request.render(
            'dev_event_planner_management.shift_answer_page',
            {'status': status, 'line': line})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
