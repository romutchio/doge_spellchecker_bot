from config import settings

import telebot
import random
import language_tool_python
from telebot.types import Sticker

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
tool = language_tool_python.LanguageToolPublicAPI('ru-RU')

sticker_set = bot.get_sticker_set('Stickerms')

if sticker_set:
	stickers = sticker_set.stickers


def letter_counter(text: str, letter: str = 'м'):
	return len([x for x in text if x == letter])


def contains_misspelling(text: str):
	matches = tool.check(text)
	for match in matches:
		if match.replacements and match.ruleIssueType == 'misspelling' \
				and letter_counter(match.replacements[0]) < letter_counter(text):
			return True
	return False


@bot.message_handler(func=lambda message: True)
def echo_all(message):
	if contains_misspelling(message.text):
		if sticker_set:
			sticker: Sticker = random.choice(sticker_set.stickers)
			bot.send_sticker(
				message.chat.id,
				sticker.file_id,
				reply_to_message_id=message.message_id,
			)
		else:
			photo = open('doge.jpg', 'rb')
			bot.send_photo(
				message.chat.id,
				photo,
				reply_to_message_id=message.message_id,
			)


bot.polling()
