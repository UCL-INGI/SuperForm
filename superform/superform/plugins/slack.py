import json
from slackclient import SlackClient

from models import StatusCode
from superform.run_plugin_exception import RunPluginException

FIELDS_UNAVAILABLE = []

CONFIG_FIELDS = ['token', 'channel name']


# This lets the manager of your module enter data that are used to communicate with other services.

def run(publishing, channel_config):
    json_data = json.loads(channel_config)
    if not('token' in json_data and 'channel name' in json_data):
        return StatusCode.ERROR, 'Please configure the channel first'

    token = json_data['token']
    name = json_data['channel name']
    slack_client = SlackClient(token)

    message = make_message(publishing)

    channels = slack_client.api_call(
        "conversations.list", types=("public_channel", "private_channel")
    )

    if not(channels['ok']):
        return StatusCode.ERROR, "Channel not found, please review your configuration"

    found = False
    for channel in channels['channels']:
        if channel['name'] == name:
            found = True
            channelid = channel['id']
            slack_client.api_call(
                "chat.postMessage",
                channel=channelid,
                text=message
            )
    if not found:
        return StatusCode.ERROR, "Channel not found, please review your configuration"
    return StatusCode.OK, None


def make_message(publishing):
    message = ""
    if publishing.title:
        message = message + "*" + publishing.title + "*\n\n"

    message = message + publishing.description

    if publishing.link_url:
        message = message + "\n\n" + publishing.link_url

    if publishing.image_url:
        message = message + "\n\n" + publishing.image_url

    return message
