from odoo import models, fields, api


class AnimalAttendance(models.Model):
    _name = "animal.attendance"
    _description = "Animal Attendance"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _get_attendance_name(self):
        return self.env["ir.sequence"].next_by_code(
            "attendance.name.sequence"
        )

    name = fields.Char(
        string="Name",
        readonly=True,
        copy=False,
        required=True,
        default=_get_attendance_name,
        track_visibility="always",
    )
    description = fields.Text(string="Description")
    animal_id = fields.Many2one(comodel_name="res.animal", string="Animal")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Tutor")
    service_ids = fields.Many2many(
        comodel_name="product.template", string="Services"
    )
    stage_id = fields.Many2one(
        comodel_name="animal.stage",
        string="Stage",
        track_visibility="onchange",
        group_expand="_read_group_stage_ids",
    )
    active = fields.Boolean(
        string="Active", track_visibility="onchange", default=True
    )
    color = fields.Integer(string="Color")
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        default=lambda self: self.env.user.id,
    )

    def button_generate_invoice(self):
        return

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env["animal.stage"].sudo().search(domain, order=order)

    @api.multi
    def name_get(self):
        res = []
        for item in self:
            res.append(
                (item.id, "{} - {}".format(item.name, item.animal_id.name))
            )
        return res


class AnimalStage(models.Model):
    _name = "animal.stage"
    _description = "Animal Stage"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
    fold = fields.Boolean(string="Fold")
