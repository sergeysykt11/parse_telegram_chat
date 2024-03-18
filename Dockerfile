FROM python
WORKDIR /scr/telegram/bots
RUN pip install telethon
RUN pip install flask
RUN pip install python-dotenv
COPY . .
CMD python main.py