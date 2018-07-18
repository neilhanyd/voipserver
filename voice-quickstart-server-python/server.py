import os,re
from flask import Flask, jsonify, request
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from faker import Factory

ACCOUNT_SID = 'AC316b2d62aabc02200000000000'
API_KEY = 'SK8fa67c9badbe6b7244800000000000'
API_KEY_SECRET = 'RIVBDCfwbDGNbXiS00000000000'
PUSH_CREDENTIAL_SID = 'CR9545e64b8f937100000000000'
APP_SID = 'AP6857aa2a80c743900000000000'

"""
Use a valid Twilio number by adding to your account via https://www.twilio.com/console/phone-numbers/verified
"""
CALLER_NUMBER = '+6531639900'

"""
The caller id used when a client is dialed.
"""
CALLER_ID = '+6531639900'
IDENTITY = 'alice'


app = Flask(__name__)
fake = Factory.create()
alphanumeric_only = re.compile('[\W_]+')

"""
Creates an access token with VoiceGrant using your Twilio credentials.
"""
@app.route('/accessToken', methods=['GET', 'POST'])
def token():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)
  push_credential_sid = os.environ.get("PUSH_CREDENTIAL_SID", PUSH_CREDENTIAL_SID)
  app_sid = os.environ.get("APP_SID", APP_SID)

  grant = VoiceGrant(
    push_credential_sid=push_credential_sid,
    outgoing_application_sid=app_sid
  )

  # identity = request.values["identity"] \
  #         if request.values and request.values["identity"] else IDENTITY

  # Generate a random user name
  identity = alphanumeric_only.sub('', fake.user_name())

  token = AccessToken(account_sid, api_key, api_key_secret, identity=identity)
  token.add_grant(grant)

  print("identity is "+identity)

  return jsonify(identity=identity, token=token.to_jwt())

  #return token.to_jwt()

"""
Creates an endpoint that plays back a greeting.
"""
@app.route('/incoming', methods=['GET', 'POST'])
def incoming():
  resp = VoiceResponse()
  resp.say("Congratulations! You have received your first inbound call! Good bye.")
  return str(resp)

"""
Creates an endpoint that plays back a greeting.
"""
@app.route('/incomingcall', methods=['GET', 'POST'])
def incomingcall():
  resp = VoiceResponse()
  resp.dial(callerId=CALLER_ID).client(IDENTITY)
  # resp.say("Congratulations! You have received your first inbound call! Good bye.")
  return str(resp)  

"""
Makes a call to the specified client using the Twilio REST API.
"""
@app.route('/placeCall', methods=['GET', 'POST'])
def placeCall():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)

  client = Client(api_key, api_key_secret, account_sid)
  to = request.values.get("to")
  call = None

  if to is None or len(to) == 0:
    call = client.calls.create(url=request.url_root + 'incoming', to='client:' + IDENTITY, from_=CALLER_ID)
  elif to[0] in "+6531639900" and (len(to) == 1 or to[1:].isdigit()):
    call = client.calls.create(url=request.url_root + 'incoming', to=to, from_=CALLER_NUMBER)
  else:
    call = client.calls.create(url=request.url_root + 'incoming', to='client:' + to, from_=CALLER_ID)
  return str(call)

"""
Creates an endpoint that can be used in your TwiML App as the Voice Request Url.

In order to make an outgoing call using Twilio Voice SDK, you need to provide a
TwiML App SID in the Access Token. You can run your server, make it publicly
accessible and use `/makeCall` endpoint as the Voice Request Url in your TwiML App.
"""
@app.route('/makeCall', methods=['GET', 'POST'])
def makeCall():
  resp = VoiceResponse()
  to = request.values.get("to")

  if to is None or len(to) == 0:
    resp.say("Congratulations! You have just made your first call! Good bye.")
  elif to[0] in "+1234567890" and (len(to) == 1 or to[1:].isdigit()):
    resp.dial(callerId=CALLER_NUMBER).number(to)
  else:
    resp.dial(callerId=CALLER_ID).client(to)
  return str(resp)

@app.route('/', methods=['GET', 'POST'])
def welcome():
  resp = VoiceResponse()
  resp.say("Welcome to Twilio")
  return str(resp)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
