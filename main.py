#!/usr/bin/env python

import sys
import os
sys.path.append(os.path.join(os.path.abspath('.'), 'venv/lib/python2.7/site-packages'))

import telegram
from flask import Flask, request

from diceroll import DiceRoll

app = Flask(__name__)

global bot
bot = telegram.Bot(token='200095754:AAGiIuriGj1Q1UDl604dWVunkc5hm5iytck')


@app.route('/200095754:AAGiIuriGj1Q1UDl604dWVunkc5hm5iytck', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True))

        chat_id = update.message.chat.id
        text = update.message.text
        result = ''

        if text.startswith('/r'):
            if len(text.split(' ')) == 2:
                num_dices = int(text.split(' ')[1])
                roll = DiceRoll(num_dices)
                if not roll.successes():
                    result += 'fail'
                else:
                    result += ' - '.join(['SUCCESS!', unicode(roll.successes())])
                result += ' - ' + ','.join([unicode(v) for v in roll.roll])

        # repeat the same message back (echo)
        if not result:
            result = 'Non entendo!'

        bot.sendMessage(chat_id=chat_id, text=result.encode('utf-8'))

    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('https://primeval-creek-130123.appspot.com/200095754:AAGiIuriGj1Q1UDl604dWVunkc5hm5iytck')
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return '.'