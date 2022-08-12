import asyncio
import logging
import os
import re
from dataclasses import dataclass
from io import BytesIO

import dotenv
import pytesseract
import requests
from PIL import Image
from requests import models as resp_models

from .line import Line

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)


CAPTCHA_URI = "NewCaptcha.aspx"

PLACE_VARIABLES = {
    "三重": {
        "english_name": "SanChong",
        "host_url": "https://fe.xuanen.com.tw",
        "place_uri": "fe01.aspx",
    },
    "中正": {
        "english_name": "JhongJheng",
        "host_url": "https://www.cjcf.com.tw",
        "place_uri": "jj01.aspx",
    },
    "南港": {
        "english_name": "NanGang",
        "host_url": "https://scr.cyc.org.tw",
        "place_uri": "tp02.aspx",
    },
    "土城": {
        "english_name": "TuCheng",
        "host_url": "https://scr.cyc.org.tw",
        "place_uri": "tp08.aspx",
    },
    "士林": {
        "english_name": "ShiLin",
        "host_url": "https://www.ymca.com.tw",
        "place_uri": "slsc68.aspx",
    },
    "大同": {
        "english_name": "DaTong",
        "host_url": "https://bwd.xuanen.com.tw",
        "place_uri": "wd02.aspx",
    },
    "板橋": {
        "english_name": "Banqiao",
        "host_url": "https://www.cjcf.com.tw",
        "place_uri": "CG01.aspx",
    },
    "永和": {
        "english_name": "YongHe",
        "host_url": "https://scr.cyc.org.tw",
        "place_uri": "tp10.aspx",
    },
}

APPOINT_RETRY_INTERVAL_SECONDS = float(os.getenv("APPOINT_RETRY_INTERVAL_SECONDS"))


@dataclass
class WebPlatform:

    place: str
    appoint_retry_interval_seconds: float = float(
        os.getenv("APPOINT_RETRY_INTERVAL_SECONDS")
    )
    asp_session_id: str = None
    captcha_number: str = None
    captcha_url: str = None
    host_url: str = None
    line_object: object = Line()
    login_id: str = os.getenv("ACCOUNT_ID")
    login_pwd: str = os.getenv("ACCOUNT_PASSWORD")
    login_retry_times: int = int(os.getenv("LOGIN_RETRY_TIMES"))

    def __post_init__(self):
        self.captcha_url = f"{PLACE_VARIABLES[self.place]['host_url']}/{CAPTCHA_URI}"
        self.host_url = f"{PLACE_VARIABLES[self.place]['host_url']}/{PLACE_VARIABLES[self.place]['place_uri']}"
        logging.info(f"Starting with the {self.place} platform")

    def _get_captcha_image(self) -> resp_models.Response:
        return requests.request("GET", self.captcha_url)

    def _set_captcha_number(self, response: resp_models.Response) -> bool:
        captcha_image = Image.open(BytesIO(response.content))
        custom_config = r"--oem 3 --psm 6 outputbase digits"
        image_string = pytesseract.image_to_string(captcha_image, config=custom_config)
        regex_captcha_number = re.findall("\\d+", image_string)

        if not regex_captcha_number:
            logging.error("Can not find regex_captcha_number")
            return False

        self.captcha_number = regex_captcha_number[0]

        if len(self.captcha_number) < 5:
            logging.error(
                f"The length of captcha_number({self.captcha_number}) is less than 5"
            )
            return False

        logging.info(f"Get the captcha number: {self.captcha_number}")
        return True

    def _set_asp_session_id(self, response: resp_models.Response) -> bool:
        try:
            self.asp_session_id = response.headers["Set-Cookie"]
            logging.info(f"Get the asp session ID: {self.asp_session_id}")
            return True
        except KeyError:
            logging.error("There was no Set-Cookie header")
            return False

    def set_existing_asp_session_id(self):
        self.asp_session_id = os.getenv(
            f"ASP_SESSION_ID_{PLACE_VARIABLES[self.place]['english_name'].upper()}",
            None,
        )

        if not self.asp_session_id:
            logging.info(
                "There is no exist asp session id. Let's login to setup a new session"
            )
            self.get_valid_asp_session_id()

        logging.info(f"The asp session ID is: {self.asp_session_id}")

    def _login_to_platform(self) -> resp_models.Response:
        login_url = f"{self.host_url}?Module=login_page&files=login"

        payload = {
            "loginid": self.login_id,
            "loginpw": self.login_pwd,
            "Captcha_text": self.captcha_number,
        }

        headers = {
            "Cookie": self.asp_session_id,
        }

        response = requests.request("POST", login_url, data=payload, headers=headers)

        return response

    def _check_login_is_success(self, response: resp_models.Response) -> bool:
        if response.text.find("驗證碼錯誤") != -1:
            logging.error("Get error: 驗證碼錯誤 when login")
            return False

        return True

    def get_valid_asp_session_id(self):
        is_login_success = False
        logging.info(f"Start to login to {self.place} platform")

        for _ in range(self.login_retry_times):
            captcha_response = self._get_captcha_image()
            if not self._set_captcha_number(captcha_response):
                continue
            if not self._set_asp_session_id(captcha_response):
                continue

            login_response = self._login_to_platform()
            if not self._check_login_is_success(login_response):
                continue

            is_login_success = True
            break

        if not is_login_success:
            self.line_object.send_notify_message(
                f"Login for {self.login_retry_times} times but still failed"
            )
            raise TimeoutError(
                f"Login for {self.login_retry_times} times but still failed"
            )

        self.store_asp_session_id_to_env_file()
        logging.info("Login Successful!")

    def store_asp_session_id_to_env_file(self):
        dotenv.set_key(
            dotenv_file,
            f"ASP_SESSION_ID_{PLACE_VARIABLES[self.place]['english_name'].upper()}",
            self.asp_session_id,
        )

    def _get_appointment_response(self, date: str, start_time: str, venue: str):
        # appoint_url = f"{self.host_url}?module=net_booking&files=booking_place&StepFlag=25&QPid=87&QTime=16&PT=1&D=2022/07/16"
        appoint_url = f"{self.host_url}?module=net_booking&files=booking_place&StepFlag=25&QPid={venue}&QTime={start_time}&PT=1&D={date}"

        headers = {
            "cookie": self.asp_session_id,
        }

        response = requests.request("GET", appoint_url, headers=headers)

        return response

    def _check_appointment_is_success(self, response: resp_models.Response) -> bool:
        success_keyword = "CG01.aspx?module=net_booking&files=booking_place&X=1"
        if response.text.find(success_keyword) == -1:
            return False

        return True

    async def appoint_with_specific_place_and_time(
        self, date: str, start_time: str, venue: str, num: int
    ):
        await asyncio.sleep(num * APPOINT_RETRY_INTERVAL_SECONDS)
        logging.info(f"Start to appoint with {self.place} platform {venue}")

        appoint_response = self._get_appointment_response(date, start_time, venue)
        if not self._check_appointment_is_success(appoint_response):
            self.line_object.send_notify_message(
                f"Appoint {self.place} {venue} in {date} {start_time}:00 but failed"
            )
            return

        self.line_object.send_notify_message(
            f"Appoint {self.place} {venue} in {date} {start_time}:00 Success!"
        )

        logging.info("Appointment Successful!")
