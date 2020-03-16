from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AttendanceInvoicing(models.TransientModel):
    _name = "attendance.invoicing"
    _description = "Attendance Invoicing"

    attendance_id = fields.Many2one(
        comodel_name="animal.attendance", string="Animal Attendance"
    )
    attendance_line_ids = fields.One2many(
        comodel_name="attendance.invoicing.line",
        inverse_name="attendance_invoicing_id",
        string="lines",
    )

    @api.model
    def default_get(self, fields):
        res = super(AttendanceInvoicing, self).default_get(fields)
        attendance = self.env["animal.attendance"].browse(
            self.env.context.get("active_id")
        )
        lines = attendance.attendance_product_ids.filtered(
            lambda x: not x.invoiced
        )
        if not lines:
            raise UserError(_("There are no invoiceable products!"))
        res.update(
            {"attendance_id": attendance.id, "attendance_line_ids": []}
        )
        for line in lines:
            res["attendance_line_ids"].append(
                (
                    0,
                    0,
                    {
                        "attedance_product_id": line.id,
                        "product_id": line.product_id.id,
                        "quantity": line.quantity,
                        "price_unit": line.price_unit,
                        "subtotal": line.subtotal,
                    },
                )
            )
        return res

    def button_generate_invoice(self):
        lines = self.attendance_line_ids.filtered(lambda x: x.invoice)
        if not lines:
            raise UserError(_("Please select some lines to invoice!"))
        res = self.env["account.invoice"].create(
            {
                "partner_id": self.attendance_id.partner_id.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": line.product_id.name,
                            "product_id": line.product_id.id,
                            "quantity": line.quantity,
                            "price_unit": line.price_unit,
                        },
                    )
                    for line in lines
                ],
            }
        )
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.invoice",
            "type": "ir.actions.act_window",
            "target": "current",
            "res_id": res.id,
        }


class AttendanceInvoicingLine(models.TransientModel):
    _name = "attendance.invoicing.line"
    _description = "Attendance Invoicing Line"

    attendance_invoicing_id = fields.Many2one(
        comodel_name="attendance.invoicing", readonly=True
    )
    attendance_product_id = fields.Many2one(
        comodel_name="animal.attendance.product", readonly=True
    )
    product_id = fields.Many2one(
        comodel_name="product.template", string="Product", readonly=True
    )
    quantity = fields.Integer(string="Quantity", readonly=True)
    price_unit = fields.Float(string="Price Unit", readonly=True)
    subtotal = fields.Float(string="Subtotal", readonly=True)
    invoice = fields.Boolean(string="To Invoice")
