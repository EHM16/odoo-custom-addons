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
from odoo.exceptions import ValidationError


class PlannerEventScheduleLine(models.Model):
    _name = 'planner.event.schedule.line'
    _description = 'Run-of-Show Line'
    _order = 'event_id, time_start, sequence, id'

    event_id = fields.Many2one(
        'planner.event', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(default=10)
    time_start = fields.Datetime(string='Start', required=True)
    time_end = fields.Datetime(string='End')
    name = fields.Char(string='Activity', required=True)
    location = fields.Char()
    responsible_type = fields.Selection([
        ('staff', 'Staff'),
        ('vendor', 'Vendor'),
        ('client', 'Client'),
    ], default='staff')
    employee_id = fields.Many2one('hr.employee', string='Staff Member')
    vendor_line_id = fields.Many2one(
        'planner.event.vendor.line', string='Vendor',
        domain="[('event_id', '=', event_id)]")
    notes = fields.Text()

    @api.constrains('time_start', 'time_end')
    def _check_times(self):
        for line in self:
            if line.time_end and line.time_end < line.time_start:
                raise ValidationError(self.env._(
                    '"%(name)s": end time cannot be before start time.', name=line.name))

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.event_id._log_post_lock_change(self.env._('run-of-show line added'))
        return lines

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get('skip_lock_log'):
            self.event_id._log_post_lock_change(self.env._('run-of-show updated'))
        return res

    def unlink(self):
        events = self.event_id
        res = super().unlink()
        events._log_post_lock_change(self.env._('run-of-show line removed'))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
