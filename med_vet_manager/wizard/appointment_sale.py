from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AppointmentSale(models.TransientModel):
    _name = "appointment.sale"
    _description = "Appointment Sale"

    appointment_id = fields.Many2one(
        comodel_name="animal.appointment", string="Animal Appointment"
    )
    appointment_line_ids = fields.One2many(
        comodel_name="appointment.sale.line",
        inverse_name="appointment_sale_id",
        string="lines",
    )

    @api.model
    def default_get(self, fields):
        res = super(AppointmentSale, self).default_get(fields)
        appointment = self.env["animal.appointment"].browse(
            self.env.context.get("active_id")
        )
        lines = appointment.appointment_product_ids.filtered(
            lambda x: not x.invoiced
        )
        if not lines:
            raise UserError(_("There are no invoiceable products!"))
        line_ids = self.env["appointment.sale.line"]
        for line in lines:
            line_ids += self.env["appointment.sale.line"].create(
                {
                    "appointment_product_id": line.id,
                    "product_id": line.product_id.id,
                    "quantity": line.quantity,
                    "price_unit": line.price_unit,
                    "subtotal": line.subtotal,
                },
            )
        res.update(
            {
                "appointment_id": appointment.id,
                "appointment_line_ids": line_ids.ids,
            }
        )
        return res

    def _prepare_sale_vals(self):
        return {
            "partner_id": self.appointment_id.partner_id.id,
            "animal_id": self.appointment_id.animal_id.id,
            "user_id": self.appointment_id.user_id.id,
        }

    def _prepare_sale_line_vals(self, line, order):
        return {
            "order_id": order.id,
            "name": line.product_id.name,
            "product_id": line.product_id.id,
            "quantity": line.quantity,
            "price_unit": line.price_unit,
        }

    def button_generate_sale(self):
        lines = self.appointment_line_ids.filtered(lambda x: x.to_invoice)
        if not lines:
            raise UserError(_("Please select some lines to invoice!"))
        order_vals = self._prepare_sale_vals()
        order = self.env['sale.order'].create(order_vals)
        for line in lines:
            vals = self._prepare_sale_line_vals(line, order)
            sale_line = self.env["sale.order.line"].create(vals)
            line.appointment_product_id.order_line_id = sale_line
        view_id = self.env.ref("account.view_move_form").id
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
            "target": "current",
            "res_id": order.id,
            "views": [[view_id, "form"]],
        }


class AppointmentSaleLine(models.TransientModel):
    _name = "appointment.sale.line"
    _description = "Appointment Sale Line"

    appointment_sale_id = fields.Many2one(
        comodel_name="appointment.sale", readonly=True
    )
    appointment_product_id = fields.Many2one(
        comodel_name="animal.appointment.product", readonly=True
    )
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", readonly=True
    )
    quantity = fields.Integer(string="Quantity", readonly=True)
    price_unit = fields.Float(string="Price Unit", readonly=True)
    subtotal = fields.Float(string="Subtotal", readonly=True)
    to_invoice = fields.Boolean(string="To Invoice")
