import pytest
from unittest.mock import MagicMock, patch

import json

import app
from utils.helpers import channel_token


@pytest.fixture
def app_mock(monkeypatch):
	# See also https://flask.palletsprojects.com/en/1.0.x/testing/#testing-json-apis
	# First, before using app.app, mock the external API's
	app.twilio_client = MagicMock()

	app.slack_client = MagicMock()
	app.slack_client.start_engagement.return_value = (channel_token("+15551111111"), "+15551111111")
	app.slack_client.forward_twilio_message.return_value = "200"
	#app.slack_client.does_channel_exist
	app.slack_client.group_name_from_group_id.return_value = "vengeful-ant"
	#app.slack_client.get_phone_number_by_user_name

	app.unomi_client = MagicMock()  # methods are currently overwritten in the tests
	app.too_client = MagicMock()

	# Now that the external API's are mocked, use flask's test capabilities
	test_app = app.app.test_client()
	yield test_app

def get_updated_profile(called_unomi_mock):
	# Extracts the updated profile submitted to the unomi_client mock object.
	# To parse the mock's args list, we need to unpack the method call's
	# (args, kwargs) tuple then get the second arg of update_profile
	return called_unomi_mock.update_profile.call_args[0][1]

def test_need(app_mock):
	app.unomi_client.profile_search.return_value = {'properties': {'needs': []}}
	rv = app_mock.post('/need?channel_id=CDF8LERL6&channel_name=vengeful-ant&command=/need&text=dentist&user_name=g_kip')
	assert json.loads(rv.data) == {'response_type': 'in_channel', 'text': 'Need saved: dentist'}
	assert get_updated_profile(app.unomi_client)['needs'][0]['name'] == 'dentist'
	app.unomi_client.update_profile.assert_called_once()

def test_demographics(app_mock):
	test_route = '/demographics?channel_id=CDF8LERL6&channel_name=vengeful-ant&command=/demographics&text=age%2026&user_name=g_kip'
	expected_response = {'response_type': 'in_channel', 'text': 'Demographic saved: age=26'}

	# Test case when no demographics have been previously set
	app.unomi_client.profile_search.return_value = {'properties': {}}
	rv = app_mock.post(test_route)
	assert json.loads(rv.data) == expected_response
	assert get_updated_profile(app.unomi_client)['demographics']['age'] == '26'
	app.unomi_client.update_profile.assert_called_once()

	# Test overriding the existing demographics (default try, without KeyError)
	app.unomi_client.reset_mock()
	app.unomi_client.profile_search.return_value = {'properties': {
		'demographics': {'age': '200', 'height': 'tall'}
	}}
	rv = app_mock.post(test_route)
	assert json.loads(rv.data) == expected_response
	assert get_updated_profile(app.unomi_client)['demographics']['age'] == '26'

def test_event(app_mock):
	rv = app_mock.post('/event?channel_id=CDF8LERL6&channel_name=vengeful-ant&command=/event&text=meeting&user_name=g_kip')
	assert json.loads(rv.data) == {'response_type': 'in_channel', 'text': 'Event saved: meeting'}
	app.unomi_client.track_event.assert_called_once_with(
		'vengeful-ant', 'userGenerated', {'value': 'meeting'}, 'g_kip'
	)

def test_stage(app_mock):
	app.unomi_client.profile_search.return_value = {'properties': {}}
	rv = app_mock.post('/stage?channel_id=CDF8LERL6&channel_name=vengeful-ant&command=/stage&text=action%20went%20to%20meeting&user_name=g_kip')
	assert json.loads(rv.data) == {'response_type': 'in_channel', 'text': 'Event saved'}
	assert get_updated_profile(app.unomi_client)['stage'] == {'name': 'action', 'notes': 'went to meeting'}
	app.unomi_client.update_profile.assert_called_once()

def test_211(app_mock):
	app.too_client.search.return_value = 'fake_results'
	rv = app_mock.post('/211?channel_id=CDF8LERL6&channel_name=brown-dear&command=/211&text=shelter%2018018&user_name=g_kip')
	assert json.loads(rv.data) == {'response_type': 'in_channel', 'text': '211 Results', 'attachments': 'fake_results'}
	app.too_client.search.assert_called_once_with('shelter', '18018')
	app.unomi_client.track_event.assert_called_once()
