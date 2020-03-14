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
    "depends": ["mail", "sale"],
    "data": [
        "views/animal.xml",
        "views/animal_species.xml",
        "views/animal_breed.xml",
        "views/animal_class.xml",
        "views/animal_attendance.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": True,
}
