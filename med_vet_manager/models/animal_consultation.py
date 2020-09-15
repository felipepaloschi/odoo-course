from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AnimalConsultation(models.Model):
    _name = "animal.consultation"
    _description = "Animal Consultation"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]

    _order = "date, id"

    def _get_consultation_name(self):
        return self.env["ir.sequence"].next_by_code(
            "consultation.name.sequence"
        )

    name = fields.Char(
        string="Name",
        readonly=True,
        copy=False,
        required=True,
        default=_get_consultation_name,
        track_visibility="always",
    )
    description = fields.Text(string="Description")
    animal_id = fields.Many2one(comodel_name="res.animal", string="Animal")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Tutor")
    consultation_product_ids = fields.One2many(
        comodel_name="animal.consultation.product",
        inverse_name="consultation_id",
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

    date = fields.Datetime(string="Date")
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        default=lambda self: self.env.user.company_id.currency_id.id,
    )

    def _compute_invoice_counter(self):
        for item in self:
            item.invoice_counter = len(
                item.consultation_product_ids.mapped(
                    "move_line_id"
                ).mapped("move_id")
            )

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env["animal.stage"].sudo().search(domain, order=order)

    def name_get(self):
        res = []
        for item in self:
            res.append(
                (item.id, "{} - {}".format(item.name, item.animal_id.name))
            )
        return res

    def _compute_total_products(self):
        for item in self:
            item.total_products = sum(
                product.subtotal for product in item.consultation_product_ids
            )

    def _compute_total_invoiced(self):
        for item in self:
            item.total_invoiced = sum(
                product.subtotal
                for product in item.consultation_product_ids
                if product.invoiced
            )

    def open_invoices(self):
        moves = self.consultation_product_ids.mapped(
            "move_line_id"
        ).mapped("move_id")
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["id", "in", moves.ids]],
            "name": "{} - {} Invoices".format(self.name, self.animal_id.name),
        }

    def check_animal_tutor(self):
        if self.partner_id != self.animal_id.tutor_id:
            raise UserError(
                _("The consultation partner must be the animal tutor!")
            )

    @api.model
    def create(self, vals):
        res = super(AnimalConsultation, self).create(vals)
        res.check_animal_tutor()
        return res

    def write(self, vals):
        res = super(AnimalConsultation, self).write(vals)
        for item in self:
            item.check_animal_tutor()
        return res

    def _compute_access_url(self):
        super(AnimalConsultation, self)._compute_access_url()
        for consultation in self:
            consultation.access_url = "/my/consultations/%s" % (
                consultation.id
            )


class AnimalStage(models.Model):
    _name = "animal.stage"
    _description = "Animal Stage"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
    fold = fields.Boolean(string="Fold")
    description = fields.Char(string="Description")


class AnimalConsultationProduct(models.Model):
    _name = "animal.consultation.product"
    _description = "Animal Consultation product"

    product_id = fields.Many2one(
        comodel_name="product.product", string="Product",
    )
    quantity = fields.Integer(string="Quantity", default=1)
    price_unit = fields.Float(string="Price Unit")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal")
    invoiced = fields.Boolean(
        string="Invoiced", compute="_compute_invoiced"
    )
    consultation_id = fields.Many2one(
        comodel_name="animal.consultation", string="Consultation"
    )
    move_line_id = fields.Many2one(
        comodel_name="account.move.line", string="Invoice Line"
    )

    def _compute_invoiced(self):
        for item in self:
            item.invoiced = True if item.move_line_id else False

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for item in self:
            item.price_unit = item.product_id.list_price

    @api.onchange("product_id", "price_unit", "quantity")
    def _compute_subtotal(self):
        for item in self:
            item.subtotal = item.price_unit * item.quantity

    def unlink(self):
        if any(item.invoiced for item in self):
            raise UserError(_("You can't delete a invoiced line!"))
        return super(AnimalConsultationProduct, self).unlunk()
