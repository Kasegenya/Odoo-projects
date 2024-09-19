from odoo import models,fields

class UserData(models.Model):
    _name = 'user.data'
    _description = 'Users Information'
    name = fields.Char(string="Name")
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string="Email")
    nida = fields.Char(string="Nida Number")
    tin = fields.Char(string="TIN Number")
    user_role = fields.Selection(
        [
            ("agents", "Agents"),
            ("buyers", "Buyers"),
            ("sellers", "Sellers"),
            ("admins", "Administrators")
        ],

        string="User role")
