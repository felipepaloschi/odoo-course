from odoo import models, fields


class ResAnimal(models.Model):
    _name = "res.animal"
    _description = "Animal"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]

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

    consultation_counter = fields.Integer(
        string="Consultation Counter", compute="_compute_consultation_counter"
    )
    amount_invoiced = fields.Float(
        string="Amount Invoiced", compute="_compute_amount_invoiced"
    )

    def _compute_access_url(self):
        super(ResAnimal, self)._compute_access_url()
        for animal in self:
            animal.access_url = "/my/animals/%s" % (animal.id)

    def _compute_age(self):
        for item in self:
            if item.birthday:
                item.age = int(
                    (fields.Date.today() - item.birthday).days / 365.25
                )
            else:
                item.age = 0

    def _compute_consultation_counter(self):
        for item in self:
            item.consultation_counter = self.env[
                "animal.consultation"
            ].search_count([("animal_id", "=", item.id)])

    def _compute_amount_invoiced(self):
        for item in self:
            invoices = self.env["account.move"].search(
                [
                    ("animal_id", "=", item.id),
                    ("state", "in", ["open", "paid"]),
                ]
            )
            item.amount_invoiced = sum(inv.amount_total for inv in invoices)

    def create_new_consultation(self):
        consultation = self.env["animal.consultation"].create(
            {
                "animal_id": self.id,
                "partner_id": self.tutor_id.id,
                "stage_id": self.env.ref(
                    "med_vet_manager.consultation_waiting_consultation"
                ).id,
            }
        )
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "animal.consultation",
            "type": "ir.actions.act_window",
            "target": "current",
            "res_id": consultation.id,
        }

    def open_consultations(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "animal.consultation",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["animal_id", "=", self.id]],
            "name": "{} Consultations".format(self.name),
        }

    def open_invoices(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["animal_id", "=", self.id]],
            "name": "{} Invoices".format(self.name),
        }
