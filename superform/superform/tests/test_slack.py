import pytest
from superform.models import Publishing
from superform.plugins.slack import run, make_message
import json
import os
from slackclient import SlackClient
import time

json_data = open(os.path.dirname(os.path.abspath(__file__)) + '/../config.json')
data = json.load(json_data)

cha_conf = json.dumps({"token": data["BOT_TOKEN"],
                       "channel name": "bot-channel"})


class Publish(Publishing):
    def __init__(self, post_id, title, description, link_url, image_url,
                 date_from, date_until, channel_id="Slack bot test", state=-1):
        self.post_id = post_id
        self.channel_id = channel_id
        self.state = state
        self.title = title
        self.description = description
        self.link_url = link_url
        self.image_url = image_url
        self.date_from = date_from
        self.date_until = date_until


def test_make_message_regular():
    new_publish = Publish(0, "testing slack", "This is not a description", "www.test.com",
                          "www.just_a_cat.com", "29-11-2018", "30-12-9999")
    message = make_message(new_publish)
    message_splitted = message.split("\n\n")
    assert len(message_splitted) == 4
    assert message_splitted[0] == "*" + new_publish.title + "*"
    assert message_splitted[1] == new_publish.description
    assert message_splitted[2] == new_publish.link_url
    assert message_splitted[3] == new_publish.image_url


def test_make_message_empty():
    new_publish = Publish(0, None, "", None, None, None, None)
    message = make_message(new_publish)
    message_splitted = message.split("\n\n")
    assert len(message_splitted) == 1
    assert message_splitted[0] == new_publish.description


def test_make_message_no_title():
    new_publish = Publish(0, None, "This is not a description", "www.test.com",
                          "www.just_a_cat.com", "29-11-2018", "30-12-9999")
    message = make_message(new_publish)
    message_splitted = message.split("\n\n")
    assert len(message_splitted) == 3
    assert message_splitted[0] == new_publish.description
    assert message_splitted[1] == new_publish.link_url
    assert message_splitted[2] == new_publish.image_url


def test_make_message_no_link():
    new_publish = Publish(0, "testing slack", "This is not a description", None,
                          "www.just_a_cat.com", "29-11-2018", "30-12-9999")
    message = make_message(new_publish)
    message_splitted = message.split("\n\n")
    assert len(message_splitted) == 3
    assert message_splitted[0] == "*" + new_publish.title + "*"
    assert message_splitted[1] == new_publish.description
    assert message_splitted[2] == new_publish.image_url


def test_make_message_no_image():
    new_publish = Publish(0, "testing slack", "This is not a description", "www.test.com",
                          None, "29-11-2018", "30-12-9999")
    message = make_message(new_publish)
    message_splitted = message.split("\n\n")
    assert len(message_splitted) == 3
    assert message_splitted[0] == "*" + new_publish.title + "*"
    assert message_splitted[1] == new_publish.description
    assert message_splitted[2] == new_publish.link_url


def test_run_regular():
    new_publish = Publish(0, "testing slack", "This is not a description", None,
                          None, "29-11-2018", "30-12-9999")

    slack_master = SlackClient(data["BOT_TOKEN"])
    slack_user = SlackClient(data["OTHER_TOKEN"])
    run(new_publish, cha_conf)
    for channel in slack_user.api_call("conversations.list")['channels']:
        if channel['name'] == "testing-bot":
            channelid = channel['id']
    res = slack_user.api_call("channels.history",
                              channel=channelid)

    assert res["messages"][0]['text'] == make_message(new_publish)
    count = 0
    res = slack_user.api_call("channels.history",
                              channel=channelid)
    while count < len(res["messages"]):
        msg_ts = res["messages"][count]['ts']
        slack_master.api_call("chat.delete", ts=msg_ts, channel=channelid, as_user=True)
        count += 1


def test_run_no_title():
    new_publish = Publish(0, None, "This is not a description anymore", None,
                          None, "29-11-2018", "30-12-9999")

    slack_master = SlackClient(data["BOT_TOKEN"])
    slack_user = SlackClient(data["OTHER_TOKEN"])
    run(new_publish, cha_conf)
    for channel in slack_user.api_call("conversations.list")['channels']:
        if channel['name'] == "testing-bot":
            channelid = channel['id']
    res = slack_user.api_call("channels.history",
                              channel=channelid)

    assert res["messages"][0]['text'] == make_message(new_publish)
    count = 0
    res = slack_user.api_call("channels.history",
                              channel=channelid)
    while count < len(res["messages"]):
        msg_ts = res["messages"][count]['ts']
        slack_master.api_call("chat.delete", ts=msg_ts, channel=channelid, as_user=True)
        count += 1


def test_run_no_content():
    new_publish = Publish(0, "My_title", "", None,
                          None, "29-11-2018", "30-12-9999")

    slack_master = SlackClient(data["BOT_TOKEN"])
    slack_user = SlackClient(data["OTHER_TOKEN"])
    run(new_publish, cha_conf)
    for channel in slack_user.api_call("conversations.list")['channels']:
        if channel['name'] == "testing-bot":
            channelid = channel['id']
    res = slack_user.api_call("channels.history",
                              channel=channelid)

    assert res["messages"][0]['text'] == make_message(new_publish)
    count = 0
    res = slack_user.api_call("channels.history",
                              channel=channelid)
    while count < len(res["messages"]):
        msg_ts = res["messages"][count]['ts']
        slack_master.api_call("chat.delete", ts=msg_ts, channel=channelid, as_user=True)
        count += 1
