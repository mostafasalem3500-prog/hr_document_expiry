# -*- coding: utf-8 -*-
import logging
from datetime import date, timedelta

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class HrDocument(models.Model):
    _name = 'hr.document'
    _description = 'Document & License Expiry | منبّه انتهاء الوثائق'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'expiry_date asc, state asc'
    _rec_name = 'name'

    # ── Core fields ────────────────────────────────────────────────────────
    name = fields.Char(
        string='Document Number / Reference',
        required=True,
        tracking=True,
    )
    document_type_id = fields.Many2one(
        'hr.document.type',
        string='Document Type',
        required=True,
        tracking=True,
        ondelete='restrict',
    )

    # ── Who owns the document ──────────────────────────────────────────────
    entity_type = fields.Selection([
        ('employee', 'Employee | موظف'),
        ('company', 'Company / Partner | شركة'),
    ], string='Belongs To', default='employee', required=True, tracking=True)

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        tracking=True,
        ondelete='cascade',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Company / Person',
        tracking=True,
        ondelete='cascade',
    )

    # ── Dates ──────────────────────────────────────────────────────────────
    issue_date = fields.Date(string='Issue Date', tracking=True)
    expiry_date = fields.Date(string='Expiry Date', required=True, tracking=True)

    # ── Computed status ────────────────────────────────────────────────────
    days_remaining = fields.Integer(
        string='Days Remaining',
        compute='_compute_days_remaining',
        store=True,
    )
    state = fields.Selection([
        ('valid', 'Valid | سارية'),
        ('warning', 'Warning ≤90d | تحذير'),
        ('critical', 'Critical ≤30d | حرج'),
        ('expired', 'Expired | منتهية'),
    ], string='Status', compute='_compute_state', store=True, tracking=True)

    # ── Notification tracking ──────────────────────────────────────────────
    notify_90_sent = fields.Boolean(string='90-day Alert Sent', default=False, copy=False)
    notify_60_sent = fields.Boolean(string='60-day Alert Sent', default=False, copy=False)
    notify_30_sent = fields.Boolean(string='30-day Alert Sent', default=False, copy=False)

    # ── Extra info ─────────────────────────────────────────────────────────
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
    )
    notes = fields.Text(string='Notes | ملاحظات')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True, tracking=True)

    # ══════════════════════════════════════════════════════════════════════
    # Compute methods
    # ══════════════════════════════════════════════════════════════════════

    @api.depends('expiry_date')
    def _compute_days_remaining(self):
        today = date.today()
        for rec in self:
            if rec.expiry_date:
                rec.days_remaining = (rec.expiry_date - today).days
            else:
                rec.days_remaining = 0

    @api.depends('days_remaining')
    def _compute_state(self):
        for rec in self:
            d = rec.days_remaining
            if d < 0:
                rec.state = 'expired'
            elif d <= 30:
                rec.state = 'critical'
            elif d <= 90:
                rec.state = 'warning'
            else:
                rec.state = 'valid'

    # ══════════════════════════════════════════════════════════════════════
    # ORM overrides
    # ══════════════════════════════════════════════════════════════════════

    def write(self, vals):
        # Reset notification flags whenever expiry date is updated (renewal)
        if 'expiry_date' in vals:
            vals.setdefault('notify_90_sent', False)
            vals.setdefault('notify_60_sent', False)
            vals.setdefault('notify_30_sent', False)
        return super().write(vals)

    # ══════════════════════════════════════════════════════════════════════
    # Actions
    # ══════════════════════════════════════════════════════════════════════

    def action_mark_renewed(self):
        """Reset notification flags after manual renewal."""
        self.write({
            'notify_90_sent': False,
            'notify_60_sent': False,
            'notify_30_sent': False,
        })
        return True

    def action_send_notification_now(self):
        """Manually send the 30-day notification email immediately."""
        template = self.env.ref(
            'hr_document_expiry.email_template_expiry_30', raise_if_not_found=False
        )
        if not template:
            return False
        for rec in self:
            template.send_mail(rec.id, force_send=True)
        return True

    # ══════════════════════════════════════════════════════════════════════
    # Scheduled action (Cron)
    # ══════════════════════════════════════════════════════════════════════

    @api.model
    def _cron_check_expiry(self):
        """
        Run daily. Sends email notifications when a document is within
        90 / 60 / 30 days of expiry (once per threshold per document).
        """
        today = date.today()

        thresholds = [
            (90, 'notify_90_sent', 'hr_document_expiry.email_template_expiry_90'),
            (60, 'notify_60_sent', 'hr_document_expiry.email_template_expiry_60'),
            (30, 'notify_30_sent', 'hr_document_expiry.email_template_expiry_30'),
        ]

        for days, flag, template_xml_id in thresholds:
            cutoff = today + timedelta(days=days)
            # Documents where expiry ≤ threshold AND notification not yet sent
            docs = self.search([
                (flag, '=', False),
                ('expiry_date', '>=', today),
                ('expiry_date', '<=', cutoff),
                ('active', '=', True),
            ])
            if not docs:
                continue

            template = self.env.ref(template_xml_id, raise_if_not_found=False)
            if not template:
                _logger.warning('hr_document_expiry: template %s not found', template_xml_id)
                continue

            for doc in docs:
                try:
                    template.send_mail(doc.id, force_send=False)
                    doc.write({flag: True})
                except Exception as exc:  # noqa: BLE001
                    _logger.error(
                        'hr_document_expiry: failed to notify doc id=%s name=%s: %s',
                        doc.id, doc.name, exc,
                    )

        _logger.info('hr_document_expiry: daily expiry check done (%s)', today)
