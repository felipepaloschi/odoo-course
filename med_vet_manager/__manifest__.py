{  # pylint: disable=C8101,C8103
    "name": "Gerenciador de Clinica Veterinária",
    "summary": """Adapta o Odoo para ser um sistema que permite
    o gerenciamento de uma clinica veterinária.""",
    "description": """Adapta o Odoo para ser um sistema que permite
    o gerenciamento de uma clinica veterinária.""",
    "version": "12.0.0.0.1",
    "category": "Sales",
    "author": "Felipe Paloschi",
    "contributors": ["Felipe Paloschi <paloschi.eca@gmail.com>"],
    "depends": ["mail", "sale", "portal"],
    "data": [
        "wizard/attendance_invoicing.xml",
        "views/animal.xml",
        "views/animal_species.xml",
        "views/animal_breed.xml",
        "views/animal_class.xml",
        "views/animal_attendance.xml",
        "views/account_invoice.xml",
        "templates/main.xml",
        "reports/attendance_report.xml",
        "data/data.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": True,
}
