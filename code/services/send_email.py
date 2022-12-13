# reference flask email package
from datetime import datetime
from flask_mail import Message


class Email:
    def __init__(self, mail):
        # initialize required variables
        self.mail = mail
        self.sender = "sales@reuniteTag.com"
        self.date_created = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    # Send email to recipient
    def send_enquiry(self, data):
        # 'nic@iserve.ie', 'ken@iserve.ie'
        _recipient = ['dchidi4real@yahoo.com']
        msg = Message("ReuniteTag Enquiry Form", sender=self.sender, recipients=_recipient)
        msg.html = '''
        <div style="width:400px;">
            <div style="background-color:#30628c;padding:20px;color:#fff;text-align:center;">
                <h2>ReuniteTag ENQUIRIES</h2>
            </div>
            <div  style="padding:20px;">
              <h3 style="margin-bottom:-10px; font-size:16px">Date Created</h3>
              <p>{}</p>
              <h3 style="margin-bottom:-10px; font-size:16px">Name</h3>
              <p>{}</p>
              <h3 style="margin-bottom:-10px;font-size:16px">Email</h3>
              <p>{}</p>
              <h3 style="margin-bottom:-10px;font-size:16px">Phone</h3>
              <p>{}</p>
              <h3 style="margin-bottom:-10px; font-size:16px">Message </h3>
              <p>{}</p>
            </div>
        </div>
        '''.format(self.date_created, data['name'], data['email'], data['phone'], data['message'])
        try:
            self.mail.send(msg)
            return {'status': 200, 'msg': 'Message sent'}
        except Exception as e:
            return {'status': 500, 'msg': 'Internal Server Error'}

    # Send email to recipient
    def send_ticket(self, data):
        # 'nic@iserve.ie', 'ken@iserve.ie'
        _recipient = ['dchidi4real@yahoo.com']
        msg = Message("ReuniteTag Ticket", sender='ticket@reunitetag.com', recipients=_recipient)
        msg.html = '''
            <div style="width:400px;">
                <div style="background-color:#30628c;padding:20px;color:#fff;text-align:center;">
                    <h2>ReuniteTag ENQUIRIES</h2>
                </div>
                <div  style="padding:20px;">
                  <h3 style="margin-bottom:-10px; font-size:16px">Date Created</h3>
                  <p>{}</p>
                  <h3 style="margin-bottom:-10px;font-size:16px">Phone</h3>
                  <p>{}</p>
                  <h3 style="margin-bottom:-10px; font-size:16px">Message </h3>
                  <p>{}</p>
                </div>
            </div>
            '''.format(self.date_created, data['phone'], data['message'])
        try:
            self.mail.send(msg)
            return {'status': 200, 'msg': 'Message sent'}
        except Exception as e:
            return {'status': 500, 'msg': 'Internal Server Error'}
