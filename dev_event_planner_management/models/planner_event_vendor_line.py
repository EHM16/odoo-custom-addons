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
from odoo.exceptions import UserError


class PlannerEventVendorLine(models.Model):
    _name = 'planner.event.vendor.line'
    _description = 'Event Vendor Booking'
    _order = 'event_id, sequence, id'
    _rec_name = 'description'

    event_id = fields.Many2one(
        'planner.event', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='event_id.company_id')
    currency_id = fields.Many2one(related='event_id.currency_id')
    sequence = fields.Integer(default=10)
    category_id = fields.Many2one('planner.vendor.category', string='Category')
    vendor_id = fields.Many2one(
        'res.partner', string='Vendor', domain=[('is_event_vendor', '=', True)])
    description = fields.Char(string='Needed Service')
    state = fields.Selection([
        ('to_source', 'To Source'),
        ('requested', 'Requested'),
        ('quoted', 'Quoted'),
        ('booked', 'Booked'),
        ('confirmed', 'Confirmed'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], default='to_source', required=True)
    estimated_cost = fields.Monetary()
    contracted_cost = fields.Monetary(
        compute='_compute_contracted_cost', store=True, readonly=False,
        help='Defaults to the confirmed purchase order total; can be overridden.')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', copy=False)
    po_state = fields.Selection(related='purchase_order_id.state', string='PO Status')
    amount_billed = fields.Monetary(
        compute='_compute_amount_billed', string='Billed',
        help='Untaxed total of posted vendor bills on the linked purchase order.')
    arrival_time = fields.Datetime(string='Arrival Time')
    needs_reconfirmation = fields.Boolean(copy=False)
    contact_name = fields.Char(compute='_compute_contact', store=True, readonly=False)
    contact_phone = fields.Char(compute='_compute_contact', store=True, readonly=False)
    notes = fields.Text()

    @api.depends('vendor_id.name', 'description')
    def _compute_display_name(self):
        for line in self:
            vendor_name = line.vendor_id.name or 'New Vendor'
            desc = line.description or 'Service'
            line.display_name = f"{vendor_name} ({desc})"

    @api.depends('purchase_order_id.state', 'purchase_order_id.amount_total')
    def _compute_contracted_cost(self):
        for line in self:
            po = line.purchase_order_id
            if po and po.state in ('purchase', 'done'):
                line.contracted_cost = po.amount_total
            elif not line.contracted_cost:
                line.contracted_cost = 0.0

    @api.depends('purchase_order_id.invoice_ids.state',
                 'purchase_order_id.invoice_ids.amount_untaxed_signed')
    def _compute_amount_billed(self):
        for line in self:
            bills = line.purchase_order_id.invoice_ids.filtered(
                lambda m: m.state == 'posted')
            line.amount_billed = -sum(bills.mapped('amount_untaxed_signed'))

    @api.depends('vendor_id')
    def _compute_contact(self):
        for line in self:
            if line.vendor_id:
                line.contact_name = line.vendor_id.name
                line.contact_phone = line.vendor_id.phone

    def action_create_rfq(self):
        self.ensure_one()
        if not self.vendor_id:
            raise UserError(self.env._('Set a vendor on the line first.'))
        if self.purchase_order_id:
            raise UserError(self.env._('A purchase order is already linked.'))
        self.event_id._ensure_analytic_account()
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor_id.id,
            'planner_event_id': self.event_id.id,
            'origin': self.event_id.reference,
            'date_planned': self.arrival_time or self.event_id.date_start,
        })
        self.write({'purchase_order_id': po.id,
                    'state': 'requested' if self.state == 'to_source' else self.state})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': po.id,
        }

    def action_cancel_line(self):
        """Vendor drop-out flow: cancel the line, handle the PO, keep billed
        amounts as cancellation fees, offer a re-sourcing duplicate."""
        for line in self:
            po = line.purchase_order_id
            was_booked = line.state in ('booked', 'confirmed')
            if po and po.state in ('draft', 'sent'):
                po.button_cancel()
            elif po and po.state in ('purchase', 'done'):
                if not line.amount_billed:
                    po.button_cancel()
                else:
                    po.activity_schedule(
                        'mail.mail_activity_data_todo',
                        summary=self.env._('Vendor dropped out — settle this order'),
                        user_id=line.event_id.user_id.id)
            if line.amount_billed:
                cancel_categ = self.env['planner.budget.category'].search(
                    [('is_cancellation_fee', '=', True)], limit=1)
                if not cancel_categ:
                    cancel_categ = self.env['planner.budget.category'].with_context(
                        active_test=False).search(
                        [('is_cancellation_fee', '=', True)], limit=1)
                if cancel_categ:
                    self.env['planner.event.budget.line'].create({
                        'event_id': line.event_id.id,
                        'category_id': cancel_categ.id,
                        'description': self.env._(
                            'Cancellation: %(vendor)s', vendor=line.vendor_id.name),
                        'amount_actual': line.amount_billed,
                    })
                else:
                    line.event_id.message_post(body=self.env._(
                        '%(amount).2f already billed by %(vendor)s could not be '
                        'reclassified: no budget category is flagged as '
                        '"Cancellation Fees".',
                        amount=line.amount_billed, vendor=line.vendor_id.name))
            line.write({'state': 'cancelled', 'contracted_cost': 0.0})
            line.event_id.message_post(body=self.env._(
                'Vendor booking cancelled: %(vendor)s (%(service)s).',
                vendor=line.vendor_id.name or '-', service=line.description or '-'))
            if was_booked:
                line.copy({
                    'state': 'to_source',
                    'vendor_id': False,
                    'purchase_order_id': False,
                    'contracted_cost': 0.0,
                    'needs_reconfirmation': False,
                })

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.event_id._log_post_lock_change(self.env._('vendor booking added'))
        return lines

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get('skip_lock_log') and set(vals) - {'needs_reconfirmation'}:
            self.event_id._log_post_lock_change(self.env._('vendor booking updated'))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
