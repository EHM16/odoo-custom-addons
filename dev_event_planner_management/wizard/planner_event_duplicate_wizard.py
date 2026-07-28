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


class PlannerEventDuplicateWizard(models.TransientModel):
    _name = 'planner.event.duplicate.wizard'
    _description = 'Duplicate Event'

    event_id = fields.Many2one('planner.event', required=True)
    name = fields.Char(string='New Event Title', required=True)
    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    date_start = fields.Datetime(string='New Event Start', required=True)

    @api.onchange('event_id')
    def _onchange_event_id(self):
        if self.event_id:
            self.name = self.env._('%(name)s (copy)', name=self.event_id.name)
            self.partner_id = self.event_id.partner_id

    def action_duplicate(self):
        """Clone for repeat clients: vendor and run-of-show lines come along
        (copy=True), schedule times shift to the new date; financials, staff
        and guest data start fresh."""
        self.ensure_one()
        source = self.event_id
        delta = self.date_start - source.date_start
        new_event = source.copy({
            'name': self.name,
            'partner_id': self.partner_id.id,
            'date_start': self.date_start,
            'date_end': source.date_end + delta if source.date_end else False,
            'stage_id': self.env['planner.event.stage'].search([], limit=1).id,
        })
        # copy() does not remap cross-links between copied one2many lines:
        # schedule lines still point at the SOURCE event's vendor lines.
        vendor_map = dict(zip(source.vendor_line_ids.ids,
                              new_event.vendor_line_ids.ids))
        for line in new_event.schedule_line_ids:
            line.with_context(skip_lock_log=True).write({
                'time_start': line.time_start + delta,
                'time_end': line.time_end + delta if line.time_end else False,
                'vendor_line_id': vendor_map.get(line.vendor_line_id.id, False),
            })
        new_event.vendor_line_ids.with_context(skip_lock_log=True).write({
            'state': 'to_source',
            'purchase_order_id': False,
            'contracted_cost': 0.0,
            'needs_reconfirmation': False,
        })
        new_event.message_post(body=self.env._(
            'Duplicated from %(ref)s.', ref=source.reference))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'planner.event',
            'view_mode': 'form',
            'res_id': new_event.id,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
