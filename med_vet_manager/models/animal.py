from odoo import models, fields, api


class ResAnimal(models.Model):
    _name = "res.animal"
    _description = "Animal"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True)
    species_id = fields.Many2one(
        comodel_name="animal.species", string="Species", required=True
    )
    breed_id = fields.Many2one(comodel_name="animal.breed", string="Breed")
    tutor_id = fields.Many2one(
        comodel_name="res.partner", string="Tutor", required=True
    )
    birthday = fields.Date(string="Birthday")
    age = fields.Integer(string="Age", compute="_compute_age")

    @api.multi
    def _compute_age(self):
        for item in self:
            if item.birthday:
                item.age = (fields.Date.today() - item.birthday).years
            else:
                item.age = 0
