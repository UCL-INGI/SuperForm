import datetime
import time
from selenium import webdriver
from selenium.webdriver.support.select import Select


channel_name = "A-beautiful-channel-name"
channel_server_fqdn = "0.0.0.0:8000"
channel_ictv_id = "1"
channel_api_key = "azertyuiop"

post_title = "A nice post title"
post_description = "A huuuuge description, because we love it this way"
post_publication_date = datetime.date.today()
post_publication_until = datetime.date.today() + datetime.timedelta(1)
ictv_template = "text-image"

comfort_delay = 0.5
waiting_delay = 1


def test_selenium_open_superform(driver):
    try:
        driver.get("https://127.0.0.1:5000")
        assert "Superform" in driver.title
    except:
        driver.get("http://127.0.0.1:5000")
        assert "Superform" in driver.title


def test_selenium_auth(driver):
    login_link = driver.find_element_by_link_text('Login')
    assert login_link
    login_link.click()
    assert "TestShib Identity Provider Login" in driver.title
    username_field = driver.find_element_by_name("j_username")
    username_field.send_keys("myself")
    time.sleep(comfort_delay)
    password_field = driver.find_element_by_name("j_password")
    password_field.send_keys("myself")
    time.sleep(comfort_delay)
    submit_button = driver.find_element_by_xpath("//input[@value='Login']")
    submit_button.click()
    time.sleep(waiting_delay)
    assert "Index - Superform" in driver.title


def test_selenium_new_ictv_channel(driver):
    channels_link = driver.find_element_by_link_text('Channels')
    assert channels_link
    channels_link.click()
    channel_name_field = driver.find_element_by_xpath("//input[@id='inlineFormInputText']")
    assert channel_name_field
    channel_name_field.send_keys(channel_name)
    time.sleep(comfort_delay)
    channel_module_select = Select(driver.find_element_by_xpath("//select[@id='inlineFormCustomSelectModule']"))
    assert channel_module_select
    channel_module_select.select_by_value("ictv")
    time.sleep(comfort_delay)
    submit_button = driver.find_element_by_class_name("fa-plus")
    assert submit_button
    submit_button.click()
    time.sleep(comfort_delay)


def test_selenium_conf_ictv_channel(driver):
    channels = driver.find_elements_by_link_text('Configure')
    assert channels
    channel = channels[len(channels) - 1]
    channel.click()
    time.sleep(waiting_delay)
    channel_server_field = driver.find_element_by_name("ictv_server_fqdn")
    assert channel_server_field
    channel_server_field.clear()
    channel_server_field.send_keys(channel_server_fqdn)
    time.sleep(comfort_delay)
    channel_id_field = driver.find_element_by_name("ictv_channel_id")
    assert channel_id_field
    channel_id_field.clear()
    channel_id_field.send_keys(channel_ictv_id)
    time.sleep(comfort_delay)
    channel_api_field = driver.find_element_by_name("ictv_api_key")
    assert channel_api_field
    channel_api_field.clear()
    channel_api_field.send_keys(channel_api_key)
    time.sleep(comfort_delay)
    save_button = driver.find_element_by_xpath("//button[text()='Save Configuration']")
    assert save_button
    save_button.click()
    time.sleep(comfort_delay)


def test_selenium_add_moderator(driver):
    authorizations_link = driver.find_element_by_link_text('Authorizations')
    assert authorizations_link
    authorizations_link.click()
    time.sleep(waiting_delay)
    expands = driver.find_elements_by_xpath("//button[@aria-controls='collapseOne']")
    expand = expands[-1]
    assert expand
    expand.click()
    username_fields = driver.find_elements_by_xpath("//input[@placeholder='Username']")
    username_field = username_fields[-1]
    assert username_field
    username_field.clear()
    username_field.send_keys("myself")
    time.sleep(comfort_delay)
    auth_select = Select(driver.find_elements_by_xpath("//select[@id='sel1']")[-1])
    assert auth_select
    auth_select.select_by_value("2")
    time.sleep(comfort_delay)
    add_buttons = driver.find_elements_by_link_text("Add")
    add_button = add_buttons[-1]
    assert add_button
    add_button.click()
    time.sleep(comfort_delay)
    update_button = driver.find_element_by_xpath("//button[text()='Update']")
    update_button.click()
    time.sleep(comfort_delay)


def test_selenium_new_post_ictv(driver):
    new_link = driver.find_element_by_link_text('New post')
    assert new_link
    new_link.click()
    time.sleep(waiting_delay)
    title_field = driver.find_element_by_xpath("//input[@id='titlepost']")
    assert title_field
    title_field.send_keys(post_title)
    time.sleep(comfort_delay)
    description_field = driver.find_element_by_xpath("//textarea[@id='descriptionpost']")
    assert description_field
    description_field.send_keys(post_description)
    time.sleep(comfort_delay)
    date_from_field = driver.find_element_by_xpath("//input[@id='datefrompost']")
    assert date_from_field
    date_from_field.send_keys(datetime.datetime.strftime(post_publication_date, "%Y-%m-%d"))
    time.sleep(comfort_delay)
    date_until_field = driver.find_element_by_xpath("//input[@id='dateuntilpost']")
    assert date_until_field
    date_until_field.send_keys(datetime.datetime.strftime(post_publication_until, "%Y-%m-%d"))
    time.sleep(comfort_delay)
    ictv_channel_check = driver.find_element_by_xpath("//input[@data-namechan='" + channel_name + "']")
    assert ictv_channel_check
    ictv_channel_check.click()
    time.sleep(comfort_delay)
    ictv_channel_tab = driver.find_element_by_link_text(channel_name)
    assert ictv_channel_tab
    ictv_channel_tab.click()
    time.sleep(comfort_delay)
    ictv_slide_type_select = Select(driver.find_element_by_id(channel_name + "_slide-selector"))
    assert ictv_slide_type_select
    ictv_slide_type_select.select_by_value(ictv_template)
    time.sleep(comfort_delay)
    ictv_input_1 = driver.find_element_by_id(channel_name + '_data_' + ictv_template + '_logo-1')
    assert ictv_input_1
    ictv_input_1.send_keys("http://thecatapi.com/api/images/get")
    time.sleep(comfort_delay)
    ictv_input_2 = driver.find_element_by_id(channel_name + '_data_' + ictv_template + '_logo-2')
    assert ictv_input_2
    ictv_input_2.send_keys("http://thecatapi.com/api/images/get")
    time.sleep(comfort_delay)
    ictv_input_3 = driver.find_element_by_id(channel_name + '_data_' + ictv_template + '_image-1')
    assert ictv_input_3
    ictv_input_3.send_keys("http://thecatapi.com/api/images/get")
    time.sleep(comfort_delay)
    publish_button = driver.find_element_by_id("publish-button")
    assert publish_button
    publish_button.click()
    time.sleep(comfort_delay)


def test_selenium_moderate_publishing(driver):
    unmoderated_link = driver.find_element_by_link_text('Unmoderated publishings')
    assert unmoderated_link
    unmoderated_link.click()
    time.sleep(waiting_delay)
    moderate_button = driver.find_element_by_link_text('Moderate')
    assert moderate_button
    moderate_button.click()
    time.sleep(waiting_delay)
    submit_button = driver.find_element_by_xpath('//button[text()="Publish"]')
    assert submit_button
    submit_button.click()
    time.sleep(comfort_delay)


def test_selenium_view_publishing(driver):
    my_pub_link = driver.find_element_by_link_text('My publishings')
    assert my_pub_link
    my_pub_link.click()
    time.sleep(comfort_delay)
    acc_pub_link = driver.find_element_by_link_text('Accepted publishings')
    assert acc_pub_link
    acc_pub_link.click()
    time.sleep(waiting_delay)
    assert driver.page_source.__contains__(post_title)
    detail_button = driver.find_element_by_link_text('View feedback')
    assert detail_button
    detail_button.click()
    time.sleep(waiting_delay)
    detail_title = driver.find_element_by_xpath('//input[@id="titlepost"]')
    assert detail_title
    assert driver.page_source.__contains__(post_title)
    time.sleep(comfort_delay)


def test_selenium_delete_channel(driver):
    channels_link = driver.find_element_by_link_text('Channels')
    assert channels_link
    channels_link.click()
    time.sleep(waiting_delay)
    delete_buttons = driver.find_elements_by_class_name("fa-trash")
    delete_button = delete_buttons[-1]
    assert delete_button
    delete_button.click()
    time.sleep(comfort_delay)
    confirm_delete_button = driver.find_element_by_xpath("//button[text()='Delete']")
    assert confirm_delete_button
    confirm_delete_button.click()
    time.sleep(comfort_delay)


def test_selenium_logout(driver):
    user_link = driver.find_element_by_link_text('Me Myself And I')
    assert user_link
    user_link.click()
    time.sleep(comfort_delay)
    logout_link = driver.find_element_by_link_text('Logout')
    assert logout_link
    logout_link.click()
    time.sleep(comfort_delay)
    assert "You are not logged in." in driver.page_source


driver = webdriver.Firefox()
test_selenium_open_superform(driver)
test_selenium_auth(driver)
test_selenium_new_ictv_channel(driver)
test_selenium_conf_ictv_channel(driver)
test_selenium_add_moderator(driver)
test_selenium_new_post_ictv(driver)
test_selenium_moderate_publishing(driver)
test_selenium_view_publishing(driver)
test_selenium_delete_channel(driver)
test_selenium_logout(driver)
driver.close()

