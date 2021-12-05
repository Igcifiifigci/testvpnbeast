""" tbot.py """

from telebot import TeleBot

TOKEN = "5006835603:AAElOkjovuA1-qyw2PD7ZRzXabuqnWoHncE"
URL = "https://beastofwar.pythonanywhere.com/"

bot = TeleBot(TOKEN, parse_mode = "Markdown", threaded = False, skip_pending = True)
bot.bot_info = bot.get_me()
bot.remove_webhook()
bot.set_webhook(URL + bot.token)

import run
