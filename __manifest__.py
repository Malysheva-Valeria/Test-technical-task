{
    'name': 'Hospital Management',
    'version': '1.0.0',
    'category': 'Healthcare',
    'summary': 'Manage hospital doctors, patients, diseases and visits',
    'description': """
        Hospital Management System
        This module allows you to manage:
         Doctors
         Patients
         Disease types
         Patient visits
    """,
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/disease_data.xml',
        'views/doctor_views.xml',
        'views/patient_views.xml',
        'views/disease_views.xml',
        'views/visit_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/doctor_demo.xml',
        'demo/patient_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
