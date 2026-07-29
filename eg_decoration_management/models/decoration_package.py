from odoo import models, fields, api
from odoo.exceptions import ValidationError
from random import randint
from odoo.exceptions import UserError
import base64


class DecorationPackage(models.Model):
    _name = 'decoration.package'
    _description = 'Decoration Package'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Name")
    color = fields.Integer(string="Color", default=_get_default_color)
    image = fields.Image(string="Image")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], default='draft', tracking=True)
    bom_id = fields.Many2one(comodel_name='mrp.bom', string="BoM", )
    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    currency_id = fields.Many2one(comodel_name='res.currency', default=lambda self: self.env.company.currency_id)
    sales_price = fields.Monetary(string='Sales Price')
    uom_id = fields.Many2one(comodel_name='uom.uom', related='product_id.uom_id', string='Units')
    cost_price = fields.Monetary(string='Cost')
    uom = fields.Char(related='product_id.uom_name')
    package_item_ids = fields.One2many(comodel_name='decoration.package.item', inverse_name='decoration_package_id',
                                       string='Decoration Items')
    image_ids = fields.One2many(comodel_name='decoration.package.image', inverse_name='decoration_package_id',
                                string='Decoration Images')
    description = fields.Text(string="Description")

    def action_confirm(self):
        for rec in self:
            if not rec.package_item_ids:
                raise UserError("Please add at least one package item before confirming.")
            rec.state = 'confirm'

    def action_send_decoration_package_mail(self):
        if not self.product_id:
            raise UserError("Please select Product before sending email.")
        report_id = self.env.ref('eg_decoration_management.report_decoration_package_custom')
        pdf_content, _ = report_id._render_qweb_pdf(report_id.report_name, [self.id])
        attachment_id = self.env['ir.attachment'].create({
            'name': f"Decoration_Package_{self.name}.pdf",
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'decoration.package',
            'res_id': self.id,
            'mimetype': 'application/pdf', })
        subject = f"Decoration Package - {self.name}"
        body_html = f"""
            <p>Hello,</p>
            <p>Please find attached the details of decoration package.</p>
            <ul>
                <li><strong>Package Name:</strong> {self.name}</li>
                <li><strong>Product:</strong> {self.product_id.display_name or '-'}</li>
                <li><strong>Sale Price:</strong> {self.sales_price} {self.currency_id.symbol}</li>
                <li><strong>Description:</strong> {self.description or '-'}</li>
            </ul>
            <p>For any queries, please contact us.</p>
            <p>Regards,<br/>
            {self.env.user.name}</p>
        """
        action = self.env['ir.actions.actions']._for_xml_id('mail.action_email_compose_message_wizard')
        action['context'] = {
            'default_model': 'decoration.package',
            'default_res_ids': [self.id],
            'default_composition_mode': 'comment',
            'default_subject': subject,
            'default_attachment_ids': [(6, 0, [attachment_id.id])],
            'default_body': body_html,
        }
        return action
