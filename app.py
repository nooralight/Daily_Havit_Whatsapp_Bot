from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from twilio.base.exceptions import TwilioRestException
from flask import Flask, request,session
from flask_session import Session
from datetime import timedelta
import os

import phonenumbers
import pytz

from dotenv import load_dotenv
load_dotenv()

account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
phone_number = os.getenv('PHONE_NUMBER')
messaging_sid=os.getenv('MESSAGING_SID')
client = Client(account_sid, auth_token)

app = Flask(__name__)
app.config['secret_key'] = '5800d5d9e4405020d527f0587538ctqe'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/whatsapp', methods=['POST'])
def handle_incoming_message():
    message = request.form.get('Body')
    sender = request.form.get('From')
    if session.get("context")==None:
        send_message = client.messages.create(
            from_=messaging_sid,
            body="Thanks for coming here. Please choose what service you want to use.\n\nPress 1: Talk with Chatbot\nPress 2: Create a new Habit", 
            to=sender
        )
        session['context']="0"
        #session['context']="0"
        return "okay"
    elif session.get("context")=="0":
        if message =="1":
            send_message = client.messages.create(
                from_=messaging_sid,
                body="Thanks for choosing to talk with the bot. Our bot supports Openai GPT-3.5 api resources.\n\nThis feature will come very soon! Stay with us..", 
                to=sender
            )
            session['context']= None
            return "okay"
        elif message == "2":
            send_message = client.messages.create(
                from_=messaging_sid,
                body="Please tell me your *Daily Havit Title*\n\nExample: '''Cycling in the evening''' ", 
                to=sender
            )
            session['context']= "title_of_havit"
            return "okay"
    elif session.get("context")=="title_of_havit":
        send_message = client.messages.create(
                from_=messaging_sid,
                body="Please tell me your *Starting time of the daily Havit*\n\nExample: '''4:15 pm''' ", 
                to=sender
            )
        session['context']= "time_of_havit"
        return "okay"
    elif session.get("context")=="time_of_havit":
        sender_number = sender[9:]
        timezone = get_default_timezone(sender_number)
        send_message = client.messages.create(
                from_=messaging_sid,
                body=f"Awesome! we are currently set timezone using your country's default timezone which is {timezone}.\n\nYour havit has been created. We will monitor everyday of your havit progress. Thanks for using our service!", 
                to=sender
            )
        session['context']= None
        return "okay"
    
def get_default_timezone(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        country_code = phonenumbers.region_code_for_number(parsed_number)
        country_timezone = pytz.country_timezones[country_code][0]
        return country_timezone
    except phonenumbers.phonenumberutil.NumberParseException:
        return None
    except KeyError:
        return None
    
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=8000)