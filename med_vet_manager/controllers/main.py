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
        consultation_count = request.env["animal.consultation"].search_count(
            []
        )
        values.update(
            {
                "animal_count": animal_count,
                "consultation_count": consultation_count,
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

    # CONSULTATIONS

    @http.route("/my/consultations", type="http", auth="user", website=True)
    def consultations_list(self, sortby=None, **kw):
        values = self._prepare_portal_layout_values()

        searchbar_sortings = {
            "name": {"label": _("Name"), "order": "name"},
            "date": {"label": _("Date"), "order": "date desc"},
            "stage": {"label": _("Stage"), "order": "stage_id"},
        }

        if not sortby:
            sortby = "date"
        sort_order = searchbar_sortings[sortby]["order"]

        consultations = request.env["animal.consultation"].search(
            [], order=sort_order
        )

        values.update(
            {
                "consultations": consultations,
                "page_name": "my_consultations",
                "default_url": "/my/consultations",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("med_vet_manager.consultations_list", values)

    def _consultation_get_page_view_values(
        self, consultation, access_token, **kwargs
    ):
        values = {
            "page_name": "consultation",
            "consultation": consultation,
        }
        return self._get_page_view_values(
            consultation,
            access_token,
            values,
            "my_consultations_history",
            False,
            **kwargs
        )

    @http.route(
        ["/my/consultations/<int:consultation_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_consultation(
        self, consultation_id=None, access_token=None, **kw
    ):
        try:
            consultation_sudo = self._document_check_access(
                "animal.consultation", consultation_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        values = self._consultation_get_page_view_values(
            consultation_sudo, access_token, **kw
        )
        return request.render(
            "med_vet_manager.portal_my_consultation", values
        )
