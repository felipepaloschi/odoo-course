from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ConsultationInvoicing(models.TransientModel):
    _name = "consultation.invoicing"
    _description = "Consultation Invoicing"

    consultation_id = fields.Many2one(
        comodel_name="animal.consultation", string="Animal Consultation"
    )
    consultation_line_ids = fields.One2many(
        comodel_name="consultation.invoicing.line",
        inverse_name="consultation_invoicing_id",
        string="lines",
    )

    @api.model
    def default_get(self, fields):
        res = super(ConsultationInvoicing, self).default_get(fields)
        consultation = self.env["animal.consultation"].browse(
            self.env.context.get("active_id")
        )
        lines = consultation.consultation_product_ids.filtered(
            lambda x: not x.invoiced
        )
        if not lines:
            raise UserError(_("There are no invoiceable products!"))
        line_ids = self.env["consultation.invoicing.line"]
        for line in lines:
            line_ids += self.env["consultation.invoicing.line"].create(
                {
                    "consultation_product_id": line.id,
                    "product_id": line.product_id.id,
                    "quantity": line.quantity,
                    "price_unit": line.price_unit,
                    "subtotal": line.subtotal,
                },
            )
        res.update(
            {
                "consultation_id": consultation.id,
                "consultation_line_ids": line_ids.ids,
            }
        )
        return res

    def button_generate_invoice(self):
        lines = self.consultation_line_ids.filtered(lambda x: x.to_invoice)
        if not lines:
            raise UserError(_("Please select some lines to invoice!"))
        move = self.env["account.move"].create(
            {
                "partner_id": self.consultation_id.partner_id.id,
                "animal_id": self.consultation_id.animal_id.id,
            }
        )
        MoveLine = self.env["account.move.line"]
        for line in lines:
            account = MoveLine.get_invoice_line_account(
                "out_invoice",
                line.product_id,
                False,
                self.env.user.company_id,
            )
            move_line = MoveLine.create(
                {
                    "move_id": move.id,
                    "name": line.product_id.name,
                    "product_id": line.product_id.id,
                    "quantity": line.quantity,
                    "price_unit": line.price_unit,
                    "account_id": account.id if account else False,
                }
            )
            line.consultation_product_id.move_line_id = move_line
        view_id = self.env.ref("account.view_move_form").id
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "target": "current",
            "res_id": move.id,
            'views': [[view_id, 'form']],
        }


class ConsultationInvoicingLine(models.TransientModel):
    _name = "consultation.invoicing.line"
    _description = "Consultation Invoicing Line"

    consultation_invoicing_id = fields.Many2one(
        comodel_name="consultation.invoicing", readonly=True
    )
    consultation_product_id = fields.Many2one(
        comodel_name="animal.consultation.product", readonly=True
    )
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", readonly=True
    )
    quantity = fields.Integer(string="Quantity", readonly=True)
    price_unit = fields.Float(string="Price Unit", readonly=True)
    subtotal = fields.Float(string="Subtotal", readonly=True)
    to_invoice = fields.Boolean(string="To Invoice")
