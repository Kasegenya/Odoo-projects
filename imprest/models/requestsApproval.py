from odoo import models, fields, api


class RequestApproval(models.Model):
    _name = 'request.approval'
    _description = 'Requests Approval view'

    requests_submitted_id = fields.Many2one('employee.data', string="Requests Submitted")
