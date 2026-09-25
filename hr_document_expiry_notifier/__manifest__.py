# -*- coding: utf-8 -*-
{
    'name': 'Document & License Expiry Notifier | منبّه انتهاء الوثائق',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Track Iqama, Passport, Work Permit, Insurance & Company Licenses — auto email alerts at 90/60/30 days | تتبع انتهاء الإقامات والجوازات والتراخيص مع تنبيهات تلقائية',
    'description': """
Track expiry dates of employee documents (Iqama, Passport, Work Permit, Driving License,
Health Insurance, Medical Certificate) and company documents (CR, GOSI, Zakat/VAT, ZATCA,
Municipality License, Chamber of Commerce, Lease). Automatic bilingual e-mail reminders
90, 60 and 30 days before expiry, colour-coded status, employee smart button, kanban,
calendar and reporting views.

تتبّع تواريخ انتهاء وثائق الموظفين والشركة مع تنبيهات بريدية تلقائية ثنائية اللغة
قبل الانتهاء بـ 90 و60 و30 يوماً.
""",
    'author': 'Mostafa Salem',
    'website': 'https://github.com/mostafasalem3500-prog/hr_document_expiry',
    'license': 'LGPL-3',
    'depends': ['hr', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/document_types.xml',
        'data/email_templates.xml',
        'data/cron.xml',
        'views/document_type_views.xml',
        'views/hr_document_views.xml',
        'views/hr_employee_views.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'maintainer': 'Mostafa Salem',
    'installable': True,
    'application': False,
    'auto_install': False,
}
