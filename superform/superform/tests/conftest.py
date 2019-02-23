import time

from tests.test_basic import create_user

pytest_plugins = ['helpers_namespace']

import json

import pytest
from selenium.webdriver.common.by import By

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from superform import db

from selenium.webdriver.support.wait import WebDriverWait

from superform.models import Channel, Authorization, Post, Publishing, User
from superform.utils import datetime_converter
from _pytest.warning_types import RemovedInPytest4Warning
from sqlalchemy.exc import InvalidRequestError
import warnings

warnings.filterwarnings("ignore", category=RemovedInPytest4Warning)

user_admin = 0   # Save if user is an admin


@pytest.helpers.plugin.register
def setup_db(channelName, pluginName):
    global user_admin
    myself_user = db.session.query(User).get('myself')
    if not myself_user:
        myself_user = create_user(id="myself", name="myself", first_name="myself",
                           email="myself")
    user_admin = myself_user.admin
    myself_user.admin = 1

    id_channel = 0

    channel = Channel(id=id_channel, name=channelName, module=pluginName, config="{}")
    db.session.add(channel)
    authorization = Authorization(user_id="myself", channel_id=id_channel, permission=2)
    db.session.add(authorization)

    id_post = 0

    post = Post(id=id_post, user_id="myself", title="first title",
                description="That know ask case sex ham dear her spot. Weddings followed the all marianne nor whatever settling. Perhaps six prudent several her had offence. Did had way law dinner square tastes. Recommend concealed yet her procuring see consulted depending. Adieus hunted end plenty are his she afraid. Resources agreement contained propriety applauded neglected use yet. ",
                link_url="http://facebook.com/", image_url="pas", date_from=datetime_converter("2018-07-01"),
                date_until=datetime_converter("2018-07-01"))
    db.session.add(post)

    try:
        db.session.commit()
    except Exception as e:
        print(str(e))
        db.session.rollback()
    return id_channel, id_post


@pytest.helpers.plugin.register
def teardown_db(id_channel, id_post):
    global user_admin
    myself_user = db.session.query(User).get('myself')
    myself_user.admin = user_admin
    post = db.session.query(Post).filter(Post.id == id_post).first()
    channel = db.session.query(Channel).filter(Channel.id == id_channel).first()
    publishing = db.session.query(Publishing).filter(
        Publishing.post_id == id_post and Publishing.channel_id == id_channel).first()
    if publishing is not None:
        db.session.delete(publishing)
    if post is not None:
        db.session.delete(post)
    if channel is not None:
        db.session.delete(channel)
    try:
        db.session.commit()
    except:
        db.session.rollback()


@pytest.helpers.plugin.register
def test_basic(client, channelName, pluginName, fieldTested):
    id_channel, id_post = setup_db(channelName, pluginName)
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

        if "title" in fieldTested:
            assert driver.find_element_by_id(channelName + "_titlepost").get_attribute(
                "value") == "Test"
        if "description" in fieldTested:
            assert driver.find_element_by_id(channelName + "_descriptionpost").get_attribute(
                "value") == "Frontend"
        if "link" in fieldTested:
            assert driver.find_element_by_id(channelName + "_linkurlpost").get_attribute(
                "value") == "http://localhost:5000/new"
    except AssertionError as e:
        teardown_db(id_channel, id_post)
        driver.close()
        assert False, str(e)
    except InvalidRequestError as e:
        teardown_db(id_channel, id_post)
        driver.close()
        assert False, "An error occurred while testing: {}".format(str(e))
    teardown_db(id_channel, id_post)
    driver.close()


@pytest.helpers.plugin.register
def test_basic_moderate(client, channelName, pluginName, fieldTested):
    id_channel, id_post = setup_db(channelName, pluginName)
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
                         description=driver.find_element_by_id(channelName + "_descriptionpost").get_attribute("value"),
                         link_url=driver.find_element_by_id(channelName + "_linkurlpost").get_attribute("value"),
                         image_url="pas",
                         date_from=datetime_converter("2018-07-01"),
                         date_until=datetime_converter("2018-07-01"), extra=json.dumps(extra))
        db.session.add(pub)
        db.session.commit()
        driver.get('http://localhost:5000/')
        # wait.until(EC.element_to_be_clickable((By.ID, "moderate_" + str(id_channel))))
        driver.find_element_by_id("moderate_" + str(id_post)).click()
        if "title" in fieldTested:
            assert driver.find_element_by_id("titlepost").get_attribute(
                "value") == "Test"
        if "description" in fieldTested:
            assert driver.find_element_by_id("descrpost").get_attribute(
                "value") == "Frontend"
        if "link" in fieldTested:
            assert driver.find_element_by_id("linkurlpost").get_attribute(
                "value") == "http://localhost:5000/new"
    except AssertionError as e:
        teardown_db(id_channel, id_post)
        driver.close()
        assert False, str(e)
    except InvalidRequestError as e:
        teardown_db(id_channel, id_post)
        driver.close()
        assert False, "An error occurred while testing: {}".format(str(e))
    teardown_db(id_channel, id_post)
    driver.close()


@pytest.helpers.plugin.register
def test_basic_warning(client, channelName, pluginName):
    id_channel, id_post = setup_db(channelName, pluginName)
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
                         description=driver.find_element_by_id(channelName + "_descriptionpost").get_attribute("value"),
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
            "(.//*[normalize-space(text()) and normalize-space(.)='Moderate this publication'])[1]/following::div[1]").text == "Warning!: Please configure the channel first"
    except AssertionError as e:
        teardown_db(id_channel, id_post)
        driver.close()
        assert False, str(e)
    except InvalidRequestError as e:
        teardown_db(id_channel, id_post)
        driver.close()
        assert False, "An error occurred while testing: {}".format(str(e))
    teardown_db(id_channel, id_post)
    driver.close()


@pytest.helpers.plugin.register
def test_basic_publish(client, channelName, pluginName, configuration, extra):
    id_channel, id_post = setup_db(channelName, pluginName)
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
        time.sleep(0.3)
        driver.get('http://localhost:5000/')
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Channels")))
        driver.find_element_by_link_text("Channels").click()
        driver.find_element_by_link_text("Configure").click()
        for key in configuration:
            driver.find_element_by_id(key).click()
            driver.find_element_by_id(key).clear()
            driver.find_element_by_id(key).send_keys(configuration[key])
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='" + list(configuration.keys())[
                -1] + "'])[1]/following::button[1]").click()

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
        pub = Publishing(post_id=id_post, channel_id=id_channel, state=0,
                         title=driver.find_element_by_id(channelName + "_titlepost").get_attribute("value"),
                         description=driver.find_element_by_id(channelName + "_descriptionpost").get_attribute("value"),
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
        assert driver.title == 'Index - Superform', driver.title
    except AssertionError as e:
        teardown_db(id_channel, id_post)
        driver.close()
        assert False, str(e)
    except InvalidRequestError as e:
        teardown_db(id_channel, id_post)
        driver.close()
        assert False, "An error occurred while testing: {}".format(str(e))
    teardown_db(id_channel, id_post)
    driver.close()
