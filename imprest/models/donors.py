from odoo import models, fields, api


class DonorContribution(models.Model):
    _name = 'imprest.donor.contribution'
    _description = 'Donor Contribution'

    request_id = fields.Many2one('employee.data', string='Imprest Request', ondelete='cascade')
    donor_id = fields.Many2one('res.partner', string='Donor', required=True,)
    contribution_percentage = fields.Float(string='Contribution Percentage', required=True)
