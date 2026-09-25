# Document & License Expiry Notifier | منبّه انتهاء الوثائق والتصاريح

Free Odoo 18 module (LGPL-3) that tracks expiry dates of employee and company documents
and e-mails reminders automatically **90, 60 and 30 days** before they expire.

- Employee documents: Iqama, Passport, Work Permit, Driving License, Health Insurance, Medical Certificate, National ID
- Company documents: Commercial Registration, GOSI, Zakat/Tax, ZATCA/VAT, Municipality License, Chamber of Commerce, Lease
- Colour-coded status (Valid · Expiring Soon · Critical · Expired) refreshed daily
- Each reminder sent once; changing the expiry date (renewal) resets them
- To-do activity for the responsible user at 30 days
- Smart button on the employee form, list / kanban / calendar / pivot / graph views
- HR-only access and multi-company rules

## Installation
1. Copy the `hr_document_expiry_notifier` folder into your addons path.
2. Update the Apps list and install **Document & License Expiry Notifier**.
3. Configure an outgoing mail server so reminders can be delivered.

Menu: **Employees › Document Expiry**. Document types: **Employees › Configuration › Document Types**.

## العربية
موديول مجاني لأودو 18 لتتبّع تواريخ انتهاء وثائق الموظفين (الإقامة، الجواز، تصريح العمل…)
ووثائق الشركة (السجل التجاري، التأمينات، الزكاة…) مع تنبيهات بريدية تلقائية ثنائية اللغة
قبل الانتهاء بـ 90 و60 و30 يوماً.

Author: Mostafa Salem · License: LGPL-3
