from odoo import api, models, fields,exceptions
from . import estatePropertyOffer
from odoo.exceptions import ValidationError




class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'

    description = fields.Text(string="Description")
    active = fields.Boolean(default=True)
    name = fields.Char(string="name", default="House", required=True)
    expected_price = fields.Float(string="Expected Price")
    date = fields.Date(string="date")
    state = fields.Selection(
        [
            ("new", "New"),
            ("received", "Offer Received"),
            ("accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        required=True,
        copy=False,
        default="new"

    )

    status = fields.Char()
    postcode = fields.Char()
    property_type_id = fields.Many2one("estate.property.type", required=True)
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesperson_id = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.user)
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    best_offer = fields.Float(string="Best Offer", compute="_compute_best_offer")
    selling_price = fields.Float(string="Selling Price",)
    tag_ids = fields.Many2many("estate.property.tags")

    _sql_constraints = [
        ("check_postive_amount",
         "CHECK(expected_price >=0)",
         "Cannot have negative amount"),
        ("unique_names","UNIQUE(name)", "Name should be Unique"),

    ]


    bedrooms = fields.Char()
    living_area = fields.Float(string="Living Area (sqm)")
    facades = fields.Char()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Float(string="Garden Area (sqm)")
    total_area = fields.Float(compute="_compute_total")
    image = fields.Binary()

    @api.depends("living_area", "garden_area")
    def _compute_total(self):
        for entry in self:
            entry.total_area = entry.living_area + entry.garden_area


    @api.depends("offer_ids.price")
    def _compute_best_offer(self):
        for record in self:
            record.best_offer = max(record.offer_ids.mapped("price")) if record.offer_ids else 0

   # @api.depends("offer_ids")
   #  def _compute_selling_price(self):
   #      for record in self:
   #          accepted_offer = record.offer_ids.filtered(lambda o: o.state == 'accepted')
   #          if accepted_offer:
   #              record.selling_price = record.offer_ids.price
   #          elif estatePropertyOffer.refuse_action(self):
   #              record.selling_price = "0.00"

    status_state = fields.Boolean(default=False)

    def sell_action(self):
        for record in self:
            if record.status_state == False:
               record.status = "Sold"
               record.status_state =True
            elif record.status_state == True and record.status == "Sold":
                raise exceptions.UserError("Property is already Sold")
            else:
                raise exceptions.UserError("Property is already Cancelled")

    def cancel_action(self):
        for record in self:
            if record.status_state == False:
                record.status = "Cancelled"
                record.status_state = True
            elif record.status_state == True and record.status == "Cancelled":
                raise exceptions.UserError("Property is already Cancelled")

    @api.constrains("selling_price")
    def _check_price(self):
        for record in self:
            if record.selling_price < 0:
                raise ValidationError("Amount is negative")