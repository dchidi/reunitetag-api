import datetime
import mongoengine
import json
from bson.json_util import dumps


#  To avoid randomly generated numbers by malicious users to be registered, tag validation methode should check status
#  when uploading TagID. Status will be controlled only internally. If has_hard_copy is true, status should be 1.
#  This will reduce exposure to only printed tags
# TODO:: Keep a log of printed tags for easy resolution if compromised
# status {0 - Not purchased, 1 - Purchased, 2 - Registered}
class TagModel(mongoengine.Document):
    tag_id = mongoengine.StringField(primary_key=True)
    date_created = mongoengine.StringField(default=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    last_modified = mongoengine.StringField()
    status = mongoengine.IntField(default=0)
    tag = mongoengine.StringField(unique=True)
    has_hard_copy = mongoengine.BooleanField(default=False)
    phone_number = mongoengine.StringField()

    def to_json(self):
        data = {
            'tag_id': self.tag_id,
            'date_created': self.date_created,
            'last_modified': self.last_modified,
            'status': self.status,
            'tag': self.tag,
            'phone_number': self.phone_number,
            'has_hard_copy': self.has_hard_copy,
        }
        return json.loads(dumps(data))
