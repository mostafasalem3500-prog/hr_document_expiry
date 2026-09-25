# -*- coding: utf-8 -*-
from odoo import _, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    document_ids = fields.One2many(
        'hr.document', 'employee_id', string='Documents | الوثائق',
        groups='hr.group_hr_user')
    document_count = fields.Integer(
        compute='_compute_document_count', groups='hr.group_hr_user')
    document_alert_count = fields.Integer(
        compute='_compute_document_count', groups='hr.group_hr_user')

    def _compute_document_count(self):
        data = self.env['hr.document']._read_group(
            [('employee_id', 'in', self.ids)],
            ['employee_id', 'state'], ['__count'])
        totals, alerts = {}, {}
        for employee, state, count in data:
            totals[employee.id] = totals.get(employee.id, 0) + count
            if state in ('critical', 'expired'):
                alerts[employee.id] = alerts.get(employee.id, 0) + count
        for employee in self:
            employee.document_count = totals.get(employee.id, 0)
            employee.document_alert_count = alerts.get(employee.id, 0)

    def action_open_documents(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'hr_document_expiry_notifier.action_hr_document')
        action.update({
            'name': _('Documents of %s', self.name),
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
                'default_owner_type': 'employee',
                'default_company_id': self.company_id.id,
            },
        })
        return action
