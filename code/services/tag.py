import mongoengine as db
import uuid
import random
from datetime import datetime
from .db_connection import DB_URI
from .send_message import send_message
from models.Tag import TagModel
from models.MessageLog import MessageLogModel
from models.User import UserModel


class TagService:
    def __init__(self, data):
        db.connect(host=DB_URI)
        if 'total_tags' in data:
            self.total_tags = data['total_tags']

    @staticmethod
    def generate_tag(tag_length=8):
        min = pow(10, tag_length - 1)
        max = pow(10, tag_length) - 1
        return random.randint(min, max)

    def set_of_tags(self):
        tags = set()
        for _ in range(0, self.total_tags):
            tags.add(TagService.generate_tag())
        return tags

    # TODO:: Check if tag exist in database before loading
    def load(self):
        tag_model = TagModel()
        for _tag in self.set_of_tags():
            tag_model.tag_id = uuid.uuid4().hex
            tag_model.last_modified = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            tag_model.tag = 'AA{}'.format(_tag)
            try:
                tag_model.save(force_insert=True)
            except Exception as e:
                return {'status': 500, 'msg': "Internal server error. Server is unresponsive"}
        return {'status': 201, 'msg': 'Tags upload completed'}

    @staticmethod
    def update(phone, tag):
        try:
            _status = TagModel.objects(tag=tag, status=0).update(
                set__last_modified=datetime.now().strftime('%d-%m-%Y %H:'),
                set__status=1,
                set__phone_number=phone
            )
            if _status == 1:
                return {'status': 204}
        except Exception as e:
            return {'status': 500, 'msg': str(e)}
        return {'status': 400}

    @staticmethod
    def assign_tag_to_phone_number(phone):
        try:
            tag_details = TagModel.objects.filter(status=0, has_hard_copy=False)[0].to_json()
            _update_status = TagService.update(phone['phone'], tag_details['tag'])
            if _update_status['status'] == 204:
                tag_details['phone_number'] = phone['phone']
                tag_details['status'] = 1
                send_message(_to=[phone['phone']],
                             _msg="Your ReuniteTag ID is {}".format(tag_details['tag']))
                return {'status': 200, 'msg': tag_details}
            else:
                # send email to admin when status code is 501
                return {'status': 501, 'msg': 'Assign phone number to tag process failed',
                        'error': _update_status['msg'], 'data': {'phone': phone['phone']}}
        except Exception as e:
            return {'status': 501, 'msg': 'No available tags. Contact Admin', 'data': {'phone': phone['phone']}}

    @staticmethod
    def top_up(tag='', units=10):
        try:
            _status = UserModel.objects(tag=tag).update_one(
                upsert=True,
                set__last_modified=datetime.now().strftime('%d-%m-%Y %H:'),
                inc__available_units=units,
            )
            if _status == 1:
                return {'status': 204, 'msg': 'User Tag units updated'}
        except Exception as e:
            return {'status': 500, 'msg': str(e)}
        return {'status': 400, 'msg': 'Invalid input parameters'}

    @staticmethod
    def verify_tag(tag):
        tag_details = UserModel.objects.filter(tag=tag)
        if tag_details:
            # checking status == 1 because only paid tagIDs should be registered. All has_hard_copy tags are assumed
            # to be paid for.
            if tag_details[0].status == 1:
                return {'status': 200, 'msg': 'Tag verification successful', 'tag_details': tag_details[0].to_json()}
            else:
                return {'status': 400, 'msg': 'Tag number has been assigned to a user'}
        return {'status': 400, 'msg': 'Invalid tag number'}
