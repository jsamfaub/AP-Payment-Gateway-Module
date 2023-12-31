# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.tools import is_html_empty


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'
    name = fields.Char(string='Name', default="AP Payment Provider")

    _sql_constraints = [(
        'custom_providers_setup',
        "CHECK(custom_mode IS NULL OR (code = 'custom' AND custom_mode IS NOT NULL))",
        "Only custom providers should have a custom mode."
    )]

    code = fields.Selection(
        selection_add=[('custom', "Custom")], ondelete={'custom': 'set default'}
    )
    custom_mode = fields.Selection(
        string="Custom Mode",
        selection=[('ap_payment_provider', "AP Payment Provider selection name")],
        required_if_provider='custom',
    )
    qr_code = fields.Boolean(
        string="Enable QR Codes", help="Enable the use of QR-codes when paying by wire transfer.")

    @api.depends('code')
    def _compute_view_configuration_fields(self):
        """ Override of payment to hide the credentials page.

        :return: None
        """
        super()._compute_view_configuration_fields()
        self.filtered(lambda p: p.code == 'custom').update({
            'show_credentials_page': False,
            'show_payment_icon_ids': False,
            'show_pre_msg': False,
            'show_done_msg': False,
            'show_cancel_msg': False,
        })

    def _transfer_ensure_pending_msg_is_set(self):
        transfer_providers_without_msg = self.filtered(
            lambda p: p.code == 'custom'
            and p.custom_mode == 'ap_payment_provider'
            and is_html_empty(p.pending_msg)
        )

        if not transfer_providers_without_msg:
            return  # Don't bother translating the messages.

        account_payment_module = self.env['ir.module.module']._get('account_payment')
        if account_payment_module.state != 'installed':
            transfer_providers_without_msg.pending_msg = f'<div>' \
                f'<h3>{_("Thank you for ordering from Alexander Press!")}</h3>' \
                f'<h4>{_("An email containing further information about the payment should be sent to you.")}</h4>' \
                f'<h4>{_("Communication")}</h4>' \
                f'<p>{_("Please use the order name as communication reference if you contact us about the order at alexanderpress@gmail.com")}</p>' \
                f'</div>'
            return

        for provider in transfer_providers_without_msg:
            company_id = provider.company_id.id
            accounts = self.env['account.journal'].search([
                ('type', '=', 'bank'), ('company_id', '=', company_id)
            ]).bank_account_id
            provider.pending_msg = f'<div>' \
                f'<h3>{_("Thank you for ordering from Alexander Press!")}</h3>' \
                f'<h4>{_("An email containing further information about the payment should be sent to you.")}</h4>' \
                f'<h4>{_("Communication")}</h4>' \
                f'<p>{_("Please use the order name as communication reference if you contact us about the order at alexanderpress@gmail.com")}</p>' \
                f'</div>'

    def _get_removal_values(self):
        """ Override of `payment` to nullify the `custom_mode` field. """
        res = super()._get_removal_values()
        res['custom_mode'] = None
        return res
