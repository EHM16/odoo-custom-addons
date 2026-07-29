from odoo import models, fields, api


class DecorationPackageItem(models.Model):
    _name = 'decoration.package.item'
    _description = 'Decoration Package Item'
    _order = 'sequence, id'

    decoration_order_id = fields.Many2one(comodel_name='decoration.order', string='Decoration Order')
    sequence = fields.Integer(default=10)
    display_type = fields.Selection([('line_section', "Section"), ('line_note', "Note")], default=False, string='Type')
    decoration_package_id = fields.Many2one(comodel_name='decoration.package', string='Decoration Package')
    product_id = fields.Many2one(comodel_name='product.product', string='Item')
    name = fields.Char(string='Name')
    quantity = fields.Float(default=1.0)
    uom_id = fields.Many2one(comodel_name='uom.uom', related='product_id.uom_id')
    price_unit = fields.Float(string='Price Unit', related='product_id.list_price')
    total_price = fields.Monetary(string='Total Price', compute='_compute_total_price', store=True)
    currency_id = fields.Many2one(comodel_name='res.currency', default=lambda self: self.env.company.currency_id)

    @api.depends('quantity', 'price_unit')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.quantity * line.price_unit
