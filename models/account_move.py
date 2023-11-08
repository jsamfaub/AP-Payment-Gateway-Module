from odoo import models, fields

class AccountMove(models.Model):
        _inherit = "account.move"

        ap_payment_link_information = fields.Char(string='AP Payment Link Information',default="")
