from odoo import models, fields, api
import stripe, qrcode, io, base64, json
from decimal import Decimal
from urllib.parse import quote

class CustomInvoiceDocument(models.AbstractModel):
    _inherit = 'report.account.report_invoice_with_payments'

    @api.model
    def _get_report_values(self, docids, data=None):
        stripe.api_key=self.get_stripe_api_key()
        report_values = super(CustomInvoiceDocument, self)._get_report_values(docids, data=data)
        if not docids:
            return report_values
        docid=docids[0]
        invoice=self.env['account.move'].browse(docid)
        base64_encoded_qrcode=self.generate_base64_encoded_qrcode_from_invoice(invoice)
        new_context = self.env.context.copy()
        new_context.update({
            "ap_base64_encoded_qrcode": base64_encoded_qrcode['qrcode'],
            "ap_payment_link": base64_encoded_qrcode['payment_link'],
        })
        report_values['context'] = new_context
        
        return report_values

    def generate_base64_encoded_qrcode_from_invoice(self,invoice):
        payment_link=self.get_payment_link_from_invoice(invoice)
        if not payment_link:
            price=invoice.amount_total
            unit_price=int(round(price*100,2))
            invoice_number=invoice.name
            product_identifier=invoice_number+"{}".format(unit_price) #We do this so that when the invoice is changed (and thus the price), a new product will used instead of keeping the old one
            currency_id=invoice.currency_id
            currency=self.get_lowercase_currency_from_currency(currency_id)
            line_items=self.get_stripe_line_items_from_invoice(invoice)
            payment_link_object=stripe.PaymentLink.create(
                line_items=line_items,
                metadata={'invoice_number':"Payment for invoice {}".format(invoice.name)}
            )
            if payment_link_object :
                payment_link=payment_link_object['url']
                self.set_payment_link_on_invoice(payment_link, invoice)
            else:
                return ""
        base64_encoded_qrcode={}
        base64_encoded_qrcode['qrcode']=self.get_base64_encoded_qrcode_from_payment_link(payment_link)
        base64_encoded_qrcode['payment_link']=payment_link
        if base64_encoded_qrcode:
            return base64_encoded_qrcode
        return ""

    def get_payment_link_from_invoice(self,invoice):
        if not invoice.ap_payment_link_information:
            return False
        payment_link_info_string=invoice.ap_payment_link_information
        if not payment_link_info_string:
            return False
        payment_link_info=json.loads(payment_link_info_string)
        total_amount=invoice.amount_total
        if payment_link_info['total_amount'] != total_amount:
            return False
        return payment_link_info['payment_link']
    def set_payment_link_on_invoice(self,payment_link,invoice):
        total_amount=invoice.amount_total
        payment_link_info={'total_amount':total_amount, 'payment_link':payment_link}
        payment_link_info_string=json.dumps(payment_link_info)
        invoice.ap_payment_link_information=payment_link_info_string
    def get_base64_encoded_qrcode_from_payment_link(self,url):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
    
        qr_image = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        qr_image.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return qr_base64

    def get_stripe_line_items_from_invoice(self, invoice):
        subtotal=invoice.amount_total
        currency=self.get_lowercase_currency_from_currency(invoice.currency_id)
        invoice_origin=invoice.invoice_origin
        if invoice_origin:
            price_name="Payment for invoice {} of order {}".format(invoice.name, invoice_origin)
        else:
            price_name="Payment for invoice {}".format(invoice.name)
        price_object=self.get_price_object(int(round(subtotal*100,2)), currency, price_name)
        price_id=price_object['id']
        stripe_line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ]

        return stripe_line_items

    def get_lines_from_invoice_id(self,invoice_id):
        lines=self.env['account.move.line'].search([('move_id', '=', invoice_id)])
        return lines

    def get_product_object(self,name):
        url=quote(name)
        listed_products=stripe.Product.list(url=url, limit=1, active=True)
        if listed_products:
            product_object=listed_products['data'][0]
        else:
            product_object=stripe.Product.create(name=name,url=url)
        return product_object
    
    def get_price_object(self, unit_price, currency, product_name):
        product_object=self.get_product_object(product_name)
        product_id=product_object.id
        listed_prices=stripe.Price.list(unit_amount=unit_price, currency=currency, product=product_id, limit=1, active=True)
        if listed_prices:
            return listed_prices['data'][0]
        price_object=stripe.Price.create(
            unit_amount=unit_price,
            currency=currency,
            recurring=None,
            product=product_id,
        )
        return price_object

    def get_stripe_api_key(self):
        return "" #TODO add stripe key 

    def get_lowercase_currency_from_currency(self, currency):
        return currency.name.lower()




# "ReportInvoiceWithPayment" could be used if we only want the qrcode for invoice with payment
