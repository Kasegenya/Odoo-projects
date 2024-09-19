from odoo import api, models, fields

class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "test"
    _order = 'sequence desc'

    sequence = fields.Integer(default=1)


    name = fields.Selection(
        [
            ("commercial", "Commercial"),
            ("residential", "Residential")
        ],

        string="Purpose")
    type = fields.Selection(
    [
        ('retail', 'Retail'),
        ('office', 'Office'),
        ('industrial', 'Industrial'),
        ('residential', 'Residential')
    ],

    string="Type")
    attributes = fields.Char()
    property_ids = fields.One2many("estate.property", "property_type_id")

