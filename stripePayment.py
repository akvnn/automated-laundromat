from flask import Flask, request, redirect
import stripe
# This is your test secret API key.
stripe.api_key = 'sk_test_51PEyJGRwrxHql92ZopFVxaDWQqmX39GCDCiNb8VncXt8WxktfHt8rrmNJuT0l9IpG3u26kny1e834rJZcQhxUnCV00i34Dtm3Q'

domain = 'http://127.0.0.1:8080'


def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1PEyeXRwrxHql92Zog2i1XDe',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=domain + '/success',
            cancel_url=domain + '/cancel',
        )
    except Exception as e:
        print(e)
        raise e
    return checkout_session.url
