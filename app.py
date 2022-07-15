# from modules.line import Line
# from modules.sporestrofit import Sporestrofit
from modules.web_platform import WebPlatform

web_platform = WebPlatform("板橋", "羽B", "19", "21", date="2022-07-16")
web_platform.get_valid_asp_session_id()

# TODO (now is for test)
# line = Line()
# sporestrofit = Sporestrofit()
# get_available_date = sporestrofit.get_location_query_data(
#     "2022-07-09", "2022-07-10", "00:00", "23:00"
# )
# query_data = sporestrofit._filter_location_query_data(get_available_date)
# print(query_data)
# msg = ""
# for j in query_data:
#     available_data = sporestrofit.get_location_available_data(
#         j["LID_key"], j["use_date"]
#     )
#     print(available_data)
#     for i in available_data:
#         msg += f"\n[{j['use_date']}] \n區域： {j['LID_name']} \n場地：{j['LSID_name']}\n總共有 {len(available_data)} 個時段！\n時段如下:\n{i['Time']}\n價格為: {j['price']}\n"

# line.send_notify_message("test")


"""
[日期]
[地點]
時段 [場地名 list]
時段 [場地名 list]
時段 [場地名 list]
[地點]
時段 [場地名 list]
時段 [場地名 list]
------------------
[日期]
[地點]
時段 [場地名 list]

"""
