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
from odoo.exceptions import UserError


class PlannerEventCancelWizard(models.TransientModel):
    _name = 'planner.event.cancel.wizard'
    _description = 'Cancel Event'

    event_id = fields.Many2one('planner.event', required=True)
    reason = fields.Text(string='Cancellation Reason', required=True)
    po_action = fields.Selection([
        ('cancel', 'Cancel open purchase orders'),
        ('keep', 'Keep purchase orders (settle manually)'),
    ], string='Vendor Orders', default='cancel', required=True)
    deposit_action = fields.Selection([
        ('retain', 'Retain deposit as cancellation fee'),
        ('credit', 'Refund deposit (create credit note)'),
    ], string='Paid Deposits', default='retain', required=True)
    notify_staff = fields.Boolean(string='Notify Confirmed Staff', default=True)

    def action_cancel(self):
        self.ensure_one()
        event = self.event_id
        cancelled_stage = self.env['planner.event.stage'].search(
            [('is_cancelled_stage', '=', True)], limit=1)
        if not cancelled_stage:
            raise UserError(self.env._('No cancelled stage is configured.'))

        # Staff: cancel unconfirmed shifts, notify confirmed ones
        confirmed_staff = event.staff_line_ids.filtered(lambda l: l.state == 'confirmed')
        (event.staff_line_ids - confirmed_staff).write({'state': 'cancelled'})
        if self.notify_staff:
            for line in confirmed_staff.filtered(lambda l: l.employee_id.user_id):
                event.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=self.env._(
                        'Event cancelled — shift released: %(event)s', event=event.name),
                    user_id=line.employee_id.user_id.id)
        confirmed_staff.write({'state': 'cancelled'})

        # Vendor purchase orders
        if self.po_action == 'cancel':
            for po in event.purchase_order_ids:
                if po.state in ('draft', 'sent'):
                    po.button_cancel()
                elif po.state in ('purchase', 'done'):
                    billed = po.invoice_ids.filtered(lambda m: m.state == 'posted')
                    if billed:
                        po.activity_schedule(
                            'mail.mail_activity_data_todo',
                            summary=self.env._(
                                'Event cancelled — order has posted bills, '
                                'settle with the vendor'),
                            user_id=event.user_id.id)
                    else:
                        po.button_cancel()
        event.vendor_line_ids.filtered(
            lambda l: l.state not in ('closed', 'cancelled')).with_context(
            skip_lock_log=True).write({'state': 'cancelled'})

        # Payment schedule: void what is not invoiced, handle paid deposits
        event.payment_line_ids.filtered(lambda l: not l.invoice_ids).unlink()
        paid_lines = event.payment_line_ids.filtered(lambda l: l.state == 'paid')
        if paid_lines and self.deposit_action == 'credit':
            invoices = paid_lines.invoice_ids.filtered(lambda m: m.state == 'posted')
            if invoices:
                reversal = self.env['account.move.reversal'].with_context(
                    active_model='account.move', active_ids=invoices.ids).create({
                        'journal_id': invoices[0].journal_id.id,
                        'reason': self.env._('Event cancelled: %(name)s', name=event.name),
                    })
                reversal.reverse_moves()
        elif paid_lines:
            event.message_post(body=self.env._(
                'Deposit of %(amount).2f retained as cancellation fee.',
                amount=sum(paid_lines.mapped('amount'))))

        # Checklist: cancel open template tasks
        event.project_id.task_ids.filtered(
            lambda t: t.state not in ('1_done', '1_canceled')).write(
            {'state': '1_canceled'})

        event.write({'stage_id': cancelled_stage.id})
        event.message_post(body=self.env._(
            'Event cancelled. Reason: %(reason)s', reason=self.reason))
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
