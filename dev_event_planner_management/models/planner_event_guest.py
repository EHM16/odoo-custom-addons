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


class PlannerMealChoice(models.Model):
    _name = 'planner.meal.choice'
    _description = 'Meal Choice'
    _order = 'event_id, name'

    event_id = fields.Many2one(
        'planner.event', required=True, ondelete='cascade', index=True)
    name = fields.Char(required=True)
    notes = fields.Char(string='Dietary Notes')
    guest_count = fields.Integer(compute='_compute_guest_count', string='Guests')

    def _compute_guest_count(self):
        counts = {
            choice: seats
            for choice, seats in self.env['planner.event.guest']._read_group(
                [('meal_choice_id', 'in', self.ids)], ['meal_choice_id'], ['seats:sum'])
        }
        for choice in self:
            choice.guest_count = counts.get(choice, 0)


class PlannerEventGuest(models.Model):
    _name = 'planner.event.guest'
    _description = 'Event Guest'
    _order = 'event_id, name'

    event_id = fields.Many2one(
        'planner.event', required=True, ondelete='cascade', index=True)
    name = fields.Char(string='Guest Name', required=True)
    email = fields.Char()
    phone = fields.Char()
    rsvp_state = fields.Selection([
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ], string='Attendance Status', default='pending', required=True)
    meal_choice_id = fields.Many2one(
        'planner.meal.choice', string='Meal Choice',
        domain="[('event_id', '=', event_id)]")
    table_ref = fields.Char(string='Table')
    seats = fields.Integer(default=1, help='Guest plus companions.')
    is_vip = fields.Boolean(string='VIP')
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        guests = super().create(vals_list)
        guests.event_id._log_post_lock_change(self.env._('guest list changed'))
        return guests

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get('skip_lock_log'):
            self.event_id._log_post_lock_change(self.env._('guest list changed'))
        return res

    def unlink(self):
        events = self.event_id
        res = super().unlink()
        events._log_post_lock_change(self.env._('guest removed'))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
