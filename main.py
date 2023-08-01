from rebelbetting.stream_website import ScrapRebelBetting
from rebelbetting.telegram_group import TelegramBOT
import time
import traceback
import os
from dotenv import load_dotenv

if __name__ == '__main__':

    load_dotenv(".env")
    username = os.getenv("username")
    password = os.getenv("password")

    sent_bets = []
    while True:
        try:
            rebel_website = ScrapRebelBetting()
            telegram_bot = TelegramBOT()
            last_time_bet_detected = time.time()

            time.sleep(1)

            print("Connecting to rebelbetting.com")
            rebel_website.login(username=username,
                                password=password)
            print("Connected\nStreaming for new bets")
            time.sleep(1)

            bets_ids = rebel_website.get_all_bets_ids()

            while True:
                time.sleep(10)

                if time.time() - last_time_bet_detected > 600:
                    raise Exception("No detection for 10min")
                
                rebel_website.check_connection()
                rebel_website.close_ad()
                new_ids = rebel_website.get_all_bets_ids()

                for bet_id in new_ids:
                    if (not bet_id in bets_ids) and (not bet_id in sent_bets):
                        last_time_bet_detected = time.time()
                        print("New bet:")
                        bet_info = rebel_website.get_bet_info(bet_id=bet_id)
                        print(bet_info)
                        telegram_bot.send_bet(bet_info=bet_info)
                        sent_bets.append(bet_id)
                        sent_bets = sent_bets[-1000:]
                bets_ids = new_ids

        except Exception as e:
            traceback.print_exc()
            print(f"Bot will restart in 2 seconds")
            time.sleep(2)