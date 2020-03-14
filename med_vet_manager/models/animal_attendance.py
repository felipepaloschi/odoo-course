from odoo import models, fields


class AnimalAttendance(models.Model):
    _name = "animal.attendance"
    _description = "Animal Attendance"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
    animal_id = fields.Many2one(comodel_name="res.animal", string="Animal")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Tutor")
    service_ids = fields.Many2many(
        comodel_name="product.template", string="Services"
    )
    stage_id = fields.Many2one(comodel_name="animal.stage", string="Stage")

    def button_generate_invoice(self):
        return


class AnimalStage(models.Model):
    _name = "animal.stage"
    _description = "Animal Stage"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
    folded = fields.Boolean(string="Folded")
