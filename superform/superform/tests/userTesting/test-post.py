from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import random
import string
import time
import unittest
import datetime

class Post(unittest.TestCase):

    r = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=16))

    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_3_edit(self):
        driver = self.driver
        driver.get("https://127.0.0.1:5000/login")

        try:
            WebDriverWait(driver, 1).until(EC.title_contains("TestShib"))
            driver.find_element(By.NAME, "j_username").send_keys("myself")
            pwd = driver.find_element(By.NAME, "j_password")
            pwd.send_keys("myself")
            pwd.submit()
        except:
            driver.get("https://127.0.0.1:5000/login?name=myself")

        rTitle = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=16))
        rDesc = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=50))

        driver.find_element(By.LINK_TEXT, "Edit").click()
        title = driver.find_element(By.NAME, "titlepost")
        title.send_keys(Keys.CONTROL + "a")
        title.send_keys(Keys.DELETE)
        title.send_keys(rTitle)

        desc = driver.find_element(By.NAME, "descriptionpost")
        desc.send_keys(Keys.CONTROL + "a")
        desc.send_keys(Keys.DELETE)
        desc.send_keys(rDesc)
        desc.submit()

        driver.find_element(By.LINK_TEXT, "Edit").click()
        tit = driver.find_element(By.XPATH, '//*[@id="titlepost"]')
        assert tit.get_attribute('value') == rTitle

        des = driver.find_element(By.NAME, "descriptionpost")
        assert des.text == rDesc

    def test_1_new_post_linkedin_facebook(self):
        driver = self.driver

        driver.get("https://127.0.0.1:5000/login")

        try:
            WebDriverWait(driver, 1).until(EC.title_contains("TestShib"))
            driver.find_element(By.NAME, "j_username").send_keys("myself")
            pwd = driver.find_element(By.NAME, "j_password")
            pwd.send_keys("myself")
            pwd.submit()
        except:
            driver.get("https://127.0.0.1:5000/login?name=myself")

        now = datetime.datetime.now()
        driver.get("https://127.0.0.1:5000/new")
        WebDriverWait(driver, 2).until(EC.title_contains("New"))
        driver.find_element(By.NAME, "titlepost").send_keys("this is a random text: " + self.r)
        driver.find_element(By.NAME, "descriptionpost").send_keys("this is a random text: " + self.r)
        driver.find_element(By.NAME, "linkurlpost").send_keys("https://www.seleniumhq.org")
        driver.find_element(By.NAME, "datefrompost").send_keys(now.strftime("%m%d%Y"))
        driver.find_element(By.NAME, "dateuntilpost").send_keys(now.strftime("%m%d%Y"))
        driver.find_element(By.XPATH, "//*[@id='home']/div/div[2]/div[1]/div/label/input").click()
        driver.find_element(By.XPATH, "//*[@id='home']/div/div[2]/div[1]/div[2]/label/input").click()
        driver.find_element(By.ID, "publish-button").click()
        WebDriverWait(driver, 2).until(EC.title_contains("Index"))

    def test_2_publish(self):
        driver = self.driver
        driver.get("https://127.0.0.1:5000/login")
        try:
            WebDriverWait(driver, 1).until(EC.title_contains("TestShib"))
            driver.find_element(By.NAME, "j_username").send_keys("alterego")
            pwd = driver.find_element(By.NAME, "j_password")
            pwd.send_keys("myself")
            pwd.submit()
        except:
            driver.get("https://127.0.0.1:5000/login?name=alterego")

        driver.find_element(By.LINK_TEXT, "Moderate").click()
        driver.find_element(By.ID, "publish-button").click()
        WebDriverWait(driver, 2).until(EC.title_contains("Index"))

        driver.find_element(By.LINK_TEXT, "Moderate").click()
        driver.find_element(By.ID, "publish-button").click()
        WebDriverWait(driver, 2).until(EC.title_contains("Index"))

        self.check_linkedin(self.r)
        self.check_facebook(self.r)


    def check_linkedin(self, text):
        driver = self.driver
        # Open linked in
        driver.get("https://www.linkedin.com/")
        if EC.title_contains("Logg In"):
            driver.find_element(By.NAME, "session_key").send_keys("spam001@hotmail.be")
            pwd = driver.find_element(By.NAME, "session_password")
            pwd.send_keys("test1234")
            pwd.submit()

        driver.get("https://www.linkedin.com/company/12654611/admin/")

        try:
            # driver.find_elements_by_xpath("//*[contains(text(), "+text+")]")
            WebDriverWait(driver, 5).until(
                EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "this is a random text:"))
        except:
            assert False

    def check_facebook(self, text):
        driver = self.driver
        driver.get("https://www.facebook.com/")
        driver.find_element(By.NAME, "email").send_keys("superform@moff.be")
        pwd = driver.find_element(By.NAME, "pass")
        pwd.send_keys("testsuperform")
        pwd.submit()
        driver.get("https://www.facebook.com/Testsuperform-1625488667557071/?notif_id=1544184537965808&notif_t=page_admin")

        try:
            #driver.find_elements_by_xpath("//*[contains(text(), " + text + ")]")
            WebDriverWait(driver, 5).until(
                EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "this is a random text:"))
        except:
            assert False

    def test_configure_fb(self):
        driver = self.driver

        driver.get("https://www.facebook.com")

        WebDriverWait(driver, 1).until(EC.title_contains("Facebook"))
        driver.find_element(By.NAME, "email").send_keys("superform@moff.be")
        pwd = driver.find_element(By.NAME, "pass")
        pwd.send_keys("testsuperform")
        pwd.submit()

        driver.get("https://127.0.0.1:5000/login")

        try:
            WebDriverWait(driver, 1).until(EC.title_contains("TestShib"))
            driver.find_element(By.NAME, "j_username").send_keys("myself")
            pwd = driver.find_element(By.NAME, "j_password")
            pwd.send_keys("myself")
            pwd.submit()
        except:
            driver.get("https://127.0.0.1:5000/login?name=myself")

        driver.get("https://127.0.0.1:5000/channels")

        driver.find_element(By.XPATH, "/html/body/div/table/tbody//tr[contains(.,'facebook')]/td[3]/div/a").click()
        prevAT = driver.find_element(By.NAME, 'access_token').get_attribute('value')
        driver.find_element(By.LINK_TEXT, "Get Access-Token").click()
        assert prevAT != driver.find_element(By.NAME, 'access_token').get_attribute('value')
        driver.find_element(By.XPATH, "/html/body/div/form/button").click()

    def test_configure_li(self):
        driver = self.driver

        driver.get("https://www.linkedin.com/")
        if EC.title_contains("Logg In"):
            driver.find_element(By.NAME, "session_key").send_keys("spam001@hotmail.be")
            pwd = driver.find_element(By.NAME, "session_password")
            pwd.send_keys("test1234")
            pwd.submit()

        driver.get("https://127.0.0.1:5000/login")

        try:
            WebDriverWait(driver, 1).until(EC.title_contains("TestShib"))
            driver.find_element(By.NAME, "j_username").send_keys("myself")
            pwd = driver.find_element(By.NAME, "j_password")
            pwd.send_keys("myself")
            pwd.submit()
        except:
            driver.get("https://127.0.0.1:5000/login?name=myself")

        driver.get("https://127.0.0.1:5000/channels")

        driver.find_element(By.XPATH, "/html/body/div/table/tbody//tr[contains(.,'linkedin')]/td[3]/div/a").click()
        prevAT = driver.find_element(By.NAME, 'access_token').get_attribute('value')
        driver.find_element(By.LINK_TEXT, "Get Access-Token").click()
        assert prevAT != driver.find_element(By.NAME, 'access_token').get_attribute('value')
        driver.find_element(By.XPATH, "/html/body/div/form/button").click()

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":

    unittest.main()


