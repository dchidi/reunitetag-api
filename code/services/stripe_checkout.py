import os
import mongoengine as db
import stripe
import math
import uuid
from .db_connection import DB_URI
from dotenv import load_dotenv, find_dotenv
from flask import session
from code.models.PaymentHistory import PaymentHistoryModel
from code.models.Fulfillment import FulfillmentModel

# find and load possible environment variable file
load_dotenv(find_dotenv())
stripe.api_key = os.getenv('STRIP_SECRETE_KEY')


class StripeCheckoutService:
    def __init__(self, data):
        db.connect(host=DB_URI)
        self.data = data
        self.shipping_cost = 15 * 100  # 15 euro
        self.currency = 'eur'
        self.countries = [
            # 'AC', 'AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AR',
            # 'AT', 'AU', 'AW', 'AX', 'AZ', 'BA', 'BB', 'BD', 'BE', 'BF', 'BG',
            # 'BH', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BO', 'BQ',
            # 'BR',
            # 'BS',
            # 'BT',
            # 'BV', 'BW', 'BY', 'BZ',
            'CA',
            # 'CD', 'CF', 'CG', 'CH', 'CI', 'CK',
            # 'CL', 'CM', 'CN', 'CO', 'CR', 'CV', 'CW', 'CY', 'CZ', 'DE', 'DJ',
            # 'DK', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'EH', 'ER', 'ES', 'ET',
            # 'FI', 'FJ', 'FK', 'FO', 'FR', 'GA',
            'GB',
            # 'GD', 'GE', 'GF', 'GG',
            # 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR', 'GS', 'GT', 'GU',
            # 'GW', 'GY', 'HK', 'HN', 'HR', 'HT', 'HU', 'ID',
            'IE',
            # IL, IM,
            # IN, IO, IQ, IS, IT, JE, JM, JO, JP, KE, KG,
            # KH, KI, KM, KN, KR, KW, KY, KZ, LA, LB, LC,
            # LI, LK, LR, LS, LT, LU, LV, LY, MA, MC, MD,
            # ME, MF, MG, MK, ML, MM, MN, MO, MQ, MR, MS,
            # MT, MU, MV, MW, MX, MY, MZ, NA, NC, NE,
            'NG',
            # NI, NL, NO, NP, NR, NU, NZ, OM, PA, PE, PF,
            # PG, PH, PK, PL, PM, PN, PR, PS, PT, PY, QA,
            # RE, RO, RS, RU, RW, SA, SB, SC, SE, SG, SH,
            # SI, SJ, SK, SL, SM, SN, SO, SR, SS, ST, SV,
            # SX, SZ, TA, TC, TD, TF, TG, TH, TJ, TK, TL,
            # TM, TN, TO, TR, TT, TV, TW, TZ, UA, UG,
            'US',
            # UY, UZ, VA, VC, VE, VG, VN, VU, WF, WS, XK,
            # YE, YT, ZA, ZM, ZW, ZZ
        ]
        self.delivery_date = {'min': 3, 'max': 5}
        self.urls = {
            'success': 'http://127.0.0.1:5000/checkout_response/{CHECKOUT_SESSION_ID}',
            'cancel': 'http://localhost:3000/cancel_payment'
        }

    def checkout(self):
        _data = []
        has_shipping_option = 0
        for item in self.data:
            _data.append({
                'price_data': {
                    'currency': self.currency,
                    'product_data': {
                        'name': item['title'],
                        # 'images': [item['image']],
                    },
                    # stripe only accepts integers for unit amount. Also it requires it in the lowest form of the
                    # currency. E.g euro will be in cents. 100 cents makes 1 euro reason for multiplying the total by
                    # 100
                    'unit_amount': math.ceil(float(item['amount'])) * 100,
                },
                'quantity': int(item['qty']),
            })
            has_shipping_option += int(item['has_shipping'])

        _shipping_option = [{
            'shipping_rate_data': {
                'type': 'fixed_amount',
                'fixed_amount': {
                    'amount': 0,
                    'currency': 'eur',
                },
                'display_name': 'No shipping',
            }
        }]
        if has_shipping_option > 0:
            _shipping_option.append({
                'shipping_rate_data': {
                    'type': 'fixed_amount',
                    'fixed_amount': {
                        'amount': self.shipping_cost,
                        'currency': self.currency,
                    },
                    'display_name': 'We deliver within',
                    'delivery_estimate': {
                        'minimum': {
                            'unit': 'business_day',
                            'value': self.delivery_date['min'],
                        },
                        'maximum': {
                            'unit': 'business_day',
                            'value': self.delivery_date['max'],
                        },
                    }
                }
            })
        try:
            stripe_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                shipping_address_collection={
                    'allowed_countries': self.countries,
                },
                shipping_options=_shipping_option,
                line_items=_data,
                mode='payment',
                success_url=self.urls['success'],
                cancel_url=self.urls['cancel'],
            )
            return {'url': stripe_session.url, 'status': 303}
        except Exception as e:
            print(e)
            return {'msg': 'Stripe API checkout endpoint not reachable', 'status': 500}

    @staticmethod
    def checkout_response(id):
        products = []

        try:
            _data = stripe.checkout.Session.retrieve(id)
            for line_item in stripe.checkout.Session.list_line_items(id):
                products.append({'id': line_item['id'], 'amount_total': float(line_item['amount_total']) / 100,
                                 'currency': line_item['currency'], 'description': line_item['description'],
                                 'quantity': line_item['quantity']})
            if _data['payment_status'] == 'paid':
                _shipping_cost = 0
                # if shipping cost is greater than 0, update fulfillment
                if _data['shipping_cost']['amount_total'] > 0:
                    _shipping_cost = float(_data['shipping_cost']['amount_total']) / 100
                    StripeCheckoutService.update_fulfillment(
                        {'shipping_cost': _shipping_cost, 'currency': _data['currency'],
                         'shipping_details': _data['shipping_details'],
                         'products': products})

                _payment_data = {'product_cost': float(_data['amount_subtotal']) / 100, 'shipping_cost': _shipping_cost,
                                 'total_cost': float(_data['amount_total']) / 100, 'currency': _data['currency'],
                                 'customer_details': _data['customer_details'], 'products': products}
                return StripeCheckoutService.update_payment_history(_payment_data)
        except Exception as e:
            print(e)
            return {'msg': 'Stripe API checkout endpoint not reachable', 'status': 500}

    @staticmethod
    def update_payment_history(data):
        payment_model = PaymentHistoryModel()
        payment_model.payment_id = uuid.uuid4().hex
        payment_model.product_cost = data['product_cost']
        payment_model.shipping_cost = data['shipping_cost']
        payment_model.total_cost = data['total_cost']
        payment_model.currency = data['currency']
        payment_model.customer_details = data['customer_details']
        payment_model.products = data['products']
        try:
            payment_model.save(force_insert=True)
            return {'msg': 'Transaction saved successfully', 'status': 201}
        except Exception as e:
            print(e)
            return {'msg': 'Payment operation failed', 'status': 500}

    @staticmethod
    def update_fulfillment(data):
        fulfillment_model = FulfillmentModel()
        fulfillment_model.fulfillment_id = uuid.uuid4().hex
        fulfillment_model.shipping_cost = data['shipping_cost']
        fulfillment_model.currency = data['currency']
        fulfillment_model.shipping_details = data['shipping_details']
        fulfillment_model.products = data['products']
        try:
            fulfillment_model.save(force_insert=True)
            return {'msg': 'Transaction saved successfully', 'status': 201}
        except Exception as e:
            return {'msg': 'Fulfillment operation failed', 'status': 500}
