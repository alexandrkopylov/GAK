{
    'name': 'ActiveGIS Google maps',
    'category': 'Uncategorized',
    'summary': '',
    'version': '1.0',
    'description': """
Module ActiveGIS Google maps.
========================================
This module allows you to display on the Google maps information on the location of pillars, air power lines, and other objects
information for which information is availeble in Activ.GIS system

        """,
    'depends': ['passportvl','base_geolocalize'],
    'data': [
        'views/web.xml',
        'views/layers_views.xml',
        'views/mod_apl_view.xml',
        'views/v2/carto_template.xml'
    ],
    'installable': True,
    'auto_install': False,
    'author': "Active.GIS Inc",
    'application' :True,
    'website': "http://www.uisgis.ru",
}
