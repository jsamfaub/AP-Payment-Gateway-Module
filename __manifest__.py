# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'AP Payment Provider',
    'version': '2.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'summary': "A payment provider for custom flows like wire transfers.",
    'depends': ['payment','sale','account','account_payment','website_sale'],
    'data': [
        'views/payment_custom_templates.xml',
        'views/payment_provider_views.xml',

        'data/payment_provider_data.xml',
        'data/payment_process_pages_templates.xml',
        'data/invoice_customization.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ap_payment_provider/static/src/js/post_processing.js',
        ],
    },
    'application': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
