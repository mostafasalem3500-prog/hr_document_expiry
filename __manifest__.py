# -*- coding: utf-8 -*-
{
    'name': 'Document & License Expiry Notifier | منبّه انتهاء الوثائق',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Track Iqama, Passport, Work Permit, Insurance & Company Licenses — auto email alerts at 90/60/30 days | تتبع انتهاء الإقامات والجوازات والتراخيص مع تنبيهات تلقائية',
    'description': """
Document & License Expiry Notifier | منبّه انتهاء الوثائق والتصاريح
======================================================================

**English**
Track and manage expiry dates for all important employee and company documents.
Never face surprise expirations again!

Employee Documents:
- Iqama (Residence Permit)
- Passport
- Work Permit
- Driving License
- Health Insurance
- Medical Certificate

Company Documents:
- Commercial Registration (CR)
- GOSI Certificate
- ZATCA / VAT Certificate
- Municipality License
- Chamber of Commerce Certificate
- Lease / Rental Contract

Features:
✅ Automatic daily email notifications at 90, 60, and 30 days before expiry
✅ Color-coded status list: Green (Valid) | Yellow (Warning) | Red (Critical) | Grey (Expired)
✅ Smart button on Employee form showing document count
✅ Kanban view grouped by status
✅ Chatter/history for every document change
✅ Full Arabic RTL support (واجهة عربية كاملة)
✅ Multi-company support
✅ Archive/renew documents with automatic notification reset

**العربي**
تتبع تواريخ انتهاء جميع الوثائق الرسمية للموظفين والشركات، مع تنبيهات بريد إلكتروني تلقائية.

الوثائق المدعومة:
• إقامة • جواز سفر • تصريح عمل • رخصة قيادة • تأمين صحي
• سجل تجاري • شهادة GOSI • شهادة الزكاة • رخصة بلدية • عقد إيجار

الميزات:
✅ تنبيهات بريد إلكتروني تلقائية قبل 90 و 60 و 30 يوم من الانتهاء
✅ قائمة ملونة: أخضر (سارية) | أصفر (تحذير) | أحمر (حرج) | رمادي (منتهية)
✅ زر ذكي على بطاقة الموظف يعرض عدد وثائقه
✅ دعم متعدد الشركات
✅ تاريخ التغييرات والمراسلات (Chatter)
    """,
    'author': 'Mostafa Salem',
    'website': 'https://apps.odoo.com/apps/modules/browse?search=mostafa+salem',
    'license': 'LGPL-3',
    'depends': ['hr', 'mail'],
    'data': [
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
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 0,
    'currency': 'USD',
}
