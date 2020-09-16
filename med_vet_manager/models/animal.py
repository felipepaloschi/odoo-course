from odoo import models, fields


class ResAnimal(models.Model):
    _name = "res.animal"
    _description = "Animal"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "portal.mixin",
        "image.mixin",
    ]

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

    appointment_counter = fields.Integer(
        string="Appointment Counter", compute="_compute_appointment_counter"
    )
    amount_sold = fields.Float(
        string="Amount Invoiced", compute="_compute_amount_sold"
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

    def _compute_appointment_counter(self):
        for item in self:
            item.appointment_counter = self.env[
                "animal.appointment"
            ].search_count([("animal_id", "=", item.id)])

    def _compute_amount_sold(self):
        for item in self:
            orders = self.env["sale.order"].search(
                [
                    ("animal_id", "=", item.id),
                    ("state", "in", ["sale", "done"]),
                ]
            )
            item.amount_sold = sum(order.amount_total for order in orders)

    def create_new_appointment(self):
        appointment = self.env["animal.appointment"].create(
            {
                "animal_id": self.id,
                "partner_id": self.tutor_id.id,
                "stage_id": self.env.ref(
                    "med_vet_manager.appointment_waiting_appointment"
                ).id,
            }
        )
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "animal.appointment",
            "type": "ir.actions.act_window",
            "target": "current",
            "res_id": appointment.id,
        }

    def open_appointments(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "animal.appointment",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["animal_id", "=", self.id]],
            "name": "{} Appointments".format(self.name),
        }

    def open_sales(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["animal_id", "=", self.id]],
            "name": "{} Sales".format(self.name),
        }
