import random
import time

import telebot
from secrets import SUPP_TOKEN as TOKEN
bot = telebot.TeleBot(TOKEN, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

from bureau import Bureau
bureau = Bureau('test.db')

from constants import bcolors as bf

@bot.message_handler(commands=['start'])
def send_welcome(message):
	chat_id = message.chat.id
	status, secret = bureau.inscrire_user(chat_id)
	bot.send_message(chat_id, f"ID {chat_id} " + status + f"\nSECRET: {secret}")

@bot.message_handler(func=lambda message: True)
def add_word(message):
	chat_id = message.chat.id
	word = message.text.upper()
	if not word.replace('-', '').isalpha():
		bot.reply_to(message, 'please give ONE word of LATIN letters and hyphens only.\nwords with diacritics do not work (yet).')
		return
		
	status, expl, demos = bureau.inscrire_word(chat_id, word)
	if status == "FAILED":
		msg = ""
	else:
		msg =  '\n\n' + expl
		for d in demos:
			msg += '\n\n' + d	
	
	try:
		bot.send_message(chat_id, f'{word} {status}' + msg)
	except:
		print('{bf.FAIL}[ADD_WORD_EXCEPTION]{bf.ENDC}: chat_id={chat_id}, msg=', f'{word} {status}' + msg)
		print(e)

bot.infinity_polling()
