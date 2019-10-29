import requests
import logging
#from flask.logging import default_handler  # FIXME: this line does not work in Flask 0.12.2, causing test_app.py to fail
from requests.auth import HTTPBasicAuth
from json import loads
from datetime import datetime
from utils.helpers import channel_token
from utils.logger import logger

"""
The profile and session IDs are equal to channel_token(phone_number)
"""

ENDPOINT = "http://unomi:8181"
AUTH = ('karaf','karaf')


class Unomi:
    def create_profile(self, profile_id, properties):
        """
        Create a new profile (and session) for a client in Unomi
        """
        profile = self.update_profile(profile_id, properties)
        session = {
            "itemId":profile_id,
            "itemType":"session",
            "scope":None,
            "version":1,
            "profileId":profile_id,
            "profile": profile,
            "properties":{
                "demographics": {},
            },
            "systemProperties":{},
            "timeStamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        # Create session
        r = requests.post('{endpoint}/cxs/profiles/sessions/{profile_id}'\
                    .format(endpoint=ENDPOINT, profile_id=profile_id),
            auth=('karaf', 'karaf'),
            json=session)
        return profile


    def update_profile(self, profile_id, properties):
        """
        Update profile in Unomi for profile_id
        """
        profile = {
            "itemId": profile_id,
            "itemType":"profile",
            "version":None,
            "properties": properties,
            "systemProperties":{},
            "segments":[],
            "scores":{},
            "mergedWith":None,
            "consents":{}
        }
        r = requests.post('{endpoint}/cxs/profiles/'.format(endpoint=ENDPOINT),
                auth=AUTH,
                json=profile)
        return profile


    def track_inbound_message(self, profile_id, message):
        properties = {'text': message}
        self.track_event(profile_id, 'inboundMessage', properties)
        return


    def track_outbound_message(self, profile_id, message, user):
        properties = {'text': message}
        self.track_event(profile_id, 'outboundMessage', properties, user)
        return


    # TODO: Integrate with slash command
    def track_event(self, profile_id, type, properties, user=None):
        """
        Tracks and event in unomi.
        user == the Slack user recording the event
        type == the eventType (e.g. message)
        properties == a dictionary of properties to add (e.g. {"text": "Help me"})
        """
        json = {
            "events": [
                {
                    "eventType":type,
                    "scope": "reach",
                    "properties": properties
                }
            ]
        }
        if user:
            json["events"][0]["source"] = {
                "itemType": "slackUser",
                "itemId": user
            }
        r = requests.post('{endpoint}/eventcollector?sessionId={profile_id}'\
                    .format(endpoint=ENDPOINT, profile_id=profile_id),
                auth=('karaf', 'karaf'),
                json=json)
        return


    def profile_search(self, text):
        """
        Fetches a clients profile from Unomi based properties search.
        Uses a match all Elasticsearch query to find the profile
        """
        # TODO: Use proper condition:
        # {
        #   "type":"profilePropertyCondition",
        #   "parameterValues":{
        #       "propertyName":"properties.phoneNumber",
        #       "comparisonOperator":"equals",
        #       "propertyValue": phone_number
        #   }
        # }
        json = {
            "text": text
        }
        r = requests.post('{endpoint}/cxs/profiles/search'.format(endpoint=ENDPOINT),
            auth=('karaf', 'karaf'),
            json =json)
        content = r.content.decode()

        try:
            profile = loads(content)["list"][0]
        except IndexError as e: # Case when no results
            return None

        return profile


    def phone_number_from_channel(self, channel):
        """
        Fetches a clients phone number from Unomi based on the channel.
        The clients profile ID is the same as the channel name.
        """
        profile = self.profile_search(channel)
        return profile["properties"]["phoneNumber"]


    def channel_from_phone_number(self, phone_number):
        """
        Fetches a clients channel (i.e. itemId) from Unomi based on phone number
        """
        profile = self.profile_search(phone_number)
        logger.debug("PROFILE: {0}".format(profile))
        if profile:
            return profile["itemId"]
        else:
            return channel_token(phone_number)

    def list_profiles(self):
        """
        Fetches a clients profile from Unomi based properties search.
        Uses a match all Elasticsearch query to find the profile
        """
        json = {
            "limit": 1000,
            "condition":{
                "type":"matchAllCondition",
                "parameterValues": {}
            }}
        r = requests.post('{endpoint}/cxs/profiles/search'.format(endpoint=ENDPOINT),
            auth=('karaf', 'karaf'),
            json =json)
        profiles = loads(r.content.decode())["list"]
        return profiles

    def list_events(self, profile_id):
        """
        Lists all the events for a profile
        Uses a match all Elasticsearch query to find the profile
        """
        r = requests.get('{endpoint}/cxs/profiles/sessions/{profile_id}/events/'.format(endpoint=ENDPOINT,
            profile_id=profile_id),
            auth=('karaf', 'karaf'))
        profiles = loads(r.content.decode())["list"]
        return profiles
