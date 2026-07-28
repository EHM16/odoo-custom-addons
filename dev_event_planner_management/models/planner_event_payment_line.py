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

PAID_STATES = ('paid', 'in_payment', 'reversed')


class PlannerEventPaymentLine(models.Model):
    _name = 'planner.event.payment.line'
    _description = 'Event Payment Installment'
    _order = 'event_id, sequence, id'

    event_id = fields.Many2one(
        'planner.event', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='event_id.company_id')
    currency_id = fields.Many2one(related='event_id.currency_id')
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Installment', required=True)
    percentage = fields.Float(string='%')
    fixed_amount = fields.Monetary(
        help='Used instead of the percentage when set.')
    amount = fields.Monetary(
        compute='_compute_amount', string='Amount',
        help='Live base: percentage of the total of confirmed sale orders — '
             'change orders automatically flow into remaining installments.')
    trigger = fields.Selection([
        ('booking', 'On Booking'),
        ('before_event', 'Days Before Event'),
        ('after_event', 'Days After Event'),
    ], default='before_event', required=True)
    days_offset = fields.Integer(string='Days')
    due_date = fields.Date(
        compute='_compute_due_date', store=True, readonly=False, copy=False)
    invoice_ids = fields.Many2many(
        'account.move', 'planner_payment_line_invoice_rel',
        'payment_line_id', 'move_id', string='Invoices', copy=False)
    invoice_id = fields.Many2one(
        'account.move', string='Invoice', compute='_compute_invoice_id',
        help='First invoice of the installment (installments prorated over '
             'several orders can have one invoice per order).')
    state = fields.Selection([
        ('to_invoice', 'To Invoice'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ], compute='_compute_state', string='Status', store=True)
    is_final = fields.Boolean(compute='_compute_is_final')
    reminder_sent_date = fields.Date(copy=False)

    @api.depends('percentage', 'fixed_amount', 'event_id.sale_order_ids.state',
                 'event_id.sale_order_ids.amount_total')
    def _compute_amount(self):
        for line in self:
            if line.fixed_amount:
                line.amount = line.fixed_amount
            else:
                base = sum(line.event_id.sale_order_ids.filtered(
                    lambda so: so.state == 'sale').mapped('amount_total'))
                line.amount = base * line.percentage / 100.0

    @api.depends('trigger', 'days_offset', 'event_id.date_start', 'event_id.date_booked')
    def _compute_due_date(self):
        for line in self:
            if line.invoice_ids:
                # Invoiced installments keep their contractual due date; a
                # reschedule must not silently move what was already billed.
                line.due_date = line.due_date
                continue
            event = line.event_id
            if line.trigger == 'booking':
                base = event.date_booked or fields.Datetime.now()
                line.due_date = base.date()
            elif event.date_start:
                delta = timedelta(days=line.days_offset)
                if line.trigger == 'before_event':
                    line.due_date = (event.date_start - delta).date()
                else:
                    line.due_date = (event.date_start + delta).date()
            else:
                line.due_date = line.due_date

    @api.depends('invoice_ids')
    def _compute_invoice_id(self):
        for line in self:
            line.invoice_id = line.invoice_ids[:1]

    @api.depends('invoice_ids.state', 'invoice_ids.payment_state', 'due_date')
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for line in self:
            posted = line.invoice_ids.filtered(lambda m: m.state == 'posted')
            if posted and all(m.payment_state in PAID_STATES for m in posted):
                line.state = 'paid'
            elif line.due_date and line.due_date < today:
                line.state = 'overdue'
            elif posted:
                line.state = 'invoiced'
            else:
                line.state = 'to_invoice'

    def _compute_is_final(self):
        for line in self:
            ordered = line.event_id.payment_line_ids.sorted(
                lambda l: (l.sequence, l.id))
            line.is_final = bool(ordered) and line == ordered[-1]

    def action_create_invoice(self):
        """Create the installment invoice(s) through the standard down-payment
        wizard (locked decision 12.2). The final installment invoices the
        remaining balance and deducts prior down payments. Non-final
        installments are prorated across all confirmed orders — a fixed down
        payment can only target one order at a time, and piling the whole
        amount on one order would corrupt the final deduction."""
        self.ensure_one()
        if self.invoice_ids:
            raise UserError(self.env._('This installment is already invoiced.'))
        orders = self.event_id.sale_order_ids.filtered(lambda so: so.state == 'sale')
        if not orders:
            raise UserError(self.env._(
                'No confirmed sale order on this event to invoice against.'))
        invoices = self.env['account.move']
        if self.is_final:
            wizard = self.env['sale.advance.payment.inv'].with_context(
                active_model='sale.order', active_ids=orders.ids).create({
                    'advance_payment_method': 'delivered',
                    'deduct_down_payments': True,
                })
            before = orders.invoice_ids
            wizard._create_invoices(orders)
            invoices = orders.invoice_ids - before
        else:
            if not self.amount:
                raise UserError(self.env._('The installment amount is zero.'))
            total_base = sum(orders.mapped('amount_total'))
            for order in orders:
                share = (self.amount * order.amount_total / total_base
                         if total_base else 0.0)
                if order.currency_id.is_zero(share):
                    continue
                wizard = self.env['sale.advance.payment.inv'].with_context(
                    active_model='sale.order', active_ids=order.ids).create({
                        'advance_payment_method': 'fixed',
                        'fixed_amount': share,
                    })
                before = order.invoice_ids
                wizard._create_invoices(order)
                invoices |= order.invoice_ids - before
        if invoices:
            invoices.write({
                'planner_event_id': self.event_id.id,
                'invoice_date_due': self.due_date,
            })
            self.invoice_ids = [(6, 0, invoices.ids)]
        if len(invoices) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': invoices.id,
            }
        return self.action_view_invoice()

    @api.model
    def _cron_send_payment_reminders(self):
        """Remind clients of installments due within 7 days or overdue, at most
        once a week per installment. Cancelled events are excluded."""
        template = self.env.ref(
            'dev_event_planner_management.mail_template_payment_reminder',
            raise_if_not_found=False)
        if not template:
            return
        today = fields.Date.context_today(self)
        horizon = today + timedelta(days=7)
        lines = self.search([
            ('due_date', '!=', False),
            ('due_date', '<=', horizon),
            ('event_id.stage_id.is_cancelled_stage', '=', False),
            ('event_id.stage_id.is_booked_stage', '=', True),
            '|', ('reminder_sent_date', '=', False),
            ('reminder_sent_date', '<=', today - timedelta(days=7)),
        ]).filtered(lambda l: l.state != 'paid' and l.amount)
        for line in lines:
            template.send_mail(line.id, force_send=False)
            line.reminder_sent_date = today

    def action_view_invoice(self):
        self.ensure_one()
        if len(self.invoice_ids) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self.invoice_ids.id,
            }
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Installment Invoices'),
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
