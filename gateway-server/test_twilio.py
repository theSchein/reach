import pytest

# TODO: replace these three lines of code with entries in values.yaml (or environment variables)
import os
os.environ["TWILIO_TEST_ACCOUNT_SID"] = "ACcca96db1f7fd350f4dde95d76b0bef57"
os.environ["TWILIO_TEST_AUTH_TOKEN"] = "afb4a212bfaef9ea00d444e24e201a18"

from clients.twilio import Twilio
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from utils.logger import logger


class TwilioTester(Twilio):
  def __init__(self):
    account_sid = os.environ["TWILIO_TEST_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_TEST_AUTH_TOKEN"]
    self.client = Client(account_sid, auth_token)


  def text(self, number, body="", expected_result="queued"):
    # Use the Twilio testing API, which uses magic phone numbers for testing,
    # per https://www.twilio.com/docs/iam/test-credentials#test-sms-messages
    if expected_result == "queued":  # "success"
      magic_number = "+15005550006"
    else:  # Any other "invalid phone number" raises the same exception
      magic_number = "+15005550001"

    message = self.client.messages.create(
      to=number,
      from_=magic_number,
      body=body
      # messaging_service_sid is not valid for the test account
    )
    assert message.status == "queued"
    logger.error("TwilioTester: Sent message to {0} with body: {1}".format(number, body))

    return "200"


def test_twilio_connection_valid():
  TwilioTester().text("+15005555555", "Test")

def test_twilio_connection_invalid():
  with pytest.raises(TwilioRestException):
    TwilioTester().text("+15005555555", "Test", "Failure")

# Run this code from /reach/gateway-server by running pytest
