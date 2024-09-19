from odoo import models, fields
from odoo.exceptions import ValidationError


class EmployeeData(models.Model):
    _name = "employee.data"
    _description = "All Employee's Details"

    name = fields.Many2one("res.users", string="Request Name", default=lambda self: self.env.user.id)
    description = fields.Char(string="Description")
    start_date = fields.Date(string="Start Date")
    return_date = fields.Date(string="Return Date")
    amount_required = fields.Float(string="Amount required")
    project = fields.Selection(
        [
            ("tpdc", "TPDC PROJECT"),
            ("eacop", "EACOP PROJECT"),
            ("kidimbi", "KIDIMBWI PROJECT")

        ],
        string="Project")
    project_manager = fields.Selection(
        [
            ("prisca", "Madam Prisca"),
            ("martha", "Madam Martha")
        ],
        string="Project Manager")

    executive_director = fields.Selection(
        [
            ("careen", "Madam Careen"),
            ("ima", "Mr Ima")
        ]
    )

    managing_director = fields.Selection(
        [
            ("chris", "Mr Christopher"),
            ("calvin", "Mr Calvin")
        ]
    )

    donor_contribution_id = fields.One2many("imprest.donor.contribution", "request_id", string="Donor")

    approval_level1_date = fields.Date(string="Level 1 Approval Date", readonly=True)
    approval_level1_status = fields.Selection(
        [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        string="Level 1 Approval Status", default='pending', readonly=True)

    approval_level2_date = fields.Date(string="Level 2 Approval Date", readonly=True)
    approval_level2_status = fields.Selection(
        [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        string="Level 2 Approval Status", default='pending', readonly=True)

    approval_level3_date = fields.Date(string="Level 3 Approval Date", readonly=True)
    approval_level3_status = fields.Selection(
        [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        string="Level 3 Approval Status", default='pending', readonly=True)

    def action_approve_level1(self):
        self.approval_level1_status = 'approved'
        self.approval_level1_date = fields.Date.today()

    def action_approve_level2(self):
        if self.approval_level1_status == 'approved':
            self.approval_level2_status = 'approved'
            self.approval_level2_date = fields.Date.today()
        else:
            raise ValidationError("Level 1 must be approved before Level 2.")

    def action_approve_level3(self):
        if self.approval_level2_status == 'approved':
            self.approval_level3_status = 'approved'
            self.approval_level3_date = fields.Date.today()
        else:
            raise ValidationError("Level 2 must be approved before Level 3.")

    request_submit_id = fields.One2many('request.approval', 'requests_submitted_id', string="Request submit id")
    _sql_constraints = [
        ("unique_request_submitted_id", "UNIQUE(request_submit_id)", "Each request submitted should be linked to only "
                                                                     "one request submit")
    ]
