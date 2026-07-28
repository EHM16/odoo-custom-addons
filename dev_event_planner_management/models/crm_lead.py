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


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    planner_event_id = fields.Many2one(
        'planner.event', string='Planned Event',
        compute='_compute_planner_event_id')
    event_type_id = fields.Many2one('planner.event.type', string='Event Type')

    def _compute_planner_event_id(self):
        events = self.env['planner.event'].search([('lead_id', 'in', self.ids)])
        mapping = {event.lead_id.id: event.id for event in events}
        for lead in self:
            lead.planner_event_id = mapping.get(lead.id, False)

    def action_convert_to_event(self):
        self.ensure_one()
        if self.planner_event_id:
            return self._action_open_planner_event()
        if not self.partner_id:
            self._handle_partner_assignment(create_missing=True)
        event = self.env['planner.event'].create({
            'name': self.name,
            'partner_id': self.partner_id.id,
            'lead_id': self.id,
            'user_id': self.user_id.id or self.env.user.id,
            'event_type_id': self.event_type_id.id,
            'date_start': self.date_deadline and fields.Datetime.to_datetime(
                self.date_deadline) or fields.Datetime.now(),
            'contact_person': self.contact_name,
            'note': self.description,
        })
        self.invalidate_recordset(['planner_event_id'])
        self.message_post(body=self.env._(
            'Converted to planned event %(ref)s.', ref=event.reference))
        return self._action_open_planner_event(event)

    def _action_open_planner_event(self, event=None):
        event = event or self.planner_event_id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'planner.event',
            'view_mode': 'form',
            'res_id': event.id,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
