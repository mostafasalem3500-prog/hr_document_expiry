# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# Notification thresholds (days before expiry), highest first.
NOTIFY_THRESHOLDS = (90, 60, 30)
WARNING_DAYS = 90
CRITICAL_DAYS = 30


class HrDocument(models.Model):
    _name = 'hr.document'
    _description = 'Employee / Company Document | وثيقة'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'expiry_date asc, id desc'
    _rec_name = 'display_label'

    name = fields.Char(
        string='Document Number | رقم الوثيقة',
        required=True,
        tracking=True,
    )
    display_label = fields.Char(compute='_compute_display_label', store=True)
    document_type_id = fields.Many2one(
        'hr.document.type',
        string='Document Type | نوع الوثيقة',
        required=True,
        tracking=True,
        ondelete='restrict',
    )
    owner_type = fields.Selection([
        ('employee', 'Employee | موظف'),
        ('company', 'Company | شركة'),
    ], string='Belongs To | تابعة لـ', required=True, default='employee', tracking=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee | الموظف',
        tracking=True,
        index=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Related Partner | الجهة',
        help='Optional partner (e.g. landlord, authority) linked to this document.',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company | الشركة',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsible | المسؤول',
        default=lambda self: self.env.user,
        tracking=True,
        help='User who receives the expiry notifications.',
    )
    issuing_authority = fields.Char(string='Issuing Authority | جهة الإصدار')
    issue_date = fields.Date(string='Issue Date | تاريخ الإصدار', tracking=True)
    expiry_date = fields.Date(
        string='Expiry Date | تاريخ الانتهاء',
        required=True,
        tracking=True,
        index=True,
    )
    days_remaining = fields.Integer(
        string='Days Remaining | الأيام المتبقية',
        compute='_compute_days_remaining',
        search='_search_days_remaining',
    )
    state = fields.Selection([
        ('valid', 'Valid | سارية'),
        ('warning', 'Expiring Soon | تنتهي قريباً'),
        ('critical', 'Critical | حرجة'),
        ('expired', 'Expired | منتهية'),
    ], string='Status | الحالة', compute='_compute_state', store=True,
        tracking=True, index=True, group_expand='_expand_states')
    color = fields.Integer(compute='_compute_color')
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'hr_document_attachment_rel',
        'document_id',
        'attachment_id',
        string='Attachments | المرفقات',
    )
    note = fields.Html(string='Notes | ملاحظات')
    active = fields.Boolean(default=True, tracking=True)

    notified_90 = fields.Boolean(string='90-day notice sent', copy=False)
    notified_60 = fields.Boolean(string='60-day notice sent', copy=False)
    notified_30 = fields.Boolean(string='30-day notice sent', copy=False)

    _sql_constraints = [
        ('doc_uniq', 'UNIQUE(document_type_id, name, company_id)',
         'This document number already exists for this document type!'),
    ]

    # ------------------------------------------------------------------
    # Computes
    # ------------------------------------------------------------------
    @api.depends('document_type_id.name', 'name', 'employee_id.name')
    def _compute_display_label(self):
        for doc in self:
            parts = [doc.document_type_id.name or '', doc.name or '']
            if doc.employee_id:
                parts.append(doc.employee_id.name)
            doc.display_label = ' — '.join(p for p in parts if p)

    @api.depends('expiry_date')
    def _compute_days_remaining(self):
        today = fields.Date.context_today(self)
        for doc in self:
            doc.days_remaining = (doc.expiry_date - today).days if doc.expiry_date else 0

    def _search_days_remaining(self, operator, value):
        if operator not in ('<', '<=', '>', '>=', '=', '!='):
            raise ValidationError(_('Unsupported search operator on days remaining.'))
        target = fields.Date.context_today(self) + timedelta(days=int(value))
        return [('expiry_date', operator, target)]

    @api.model
    def _state_for_date(self, expiry_date):
        if not expiry_date:
            return 'valid'
        days = (expiry_date - fields.Date.context_today(self)).days
        if days < 0:
            return 'expired'
        if days <= CRITICAL_DAYS:
            return 'critical'
        if days <= WARNING_DAYS:
            return 'warning'
        return 'valid'

    @api.depends('expiry_date')
    def _compute_state(self):
        for doc in self:
            doc.state = self._state_for_date(doc.expiry_date)

    @api.model
    def _expand_states(self, states, domain):
        # Kanban columns ordered by urgency.
        return ['expired', 'critical', 'warning', 'valid']

    @api.depends('state')
    def _compute_color(self):
        colors = {'valid': 10, 'warning': 3, 'critical': 1, 'expired': 0}
        for doc in self:
            doc.color = colors.get(doc.state, 0)

    # ------------------------------------------------------------------
    # Constraints / onchanges
    # ------------------------------------------------------------------
    @api.constrains('issue_date', 'expiry_date')
    def _check_dates(self):
        for doc in self:
            if doc.issue_date and doc.expiry_date and doc.issue_date > doc.expiry_date:
                raise ValidationError(_('The expiry date must be after the issue date.'))

    @api.constrains('owner_type', 'employee_id')
    def _check_owner(self):
        for doc in self:
            if doc.owner_type == 'employee' and not doc.employee_id:
                raise ValidationError(_('Please select the employee this document belongs to.'))

    @api.onchange('document_type_id')
    def _onchange_document_type_id(self):
        applies = self.document_type_id.applies_to
        if applies in ('employee', 'company'):
            self.owner_type = applies

    @api.onchange('owner_type')
    def _onchange_owner_type(self):
        if self.owner_type == 'company':
            self.employee_id = False

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id and self.employee_id.company_id:
            self.company_id = self.employee_id.company_id

    # ------------------------------------------------------------------
    # ORM
    # ------------------------------------------------------------------
    def write(self, vals):
        if 'expiry_date' in vals:
            # A new expiry date means a renewal: notifications start over.
            vals.update(notified_90=False, notified_60=False, notified_30=False)
        return super().write(vals)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_renew(self):
        """Open the form so the user can enter the new expiry date."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Renew Document | تجديد الوثيقة'),
            'res_model': 'hr.document',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {'renewing': True},
        }

    def action_send_reminder(self):
        """Send the reminder matching the current remaining days right now."""
        for doc in self:
            threshold = doc._matching_threshold() or CRITICAL_DAYS
            doc._send_expiry_notice(threshold)
        return True

    def _matching_threshold(self):
        self.ensure_one()
        days = self.days_remaining
        for threshold in sorted(NOTIFY_THRESHOLDS):
            if days <= threshold:
                return threshold
        return False

    def _send_expiry_notice(self, threshold):
        self.ensure_one()
        template = self.env.ref(
            'hr_document_expiry.email_template_expiry_%s' % threshold,
            raise_if_not_found=False,
        )
        if template:
            template.send_mail(self.id, force_send=False)
        self.message_post(
            body=_('Expiry reminder (%(threshold)s days) sent — %(days)s days remaining.',
                   threshold=threshold, days=self.days_remaining),
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        if threshold == CRITICAL_DAYS and self.responsible_id:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                date_deadline=self.expiry_date,
                summary=_('Renew %s', self.display_label),
                user_id=self.responsible_id.id,
            )

    # ------------------------------------------------------------------
    # Cron
    # ------------------------------------------------------------------
    @api.model
    def _cron_check_expiry(self):
        docs = self.search([('expiry_date', '!=', False)])
        # 1) Refresh stored status, since it moves with the calendar.
        self.env.add_to_compute(self._fields['state'], docs)
        docs.flush_recordset(['state'])

        # 2) Send the notification for the tightest threshold reached, once.
        today = fields.Date.context_today(self)
        upcoming = docs.filtered(lambda d: d.expiry_date >= today)
        for doc in upcoming:
            threshold = doc._matching_threshold()
            if not threshold or doc['notified_%s' % threshold]:
                continue
            try:
                doc._send_expiry_notice(threshold)
            except Exception:  # keep processing the other documents
                _logger.exception('Could not send expiry notice for document %s', doc.id)
                continue
            # Mark this threshold and every wider one as done.
            doc.write({'notified_%s' % t: True for t in NOTIFY_THRESHOLDS if t >= threshold})
        return True
