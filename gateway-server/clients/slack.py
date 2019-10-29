import os
import re
import logging
import slack
#from flask.logging import default_handler  # FIXME: this line does not work in Flask 0.12.2, causing test_slack.py to fail
from utils.helpers import channel_token, to_E_164_number
from utils.logger import logger

class Team:
    """
    Teams contain many users contact and availability information.
    """
    def __init__(self):
        self.members = [{"user_name": "mike", "name": "Michael Ghen", "user_id": "UD0PP9S48", "phone_number": "+12154781286", "priority": 1},
                        {"user_name": "julie", "name": "Julie Vitale", "user_id": "UE1KYA37H", "phone_number": "+14844781286", "priority": 1},
                        {"user_name": "user1", "name": "User One", "user_id": "ULG64DT1T", "phone_number": "+15551111111", "priority": 1},
                        {"user_name": "user2", "name": "User Two", "user_id": "UL9QXKJTT", "phone_number": "+15552222222", "priority": 1}]


    #
    # def get_members_by_priority(priority):
    #     return list(map(self.members, lambda m: if m["priority"] == priority: return m))
    #

class Slack:
  def __init__(self):
    self.sc =slack.WebClient(token=os.environ['SLACK_TOKEN'])


  def start_engagement(self, number, texting_client=None):
    logger.error("Inside start engagement: {0}".format(number))
    group_name = channel_token(number)
    phone_number = to_E_164_number(number)
    # TODO: Add disclaimer, informed consent language
    message = """
Hello, from the Reach Test Network!
How can we help you?
Reply Stop to stop all contact.
    """

    is_intro = True
    try:
        group = self.sc.groups_create(
          name=group_name,
          is_private=True,
          validate=True
        )
    except slack.errors.SlackApiError as e:
        # TODO: We have already seen this client
        logger.error("Error: {0}".format(str(e)))
        is_intro = False
        # message = "@channel: This client has signed up again."
        group = group_name
        # self.message_to_group(message, self.group_id_from_group_name(group_name))
        return group_name, phone_number

    group_id = group["group"]["id"]
    self.message_to_group(message, group_id)
    if is_intro and texting_client is not None:
        text = texting_client.text(phone_number, message)



    # Setup purpose to include the patients phone number
    # for emergency contact purposes
    response = self.sc.groups_setTopic(
      channel=group_id,
      topic=":warning: {0}".format(phone_number)
    )
    response = self.sc.groups_setPurpose(
      channel=group_id,
      purpose="Reaching out to {0}".format(phone_number)
    )

    if not response["ok"]:
        logger.error(response)
        logger.error("Purpose for channel {0} not changed".format(group_name))


    response = self.sc.groups_invite(
      channel=group_id,
      user="ULG64DT1T" # User One
    )

    response = self.sc.groups_invite(
      channel=group_id,
      user="UE1KYA37H" # User Two
    )

    if not response["ok"]:
        logger.error("User not invited channel {0}".format(group["group"]["name"]))

    return group_name, phone_number


  def forward_twilio_message(self, group, body):
    """
    Forwards the body of a twilio message to the channel
    """
    modified_body = ":speech_balloon: " + body
    logger.error("Group: {0}".format(group))
    group_id = self.group_id_from_group_name(group)
    logger.error(group_id)
    self.message_to_group(modified_body, group_id)
    return "200"

  def message_to_group(self, body, group_id, attachments=None):
    if group_id[0] != 'G':
        # not a group ID, look it up by name
        group_id = self.group_name_from_group_id(group_id)
    message = self.sc.chat_postMessage(
      channel=group_id,
      text=body,
      attachments=attachments
    )
    return message


  def group_name_from_group_id(self, group_id):
      group = self.sc.groups_info(
        channel=group_id
      )
      logger.info(group)
      return group["group"]["name"]


  def group_id_from_group_name(self, group_name):
    groups = self.sc.groups_list()
    for group in groups["groups"]:
        if group["name"] == group_name:
            return group["id"]
    return None

  def does_channel_exist(self, channel):
    if self.group_id_from_group_name(channel):
        return True
    else:
        return False

  def get_phone_number_by_user_name(self, user_name):
      # TODO: Mocked because it's difficult to pull this from slack
      # TODO: Update test if we pull this from slack later
      team = Team()
      for member in team.members:
          logger.debug(member)
          logger.debug("{0}, {1}".format(member["user_name"], user_name))
          if member["user_name"] == user_name:
              return member["name"], member["phone_number"]
