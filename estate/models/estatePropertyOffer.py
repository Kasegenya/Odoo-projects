from odoo import api, models, fields
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from datetime import timedelta

class EstateOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Offers made for real Estate"


    price = fields.Float()
    status = fields.Selection(
        [
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy=False,
        readonly=True

    )



    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    type_id = fields.Many2one(related="property_id.property_type_id", store="True")

    validity = fields.Integer(default=7)
    date_deadline = fields.Date()

    # @api.depends("validity")
    # def _compute_date_deadline(self):
    #     for property in self:
    #         property.date_deadline = fields.Date.today() + timedelta(days=property.validity)
    #
    # def _inverse_date_deadline(self):
    #     for property in self:
    #         property.validity = timedelta(days=(property.date_deadline - fields.Date.today))



    def refuse_action(self):
        self.ensure_one()
        self.status = "refused"




    def accept_action(self):
        for record in self:
            if "accepted" in record.property_id.offer_ids.mapped("status"):
                raise UserError("already accepted")
            record.status = "accepted"
            record.property_id.selling_price = record.price
