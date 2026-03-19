import datetime
import SlackHandler
import os
from screenshot import make_screenshot
import time
import mysqlIO
import CallbackDeque
import logging
import logging.handlers


def fetch_latest_ups_data(connector):
    result = connector.query("SELECT * FROM WV_Mar_2026.Turbo_UPS ORDER BY time DESC LIMIT 1;")
    return result[0]


def fetch_latest_pressure_data(connector):
    result = connector.query("SELECT * FROM WV_Mar_2026.pressure ORDER BY time DESC LIMIT 1;")
    return result[0]


def convert2Pa(torr):
    return float(torr) * 133.3223684211


def push_screenshot_to_slack(slack_handler: SlackHandler.SlackHandler, channel, image_path, thread_ts=None):
    return slack_handler.upload_and_send_image(channel, [image_path], titles=["Worldview Micrograms Dashboard Screenshot"], thread_ts=thread_ts)


def make_screenshot_and_push_to_slack(slack_handler: SlackHandler.SlackHandler, channel, thread_ts=None):
    screenshot_path = "Worldview_micrograms_dashboard.png"
    make_screenshot(screenshot_path)
    result = push_screenshot_to_slack(slack_handler, channel, screenshot_path, thread_ts=thread_ts)
    return result


def main():
    channel = "#worldview_slow_control"

    # logger setup
    mysql_log = logging.getLogger("mysql")
    slack_log = logging.getLogger("slack")
    main_log = logging.getLogger("main")
    handler = logging.handlers.RotatingFileHandler("osaka_micrograms_info_bot.log", maxBytes=5 * 1024 * 1024, backupCount=2)
    handler.setLevel(logging.INFO)
    handler_debug = logging.handlers.RotatingFileHandler("osaka_micrograms_debug_bot.log", maxBytes=5 * 1024 * 1024, backupCount=2)
    handler_debug.setLevel(logging.DEBUG)
    handler_terminal = logging.StreamHandler()
    handler_terminal.setLevel(logging.INFO)
    mysql_log.setLevel(logging.DEBUG)
    slack_log.setLevel(logging.DEBUG)
    main_log.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s [%(levelname)s]: %(message)s'))
    handler_debug.setFormatter(logging.Formatter('%(asctime)s - %(name)s [%(levelname)s]: %(message)s'))
    handler_terminal.setFormatter(logging.Formatter('%(asctime)s - %(name)s [%(levelname)s]: %(message)s'))
    mysql_log.addHandler(handler)
    mysql_log.addHandler(handler_debug)
    mysql_log.addHandler(handler_terminal)
    slack_log.addHandler(handler)
    slack_log.addHandler(handler_debug)
    slack_log.addHandler(handler_terminal)
    main_log.addHandler(handler)
    main_log.addHandler(handler_debug)
    main_log.addHandler(handler_terminal)

    duration_img = 60 * 60 * 2  # 2 hours
    main_log.info("Starting Osaka MicroGRAMS Slack Info Bot")
    duration_txt = 60 * 60 * 2  # 2 hours
    main_log.info(f"Text push duration set to {duration_txt} seconds")
    main_log.info(f"Image push duration set to {duration_img} seconds")
    last_img_push_time = None
    last_txt_push_time = None
    delta_time = datetime.timedelta(hours=14)
    init_ = True
    host = os.getenv("LAZYINS_HOST")
    user = os.getenv("LAZYINS_USER")
    password = os.getenv("LAZYINS_PASSWD")
    main_log.info(f"host: {host}, user: {user}")
    last_ts = None
    slack_handler = SlackHandler.SlackHandler(os.getenv("SLACK_TOKEN"), logger=slack_log)
    img_queue = CallbackDeque.CallbackDeque(maxlen=999, callback=lambda file_ids: [slack_handler.delete_img(file_id) for file_id in file_ids])
    connector1 = mysqlIO.mysqlIO(host, user, password, "", logger=mysql_log)
    while True:
        current_time = datetime.datetime.now()
        if last_txt_push_time is not None and current_time - last_txt_push_time < datetime.timedelta(seconds=duration_txt):
            time.sleep(1)
            continue
        text_title = f"Current Worldview MicroGRAMS Status ({time.strftime('%Y-%m-%d %H:%M:%S')} JST)"
        try:
            blocks = []
            block = {"type": "header", "text": {"type": "plain_text", "text": text_title}}
            blocks.append(block)
            text = ""
            pressure_data = fetch_latest_pressure_data(connector1)
            text += f"_____Pressure({pressure_data['time'] + delta_time} JST)_____"
            text += "\nPressure 1: ".ljust(12) + f"{pressure_data['PR1']:.4e}".rjust(6) + " Torr, " + f"{convert2Pa(pressure_data['PR1']):.4e}".rjust(6) + " Pa"
            text += "\nPressure 2: ".ljust(12) + f"{pressure_data['PR2']:.4e}".rjust(6) + " Torr, " + f"{convert2Pa(pressure_data['PR2']):.4e}".rjust(6) + " Pa"
            text += "\nPressure 3: ".ljust(12) + f"{pressure_data['PR3']:.4e}".rjust(6) + " Torr, " + f"{convert2Pa(pressure_data['PR3']):.4e}".rjust(6) + " Pa"
            text += "\nPressure 4: ".ljust(12) + f"{pressure_data['PR4']:.4e}".rjust(6) + " Torr, " + f"{convert2Pa(pressure_data['PR4']):.4e}".rjust(6) + " Pa"
            text += "\nPressure 5: ".ljust(12) + f"{pressure_data['PR5']:.4e}".rjust(6) + " Torr, " + f"{convert2Pa(pressure_data['PR5']):.4e}".rjust(6) + " Pa"
            text += "\n___________________________________________\n"           
            ljust_value = 32
            ups_data = fetch_latest_ups_data(connector1)
            text += f"\n______Turbo({ups_data['time'] + delta_time} JST)______"
            text += "\nActual Turbo Rotation: ".ljust(ljust_value) + f"{str(ups_data.get('ActualSpd') or '0'):>5}" + " rpm"
            text += "\nTemperature Pump Bottom Part: ".ljust(ljust_value) + f"{str(ups_data.get('TempPmpBot') or '0'):>5}" + " °C"
            text += "\nTemperature Motor: ".ljust(ljust_value) + f"{str(ups_data.get('TempMotor') or '0'):>5}" + " °C"
            text += "\nTemperature Electric: ".ljust(ljust_value) + f"{str(ups_data.get('TempElec') or '0'):>5}" + " °C"
            text += "\nTemperature Bearing: ".ljust(ljust_value) + f"{str(ups_data.get('TempBearng') or '0'):>5}" + " °C"
            text += "\n___________________________________________\n"
            block = {"type": "context", "elements": [{"type": "mrkdwn", "text": f"```{text}```"}]}
            blocks.append(block)
            if init_:
                response = slack_handler.send_message_block(channel, blocks=blocks, text=text_title + "\n" + text)
                init_ = False
                last_ts = response["ts"]
                channel = response["channel"]
                result = make_screenshot_and_push_to_slack(slack_handler, channel, thread_ts=last_ts)
                if result["ok"]:
                    file_ids = [file["id"] for file in result["files"]]
                    img_queue.append(file_ids, call_callback=True)
                last_img_push_time = current_time
                last_txt_push_time = last_img_push_time
            else:
                slack_handler.edit_message_block(channel, last_ts, blocks, text)
                last_txt_push_time = current_time
                if (current_time - last_img_push_time).total_seconds() >= duration_img:
                    result = make_screenshot_and_push_to_slack(slack_handler, channel, thread_ts=last_ts)
                    if result["ok"]:
                        file_ids = [file["id"] for file in result["files"]]
                        img_queue.append(file_ids, call_callback=True)
                    last_img_push_time = current_time
        except KeyboardInterrupt:
            break
        except Exception as e:
            last_img_push_time = datetime.datetime.now()
            main_log.error("Error occurred:", exc_info=e)
            time.sleep(5)  # wait for a minute before retrying


if __name__ == "__main__":
    main()
