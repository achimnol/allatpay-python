# --*-- encoding: utf-8 --*--
#
# This example contains unfinished codes and
# uses a hypothetical "Order" model something like:
#
# class Order(models.Model):
#   order_no       = models.CharField(...)
#   buyer_id       = models.CharField(...)
#   buyer_name     = models.CharField(...)
#   recipient_name = models.CharField(...)
#   address        = models.CharField(...)
#   product_codes  = models.CommaSeparatedIntegerField(...)
#   product_names  = models.CommaSeparatedIntegerField(...)
#   payment_result = models.CharField(...)
#   def calc_amount(): ...
#
# In real shopping malls, "Product" could be a separate model and
# we could use one-to-many relationship between Order and Product.
#
# The order_no must be created before payment, and the order items
# should be managed "separately" with the payment process.
#
# You must modify this code according to your application.

from __future__ import print_function
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.template import RequestContext, Context
from django.shortcuts import render_to_response
from django.conf import settings
from django.contrib import messages
from .forms import PaymentForm, PaymentCancelForm
from .allatutil import AllAtUtil

def pay(request):

    if request.method == 'GET':

        # Show the payment form.
        # TODO: Get the order information from session or database.
        #       The following is just an example stub,
        #       so you must modify this according to your application.
        order = Order.objects.get(order_no=request.session['order_no'])

        payment_form = PaymentForm(initial={
            'allat_shop_id': settings.PAYMENT_SHOPID[order.region],
            'allat_order_no': order.order_no,
            'allat_amt': order.calc_amount(),
            'allat_pmember_id': order.buyer_id,
            'allat_product_cd': u'||'.join(order.product_codes),
            'allat_product_nm': u'||'.join(order.product_names),
            'allat_buyer_nm': order.buyer_name,
            'allat_recp_nm': order.recipient_name,
            'allat_recp_addr': order.address,
            'allat_enc_data': u'',
            # The following two fields are required for foreign payments (meaningless!).
            'allat_company_nm': u'MY SHOPPINGMALL NAME',
            'allat_company_url': u'http://example.com',
            # If this is 'Y', the PG agency will NOT perform actual payment.
            'allat_test_yn': u'Y' if settings.DEBUG else u'N',
        })

        return render_to_response('payment_form.html', {
            'payment_form': payment_form,
            'shop_id': settings.PAYMENT_SHOPID[order.region],
            'order_no': order.order_no,
            'region': order.region,
        }, context_instance=RequestContext(request))

    elif request.method == 'POST':

        try:
            # TODO: This is an example stub. You must modify this.
            order = Order.objects.get(order_no=request.POST.get('allat_order_no', None))
        except ObjectDoesNotExist:
            raise Http404()
        payment_form = PaymentForm(request.POST)

        if payment_form.is_valid():
            payment_data = payment_form.cleaned_data

            # Do the transaction with the payment agency.
            aa = AllAtUtil(region=order.region)
            payment_result = aa.query('approval', {
                'allat_amt': order.calc_amount(),  # IMPORTANT: We must recalculate this!
                'allat_enc_data': payment_data['allat_enc_data'],
            })
            payment_success = (payment_result['reply_cd'] == u'0000')

            # Check the payment result.
            # TODO: Customize here for your application.
            #       (e.g., send an email, logging, etc.)
            if payment_success:
                order.payment_result = u'success'
                currency = u'KRW' if order.region == u'DOMESTIC' else u'USD'
            else:
                order.payment_result = u'error:{0}:{1}'.format(payment_result['reply_cd'], payment_result['reply_msg'])
                messages.add_message(request, messages.ERROR, u'Payment Error: ' + payment_result['reply_msg'])
            order.save()
            return render_to_response('transaction_result.html', {
                'success': payment_success,
            }, context_instance=RequestContext(request))
        else:
            return render_to_response('payment_form.html', {
                'payment_form': payment_form,
                'shop_id': settings.PAYMENT_SHOPID[order.region],
                'order_no': order.order_no,
                'region': order.region,
            }, context_instance=RequestContext(request))

    else:
        return HttpResponseBadRequest()


def cancel(request):
    if request.method == 'GET':
        order_no = request.GET.get('order_no', None)
        if order_no:
            try:
                # TODO: This is an example stub. You must modify this.
                order = Order.objects.get(order_no=order_no)
            except ObjectDoesNotExist:
                raise Http404()
            payment_cancel_form = PaymentCancelForm(initial={
                'allat_order_no': order_no,
                'allat_amt': order.calc_amount(),
            })
        else:
            return HttpResponseBadRequest()
    elif request.method == 'POST':
        payment_cancel_form = PaymentCancelForm(request.POST)
        if payment_cancel_form.is_valid():
            data = payment_cancel_form.cleaned_data
            # TODO: do payment cancellation
            # TODO: delete registrant object
            raise NotImplementedError
            messages.add_message(request, messages.WARNING, u'Not implemented yet.')
        return render_to_response('transaction_result.html', {
            'success': True,
        })
    else:
        return HttpResponseBadRequest()

    return render_to_response('payment_cancel.html', {
        'payment_cancel_form': payment_cancel_form,
        'shop_id': settings.PAYMENT_SHOPID[order.region],
        'region': order.region,
    })
