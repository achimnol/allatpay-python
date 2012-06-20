# --*-- encoding: utf8 --*--
import socket, ssl
import urllib, urlparse
from datetime import datetime
# You may have to replace the following line
# if you want to use this module in non-Django projects.
from django.conf import settings

class InvalidEncryptionDataError(Exception):
    pass

class AllAtUtil:
    util_lang = "JSP"  # This version is based on the JSP library.
    util_ver  = "1.0.7.1"

    allat_host = "tx.allatpay.com"

    uri_map = {
        "KRW": {
            "approval"          : "/servlet/AllatPay/pay/approval.jsp",
            "sanction"          : "/servlet/AllatPay/pay/sanction.jsp",
            "cancel"            : "/servlet/AllatPay/pay/cancel.jsp",
            "cashreg"           : "/servlet/AllatPay/pay/cash_registry.jsp",
            "cashapp"           : "/servlet/AllatPay/pay/cash_approval.jsp",
            "cashcan"           : "/servlet/AllatPay/pay/cash_cancel.jsp",
            "escrowchk"         : "/servlet/AllatPay/pay/escrow_check.jsp",
            "escrowret"         : "/servlet/AllatPay/pay/escrow_return.jsp",
            "escrowconfirm"     : "/servlet/AllatPay/pay/escrow_confirm.jsp",
            "certreg"           : "/servlet/AllatPay/pay/fix.jsp",
            "certcancel"        : "/servlet/AllatPay/pay/fix_cancel.jsp",

            "c2c_approval"      : "/servlet/AllatPay/pay/c2c_approval.jsp",
            "c2c_cancel"        : "/servlet/AllatPay/pay/c2c_cancel.jsp",
            "c2c_sellerreg"     : "/servlet/AllatPay/pay/seller_registry.jsp",
            "c2c_productreg"    : "/servlet/AllatPay/pay/product_registry.jsp",
            "c2c_buyerchg"      : "/servlet/AllatPay/pay/buyer_change.jsp",
            "c2c_escrowchk"     : "/servlet/AllatPay/pay/c2c_escrow_check.jsp",
            "c2c_escrowconfirm" : "/servlet/AllatPay/pay/c2c_escrow_confirm.jsp",
        },
        "USD": {
            "approval"          : "/servlet/AllatPay/pay/approval_dol.jsp",
            "sanction"          : "/servlet/AllatPay/pay/sanction.jsp",
            "cancel"            : "/servlet/AllatPay/pay/cancel_dol.jsp",
        },
    }

    def __init__(self, region='domestic'):
        assert region in ('domestic', 'abroad', 'DOMESTIC', 'ABROAD')
        self.cross_key = settings.PAYMENT_CROSSKEY[region.upper()]
        self.shop_id = settings.PAYMENT_SHOPID[region.upper()]
        self.currency = 'KRW' if region.upper() == 'DOMESTIC' else 'USD'

    def query(self, name, params, use_ssl=True):
        result = None
        try:
            try:
                if not use_ssl:
                    assert 'allat_enc_data' in params
                    assert params['allat_enc_data'][5:6] == "1"
            except AssertionError:
                raise InvalidEncryptionDataError()
            raw_result = self._send_req(self.uri_map[self.currency][name], params, 443 if use_ssl else 80)

            # Parse the result.
            # For better error reporting, we need to parse the HTTP response headers...
            # The original library seems to just ignore them.
            tuples = raw_result.split('\r\n\r\n')[1].split('\n')
            result = {}
            for t in tuples:
                if len(t.strip()) > 0:
                    key, value = t.split('=', 1)
                    result[key.strip()] = value.strip().decode('cp949')
        except InvalidEncryptionDataError:
            result = {
                'reply_cd': u'0230',
                'reply_msg': u'Encryption error',
            }
        except socket.error as e:
            result = {
                'reply_cd': u'0212',
                'reply_msg': u'Socket Connect Error: ' + e.message,
            }
        except Exception as e:
            # This is not a good practice: we need to assume this library has NO bugs at all.
            rseult = {
                'reply_cd': u'0221',
                'reply_msg': u'Exception: ' + e.message,
            }
        return result

    def _send_req(self, call_url, params, port, method='POST'):

        assert(isinstance(call_url, basestring))
        assert(isinstance(params, dict))
        assert(isinstance(port, int))
        assert(method in ('GET', 'POST'))

        # Additional common parameters.
        params['allat_apply_ymdhms'] = datetime.now().strftime('%Y%m%d%H%M%S')
        params['allat_opt_lang'] = self.util_lang
        params['allat_opt_ver'] = self.util_ver
        params['allat_shop_id'] = self.shop_id
        params['allat_cross_key'] = self.cross_key

        # Encode and construct the sending message.
        raw_body = urllib.urlencode(params)
        req_len = len(raw_body)

        raw_send_data =  '{0} {1} HTTP/1.0\r\n'.format(method, call_url)
        raw_send_data += 'Host: {0}:{1}\r\n'.format(self.allat_host, port)
        raw_send_data += 'Content-Type: application/x-www-form-urlencoded\r\n'
        raw_send_data += 'Content-Length: {0}\r\n'.format(req_len)
        raw_send_data += 'Accept: */*\r\n\r\n'  # end of header
        raw_send_data += raw_body + '\r\n\r\n'  # end of message

        # Connect to th server.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if port == 443:
            wrapped_sock = ssl.wrap_socket(sock, ca_certs=settings.CA_CERTS_PATH, cert_reqs=ssl.CERT_REQUIRED)
        else:
            wrapped_sock = sock
        wrapped_sock.connect((self.allat_host, port))
        wrapped_sock.write(raw_send_data)

        raw_read_data = []
        while True:
            data = wrapped_sock.recv(4096)
            if not data: break
            raw_read_data.append(data)
        raw_read_data = ''.join(raw_read_data)
        wrapped_sock.close()

        return raw_read_data

    @staticmethod
    def encode_data(params):
        # Maybe used to encode multiple key-value tuples into a single field?
        data_list = []
        for key, value in params.iteritems():
            data_list.append('{0}{1}'.format(key, str(value)))
        return '00000010' + ''.join(data_list)

