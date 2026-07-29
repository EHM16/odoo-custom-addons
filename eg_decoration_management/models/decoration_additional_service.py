from odoo import models, fields, api


class DecorationAdditionalService(models.Model):
    _name = 'decoration.additional.service'
    _description = 'Decoration Additional Service'

    decoration_order_id = fields.Many2one(comodel_name='decoration.order', string='Decoration Order')
    product_id = fields.Many2one(comodel_name='product.product', string='Service')
    name = fields.Char(string='Description')
    price_unit = fields.Float(string='Service Charge')
    currency_id = fields.Many2one(comodel_name='res.currency', default=lambda self: self.env.company.currency_id)
    service_sale_order_id = fields.Many2one(comodel_name='sale.order', string='Sale Order')
    service_sale_order_state = fields.Selection(related='service_sale_order_id.state', string='Sale Order Status')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if not line.product_id:
                line.price_unit = 0.0
                line.name = False
                return
            line.price_unit = line.product_id.list_price
            line.name = line.product_id.display_name
