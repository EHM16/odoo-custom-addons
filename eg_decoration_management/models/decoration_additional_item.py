from odoo import models, fields, api


class DecorationAdditionalItem(models.Model):
    _name = 'decoration.additional.item'
    _description = 'Decoration Additional Item'

    decoration_order_id = fields.Many2one(comodel_name='decoration.order', string='Decoration Order')
    product_id = fields.Many2one(comodel_name='product.product', string='Decoration Item')
    name = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0)
    uom_id = fields.Many2one(comodel_name='uom.uom')
    price_unit = fields.Float(string='Unit Price')
    currency_id = fields.Many2one(comodel_name='res.currency', default=lambda self: self.env.company.currency_id)
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal', store=True)
    item_sale_order_id = fields.Many2one(comodel_name='sale.order', string='Sale Order')
    item_sale_order_state = fields.Selection(related='item_sale_order_id.state', string='Sale Order Status')

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if not line.product_id:
                line.price_unit = 0.0
                line.uom_id = False
                line.name = False
                return
            line.price_unit = line.product_id.list_price
            line.uom_id = line.product_id.uom_id
            line.name = line.product_id.display_name

    def action_view_delivery_order(self):
        self.ensure_one()
        if not self.item_sale_order_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivery Orders',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('sale_id', '=', self.item_sale_order_id.id)],
            'context': {'create': False},
        }
