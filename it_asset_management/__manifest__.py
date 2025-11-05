{
    'name': 'IT Asset Management',
    'version': '17.0.1.0.0',
    'category': 'Services/Asset',
    'summary': 'Управління IT-активами компанії',
    'description': """
        IT Asset Management Module
        ===========================
        Модуль для управління IT-активами компанії з наступними можливостями:

        * Облік IT-активів (комп'ютери, сервери, мобільні пристрої, ліцензії)
        * Відстеження життєвого циклу активів
        * Прив'язка активів до співробітників
        * Система заявок від співробітників
        * Портал для співробітників
        * Звітність та аналітика
    """,
    'author': 'Malysheva Valeria',
    'depends': [
        'base',
        'portal',
        'mail',
        'web',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/sequence.xml',

        # Views
        'views/it_asset_category_views.xml',
        'views/it_asset_views.xml',
        'views/it_asset_request_views.xml',
        'views/it_asset_movement_views.xml',
        'views/portal_templates.xml',
        'views/it_asset_reports.xml',
        'views/menus.xml',

        # Demo Data
        'data/demo_data.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}