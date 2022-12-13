import datetime
import mongoengine
from bson.json_util import dumps


class MessageLogModel(mongoengine.Document):
    message_id = mongoengine.StringField(primary_key=True)
    date_created = mongoengine.StringField(default=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    sender = mongoengine.StringField(required=True)
    recipients = mongoengine.ListField()
    message = mongoengine.StringField(required=True)
    language_sent = mongoengine.StringField()
    language_received = mongoengine.StringField()

    def to_json(self):
        data = {
            'message_id': self.message_id,
            'date_created': self.date_created,
            'sender': self.sender,
            'recipients': self.recipients,
            'message': self.message,
            'language_sent': self.language_sent,
            'language_received': self.language_received,
        }
        return json.loads(dumps(data))
