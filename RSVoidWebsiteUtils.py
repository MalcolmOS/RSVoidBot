import requests
import Utils
import Driver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import bs4 as bs

BOT_LOGIN = ''
BOT_PASSWORD = ''


RANKS = {'Admin': 'admin.gif', 'Head Staff': 'head-staff.gif', 'Staff': 'Staff.gif', 'Scripter': 'scripter.png', '$250 Donor': '250donor.gif', '$150 Donor': '150donor.gif', '$100 Donor': '100donor.gif',
         '$50 Donor': '50donor.gif', '$25 Donor': '25donor.gif', '$15 Donor': '15donor.gif', 'Sponsor': 'Sponsor.gif', 'GFX Designer': 'GFX-Designer.png', 'Advanced Member': 'advanced.png',
         'OG Member': 'OG-Member',  'Member': 'member.png.c5',  'New Member': 'new-member.png'}

ROLES = {'Scripter': 721149870680965122, '$250 Donor': 721149557609857085, '$150 Donor': 724310849929609227,
         '$100 Donor': 721149684986675291, '$50 Donor': 723966588394537031, '$25 Donor': 722586346069164162, '$15 Donor': 721149825785266197, 'Sponsor': 716736124562964570,
         'GFX Designer': 721149950045454337, 'Advanced Member': 721150009726205982, 'OG Member': 723722015755731045,  'Member': 721150054211256382,  'New Member': 721150090609295420}


def get_user_url_from_message(message):
    splits = message.split(' ')
    if len(splits) > 1 and 'https://www.rsvoid.com/profile/' in splits[1]:
        return splits[1]


def get_user_name_from_url(url):
    splits = url.split('/')
    if len(splits) > 3:
        user = splits[4]
        user_id = user.split('-')[0]
        user_name = user.replace('-', ' ').replace(user_id, '')
        return user_name.title()


def get_user_id_from_url(url):
    splits = url.split('/')
    if len(splits) > 3:
        user = splits[4]
        return user.split('-')[0]


def get_user_roles(url):
    Utils.log(f'Grabbing user roles for {url}')
    r = requests.get(url)
    roles = ''
    source = r.text
    for role in RANKS.keys():
        if RANKS.get(role) in source:
            Utils.log(f'Found {role}')
            roles += f'{role}\n'
    return roles


def get_user_feedback_score(url):
    Utils.log(f"Accessing {url} to get feedback score")
    r = requests.get(f'{url}?tab=node_feedback_Feedback')
    source = r.text
    soup = bs.BeautifulSoup(source, 'lxml')
    feedback = soup.find("div", {"class": "cProfileFeedbackScore"}).text.replace(' ', '').split("\n")
    return {"Positive": feedback[1], "Neutral": feedback[2], "Negative": feedback[3]}


def get_recent_feedback(url):
    Utils.log(f"Accessing {url} to get recent feedback")
    r = requests.get(f'{url}?tab=node_feedback_Feedback')
    source = r.text
    soup = bs.BeautifulSoup(source, 'lxml')
    all_feedback = soup.find_all("li", {"class": "ipsDataItem"})
    feedback_return = ''
    i = 1
    for feedback in all_feedback:
        content = feedback.text.split("\n")
        if len(content) > 20:
            fb_type = content[11].replace("\r", "").replace(' for a topic', '')
            feedback_return += f'```\n{fb_type}\n{content[19]}\n{content[20]}\n```'
            i += 1
            if i == 5:
                return feedback_return
    return feedback_return


def get_user_rep(url):
    Utils.log(f"Accessing {url} to get reputation")
    r = requests.get(url)
    source = r.text
    soup = bs.BeautifulSoup(source, 'lxml')
    rep_count = soup.find("span", {"class": "cProfileRepScore_points"}).text
    rep_title = soup.find("span", {"class": "cProfileRepScore_title"}).text
    return {"Score": rep_count, "Title": rep_title}


class SendTokenEvent:
    def __init__(self, user, token):
        self.user = user
        self.token = token

    def run(self):
        driver = Driver.get_driver()
        try:
            LoginEvent(driver=driver).run()
            user_id = get_user_id_from_url(url=self.user)
            driver.get(f'https://www.rsvoid.com/messenger/compose/?to={user_id}')
            time.sleep(10)
            SendMessageEvent(driver=driver, token=self.token).run()
            driver.quit()
            return 200
        except Exception as e:
            print(e)
            driver.quit()
            return e


class LoginEvent:
    def __init__(self, driver):
        Utils.log('Loading Login Event...')
        self.driver = driver

    def run(self):
        self.driver.get('https://www.rsvoid.com/login/')
        Utils.log("Opening RSVoid")
        time.sleep(10)

        if Driver.element_exists_by_id(self.driver, 'auth') and Driver.element_exists_by_id(self.driver, 'password'):
            self.driver.find_element_by_id('auth').send_keys(BOT_LOGIN)
            self.driver.find_element_by_id('password').send_keys(BOT_PASSWORD)
            self.driver.find_element_by_id('password').send_keys(Keys.RETURN)
            Utils.log("Logging into RSVoid")
            time.sleep(10)
        else:
            raise Exception("Error logging into RSVoid - elements do not exist.")


class SendMessageEvent:
    def __init__(self, driver, token):
        Utils.log('Loading Send Token Event...')
        self.driver = driver
        self.token = token

    def run(self):
        if Driver.element_exists_by_id(self.driver, 'elInput_messenger_title'):
            self.send_token()
        else:
            raise Exception('error finding message box')

    def send_token(self):
        element = self.driver.find_element_by_id('elInput_messenger_title')
        element.send_keys('Your Token')
        time.sleep(2)
        if Driver.element_exists_by_xpath(self.driver, '//*[@id="cke_1_contents"]/div'):
            self.driver.find_element_by_xpath('//*[@id="cke_1_contents"]/div').click()
            time.sleep(1)
            ac = ActionChains(driver=self.driver)
            ac.send_keys(self.token)
            ac.perform()
            time.sleep(2)
        else:
            raise Exception('error finding message box on message instance')
        if Driver.element_exists_by_xpath(self.driver, '//*[@id="ipsLayout_mainArea"]/form/ul/li/button'):
            self.driver.execute_script("window.scrollTo(0, 100000)")
            time.sleep(2)
            self.driver.find_element_by_xpath('//*[@id="ipsLayout_mainArea"]/form/ul/li/button').click()
            time.sleep(10)
        else:
            raise Exception('error finding message button on message instance')



