from telethon import TelegramClient
from dotenv import load_dotenv
import os

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
group_username = os.getenv('GROUP')
user_to_send = os.getenv('USER_TO_SEND')

# Здесь указываем список ключевых слов для поиска
keywords = ["Монитор", "monitor", 'игровой']

client = TelegramClient('anon', api_id, api_hash)

# Функция для чтения последнего сохраненного ID сообщения
def read_last_message_id():
    try:
        with open("last_message_id.txt", "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return None

# Функция для записи ID последнего сообщения в файл
def save_last_message_id(message_id):
    with open("last_message_id.txt", "w") as file:
        file.write(str(message_id))

async def check_and_forward_messages():
    last_message_id = read_last_message_id()
    if last_message_id is not None:
        messages = client.iter_messages(group_username, min_id=last_message_id)
    else:
        print('Я тут')
        messages = client.iter_messages(group_username, limit=100)

    async for message in messages:
        print(message)
        if message.text and any(keyword.lower() in message.text.lower() for keyword in keywords):
            message_link = f"https://t.me/c/{str(message.chat_id)[4:]}/{message.id}"  # Формируем ссылку на сообщение
            forward_text = f"{message.text}\nСсылка на сообщение: {message_link}"
            # Пересылаем сообщение с текстом и ссылкой
            # await client.send_message(user_to_send, forward_text)

    last_message = await client.get_messages(group_username, limit=1)
    # Сохраняем ID последнего обработанного сообщения
    if last_message:
        save_last_message_id(last_message[0].id)

async def main():
    await check_and_forward_messages()
    print("Завершение скрипта.")

# Запускаем скрипт
with client:
    client.loop.run_until_complete(main())