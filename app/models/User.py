import datetime
import mongoengine
import json
from bson.json_util import dumps


class UserModel(mongoengine.Document):
    user_id = mongoengine.StringField(primary_key=True)
    date_created = mongoengine.StringField(default=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    last_modified = mongoengine.StringField()
    status = mongoengine.IntField(default=1)
    tag = mongoengine.StringField()
    phones = mongoengine.ListField()
    language = mongoengine.StringField()
    languageCode = mongoengine.StringField()
    available_units = mongoengine.IntField(default=15)

    def to_json(self):
        data = {
            'user_id': self.user_id,
            'date_created': self.date_created,
            'last_modified': self.last_modified,
            'status': self.status,
            'tag': self.tag,
            'phone': self.phones,
            'language': self.language,
            'languageCode': self.languageCode,
            'available_units': self.available_units,
        }
        return json.loads(dumps(data))
