import pprint

# Сначала сюда запрос. по № счета узнаём id

url = "https://......../getAccounts/100399652"

response_1 = [{"id_PA":1343365,"number":None,"first_name":None,"last_name":None,"father_name":None,"title_org":None,"logo_org":""}]


# по id узнаём всё остальное

url = "https://.........getAccountInfo/1343365"

response_2 = {"number":"100399652","core_devices":[{"id_meter":5974604,"device_title":"Меркурий-201.5","modification":"1,0/16/5,0","serial_number":"06485054","date_check":"2010-01-24T00:00:00Z","date_check_next":"2026-01-24T00:00:00Z","type_locality":"г","locality":"Чебоксары","type_street":"б-р","street":"Эгерский","type_house":"д.","house":"35","building":"","type_building":"","condos_types":"Квартира","condos_number":"60","rates":[{"id_tariff":62,"id_indication":146710100,"title":"Сутки","cost":4.05,"code":"0","reading":21780,"title_unit":"кВт*ч","date_reading":"2023-11-17T00:00:00Z","current_month_reading_value":22000.000000,"current_month_reading_date":"2023-12-18T00:00:00Z"}]}]}