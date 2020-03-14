from odoo import models, fields


class AnimalClass(models.Model):
    _name = "animal.class"

    name = fields.Char(string="Name")
