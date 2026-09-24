# -*- coding: utf-8 -*-
from odoo import models, fields


class HrDocumentType(models.Model):
    _name = 'hr.document.type'
    _description = 'Document Type | نوع الوثيقة'
    _order = 'sequence, name'

    name = fields.Char(
        string='Document Type',
        required=True,
        translate=True,
    )
    code = fields.Char(string='Code', size=20)
    sequence = fields.Integer(default=10)
    applies_to = fields.Selection([
        ('employee', 'Employee | موظف'),
        ('company', 'Company | شركة'),
        ('both', 'Both | الاثنان'),
    ], string='Applies To', default='both', required=True)
    active = fields.Boolean(default=True)
    note = fields.Text(string='Note | ملاحظة')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Document type name must be unique!'),
    ]
