# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHrDocumentExpiry(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.email = 'hr@example.com'
        cls.today = fields.Date.today()
        cls.employee = cls.env['hr.employee'].create({'name': 'Test Employee'})
        cls.doc_type = cls.env.ref('hr_document_expiry.doc_type_iqama')

    def _doc(self, days, number):
        return self.env['hr.document'].create({
            'name': number,
            'document_type_id': self.doc_type.id,
            'employee_id': self.employee.id,
            'expiry_date': self.today + timedelta(days=days),
            'responsible_id': self.env.user.id,
        })

    def test_states(self):
        self.assertEqual(self._doc(200, 'A').state, 'valid')
        self.assertEqual(self._doc(80, 'B').state, 'warning')
        self.assertEqual(self._doc(10, 'C').state, 'critical')
        self.assertEqual(self._doc(-1, 'D').state, 'expired')

    def test_reminders_sent_once_and_reset_on_renewal(self):
        doc = self._doc(25, 'E')
        self.env['hr.document']._cron_check_expiry()
        self.assertTrue(doc.notified_30 and doc.notified_60 and doc.notified_90)
        self.assertTrue(doc.activity_ids)
        mails = self.env['mail.mail'].search_count([('model', '=', 'hr.document'), ('res_id', '=', doc.id)])
        self.env['hr.document']._cron_check_expiry()
        self.assertEqual(
            self.env['mail.mail'].search_count([('model', '=', 'hr.document'), ('res_id', '=', doc.id)]),
            mails, 'A reminder must not be sent twice')
        doc.expiry_date = self.today + timedelta(days=400)
        self.assertFalse(doc.notified_30)
        self.assertEqual(doc.state, 'valid')

    def test_employee_counts(self):
        self._doc(10, 'F')
        self._doc(300, 'G')
        self.assertEqual(self.employee.document_count, 2)
        self.assertEqual(self.employee.document_alert_count, 1)
