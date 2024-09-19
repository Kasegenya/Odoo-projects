from odoo import models, fields, api

class QuotationXlxsWizard(models.TransientModel):
    _name = 'quotation.xlxs.wizard'
    _description = 'Quotation XLXS Wizard'

    @api.model
    def default_get(self, fields_list):
        res = super(QuotationXlxsWizard, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            order = self.env['sale.order'].browse(active_id)
            res.update({
                'order_lines': [(0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'price_unit': line.price_unit,
                    'product_uom_qty': line.product_uom_qty,
                }) for line in order.order_line],
                'company_name': order.company_id.name,
                'name': 'Quotation ' + order.name + '.xlsx',

            })
        return res

    order_lines = fields.One2many('quotation.xlxs.wizard.line', 'wizard_id', string='Order Lines')
    company_name = fields.Char(string='Company Name', readonly=True)

