import os

import telegram

from flask import Flask, request, render_template


from config import Config
from bot.bot import Bot


TOKEN = os.environ.get('TOKEN')  # Security Token given from the @BotFather
NAME_APP = os.environ.get('NAME_APP')
BASE_URL = '{}.herokuapp.com'.format(NAME_APP)  # Domain name of your server, without protocol.
HOST = '0.0.0.0'  # IP Address on which Flask should listen on
PORT = os.environ.get('PORT')  # Port on which Flask should listen on

app = Flask(__name__)
app.config.from_object(Config)

bot = Bot(TOKEN)


@app.route('/{}'.format(TOKEN), methods=['POST'])
def tg_webhook_handler():
    if request.method == "POST":
        update = request.get_json(force=True)
        update = telegram.Update.de_json(update, bot.telegram_bot)
        bot.dp.process_update(update)
    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.telegram_bot.setWebhook('https://{}/{}'.format(BASE_URL, TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/features')
def features():
    return render_template('features.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, threaded=True, debug=False)