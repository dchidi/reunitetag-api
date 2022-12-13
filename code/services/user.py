import mongoengine as db
import uuid
from datetime import datetime
# import from current directory uses .
from .db_connection import DB_URI
from .send_message import send_message
# import from any other directory outside the current directory should have the directory name
from code.models.User import UserModel
from code.models.Tag import TagModel
from code.models.MessageLog import MessageLogModel
# Google translate
from googletrans import Translator


# This class interacts with the database to perform CRUD operations for profile document.
class UserService:
    def __init__(self, data):
        # connect to mongodb atlas
        db.connect(host=DB_URI)
        # Sample Data values
        # {'phones': [{'phone_number': '+8768439034', 'countryCode': 'JM'}], 'tag': 'q77', 'languageCode': 'zh-TW',
        #  'language': 'Chinese Traditional'}
        self.phones = data['phones']
        self.tag = data['tag'].upper()
        self.languageCode = data['languageCode']
        self.language = data['language']
        # Default units given to users upon registration of a tag number
        self.available_units = 15

    def validate_input(self):
        if len(self.phones) > 0 and self.tag and self.languageCode:
            return True
        return False

    def language_converter(self, msg, _src='en', _dest='en'):
        translator = Translator()
        translation = translator.translate(msg, src=_src, dest=_dest)
        return translation.text

    # This method is used both on userModel and tagModel to verify tags
    def verify_tag(self, model):
        # Check if Tag exist and if it has not been used
        tag_details = model.objects.filter(tag=self.tag)
        if tag_details:
            # checking status == 1 because only paid tagIDs should be registered. All has_hard_copy tags are assumed
            # to be paid for.
            if tag_details[0].status == 1:
                return {'status': 200, 'msg': 'Tag verification successful', 'tag_details': tag_details[0].to_json()}
            else:
                return {'status': 400, 'msg': 'Tag number has been assigned to a user'}
        return {'status': 400, 'msg': 'Invalid tag number'}

    def save(self):
        user = UserModel()
        # Validate input
        if self.validate_input():
            _verification = self.verify_tag(TagModel)
            if _verification['status'] == 200:
                # Save data
                user.user_id = uuid.uuid4().hex
                user.last_modified = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                user.tag = self.tag
                user.phones = self.phones
                user.languageCode = self.languageCode
                user.language = self.language

                try:
                    # Save user details
                    user.save(force_insert=True)
                    # Update tag
                    tag_status = self.update()
                    if tag_status['status'] == 204:
                        # Send registration SMS
                        send_message(_to=[self.phones[0]['phone_number']],
                                     _msg=self.language_converter(
                                         "ReuniteTag ID# {} are now active. Each set has {} texts alerts before expiry"
                                             .format(self.tag, self.available_units), _src='en',
                                         _dest=self.languageCode))

                        return {'status': 201, 'msg': "User registration completed"}
                    else:
                        return tag_status
                except Exception as e:
                    print(e)
                    return {'status': 500, 'msg': "Internal server error. Server is unresponsive"}
            else:
                return _verification
        return {'status': 400, 'msg': "Invalid input data"}

    def update(self):
        try:
            TagModel.objects(tag=self.tag).update(
                set__last_modified=datetime.now().strftime('%d-%m-%Y %H:'),
                set__phone_number=self.phones[0]['phone_number'],
                set__status=2
            )
            return {'msg': "Update completed", 'status': 204}
        except Exception as e:
            print(e)
            return {'status': 500, 'msg': "Internal server error. Server is unresponsive"}

    @staticmethod
    def log_message(data):
        log = MessageLogModel()
        log.message_id = uuid.uuid4().hex
        log.sender = data['sender']
        log.recipients = data['recipients']
        log.message = data['message']
        log.language_sent = data['language_sent']
        log.language_received = data['language_received']
        try:
            log.save(force_insert=True)
            return {'status': 201, 'msg': "Message logging completed"}
        except Exception as e:
            print(e)
            return {'status': 500, 'msg': "Internal server error. Server is unresponsive"}

    def found_message(self, message):
        if self.validate_input():
            tag_details = self.verify_tag(UserModel)
            if tag_details['status'] == 200:
                details = tag_details['tag_details']
                phone_list = [phone['phone_number'] for phone in details['phone']]
                total_phone_numbers = len(phone_list)
                try:
                    if details['available_units'] >= total_phone_numbers:
                        units_left = details['available_units'] - total_phone_numbers
                        _message = message + ". UNITS LEFT = {}, Contacts Phone Number = {}"\
                            .format(units_left, self.phones[0]['phone_number'])
                        print(_message)
                        send_message(_to=phone_list, _msg=self.language_converter(_message,
                                                                                  _src=self.languageCode,
                                                                                  _dest=details['languageCode']))
                        UserModel.objects(tag=details['tag']).update(
                            set__last_modified=datetime.now().strftime('%d-%m-%Y %H:'),
                            set__available_units=units_left
                        )
                        UserService.log_message(
                            {
                                'sender': self.phones[0]['phone_number'],
                                'recipients': phone_list,
                                'message': message,
                                'language_sent': self.languageCode,
                                'language_received': details['languageCode'],
                            }
                        )
                        return {'status': 200, 'msg': 'Message sent'}

                except Exception as e:
                    print(e)
                    return {'status': 500, 'msg': "Internal server error. Server is unresponsive"}

            else:
                return {'status': 400, 'msg': 'Invalid Tag ID'}
        else:
            return {'status': 400, 'msg': 'Invalid input parameters'}
        return {'status': 400, 'msg': 'Found message process failed'}
