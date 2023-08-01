from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import re


class ScrapRebelBetting:
    def __init__(self):
        # Initialize the webdriver with headless option
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service('/usr/local/bin/chromedriver')
        self.browser = webdriver.Chrome(service=service, options=chrome_options)
        self.browser.get("https://vb.rebelbetting.com/login")

    def close_browser(self):
        self.browser.quit()

    def find_element(self, by: By, value: str):
        return self.browser.find_element(by=by, value=value)

    def add_input(self, by: By, value: str, text: str):
        field = self.find_element(by=by, value=value)
        field.send_keys(text)
        time.sleep(1)

    def click_button(self, by: By, value: str):
        button = self.find_element(by=by, value=value)
        button.click()
        time.sleep(1)

    def login(self, username: str, password: str):
        self.add_input(by=By.ID, value='inputEmail', text=username)
        self.add_input(by=By.ID, value='inputPassword', text=password)
        self.click_button(by=By.CLASS_NAME, value='mt-3.btn.btn-primary.mw-7rem')

    def get_all_bets_ids(self) -> list:
        source_code = self.browser.page_source
        bets_ids = []

        bets_ids_idx = [m.start() for m in re.finditer('OddsID', source_code)]
        for div in bets_ids_idx:
            bet_id = source_code[div:div + source_code[div:].find(" ") - 1]
            if not self.is_premium_bet(bet_id):
                continue
            bets_ids.append(bet_id)

        return bets_ids

    def is_premium_bet(self, bet_id: str) -> bool:
        try:
            message = self.find_element(by=By.ID, value=bet_id).accessible_name
            return "You're missing out" not in message
        except:
            return False

    def get_bet_info(self, bet_id: str) -> dict:
        info = {}

        # Open Bet window
        field = self.find_element(by=By.ID, value=bet_id)
        # Scroll down
        self.browser.execute_script(f"window.scrollTo(0, {field.location['y']})")

        WebDriverWait(self.browser, 100).until(EC.element_to_be_clickable((By.ID, bet_id)))

        self.browser.execute_script("arguments[0].click();", field)
        time.sleep(1)

        # Get bet info
        info['Value'] = self.find_element(by=By.ID, value='Value').text
        info['display'] = self.find_element(by=By.ID, value='display').text
        info['participants'] = self.find_element(by=By.ID, value='participants').text
        info['oddstype'] = self.find_element(by=By.ID, value='oddstype').text
        info['eventname'] = self.find_element(by=By.ID, value='eventname').text
        info['sport'] = self.find_element(by=By.ID, value='sport').text
        info['start'] = self.find_element(by=By.ID, value='start').text
        info['bookmaker'] = self.find_element(by=By.ID, value='bookmaker').text
        info['url'] = self.find_element(by=By.ID, value='BetOnBookmaker').get_attribute('href')
        info['odds'] = self.find_element(by=By.ID, value='Odds').get_attribute('value')
        info['stake'] = self.find_element(by=By.ID, value='Stake').get_attribute('value')

        self.click_button(by=By.ID, value='CloseSelectedCard')

        return info

    def check_connection(self):
        source_code = self.browser.page_source

        if "Click here to try and reconnect." in source_code:
            print("Disconnected")

            self.click_button(by=By.CLASS_NAME, value='badge.text-bg-danger.m-2.p-2.clickable')

            time.sleep(3)

            source_code = self.browser.page_source
            if "Click here to try and reconnect." in source_code:
                raise Exception("Failed to reconnect")
            else:
                print("Reconnected")

    @staticmethod
    def filter_per_date(bet_info) -> bool:
        start_in = bet_info['start']
        if 'minutes' in start_in or 'seconds' in start_in:
            return True
        elif 'hours' in start_in:
            nb_hours = int(start_in.split()[2])
            if nb_hours <= 4:
                return True
        return False

    def close_ad(self):
        try:
            self.browser.switch_to.frame(0)
            self.find_element(by=By.ID, value="Rectangle-4-copy").click()
        except:
            # No iFrame => no ad
            return None

