
{
    'name': 'CYEIMS Theme',
    'version': '15.0.1',
    'author': 'CYEIMS',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'sequence': 2,
    'summary': """
   CYEIMS Branding
    """,
    'depends': [
        'base_setup',
        'web',
        'mail',
        'iap',
    ],
    'data': [
        'views/app_odoo_customize_views.xml',
        'views/res_config_settings_views.xml',
        'data/ir_config_parameter_data.xml',
        'data/res_company_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
