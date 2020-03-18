from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    animal_id = fields.Many2one(comodel_name="res.animal", string="Animal")
