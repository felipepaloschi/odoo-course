from odoo import models, fields, api, _
from odoo.exceptions import UserError


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
    attendance_product_ids = fields.One2many(
        comodel_name="animal.attendance.product",
        inverse_name="attendance_id",
        string="Products",
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
    total_products = fields.Float(
        string="Total Products", compute="_compute_total_products"
    )
    total_invoiced = fields.Float(
        string="Total Invoiced Products", compute="_compute_total_invoiced"
    )
    invoice_counter = fields.Integer(
        string="Invoice Counter", compute="_compute_invoice_counter"
    )

    @api.multi
    def _compute_invoice_counter(self):
        for item in self:
            item.invoice_counter = len(
                item.attendance_product_ids.mapped("invoice_line_id").mapped(
                    "invoice_id"
                )
            )

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

    @api.multi
    def _compute_total_products(self):
        for item in self:
            item.total_products = sum(
                product.subtotal for product in item.attendance_product_ids
            )

    @api.multi
    def _compute_total_invoiced(self):
        for item in self:
            item.total_invoiced = sum(
                product.subtotal
                for product in item.attendance_product_ids
                if product.invoiced
            )


class AnimalStage(models.Model):
    _name = "animal.stage"
    _description = "Animal Stage"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
    fold = fields.Boolean(string="Fold")


class AnimalAttendanceProduct(models.Model):
    _name = "animal.attendance.product"
    _description = "Animal Attendance product"

    product_id = fields.Many2one(
        comodel_name="product.product", string="Product",
    )
    quantity = fields.Integer(string="Quantity", default=1)
    price_unit = fields.Float(string="Price Unit")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal")
    invoiced = fields.Boolean(
        string="Invoiced", compute="_compute_invoiced", store=True
    )
    attendance_id = fields.Many2one(
        comodel_name="animal.attendance", string="Attendance"
    )
    invoice_line_id = fields.Many2one(
        comodel_name="account.invoice.line", string="Invoice Line"
    )

    @api.multi
    @api.depends("invoice_line_id")
    def _compute_invoiced(self):
        for item in self:
            item.invoiced = True if item.invoice_line_id else False

    @api.multi
    @api.onchange("product_id")
    def _onchange_product_id(self):
        for item in self:
            item.price_unit = item.product_id.list_price

    @api.multi
    @api.onchange("product_id", "price_unit", "quantity")
    def _compute_subtotal(self):
        for item in self:
            item.subtotal = item.price_unit * item.quantity

    @api.multi
    def unlink(self):
        if any(item.invoiced for item in self):
            raise UserError(_("You can't delete a invoiced line!"))
        return super(AnimalAttendanceProduct, self).unlunk()
