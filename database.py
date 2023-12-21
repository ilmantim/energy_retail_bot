import pprint

# Сначала сюда запрос. по № счета узнаём id

url = "https://......../getAccounts/100399652"

response_1 = {
  "100399652":{"id_PA":1343365,"number":None,"first_name":None,"last_name":None,"father_name":None,"title_org":None,"logo_org":""},
  "1": {"id_PA": 1343366, "number": None, "first_name": None, "last_name": None, "father_name": None, "title_org": None, "logo_org": ""},
  "2": {"id_PA": 1343367, "number": None, "first_name": None, "last_name": None, "father_name": None, "title_org": None, "logo_org": ""},
  "3": {"id_PA": 1343368, "number": None, "first_name": None, "last_name": None, "father_name": None, "title_org": None, "logo_org": ""},
  "4": {"id_PA": 1343369, "number": None, "first_name": None, "last_name": None, "father_name": None, "title_org": None, "logo_org": ""},
  "5": {"id_PA": 1343370, "number": None, "first_name": None, "last_name": None, "father_name": None, "title_org": None, "logo_org": ""},
  "6": {"id_PA": 1343371, "number": None, "first_name": None, "last_name": None, "father_name": None, "title_org": None, "logo_org": ""},
  "7": {"id_PA": 1343372, "number": None, "first_name": None, "last_name": None, "father_name": None, "title_org": None, "logo_org": ""},
  "8": {"id_PA": 1343373, "number": None, "first_name": None, "last_name": None, "father_name": None, "title_org": None, "logo_org": ""},
  "9": {"id_PA": 1343374, "number": None, "first_name": None, "last_name": None, "father_name": None, "title_org": None, "logo_org": ""},
  "10": {"id_PA": 1343375, "number": None, "first_name": None, "last_name": None, "father_name": None, "title_org": None, "logo_org": ""}
}



# по id узнаём всё остальное

url = "https://.........getAccountInfo/1343365"

response_2 = {
  "100399652": {
    "core_devices": [
      {
        "id_meter": 5974604,
        "device_title": "Меркурий-201.5",
        "modification": "1,0/16/5,0",
        "serial_number": "06485054",
        "date_check": "2010-01-24T00:00:00Z",
        "date_check_next": "2026-01-24T00:00:00Z",
        "type_locality": "г",
        "locality": "Чебоксары",
        "type_street": "б-р",
        "street": "Эгерский",
        "type_house": "д.",
        "house": "35",
        "building": "",
        "type_building": "",
        "condos_types": "Квартира",
        "condos_number": "60",
        "rates": [
          {
            "id_tariff": 62,
            "id_indication": 146710100,
            "title": "Сутки",
            "cost": 4.05,
            "code": "0",
            "reading": 21780,
            "title_unit": "кВт*ч",
            "date_reading": "2023-11-17T00:00:00Z",
            "current_month_reading_value": 22000.000000,
            "current_month_reading_date": "2023-12-18T00:00:00Z"
          }
        ]
      }
    ]
  },
  "1": {
    "core_devices": [
      {
        "id_meter": 5974605,
        "device_title": "Меркурий-201.6",
        "modification": "1,1/16/5,1",
        "serial_number": "06485055",
        "date_check": "2010-02-24T00:00:00Z",
        "date_check_next": "2026-02-24T00:00:00Z",
        "type_locality": "г",
        "locality": "Чебоксары",
        "type_street": "пр-т",
        "street": "Ленина",
        "type_house": "д.",
        "house": "36",
        "building": "1",
        "type_building": "корп",
        "condos_types": "Офис",
        "condos_number": "101",
        "rates": [
          {
            "id_tariff": 63,
            "id_indication": 146710101,
            "title": "Ночь",
            "cost": 3.95,
            "code": "1",
            "reading": 21781,
            "title_unit": "кВт*ч",
            "date_reading": "2023-11-18T00:00:00Z",
            "current_month_reading_value": 22001.000000,
            "current_month_reading_date": "2023-12-19T00:00:00Z"
          }
        ]
      }
    ]
  },
  "2": {
    "core_devices": [
      {
        "id_meter": 5974606,
        "device_title": "Меркурий-201.7",
        "modification": "1,2/16/5,2",
        "serial_number": "06485056",
        "date_check": "2010-03-24T00:00:00Z",
        "date_check_next": "2026-03-24T00:00:00Z",
        "type_locality": "г",
        "locality": "Чебоксары",
        "type_street": "ул",
        "street": "Советская",
        "type_house": "д.",
        "house": "37",
        "building": "2",
        "type_building": "корп",
        "condos_types": "Квартира",
        "condos_number": "102",
        "rates": [
          {
            "id_tariff": 64,
            "id_indication": 146710102,
            "title": "День",
            "cost": 4.15,
            "code": "2",
            "reading": 21782,
            "title_unit": "кВт*ч",
            "date_reading": "2023-11-19T00:00:00Z",
            "current_month_reading_value": 22002.000000,
            "current_month_reading_date": "2023-12-20T00:00:00Z"
          }
        ]
      }
    ]
  },
  "3": {
    "core_devices": [
      {
        "id_meter": 5974607,
        "device_title": "Меркурий-201.8",
        "modification": "1,3/17/5,3",
        "serial_number": "06485057",
        "date_check": "2010-04-24T00:00:00Z",
        "date_check_next": "2026-04-24T00:00:00Z",
        "type_locality": "г",
        "locality": "Чебоксары",
        "type_street": "пер",
        "street": "Октябрьский",
        "type_house": "д.",
        "house": "38",
        "building": "3",
        "type_building": "корп",
        "condos_types": "Магазин",
        "condos_number": "103",
        "rates": [
          {
            "id_tariff": 65,
            "id_indication": 146710103,
            "title": "Выходной",
            "cost": 4.25,
            "code": "3",
            "reading": 21783,
            "title_unit": "кВт*ч",
            "date_reading": "2023-11-20T00:00:00Z",
            "current_month_reading_value": 22003.000000,
            "current_month_reading_date": "2023-12-21T00:00:00Z"
          }
        ]
      }
    ]
  },
  "4": {
    "core_devices": [
      {
        "id_meter": 5974608,
        "device_title": "Меркурий-201.9",
        "modification": "1,4/18/5,4",
        "serial_number": "06485058",
        "date_check": "2010-05-24T00:00:00Z",
        "date_check_next": "2026-05-24T00:00:00Z",
        "type_locality": "г",
        "locality": "Чебоксары",
        "type_street": "наб",
        "street": "Волгоградская",
        "type_house": "д.",
        "house": "39",
        "building": "4",
        "type_building": "корп",
        "condos_types": "Кафе",
        "condos_number": "104",
        "rates": [
          {
            "id_tariff": 66,
            "id_indication": 146710104,
            "title": "Рабочий день",
            "cost": 4.35,
            "code": "4",
            "reading": 21784,
            "title_unit": "кВт*ч",
            "date_reading": "2023-11-21T00:00:00Z",
            "current_month_reading_value": 22004.000000,
            "current_month_reading_date": "2023-12-22T00:00:00Z"
          }
        ]
      }
    ]
  },
  "5": {
    "core_devices": [
      {
        "id_meter": 5974609,
        "device_title": "Меркурий-202.0",
        "modification": "1,5/19/5,5",
        "serial_number": "06485059",
        "date_check": "2010-06-24T00:00:00Z",
        "date_check_next": "2026-06-24T00:00:00Z",
        "type_locality": "г",
        "locality": "Чебоксары",
        "type_street": "ш",
        "street": "Гагарина",
        "type_house": "д.",
        "house": "40",
        "building": "5",
        "type_building": "корп",
        "condos_types": "Бизнес-центр",
        "condos_number": "105",
        "rates": [
          {
            "id_tariff": 67,
            "id_indication": 146710105,
            "title": "Утро",
            "cost": 4.45,
            "code": "5",
            "reading": 21785,
            "title_unit": "кВт*ч",
            "date_reading": "2023-11-22T00:00:00Z",
            "current_month_reading_value": 22005.000000,
            "current_month_reading_date": "2023-12-23T00:00:00Z"
          }
        ]
      }
    ]
  },
  "6": {
    "core_devices": [
      {
        "id_meter": 5974610,
        "device_title": "Меркурий-202.1",
        "modification": "1,6/20/6,0",
        "serial_number": "06485060",
        "date_check": "2010-07-24T00:00:00Z",
        "date_check_next": "2026-07-24T00:00:00Z",
        "type_locality": "г",
        "locality": "Чебоксары",
        "type_street": "пл",
        "street": "Революции",
        "type_house": "д.",
        "house": "41",
        "building": "6",
        "type_building": "корп",
        "condos_types": "Гостиница",
        "condos_number": "106",
        "rates": [
          {
            "id_tariff": 68,
            "id_indication": 146710106,
            "title": "Вечер",
            "cost": 4.55,
            "code": "6",
            "reading": 21786,
            "title_unit": "кВт*ч",
            "date_reading": "2023-11-23T00:00:00Z",
            "current_month_reading_value": 22006.000000,
            "current_month_reading_date": "2023-12-24T00:00:00Z"
          }
        ]
      }
    ]
  },
  "7": {
    "core_devices": [
      {
        "id_meter": 5974611,
        "device_title": "Меркурий-202.2",
        "modification": "1,7/21/6,1",
        "serial_number": "06485061",
        "date_check": "2010-08-24T00:00:00Z",
        "date_check_next": "2026-08-24T00:00:00Z",
        "type_locality": "г",
        "locality": "Чебоксары",
        "type_street": "пр-д",
        "street": "Пионерский",
        "type_house": "д.",
        "house": "42",
        "building": "7",
        "type_building": "корп",
        "condos_types": "Склад",
        "condos_number": "107",
        "rates": [
          {
            "id_tariff": 69,
            "id_indication": 146710107,
            "title": "Праздник",
            "cost": 4.65,
            "code": "7",
            "reading": 21787,
            "title_unit": "кВт*ч",
            "date_reading": "2023-11-24T00:00:00Z",
            "current_month_reading_value": 22007.000000,
            "current_month_reading_date": "2023-12-25T00:00:00Z"
          }
        ]
      }
    ]
  },
  "8": {
    "core_devices": [
      {
        "id_meter": 5974612,
        "device_title": "Меркурий-202.3",
        "modification": "1,8/22/6,2",
        "serial_number": "06485062",
        "date_check": "2010-09-24T00:00:00Z",
        "date_check_next": "2026-09-24T00:00:00Z",
        "type_locality": "г",
        "locality": "Чебоксары",
        "type_street": "бул",
        "street": "Молодежный",
        "type_house": "д.",
        "house": "43",
        "building": "8",
        "type_building": "корп",
        "condos_types": "Школа",
        "condos_number": "108",
        "rates": [
          {
            "id_tariff": 70,
            "id_indication": 146710108,
            "title": "Раннее утро",
            "cost": 4.75,
            "code": "8",
            "reading": 21788,
            "title_unit": "кВт*ч",
            "date_reading": "2023-11-25T00:00:00Z",
            "current_month_reading_value": 22008.000000,
            "current_month_reading_date": "2023-12-26T00:00:00Z"
          }
        ]
      }
    ]
  },
  "9": {
    "core_devices": [
      {
        "id_meter": 5974613,
        "device_title": "Меркурий-202.4",
        "modification": "1,9/23/6,3",
        "serial_number": "06485063",
        "date_check": "2010-10-24T00:00:00Z",
        "date_check_next": "2026-10-24T00:00:00Z",
        "type_locality": "г",
        "locality": "Чебоксары",
        "type_street": "пр",
        "street": "Космонавтов",
        "type_house": "д.",
        "house": "44",
        "building": "9",
        "type_building": "корп",
        "condos_types": "Торговый центр",
        "condos_number": "109",
        "rates": [
          {
            "id_tariff": 71,
            "id_indication": 146710109,
            "title": "Полдень",
            "cost": 4.85,
            "code": "9",
            "reading": 21789,
            "title_unit": "кВт*ч",
            "date_reading": "2023-11-26T00:00:00Z",
            "current_month_reading_value": 22009.000000,
            "current_month_reading_date": "2023-12-27T00:00:00Z"
          }
        ]
      }
    ]
  },
  "10": {
    "core_devices": [
      {
        "id_meter": 5974614,
        "device_title": "Меркурий-202.5",
        "modification": "2,0/24/7,0",
        "serial_number": "06485064",
        "date_check": "2010-11-24T00:00:00Z",
        "date_check_next": "2026-11-24T00:00:00Z",
        "type_locality": "г",
        "locality": "Чебоксары",
        "type_street": "алл",
        "street": "Зеленая",
        "type_house": "д.",
        "house": "45",
        "building": "10",
        "type_building": "корп",
        "condos_types": "Клиника",
        "condos_number": "110",
        "rates": [
          {
            "id_tariff": 72,
            "id_indication": 146710110,
            "title": "Полночь",
            "cost": 4.95,
            "code": "10",
            "reading": 21790,
            "title_unit": "кВт*ч",
            "date_reading": "2023-11-27T00:00:00Z",
            "current_month_reading_value": 22010.000000,
            "current_month_reading_date": "2023-12-28T00:00:00Z"
          }
        ]
      }
    ]
  }
}