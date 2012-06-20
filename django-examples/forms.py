# --*-- encoding: utf-8 --*--

from django import forms


class PaymentForm(forms.Form):
    
    # NOTE: cross_key must be handled at the server-side only.

    allat_shop_id = forms.SlugField(max_length=20, widget=forms.HiddenInput())      # Initialized as settings.PAYMENT_SHOPID.
    allat_order_no = forms.CharField(max_length=70, label=u'Order ID',              # Automatically generated per order.
                                     widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    allat_amt = forms.IntegerField(label=u'Amount', min_value=0,                    # NOTE: must be validated at the server-side
                                   widget=forms.HiddenInput())
    allat_pmember_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'readonly': 'readonly'}), label=u'User ID')
    allat_product_cd = forms.CharField(max_length=1000, widget=forms.HiddenInput()) # Should be initialized from order information.
    allat_product_nm = forms.CharField(max_length=1000, widget=forms.HiddenInput()) # Should be initialized from order information.
    allat_buyer_nm = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    allat_recp_nm = forms.CharField(max_length=20, widget=forms.HiddenInput())      # Should be initialized from order information.
    allat_recp_addr = forms.CharField(max_length=120, widget=forms.HiddenInput())   # Should be initialized from order information.

    allat_enc_data = forms.CharField(max_length=8192, widget=forms.HiddenInput())   # Automatically set by the frontend plugin.
                                                                                    # Unfortunately, the official documentation
                                                                                    # does not specify the max length of this field.
                                                                                    # 8 KB seems to be enough, but tests are required
                                                                                    # when people buys multiple products.

    allat_company_nm = forms.CharField(max_length=20, widget=forms.HiddenInput())   # Uses internal value.
    allat_company_url = forms.CharField(max_length=50, widget=forms.HiddenInput())  # Uses internal value.
    allat_test_yn = forms.CharField(max_length=1, widget=forms.HiddenInput())       # Depending on DEBUG mode.


class PaymentCancelForm(forms.Form):
    allat_shop_id = forms.SlugField(max_length=20, widget=forms.HiddenInput())
    allat_order_no = forms.CharField(max_length=70, label=u'Order ID', widget=forms.TextInput(attrs={'readonly':'readonly'}))
    # TODO: display amount?
    allat_amt = forms.CharField(max_length=10, widget=forms.HiddenInput())
    allat_pay_type = forms.CharField(max_length=6, widget=forms.HiddenInput(), initial=u'CARD')  # This example is for credit cards only.

    allat_enc_data = forms.CharField(max_length=8192, widget=forms.HiddenInput())
    allat_opt_pin = forms.CharField(max_length=100, widget=forms.HiddenInput(), initial=u'NOVIEW')
    allat_opt_mod = forms.CharField(max_length=100, widget=forms.HiddenInput(), initial=u'WEB')

