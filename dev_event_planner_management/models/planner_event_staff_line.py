# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
import uuid
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PlannerEventStaffLine(models.Model):
    _name = 'planner.event.staff.line'
    _description = 'Event Staff Shift'
    _order = 'date_from, id'

    event_id = fields.Many2one(
        'planner.event', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='event_id.company_id')
    event_date = fields.Datetime(related='event_id.date_start', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    role = fields.Selection([
        ('coordinator', 'Coordinator'),
        ('setup', 'Setup'),
        ('service', 'Service'),
        ('teardown', 'Teardown'),
        ('other', 'Other'),
    ], default='service', required=True)
    role_note = fields.Char(string='Role Details')
    date_from = fields.Datetime(string='Shift Start', required=True)
    date_to = fields.Datetime(string='Shift End', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('confirmed', 'Confirmed'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    ], default='draft', required=True, copy=False)
    notes = fields.Text()
    access_token = fields.Char(
        default=lambda self: uuid.uuid4().hex, copy=False, readonly=True,
        groups='dev_event_planner_management.group_event_planner_user')

    @api.depends('event_id.name', 'role')
    def _compute_display_name(self):
        for line in self:
            role_str = dict(self._fields['role'].selection).get(line.role) or line.role
            line.display_name = f"{line.event_id.name or 'Event'} - {role_str}"

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for line in self:
            if line.date_to <= line.date_from:
                raise ValidationError(self.env._('Shift end must be after shift start.'))

    @api.constrains('state', 'date_from', 'date_to', 'employee_id')
    def _check_no_double_booking(self):
        """Confirmed shifts must never overlap another confirmed shift of the
        same employee on a non-cancelled booked event (locked decision 12.3)."""
        for line in self.filtered(lambda l: l.state == 'confirmed'):
            overlap = self.search([
                ('id', '!=', line.id),
                ('employee_id', '=', line.employee_id.id),
                ('state', '=', 'confirmed'),
                ('event_id.stage_id.is_cancelled_stage', '=', False),
                ('date_from', '<', line.date_to),
                ('date_to', '>', line.date_from),
            ], limit=1)
            if overlap:
                raise ValidationError(self.env._(
                    '%(employee)s is already confirmed on "%(event)s" from %(start)s '
                    'to %(end)s.', employee=line.employee_id.name,
                    event=overlap.event_id.name, start=overlap.date_from,
                    end=overlap.date_to))

    @api.onchange('event_id')
    def _onchange_event_id(self):
        if self.event_id and not self.date_from:
            self.date_from = self.event_id.date_start
            self.date_to = self.event_id.date_end or self.event_id.date_start

    def action_request(self):
        self.filtered(lambda l: l.state == 'draft').write({'state': 'requested'})
        template = self.env.ref(
            'dev_event_planner_management.mail_template_staff_request',
            raise_if_not_found=False)
        for line in self.filtered(lambda l: l.state == 'requested'):
            if template and line.employee_id.work_email:
                template.send_mail(line.id, force_send=False)
            if line.employee_id.user_id:
                line.event_id.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=self.env._('Confirm shift: %(event)s', event=line.event_id.name),
                    user_id=line.employee_id.user_id.id,
                    date_deadline=fields.Date.context_today(line))

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_decline(self):
        self.write({'state': 'declined'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def _cron_send_confirmation_reminders(self):
        """Chase unconfirmed shifts starting within the next 3 days."""
        deadline = fields.Datetime.now() + timedelta(days=3)
        template = self.env.ref(
            'dev_event_planner_management.mail_template_staff_request',
            raise_if_not_found=False)
        if not template:
            return
        lines = self.search([
            ('state', '=', 'requested'),
            ('date_from', '<=', deadline),
            ('date_from', '>=', fields.Datetime.now()),
            ('event_id.stage_id.is_cancelled_stage', '=', False),
        ])
        for line in lines.filtered(lambda l: l.employee_id.work_email):
            template.send_mail(line.id, force_send=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
