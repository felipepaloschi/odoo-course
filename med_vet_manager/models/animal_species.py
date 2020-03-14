from odoo import models, fields


class AnimalSpecies(models.Model):
    _name = "animal.species"
    _description = "Animal Species"

    name = fields.Char(string="Name", required=True)
    class_id = fields.Many2one(
        comodel_name="animal.class", string="Class"
    )
