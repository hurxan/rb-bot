import requests
from rebelbetting.emojis import *
from dotenv import load_dotenv
import os

class TelegramBOT:

    def __init__(self):
        load_dotenv("../.env") 
        self.bot_token = os.getenv("bot_token")
        self.bot_chat_id = os.getenv("bot_chat_id")

    def telegram_bot_send_text(self, bot_message):
        send_text = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
        data = {
            'chat_id': self.bot_chat_id,
            'parse_mode': 'Markdown',
            'text': bot_message
        }
        response = requests.post(send_text, data=data)
        return response.json()

    def send_bet(self, bet_info: dict):
        if bet_info['sport'] in SPORTS.keys():
            bet_info['sport'] = f"{bet_info['sport']} {SPORTS[bet_info['sport']]}"

        if '#' in bet_info['url']:
            bet_info['url'] = bet_info['url'].replace('#', '%23')

        if '&' in bet_info['participants']:
            bet_info['participants'] = bet_info['participants'].replace('&', 'and')

        bot_message = f"*Event*: {bet_info['participants']}\n" \
                      f"*Sport*: {bet_info['sport']}\n" \
                      f"*League*: {bet_info['eventname']}\n" \
                      f"*Bet*: {bet_info['display']}\n" \
                      f"*Odds*: {bet_info['odds']}\n" \
                      f"*Stake*: {bet_info['stake']}€\n" \
                      f"*Odds type*: {bet_info['oddstype']}\n" \
                      f"*Bookmaker*: {bet_info['bookmaker']}\n" \
                      f"*Start*: {bet_info['start']}\n" \
                      f"*Link*: {bet_info['url']}"

        self.telegram_bot_send_text(bot_message=bot_message)

# Create the TelegramBOT instance with your bot_token and bot_chat_id
telegram_bot = TelegramBOT()
