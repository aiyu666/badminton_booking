import sys

from modules.web_platform import WebPlatform

if __name__ == "__main__":
    # TODO: Async, cli
    web_platform = WebPlatform("板橋")

    if sys.argv[1] == "appoint_setup":
        web_platform.get_valid_asp_session_id()

    if sys.argv[1] == "start_appoint":
        web_platform.set_existing_asp_session_id()
        web_platform.appoint_with_specific_place_and_time("2022/07/23", "19", "87")
        web_platform.appoint_with_specific_place_and_time("2022/07/23", "20", "87")
