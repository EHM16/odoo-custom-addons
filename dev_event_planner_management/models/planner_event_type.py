# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
from odoo import fields, models


class PlannerEventType(models.Model):
    _name = 'planner.event.type'
    _description = 'Event Type'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')
    description = fields.Text(translate=True)
    default_package_product_ids = fields.Many2many(
        'product.template', string='Default Packages',
        domain=[('type', '=', 'service'), ('sale_ok', '=', True)],
        help='Service products proposed by default on quotations for this event type.')
    project_template_id = fields.Many2one(
        'project.project', string='Project Template',
        help='Copied to create the event-owned project at booking.')
    checklist_template_ids = fields.One2many(
        'planner.checklist.template.line', 'event_type_id', string='Checklist Template')
    schedule_template_ids = fields.One2many(
        'planner.schedule.template.line', 'event_type_id', string='Run-of-Show Template')
    default_survey_id = fields.Many2one(
        'survey.survey', string='Feedback Survey',
        help='Sent to the client after the event ends.')
    payment_scheme_id = fields.Many2one(
        'planner.payment.scheme', string='Payment Scheme',
        help='Default installment plan applied to events of this type.')
    properties_definition = fields.PropertiesDefinition('Event Properties')
    event_count = fields.Integer(compute='_compute_event_count')

    def _compute_event_count(self):
        counts = dict(self.env['planner.event']._read_group(
            [('event_type_id', 'in', self.ids)], ['event_type_id'], ['__count']))
        for record in self:
            record.event_count = counts.get(record, 0)


class PlannerChecklistTemplateLine(models.Model):
    _name = 'planner.checklist.template.line'
    _description = 'Checklist Template Line'
    _order = 'days_offset, sequence, id'

    event_type_id = fields.Many2one('planner.event.type', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Task', required=True, translate=True)
    description = fields.Text(translate=True)
    days_offset = fields.Integer(
        string='Days Offset', default=-30,
        help='Deadline relative to the event date: -30 = 30 days before, '
             '3 = 3 days after.')
    responsible_role = fields.Selection([
        ('planner', 'Lead Planner'),
        ('coordinator', 'Coordinator'),
        ('user', 'Specific User'),
    ], required=True, default='planner')
    user_id = fields.Many2one('res.users', string='Specific User')


class PlannerScheduleTemplateLine(models.Model):
    _name = 'planner.schedule.template.line'
    _description = 'Run-of-Show Template Line'
    _order = 'day_offset, hour_start, sequence, id'

    event_type_id = fields.Many2one('planner.event.type', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Activity', required=True, translate=True)
    day_offset = fields.Integer(
        string='Day', default=0,
        help='0 = event start day, 1 = next day (multi-day events).')
    hour_start = fields.Float(string='Start Time', default=9.0)
    hour_end = fields.Float(string='End Time', default=10.0)
    location = fields.Char(translate=True)
    notes = fields.Text(translate=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
