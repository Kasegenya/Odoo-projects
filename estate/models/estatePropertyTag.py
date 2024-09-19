from odoo import models,fields

class PropertyTag(models.Model):
    _name = "estate.property.tags"
    _description = "This are estate property Tags"
    _order = "name "

    name = fields.Char()
    color = fields.Integer()



