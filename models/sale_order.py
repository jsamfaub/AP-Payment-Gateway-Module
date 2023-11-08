from odoo import models, fields


class CustomSaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_confirmation_template(self):
        """ Get the mail template sent on SO confirmation (or for confirmed SO's).

        :return: `mail.template` record or None if default template wasn't found
        """
        return self.env.ref('sale.mail_template_sale_confirmation', raise_if_not_found=False)

    def _notify_get_recipients_groups(self, msg_vals=None):
        groups=super(CustomSaleOrder, self)._notify_get_recipients_groups(msg_vals)
        for group in groups:
            group[2]['has_button_access']=False
        #super(CustomSaleOrder, self)._get_confirmation_template(msg_vals)

        return groups
