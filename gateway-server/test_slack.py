import pytest
from unittest.mock import MagicMock, Mock, patch

from clients.slack import Slack
from utils.helpers import channel_token
from slack.errors import SlackApiError


def test_slack_connection():
	# Testing the configuration and connection to the slack API,
	# per https://api.slack.com/methods/api.test
	# Valid API call
	slack_tester = Slack()
	slack_tester.sc.api_call("api.test")
	# Invalid API call
	with pytest.raises(SlackApiError):
		slack_tester.sc.api_call("api.test", json={'error': "myerror"})

@pytest.fixture
def slack_mock():
	slack_client = Slack()
	slack_client.sc = MagicMock()
	# TODO: check if these are actually reasonable return values for the Slack API
	slack_client.sc.groups_list.return_value = {"groups": [
		{"name": "Test1", "id": "G100"},
		{"name": channel_token("+15551111111"), "id": "G200"}
	]}
	slack_client.sc.groups_info.return_value = {"group": {"name": "Test1", "id": "G100"}}
	slack_client.sc.chat_postMessage.return_value = "Test return"
	slack_client.sc.groups_create.return_value = slack_client.sc.groups_info.return_value
	# did not explicitly define groups_setTopic, groups_setPurpose, or groups_invite here
	yield slack_client

def test_start_engagement_repeat(slack_mock):
	slack_mock.sc.groups_create.side_effect = SlackApiError("msg", "resp")
	# asserting the message_to_group method is not consistently working in pytest, so let's check
	#slack_mock.message_to_group = MagicMock()
	#slack_mock.message_to_group.return_value = "mocked"
	output = slack_mock.start_engagement("+15551111111")
	assert output == (channel_token("+15551111111"), "+15551111111")
	slack_mock.sc.groups_create.assert_called_once()  # attempted to create the group
	#slack_mock.message_to_group.assert_called_once()  # "client has signed up again"
	#slack_mock.sc.chat_postMessage.assert_called_once()  # replacement for "client has signed up again"

def test_start_engagement_new_client(slack_mock):
	texting_client = MagicMock()
	texting_client.text.return_value = "200"

	output = slack_mock.start_engagement("+15551111111", texting_client)
	assert output[0] == channel_token("+15551111111")

	slack_mock.sc.groups_create.assert_called_once()
	texting_client.text.assert_called_once()
	slack_mock.sc.groups_setTopic.assert_called_once()
	slack_mock.sc.groups_setPurpose.assert_called_once()
	slack_mock.sc.groups_invite.assert_called()  # inviting user(s) for response

def test_forward_twilio_message(slack_mock):
	assert slack_mock.forward_twilio_message("Test1", "Body test") == "200"

def test_message_to_group(slack_mock):
	assert slack_mock.message_to_group("Test body", "G1", None) == "Test return"
	slack_mock.sc.chat_postMessage.assert_called_with(channel="G1", text="Test body", attachments=None)

def test_group_name_from_group_id(slack_mock):
	assert slack_mock.group_name_from_group_id("G100") == "Test1"

def test_group_id_from_group_name(slack_mock):
	assert slack_mock.group_id_from_group_name("Test1") == "G100"
	assert slack_mock.group_id_from_group_name("TestFake") is None

def test_does_channel_exist(slack_mock):
	assert slack_mock.group_id_from_group_name("Test1")
	assert not slack_mock.group_id_from_group_name("TestFake")

def test_get_phone_number_by_user_name(slack_mock):
	# currently based on the Team() mock in slack.py
	assert slack_mock.get_phone_number_by_user_name("user1") == ("User One", "+15551111111")
