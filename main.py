from telethon import TelegramClient, events, sync
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
group_username = os.getenv('GROUP')
user_to_send = os.getenv('USER_TO_SEND')

# Здесь указываем список ключевых слов для поиска
keywords = ["Монитор", "monitor", "keyword1", "keyword2"]

client = TelegramClient('anon', api_id, api_hash)

async def check_and_forward_messages():
    # Вычисляем время 5 минут назад от текущего момента в UTC
    time_threshold = datetime.now(timezone.utc) - timedelta(minutes=5)

    async for message in client.iter_messages(group_username, offset_date=1):
        # Приводим время сообщения к offset-naive для сравнения, удаляя информацию о часовом поясе
        message_time_naive = message.date.replace(tzinfo=None)
        if any(keyword.lower() in message.text.lower() for keyword in keywords):
            message_link = f"https://t.me/c/{str(message.chat_id)[4:]}/{message.id}"  # Формируем ссылку на сообщение
            forward_text = f"{message.text}\nСсылка на сообщение: {message_link}"
            # Пересылаем сообщение с текстом и ссылкой
            await client.send_message(user_to_send, forward_text)

async def main():
    await check_and_forward_messages()
    print("Завершение скрипта.")

# Запускаем скрипт
with client:
    client.loop.run_until_complete(main())