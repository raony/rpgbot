#!/usr/bin/env python
import telegram
import re
import os
from flask import Flask, request
from rpgbot import RPGBot

app = Flask(__name__)
telegram_token = os.environ['TELEGRAM_TOKEN']
app_url = os.environ['APP_URL']
bot = telegram.Bot(token=telegram_token)
command_pattern = re.compile(r'/(?P<command>\w+) (?P<args>.*)')
mrpgbot = RPGBot()

@app.route('/'+telegram_token, methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True))

        chat_id = update.message.chat.id
        text = update.message.text

        match = command_pattern.match(text)

        if match:
            result = mrpgbot.command(chat_id, match.group('command').strip(), match.group('args').strip())
        else:
            result = 'Non comprendo!'

        bot.sendMessage(chat_id=chat_id, text=result.encode('utf-8'))

    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook(app_url + telegram_token)
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return '.'