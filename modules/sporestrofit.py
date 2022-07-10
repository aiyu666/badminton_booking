import json
import logging
import os
import urllib
from dataclasses import dataclass

import requests
from dotenv import load_dotenv

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)


@dataclass
class Sporestrofit:
    host: str = "http://app.sporetrofit.com:8080"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "tp-stage/2.0.10 (com.fit-foxconn.TPSportsCenter; build:1; iOS 15.5.0) Alamofire/2.0.10",
    }
    temp_ID: str = os.getenv("TP_TEMP_ID")
    UPID: str = os.getenv("TP_UPID")
    COID: str = "TP"
    category_ID: str = "Badminton"
    UUID: str = os.getenv("TP_UUID")
    type_ID: str = "ios"
    lang: str = "zh-Hant-TW"

    def _query(self, payload: dict) -> dict:
        uri = "/ws_lohas/service.asmx/EntryPoint"
        payload = urllib.parse.urlencode(payload)
        response = requests.request(
            "POST", f"{self.host}{uri}", data=payload, headers=self.headers
        )
        if response.status_code == 200:
            return self.__get_response_content(response)
        logging.error(
            f"Query all failed status is not 200,\nstatus_code = {response.status_code}, \nresponse: {response.text}"
        )
        raise

    def __get_response_content(self, response: dict) -> dict:
        prefix_split_str = '<string xmlns="http://tempuri.org/">'
        surfix_split_str = "</string>"
        return json.loads(
            response.text.split(prefix_split_str)[1].split(surfix_split_str)[0]
        )

    def _get_data_row(self, contents: dict) -> list:
        return contents["Data"]["ResultData"]["AvailableData"]["DataTable"]["DataRow"]

    def get_location_available_data(self, LID_key: str, use_date: str) -> list:
        service_name = "getResLocationAvailableData"
        payload = {
            "inputJSONStr": {
                "Data": {
                    "serviceName": service_name,
                    "RequestData": {
                        "UUID": self.UUID,
                        "typeID": self.type_ID,
                        "TempID": self.temp_ID,
                        "LIDKey": LID_key,
                        "UseDate": use_date,
                        "COID": self.COID,
                        "UPID": self.UPID,
                        "Lang": self.lang,
                    },
                }
            }
        }
        response = self._query(payload)
        data_row = self._get_data_row(response)
        return self._filter_available_date(data_row)

    def _filter_available_date(self, data: dict) -> list:
        return list(filter(lambda data: data["allowBooking"] == "Y", data))

    def get_location_query_data(
        self, start_date, end_date, start_time, end_time
    ) -> dict:
        service_name = "getLocationQueryData"
        payload = {
            "inputJSONStr": {
                "Data": {
                    "serviceName": service_name,
                    "RequestData": {
                        "UUID": self.UUID,
                        "typeID": self.type_ID,
                        "StartDate": start_date,
                        "EndTime": end_time,
                        "StartTime": start_time,
                        "Lang": self.lang,
                        "EndDate": end_date,
                        "TempID": self.temp_ID,
                        "CategoryID": self.category_ID,
                        "COID": self.COID,
                        "UPID": self.UPID,
                    },
                }
            }
        }
        response = self._query(payload)
        return response

    def _filter_location_query_data(self, contents: dict) -> list:
        all_location_data = contents["Data"]["ResultData"]["AvailableData"][
            "DataTable"
        ]["DataRow"]
        result = []
        if isinstance(all_location_data, list):
            for data in all_location_data:
                location_data = {
                    "LID_key": f"{data['LID']}┼{data['LSID']}",
                    "use_date": data["useDate"],
                    "price": data["Price"],
                    "LID_name": data["LIDName"],
                    "LSID_name": data["LSIDName"],
                }
                result.append(location_data)
        return result
