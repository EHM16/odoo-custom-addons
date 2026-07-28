# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class PlannerEventRescheduleWizard(models.TransientModel):
    _name = 'planner.event.reschedule.wizard'
    _description = 'Reschedule Event'

    event_id = fields.Many2one('planner.event', required=True)
    current_date_start = fields.Datetime(related='event_id.date_start')
    new_date_start = fields.Datetime(string='New Start', required=True)
    new_date_end = fields.Datetime(
        string='New End', compute='_compute_new_date_end', store=True, readonly=False)
    force = fields.Boolean(
        string='Ignore Conflicts',
        help='Apply the new date even if the venue or staff have conflicts.')

    @api.depends('new_date_start')
    def _compute_new_date_end(self):
        for wizard in self:
            event = wizard.event_id
            if wizard.new_date_start and event.date_start and event.date_end:
                duration = event.date_end - event.date_start
                wizard.new_date_end = wizard.new_date_start + duration

    def action_reschedule(self):
        self.ensure_one()
        event = self.event_id
        old_start = event.date_start
        delta = self.new_date_start - old_start

        # 1. Conflict check against the *target* date, before applying
        if not self.force:
            self._check_target_conflicts()

        # 2. Shift the event dates (single entry point — locked decision 12.5)
        event.with_context(skip_lock_log=True).write({
            'date_start': self.new_date_start,
            'date_end': self.new_date_end or False,
        })

        # 3. Re-align template-generated open task deadlines to the new date
        # (recomputed from the template offset — locked decision 12.5)
        open_tasks = event.project_id.task_ids.filtered(
            lambda t: t.checklist_template_line_id
            and t.state not in ('1_done', '1_canceled'))
        for task in open_tasks:
            task.date_deadline = self.new_date_start + timedelta(
                days=task.checklist_template_line_id.days_offset)

        # 4. Shift schedule lines, staff shifts, vendor arrival times
        for line in event.schedule_line_ids:
            line.with_context(skip_lock_log=True).write({
                'time_start': line.time_start + delta,
                'time_end': line.time_end + delta if line.time_end else False,
            })
        confirmed_staff = event.staff_line_ids.filtered(lambda l: l.state == 'confirmed')
        # Reset BEFORE shifting dates: staff who accepted the old date never
        # agreed to the new one, and the overlap constraint only inspects
        # confirmed lines — shifting while still confirmed would trip it on
        # back-to-back shifts of this same event.
        confirmed_staff.write({'state': 'requested'})
        for line in event.staff_line_ids.filtered(
                lambda l: l.state not in ('declined', 'cancelled')):
            line.write({
                'date_from': line.date_from + delta,
                'date_to': line.date_to + delta,
            })
        confirmed_staff.action_request()

        for vendor_line in event.vendor_line_ids.filtered('arrival_time'):
            vendor_line.with_context(skip_lock_log=True).arrival_time = (
                vendor_line.arrival_time + delta)
        booked_vendors = event.vendor_line_ids.filtered(
            lambda l: l.state in ('booked', 'confirmed'))
        booked_vendors.with_context(skip_lock_log=True).write(
            {'needs_reconfirmation': True})
        for vendor_line in booked_vendors:
            event.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=self.env._(
                    'Reconfirm vendor %(vendor)s for the new date',
                    vendor=vendor_line.vendor_id.name),
                user_id=event.user_id.id)

        # 5. Recompute offset-based payment due dates, log a tracked summary
        event.payment_line_ids.filtered(
            lambda l: not l.invoice_id)._compute_due_date()
        event.message_post(body=self.env._(
            'Event rescheduled from %(old)s to %(new)s. Open checklist deadlines, '
            'run-of-show, staff shifts, vendor arrival times and pending payment '
            'due dates were shifted. %(staff)s confirmed staff shift(s) were reset '
            'to Requested; %(vendors)s booked vendor(s) flagged for reconfirmation.',
            old=old_start, new=self.new_date_start,
            staff=len(confirmed_staff), vendors=len(booked_vendors)))
        return {'type': 'ir.actions.act_window_close'}

    def _check_target_conflicts(self):
        self.ensure_one()
        event = self.event_id
        # Venue: simulate the new dates with a search identical to the live check
        if event.venue_id:
            date_end = self.new_date_end or self.new_date_start
            confirmed = event.search([
                ('id', '!=', event.id),
                ('venue_id', '=', event.venue_id.id),
                ('stage_id.is_cancelled_stage', '=', False),
                ('stage_id.is_booked_stage', '=', True),
                ('date_start', '<=', date_end),
                '|', ('date_end', '>=', self.new_date_start),
                '&', ('date_end', '=', False),
                ('date_start', '>=', self.new_date_start),
            ], limit=1)
            if confirmed:
                raise UserError(self.env._(
                    'The venue is already booked on the target date by '
                    '"%(event)s". Tick "Ignore Conflicts" to proceed anyway.',
                    event=confirmed.name))
        delta = self.new_date_start - event.date_start
        for line in event.staff_line_ids.filtered(lambda l: l.state == 'confirmed'):
            overlap = self.env['planner.event.staff.line'].search([
                ('id', '!=', line.id),
                ('employee_id', '=', line.employee_id.id),
                ('state', '=', 'confirmed'),
                ('event_id', '!=', event.id),
                ('event_id.stage_id.is_cancelled_stage', '=', False),
                ('date_from', '<', line.date_to + delta),
                ('date_to', '>', line.date_from + delta),
            ], limit=1)
            if overlap:
                raise UserError(self.env._(
                    '%(employee)s is already confirmed on "%(event)s" at the '
                    'target date. Tick "Ignore Conflicts" to proceed anyway.',
                    employee=line.employee_id.name, event=overlap.event_id.name))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
