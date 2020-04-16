from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class VetPortalController(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(
            VetPortalController, self
        )._prepare_portal_layout_values()
        website = request.env["website"].search([], limit=1)
        values.update({"website": website})
        return values

    @http.route("/animals", type="http", auth="user")
    def route_animals(self):
        values = self._prepare_portal_layout_values()
        return request.render("med_vet_manager.animals_list", values)
