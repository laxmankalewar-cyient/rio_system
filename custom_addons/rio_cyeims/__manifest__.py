{
    'name': 'RIO CYEIMS',
    'version': '1.1',
    'category': 'Cyient',
    'sequence': -100,
    'summary': 'RIO Products',
    'description': "",
    'depends': [
        'hr',
        'base',
        'web', 'dms', 'board'
    ],
    'data': [
        'security/rio_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',

        'views/product_liner_taxonomy_views.xml',
        'views/product_liner_files_views.xml',
        'views/rio_asset_dashboard_views.xml',
        'views/rio_site_dashboard_views.xml',
        'views/flocs_register_views.xml',
        'views/unspsc_code_view.xml',
        'views/taxonomy_bom_structure_views.xml',
        'views/text_generation_config_views.xml',
        # 'views/rio_board_views.xml',
        'wizards/wizard_bom_status_views.xml',

        'views/rio_menu.xml',

        'views/tcode_views/iw38_sample_customized_view.xml',
        'views/tcode_views/mb51_sample_customized_view.xml',
        'views/tcode_views/mb52_sample_customized_view.xml',
        'views/tcode_views/me2m_sample_customized_view.xml',
        'views/tcode_views/mm60_sample_customized_view.xml',
        'views/tcode_views/spare_finder_sample_customized_view.xml',
        'views/tcode_views/z4190_sample_customized_view.xml',
        'views/tcode_views/z4191_sample_customized_view.xml',
        'views/tcode_views/z5001_sample_customized_view.xml',
        'views/tcode_views/z7116_sample_customized_view.xml',
        'views/tcode_views/z7131_sample_customized_view.xml',
        'views/tcode_views/z7134_sample_customized_view.xml',
        'views/tcode_views/ih0_bom_data_view.xml',
        'views/tcode_views/ih06_flocs_data_view.xml',

        'views/tcode_views/tcode_menu.xml',
    ],
    'assets': {

        'web.assets_backend': [
            'rio_cyeims/static/src/css/dashboard.css',
            'rio_cyeims/static/src/js/rio_dashboard.js',
            'rio_cyeims/static/src/js/lib/Chart.bundle.js',
            'rio_cyeims/static/src/css/ktsdms.css',
            'rio_cyeims/static/src/js/rio_board.js',
            'rio_cyeims/static/src/js/url_widget.js'
        ],
'web.assets_qweb': [
            'rio_cyeims/static/src/xml/rio_dashboard.xml',
        ],
         },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
