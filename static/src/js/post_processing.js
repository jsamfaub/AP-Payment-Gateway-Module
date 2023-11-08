odoo.define('ap_payment_provider.post_processing', require => {
    'use strict';

    const paymentPostProcessing = require('payment.post_processing');
    var core = require('web.core')
    var _t = core._t;

    paymentPostProcessing.include({
        /**
         * Don't wait for the transaction to be confirmed before redirecting customers to the
         * landing route because custom transactions remain in the state 'pending' forever.
         *
         * @override method from `payment.post_processing`
         * @param {Object} display_values_list - The post-processing values of the transactions
         */
        processPolledData: function (display_values_list) {
            // In almost every case, there will be a single transaction to display. If there are
            // more than one transaction, the last one will most likely be the one that counts. We
            // use that one to redirect the user to the landing page.
            if (display_values_list.length > 0 && display_values_list[0].provider_code === 'custom') {
                window.location = display_values_list[0].landing_route;
            } else {
                return this._super(...arguments);
            }
        },
        displayLoading: function () {
            var msg = _t("We are processing your order, please wait ...");
            $.blockUI({
                'message': '<h2 class="text-white"><img src="/web/static/img/spin.png" class="fa-pulse"/>' +
                    '    <br />' + msg +
                    '</h2>'
            });
        },
    });
});
