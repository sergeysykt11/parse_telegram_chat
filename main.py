from telethon import TelegramClient
from telethon.errors import FloodWaitError
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
group_username = os.getenv('GROUP')
user_to_send = os.getenv('USER_TO_SEND')

keywords = ["Монитор", "monitor", 'игровой']

client = TelegramClient('anon', api_id, api_hash)

def read_last_message_id():
    try:
        with open("last_message_id.txt", "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return None


def save_last_message_id(message_id):
    with open("last_message_id.txt", "w") as file:
        file.write(str(message_id))


async def send_message_safe(user, message):
    try:
        await client.send_message(user, message)
    except FloodWaitError as e:
        print(f"Необходимо подождать {e.seconds} секунд перед следующей отправкой.")
        await asyncio.sleep(e.seconds)  # Ожидаем требуемое время
        await send_message_safe(user, message)  # Повторная попытка отправить сообщение


async def check_and_forward_messages():
    last_message_id = read_last_message_id()
    messages = client.iter_messages(group_username,
                                    min_id=last_message_id) if last_message_id else client.iter_messages(group_username,
                                                                                                         limit=100)

    aggregate_message = ""
    max_length = 2000  # Максимальная длина собранного сообщения

    async for message in messages:
        if message.text and any(keyword.lower() in message.text.lower() for keyword in keywords):
            message_link = f"https://t.me/c/{str(message.chat_id)[4:]}/{message.id}"
            forward_text_base = f"{message.text}\n\n"
            forward_text_link = f"Ссылка на сообщение: {message_link}\n\n"

            if len(aggregate_message + forward_text_base + forward_text_link) > max_length:
                trim_length = max_length - len(aggregate_message + forward_text_link)
                forward_text_base = forward_text_base[:trim_length]

            forward_text = forward_text_base + forward_text_link

            if len(aggregate_message + forward_text) > max_length:
                if aggregate_message:
                    await send_message_safe(user_to_send, aggregate_message)
                    aggregate_message = ""
                aggregate_message += forward_text[:max_length - len(aggregate_message)]
            else:
                aggregate_message += forward_text

    if aggregate_message:
        await send_message_safe(user_to_send, aggregate_message)

    last_message = await client.get_messages(group_username, limit=1)
    if last_message:
        save_last_message_id(last_message[0].id)


async def main():
    while True:
        await check_and_forward_messages()
        print("Ожидание следующего запуска.")
        await asyncio.sleep(60)  # Ждем одну минуту


with client:
    client.loop.run_until_complete(main())
