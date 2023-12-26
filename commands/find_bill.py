import requests
from django.utils import timezone
from retail.models import Bill


def find_bill(update, context, text, step):
    url_for_id = f"https://lk-api-dev.backspark.ru/api/v0/cabinet/terminal/getAccounts/{text}"
    response = requests.get(url_for_id)
    response.raise_for_status()
    response_id = response.json()
    if response_id and "id_PA" in response_id[0]:
        bill_id = str(response_id[0]["id_PA"])
        url_for_bill = f"https://lk-api-dev.backspark.ru/api/v0/cabinet/terminal/getAccountInfo/{bill_id}"
        response = requests.get(url_for_bill)
        response.raise_for_status()
        response_bill = response.json()
        if text in response_bill.values():
            context.user_data['bill_num'] = text
            bill_here, is_found = Bill.objects.get_or_create(value=int(text))
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Счет успешно найден."
            )

            bill_here.number_and_type_pu = f'счётчик {response_bill["core_devices"][0]["serial_number"]} на электроснабжение в подъезде'
            readings = response_bill["core_devices"][0]["rates"][0][
                "current_month_reading_value"]
            if readings:
                bill_here.readings = int(round(float(readings)))
            date = response_bill["core_devices"][0]["rates"][0][
                "current_month_reading_date"]
            if date:
                moscow_timezone = timezone.get_fixed_timezone(180)
                bill_here.registration_date = timezone.datetime.strptime(
                    date,
                    "%Y-%m-%dT%H:%M:%SZ"
                ).astimezone(tz=moscow_timezone)
            bill_here.address = (
                f'{response_bill["core_devices"][0]["locality"]} '
                f'{response_bill["core_devices"][0]["street"]} '
                f'{response_bill["core_devices"][0]["type_house"]} '
                f'{response_bill["core_devices"][0]["house"]} '
                f'{response_bill["core_devices"][0]["condos_types"]} '
                f'{response_bill["core_devices"][0]["condos_number"]} ')
            bill_here.save()
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Не удалось найти счет."
            )
            return step
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не удалось найти счет."
        )
        return step
