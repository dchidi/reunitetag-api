import datetime
import mongoengine
import json
from bson.json_util import dumps


class FulfillmentModel(mongoengine.Document):
    fulfillment_id = mongoengine.StringField(primary_key=True)
    date_created = mongoengine.StringField(default=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    status = mongoengine.IntField(default=1)
    shipping_cost = mongoengine.FloatField(default=0.0)
    currency = mongoengine.StringField()
    shipping_details = mongoengine.DictField()
    products = mongoengine.ListField()

    def to_json(self):
        data = {
            'fulfillment_id': self.fulfillment_id,
            'date_created': self.date_created,
            'status': self.status,
            'shipping_cost': self.shipping_cost,
            'currency': self.currency,
            'shipping_details': self.shipping_details,
            'products': self.products,
        }
        return json.loads(dumps(data))
