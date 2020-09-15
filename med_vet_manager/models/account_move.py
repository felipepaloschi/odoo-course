from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    animal_id = fields.Many2one(comodel_name="res.animal", string="Animal")
