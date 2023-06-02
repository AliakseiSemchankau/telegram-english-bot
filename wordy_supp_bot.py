import random
import time

import telebot
from secrets import SUPP_TOKEN as TOKEN
bot = telebot.TeleBot(TOKEN, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

from decider import Decider
decider = Decider('test.db')

from colors import bcolors as bf

@bot.message_handler(commands=['start'])
def send_welcome(message):
	chat_id = message.chat.id
	status, secret = decider.register_user(chat_id)
	bot.send_message(chat_id, f"ID {chat_id} " + status + f"\nSECRET: {secret}")

@bot.message_handler(func=lambda message: True)
def add_word(message):
	chat_id = message.chat.id
	word = message.text.upper()
	if not word.isalpha():
		bot.reply_to(message, 'please give ONE word of LATIN letters only')
		return
		
	status, msg = decider.register_word(chat_id, word)
	try:
		bot.send_message(chat_id, f'{word} {status}' + msg)
	except:
		print('{bf.FAIL}[ADD_WORD_EXCEPTION]{bf.ENDC}: chat_id={chat_id}, msg=', f'{word} {status}' + msg)
		print(e)

bot.infinity_polling()
