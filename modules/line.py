from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import Dict

import os
import requests

load_dotenv(override=True)

@dataclass
class Line:
    headers: Dict[str, str] = field(default_factory=lambda: {
        "Authorization": "Bearer " + os.getenv("LINE_NOTIFY_TOKEN"), 
        "Content-Type" : "application/x-www-form-urlencoded"
    })
    host:str = "https://notify-api.line.me/api"

    def send_notify_message(self, msg: str):
        payload = {"message": msg}
        uri = "/notify"
        result = requests.post(f"{self.host}{uri}", headers = self.headers, params = payload)
        return result.status_code

