import json
import os

import tempfile
import time

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pytest
from selenium import webdriver
from sqlalchemy.exc import InvalidRequestError

from superform import db, app
from selenium.webdriver.support import expected_conditions as EC
from superform.models import Publishing
from superform.utils import datetime_converter

json_data = open(os.path.dirname(os.path.abspath(__file__)) + '/../config.json')
data = json.load(json_data)

channelName = "Slack_test"
pluginName = "superform.plugins.slack"
fieldTested = ["title", "description", "link"]
configuration = {"token": data["BOT_TOKEN"], "channel name": "testing-bot"}


@pytest.fixture
def client():
    app.app_context().push()
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    client = app.test_client()
    with app.app_context():
        db.create_all()
    yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


@pytest.mark.frontEnd
def test_basic(client):
    pytest.helpers.plugin.test_basic(client, channelName, pluginName, fieldTested)


@pytest.mark.frontEnd
def test_basic_moderate(client):
    pytest.helpers.plugin.test_basic_moderate(client, channelName, pluginName, fieldTested)


@pytest.mark.frontEnd
def test_basic_warning(client):
    pytest.helpers.plugin.test_basic_warning(client, channelName, pluginName)


@pytest.mark.frontEnd
def test_basic_publish(client):
    pytest.helpers.plugin.test_basic_publish(client, channelName, pluginName, configuration, {})


@pytest.mark.frontEnd
def test_basic_warning2(client):
    id_channel, id_post = pytest.helpers.plugin.setup_db(channelName, pluginName)
    driver = webdriver.Firefox()
    try:
        driver.get('http://localhost:5000/')
        wait = WebDriverWait(driver, 10)
        driver.find_element_by_link_text("Login").click()
        driver.find_element_by_name("j_username").click()
        driver.find_element_by_name("j_username").clear()
        driver.find_element_by_name("j_username").send_keys("myself")
        driver.find_element_by_name("j_password").click()
        driver.find_element_by_name("j_password").clear()
        driver.find_element_by_name("j_password").send_keys("myself")
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Password:'])[1]/following::input[2]").click()
        driver.switch_to.alert.accept()

        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Channels")))
        driver.find_element_by_link_text("Channels").click()
        driver.find_element_by_link_text("Configure").click()
        driver.find_element_by_id("token").click()
        driver.find_element_by_id("token").clear()
        driver.find_element_by_id("token").send_keys("xoxb-478281424595-487185661847-YVh8O74HfdCtAJj7vuSw9Acv")
        driver.find_element_by_id("channel name").click()
        driver.find_element_by_id("channel name").clear()
        driver.find_element_by_id("channel name").send_keys("major")
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='channel name'])[1]/following::button[1]").click()

        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'New post')))
        driver.find_element_by_link_text("New post").click()
        driver.find_element_by_id("chan_option_" + str(id_channel)).click()
        driver.find_element_by_id("titlepost").click()
        driver.find_element_by_id("titlepost").clear()
        driver.find_element_by_id("titlepost").send_keys("Test")
        driver.find_element_by_id("descriptionpost").click()
        driver.find_element_by_id("descriptionpost").clear()
        driver.find_element_by_id("descriptionpost").send_keys(
            "Frontend")
        driver.find_element_by_id("linkurlpost").click()
        driver.find_element_by_id("linkurlpost").clear()
        driver.find_element_by_id("linkurlpost").send_keys("http://localhost:5000/new")
        driver.find_element_by_id("datefrompost").click()
        driver.find_element_by_id("datefrompost").clear()
        driver.find_element_by_id("datefrompost").send_keys("2020-11-21")
        driver.find_element_by_id("dateuntilpost").click()
        driver.find_element_by_id("dateuntilpost").clear()
        driver.find_element_by_id("dateuntilpost").send_keys("2021-01-29")
        driver.find_element_by_link_text(channelName).click()
        extra = {}
        pub = Publishing(post_id=id_post, channel_id=id_channel, state=0,
                         title=driver.find_element_by_id(channelName + "_titlepost").get_attribute("value"),
                         description=driver.find_element_by_id(channelName + "_descriptionpost").get_attribute(
                             "value"),
                         link_url=driver.find_element_by_id(channelName + "_linkurlpost").get_attribute("value"),
                         image_url="pas",
                         date_from=datetime_converter("2050-07-01"),
                         date_until=datetime_converter("2050-07-01"), extra=json.dumps(extra))
        db.session.add(pub)
        db.session.commit()
        driver.get('http://localhost:5000/')
        # wait.until(EC.element_to_be_clickable((By.ID, "moderate_" + str(id_channel))))
        driver.find_element_by_id("moderate_" + str(id_post)).click()
        driver.find_element_by_id("pub-button").click()
        assert driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Moderate this publication'])[1]/following::div[1]").text == "Warning!: Channel not found, please review your configuration"
    except AssertionError as e:
        pytest.helpers.plugin.teardown_db(id_channel, id_post)
        driver.close()
        assert False, str(e)
    except InvalidRequestError as e:
        pytest.helpers.plugin.teardown_db(id_channel, id_post)
        driver.close()
        assert False, "An error occurred while testing: {}".format(str(e))
    pytest.helpers.plugin.teardown_db(id_channel, id_post)
    driver.close()
