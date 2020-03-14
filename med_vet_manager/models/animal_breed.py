from odoo import models, fields


class AnimalBreed(models.Model):
    _name = "animal.breed"
    _description = "Animal Breed"

    name = fields.Char(string="Name", required=True)
    species_id = fields.Many2one(
        comodel_name="animal.species", string="Species", required=True
    )
    class_id = fields.Many2one(related="species_id.class_id", string="Class")
    image = fields.Binary(string="Image", attachment=True)

    _sql_constraints = [
        (
            "breed_name_uniq",
            "unique(name)",
            "This breed is already on the system!",
        )
    ]
