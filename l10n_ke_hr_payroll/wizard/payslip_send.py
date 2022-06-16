# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PayslipSend(models.TransientModel):
    _name = 'payslip.send'
    _description = 'Payslip Send'

    is_email = fields.Boolean('Email')
    is_print = fields.Boolean('Print')
    payslip_ids = fields.Many2many('hr.payslip', 'hr_payslip_payslip_send_rel', string='Payslips')
    template_id = fields.Many2one(
        'mail.template', 'Use template', index=True,
        domain="[('model', '=', 'hr.payslip')]"
        )

    @api.model
    def default_get(self, fields):
        res = super(PayslipSend, self).default_get(fields)
        res_ids = self._context.get('active_ids')

        res.update({
            'payslip_ids': res_ids,
        })
        return res

    def _send_email(self):
        attechment_obj = self.env["ir.attachment"]
        template = self.template_id
        done_payslips = self.payslip_ids.filtered(
            lambda payslip: payslip.state == 'done')
        # other payslips
        payslips = self.payslip_ids.filtered(
            lambda payslip: payslip.state != 'done')
        if self.is_email:
            if payslips:
                raise UserError(_("Only done payslips will be proceed"))
            for payslip in done_payslips:
                attachment = attechment_obj.search([
                    ('res_id', '=', payslip.id),
                    ('res_model', '=', 'hr.payslip')], limit=1)
                subject = _("Payslip of period %s to %s") % (
                    payslip.date_from, payslip.date_to)
                if template:
                    template.send_mail(payslip.id, email_values={
                        'email_from': self.env.user.email or '',
                        'email_to': payslip.employee_id.address_home_id.email,
                        'subject': subject,
                        'attachment_ids': [(4, attachment.id)]}, force_send=True)

    def _print_document(self):
        self.ensure_one()
        action = self.payslip_ids.action_print_payslip()
        action.update({'close_on_report_download': True})
        return action

    def send_and_print_action(self):
        self.ensure_one()
        if self.is_email:
            self._send_email()
        if self.is_print:
            return self._print_document()
        return {'type': 'ir.actions.act_window_close'}

