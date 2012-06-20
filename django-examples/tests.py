from django.test import TestCase
from . import allatutil

class PaymentTest(TestCase):

    def test_ssl_connection(self):
        """
        Tests if the SSL connection to the payment server is available.
        """

        aa = allatutil.AllAtUtil()
        raw_result = aa._send_req('/ssltest/test_ok.jsp', {}, 443, method='GET')

        # This may be changed!
        self.assertTrue('https://tx.allatpay.com/ssltest/ssl_test.jpg' in raw_result)

