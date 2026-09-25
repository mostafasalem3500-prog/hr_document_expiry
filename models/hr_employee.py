# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    document_ids = fields.One2many(
        'hr.document', 'employee_id', string='Documents'
    )
    doc_total_count = fields.Integer(
        string='Total Documents',
        compute='_compute_doc_counts',
    )
    doc_alert_count = fields.Integer(
        string='Documents Needing Attention',
        compute='_compute_doc_counts',
    )

    @api.depends('document_ids', 'document_ids.state')
    def _compute_doc_counts(self):
        for emp in self:
            docs = emp.document_ids.filtered(lambda d: d.active)
            emp.doc_total_count = len(docs)
            emp.doc_alert_count = len(
                docs.filtered(lambda d: d.state in ('critical', 'expired', 'warning'))
            )

    def action_view_employee_documents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents | الوثائق',
            'res_model': 'hr.document',
            'view_mode': 'list,kanban,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
                'default_entity_type': 'employee',
            },
        }
