from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    animal_id = fields.Many2one(comodel_name="res.animal", string="Animal")
