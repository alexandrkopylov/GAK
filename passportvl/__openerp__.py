# -*- coding: utf-8 -*-
{
    'name': "Паспорт ВЛ",

    'summary': """Паспортизация технологического оборудования объектов электрических сетей. Паспорт """,

    'description': """
        Модуль управления и учета основных технологических составляющих оборудования объектов электрических сетей
    """,

    'author': "ГИС.Актив",
    'application' :True,
    'website': "http://www.uisgis.ru",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','resource'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/forms/uis_papl_tap.xml',
        'views/forms/uis_papl_apl.xml',
        'views/forms/uis_papl_disconnector.xml',
        'views/department.xml',
        'views/templates.xml',
        'views/transformation.xml',
        'views/employee_views.xml',
        'views/settings.xml',
        'views/logger.xml',
        'views/reports/uis_papl_apl_report.xml',
        'views/reports/uis_papl_apl_report_passport.xml',
        'views/schemas/apl_scheme.xml',
        

    ],
    #css
    'css':['static/src/css/passportvl.css'],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
