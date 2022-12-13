import datetime
import mongoengine
import json
from bson.json_util import dumps


class PaymentHistoryModel(mongoengine.Document):
    payment_id = mongoengine.StringField(primary_key=True)
    date_created = mongoengine.StringField(default=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    status = mongoengine.IntField(default=1)
    product_cost = mongoengine.FloatField(default=0.0)
    shipping_cost = mongoengine.FloatField(default=0.0)
    currency = mongoengine.StringField()
    customer_details = mongoengine.DictField()
    products = mongoengine.ListField()
    total_cost = mongoengine.FloatField(default=0.0)

    def to_json(self):
        data = {
            'payment_id': self.payment_id,
            'date_created': self.date_created,
            'status': self.status,
            'product_cost': self.product_cost,
            'shipping_cost': self.shipping_cost,
            'currency': self.currency,
            'customer_details': self.customer_details,
            'products': self.products,
            'total_cost': self.total_cost
        }
        return json.loads(dumps(data))
