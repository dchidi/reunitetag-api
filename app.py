import os
from flask import Flask, request, session, redirect
from flask_mail import Mail
from dotenv import load_dotenv, find_dotenv
from code.services.user import UserService
from code.services.tag import TagService
from code.services.stripe_checkout import StripeCheckoutService
from code.services.send_email import Email
# Resource : https://flask-cors.readthedocs.io
from flask_cors import CORS, cross_origin

# find and load possible environment variable file
load_dotenv(find_dotenv())

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('REUNITE_TAG_SECRET_KEY')
app.config['CORS_HEADERS'] = 'Content-Type'
# Email settings
app.config['MAIL_SERVER'] = os.getenv('EMAIL_SEVER')
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USERNAME')
# SET THE APP PASSWORD USING THIS LINK https://myaccount.google.com/apppasswords
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail_lib = Mail(app)
# SESSION SETUP
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'


# ******************************************************************
# ******************************* User *****************************
# ******************************************************************
# POST
@app.post('/register_tag')
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def register_tag():
    # expected input {phone:list, tag:string, language:string}
    user_service = UserService(request.get_json())
    return {'data': user_service.save()}


# ******************************************************************
# ****************************** Tags ******************************
# ******************************************************************
@app.post('/load_tag')
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def load_tag():
    # expected input {total_tags:int}
    tag_service = TagService(request.get_json())
    return {'data': tag_service.load()}


@app.post('/validate_tag')
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def validate_tag():
    return {'data': TagService({}).verify_tag(request.get_json()['tagId'])}


@app.get('/products')
def products():
    return {'data':"should return product list"}


@app.get('/product_details')
def product_details():
    pass


# POST


@app.post('/product')
def product():
    pass


@app.post('/assign_tag')
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def assign_tag():
    tag_service = TagService({})
    data = tag_service.assign_tag_to_phone_number(request.get_json())
    if data['status'] == 501:
        email = Email(mail_lib)
        email.send_ticket({'message': data['msg'], 'phone': data['data']['phone']})
    return {'data': data}


@app.post('/found_item')
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def found_item():
    payload = request.get_json()
    data = {'phones': [{'phone_number': payload['phone_number']}], 'tag': payload['tag_id'],
            'languageCode': payload['languageCode'], 'language': payload['language']}

    return {'data': UserService(data).found_message(payload['message'])}


# PUT
@app.put('/top_up')
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def top_up():
    data = request.get_json()
    return {'data': TagService({}).top_up(tag=data['tag'])}


# ******************************************************************
# *********************** CHECKOUT WITH STRIPE *********************
# ******************************************************************
@app.post('/checkout')
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def checkout():
    stripe_checkout = StripeCheckoutService(request.get_json()['details'])
    stripe_data = stripe_checkout.checkout()
    if stripe_data:
        return {'data': stripe_data}
    return {'data': 'Stripe checkout API endpoint failed', 'status': 400}


@app.get('/checkout_response/<id>')
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def checkout_response(id):
    live = True
    base_url = 'https://reunitetag.herokuapp.com' if live else 'http://localhost:3000'
    _url = '{}/cancel_payment'.format(base_url)
    _data = StripeCheckoutService({}).checkout_response(id)
    if _data['status'] == 201:
        _url = '{}/payment_successful/ok'.format(base_url)
        return redirect(_url)
    return {'data': _data}


# ******************************************************************
# *************************** SEND EMAIL ***************************
# ******************************************************************

@app.post('/send_mail')
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def send_mail():
    email = Email(mail_lib)
    return {'data': email.send_enquiry(request.get_json())}


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
