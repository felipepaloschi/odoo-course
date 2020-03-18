from odoo import models, fields, api


class ResAnimal(models.Model):
    _name = "res.animal"
    _description = "Animal"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Name", required=True, track_visibility="always"
    )
    species_id = fields.Many2one(
        comodel_name="animal.species",
        string="Species",
        required=True,
        track_visibility="onchange",
    )
    breed_id = fields.Many2one(
        comodel_name="animal.breed",
        string="Breed",
        track_visibility="onchange",
    )
    tutor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Tutor",
        required=True,
        track_visibility="onchange",
    )
    birthday = fields.Date(string="Birthday", track_visibility="onchange")
    age = fields.Integer(string="Age", compute="_compute_age")
    active = fields.Boolean(
        string="Active", default=True, track_visibility="onchange"
    )
    attendance_counter = fields.Integer(
        string="Attendance Counter", compute="_compute_attendance_counter"
    )
    amount_invoiced = fields.Float(
        string="Amount Invoiced", compute="_compute_amount_invoiced"
    )

    @api.multi
    def _compute_age(self):
        for item in self:
            if item.birthday:
                item.age = int(
                    (fields.Date.today() - item.birthday).days / 365.25
                )
            else:
                item.age = 0

    @api.multi
    def _compute_attendance_counter(self):
        for item in self:
            item.attendance_counter = self.env[
                "animal.attendance"
            ].search_count([("animal_id", "=", item.id)])

    @api.multi
    def _compute_amount_invoiced(self):
        for item in self:
            invoices = self.env["account.invoice"].search(
                [
                    ("animal_id", "=", item.id),
                    ("state", "in", ["open", "paid"]),
                ]
            )
            item.amount_invoiced = sum(inv.amount_total for inv in invoices)

    def create_new_attendance(self):
        attendance = self.env["animal.attendance"].create(
            {
                "animal_id": self.id,
                "partner_id": self.tutor_id.id,
                "stage_id": self.env.ref(
                    "med_vet_manager.attendance_waiting_attendance"
                ).id,
            }
        )
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "animal.attendance",
            "type": "ir.actions.act_window",
            "target": "current",
            "res_id": attendance.id,
        }

    def open_attendances(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "animal.attendance",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["animal_id", "=", self.id]],
            "name": "{} Attendancies".format(self.name),
        }

    def open_invoices(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.invoice",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["animal_id", "=", self.id]],
            "name": "{} Invoices".format(self.name),
        }
