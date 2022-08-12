import asyncio
import os
import sys

from modules.web_platform import WebPlatform

# from datetime import datetime, timedelta


async def main():
    # today = datetime.today()
    # appoint_date = today + timedelta(days=7)
    # appoint_date_str = datetime.strftime(appoint_date, "%Y/%m/%d")
    appoint_date_str = "2022/08/20"
    appoint_retry_times = int(os.getenv("APPOINT_RETRY_TIMES"))

    tasks = [
        web_platform.appoint_with_specific_place_and_time(
            appoint_date_str, "16", "1112", num
        )
        for num in range(appoint_retry_times)
    ]
    tasks += [
        web_platform.appoint_with_specific_place_and_time(
            appoint_date_str, "16", "1115", num
        )
        for num in range(appoint_retry_times)
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # TODO: Async, cli
    web_platform = WebPlatform("大同")

    if sys.argv[1] == "appoint_setup":
        web_platform.get_valid_asp_session_id()

    if sys.argv[1] == "start_appoint":
        web_platform.set_existing_asp_session_id()
        asyncio.run(main())
