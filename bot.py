import random
from typing import List

import language_tool_python
import telebot
import requests
from bs4 import BeautifulSoup
from telebot.types import Sticker, Message
import re

from config import settings

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
tool = language_tool_python.LanguageToolPublicAPI('ru-RU')

sticker_set = bot.get_sticker_set('DoggoStickerms')

if sticker_set:
    stickers = sticker_set.stickers


def letter_counter(text: str, letter: str = 'м'):
    return len([x for x in text if x == letter])


def contains_misspelling(text: str):
    matches = tool.check(text)
    for match in matches:
        if match.replacements:
            replacement = match.replacements[0]
            word = text[match.offset:match.offset + match.errorLength]
            excess_letter_count = letter_counter(word) - letter_counter(replacement)
            if match.ruleIssueType == 'misspelling' and excess_letter_count > 0 \
                    and len(word) == len(replacement) + excess_letter_count:
                return True
    return False


@bot.message_handler(func=lambda message: True)
def echo_all(message: Message) -> None:
    if is_misspelled(message.text):
        misspelled_reply(message)

    if is_aggressive(message.text):
        aggressive_reply(message)

    if 'ауф' in message.text.lower():
        bot.reply_to(message, random.choice(parse_auf()))

    success, haiku = try_get_haiku(message.text)
    if success:
        bot.reply_to(message, haiku)


def is_aggressive(text: str) -> bool:
    return letter_counter(text, letter=')') >= 2 and letter_counter(text, letter='0') >= 1


def is_misspelled(text: str) -> bool:
    return contains_misspelling(text)


def aggressive_reply(message: Message) -> None:
    bot.reply_to(
        message,
        random.choice(
            ['да ты заебаааал', 'ой, иди нахуй а', 'иди нахер, блин', 'нормас']
        )
    )


def misspelled_reply(message: Message) -> None:
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


def parse_auf():
    response = requests.get('https://citatko.com/bez-rubriki/auf-tsitaty-pro-volkov')
    soup = BeautifulSoup(response.content, "html.parser")
    return [x.text for x in soup.findAll('div', attrs={'class': 'ads-color-box'})]


VOWELS_REGEX = re.compile(r'[аеёиоуыэюя]')
NUMBERS_REGEX = re.compile(r'\d')
SPACES_REGEX = re.compile(r'\s')


HAIKU_STRUCTURE = [5, 7, 5]


def try_get_haiku(text: str) -> (bool, str):
    if count_vowels(text) != 17:
        return False, None

    if has_numbers(text):
        return False, None

    words: List[str] = SPACES_REGEX.split(text)
    line: int = 0
    line_vowels: int = 0
    haiku: List[List[str]] = [[], [], []]

    for word in words:
        haiku[line].append(word)
        line_vowels += count_vowels(word)

        if line_vowels > HAIKU_STRUCTURE[line]:
            return False, None

        if line_vowels == HAIKU_STRUCTURE[line]:
            line += 1
            line_vowels = 0

    return True, '\n'.join(map(lambda l: ' '.join(l), haiku))


def count_vowels(text: str) -> int:
    return len(VOWELS_REGEX.findall(text))


def has_numbers(text: str) -> bool:
    return bool(NUMBERS_REGEX.search(text))


def haiku_reply(message: Message, haiku: str) -> None:
    bot.reply_to(message, haiku)


bot.polling()
