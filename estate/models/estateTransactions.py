from odoo import fields, models


class Transactions(models.Model):
    _name = "estate.transactions"
    _description = "This are estate's Transaction"

    name = fields.Char(string="Transaction ID")
    lease_date = fields.Char()