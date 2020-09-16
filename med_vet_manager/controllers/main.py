from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError


class VetPortalController(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(
            VetPortalController, self
        )._prepare_portal_layout_values()
        animal_count = request.env["res.animal"].search_count([])
        appointment_count = request.env["animal.appointment"].search_count(
            []
        )
        values.update(
            {
                "animal_count": animal_count,
                "appointment_count": appointment_count,
            },
        )
        return values

    @http.route("/my/animals", type="http", auth="user", website=True)
    def animals_list(self, sortby=None, **kw):
        values = self._prepare_portal_layout_values()

        searchbar_sortings = {
            "name": {"label": _("Name"), "order": "name"},
            "age": {"label": _("Age"), "order": "birthday desc"},
        }

        if not sortby:
            sortby = "name"
        sort_order = searchbar_sortings[sortby]["order"]

        animals = request.env["res.animal"].search([], order=sort_order)

        values.update(
            {
                "animals": animals,
                "page_name": "my_animals",
                "default_url": "/my/animals",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("med_vet_manager.animals_list", values)

    def _animal_get_page_view_values(self, animal, access_token, **kwargs):
        values = {
            "page_name": "animal",
            "animal": animal,
        }
        return self._get_page_view_values(
            animal,
            access_token,
            values,
            "my_animals_history",
            False,
            **kwargs
        )

    @http.route(
        ["/my/animals/<int:animal_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_animal(self, animal_id=None, access_token=None, **kw):
        try:
            animal_sudo = self._document_check_access(
                "res.animal", animal_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        values = self._animal_get_page_view_values(
            animal_sudo, access_token, **kw
        )
        return request.render("med_vet_manager.portal_my_animal", values)

    # APPOINTMENTS

    @http.route("/my/appointments", type="http", auth="user", website=True)
    def appointments_list(self, sortby=None, **kw):
        values = self._prepare_portal_layout_values()

        searchbar_sortings = {
            "name": {"label": _("Name"), "order": "name"},
            "date": {"label": _("Date"), "order": "date desc"},
            "stage": {"label": _("Stage"), "order": "stage_id"},
        }

        if not sortby:
            sortby = "date"
        sort_order = searchbar_sortings[sortby]["order"]

        appointments = request.env["animal.appointment"].search(
            [], order=sort_order
        )

        values.update(
            {
                "appointments": appointments,
                "page_name": "my_appointments",
                "default_url": "/my/appointments",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("med_vet_manager.appointments_list", values)

    def _appointment_get_page_view_values(
        self, appointment, access_token, **kwargs
    ):
        values = {
            "page_name": "appointment",
            "appointment": appointment,
        }
        return self._get_page_view_values(
            appointment,
            access_token,
            values,
            "my_appointments_history",
            False,
            **kwargs
        )

    @http.route(
        ["/my/appointments/<int:appointment_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_appointment(
        self, appointment_id=None, access_token=None, **kw
    ):
        try:
            appointment_sudo = self._document_check_access(
                "animal.appointment", appointment_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        values = self._appointment_get_page_view_values(
            appointment_sudo, access_token, **kw
        )
        return request.render(
            "med_vet_manager.portal_my_appointment", values
        )
