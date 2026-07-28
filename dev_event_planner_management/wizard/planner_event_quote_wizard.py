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


class PlannerEventQuoteWizard(models.TransientModel):
    _name = 'planner.event.quote.wizard'
    _description = 'Create Event Quotation'

    event_id = fields.Many2one('planner.event', required=True)
    partner_id = fields.Many2one(related='event_id.partner_id')
    product_ids = fields.Many2many(
        'product.template', string='Packages / Services',
        domain=[('sale_ok', '=', True), ('type', '=', 'service')])
    sale_order_template_id = fields.Many2one(
        'sale.order.template', string='Quotation Template')
    require_signature = fields.Boolean(string='Online Signature', default=True)
    require_payment = fields.Boolean(string='Online Deposit Payment', default=True)
    prepayment_percent = fields.Float(
        string='Deposit %',
        help='Prepayment percentage requested to confirm the quote online.')

    @api.onchange('event_id')
    def _onchange_event_id(self):
        if self.event_id:
            event_type = self.event_id.event_type_id
            self.product_ids = event_type.default_package_product_ids
            self.prepayment_percent = event_type.payment_scheme_id.deposit_percentage

    def action_create_quotation(self):
        self.ensure_one()
        event = self.event_id
        bad_products = self.product_ids.filtered(
            lambda p: p.invoice_policy != 'order')
        if bad_products:
            raise UserError(self.env._(
                'These packages are invoiced on delivered quantities, which '
                'breaks installment invoicing — set their invoicing policy to '
                '"Ordered quantities": %(products)s',
                products=', '.join(bad_products.mapped('name'))))
        event._ensure_project()
        order = self.env['sale.order'].create({
            'partner_id': event.partner_id.id,
            'planner_event_id': event.id,
            'project_id': event.project_id.id,
            'origin': event.reference,
            'sale_order_template_id': self.sale_order_template_id.id or False,
        })
        if self.sale_order_template_id:
            # Template lines/options are only applied by the UI onchange —
            # a plain create() never populates them.
            order._onchange_sale_order_template_id()
        # Applied after the template so the wizard's booking terms win
        order.write({
            'require_signature': self.require_signature,
            'require_payment': self.require_payment,
            'prepayment_percent': (self.prepayment_percent or 100.0) / 100.0,
        })
        self.env['sale.order.line'].create([{
            'order_id': order.id,
            'product_id': product.product_variant_id.id,
            'product_uom_qty': 1,
        } for product in self.product_ids])
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': order.id,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
