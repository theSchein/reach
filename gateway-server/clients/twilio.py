import os
from twilio.rest import Client


class Twilio:
  def __init__(self):
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    self.client = Client(account_sid, auth_token)
    self.messaging_service_sid = os.environ["TWILIO_MESSAGE_SERVICE_SID"]


  def text(self, number, body=""):
    message = self.client.messages.create(
      to=number,
      messaging_service_sid=self.messaging_service_sid,
      body=body
    )

    return "200"

    
