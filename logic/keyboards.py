from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_LINK

subscribe_channel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Subscribe", url=CHANNEL_LINK)],
    [InlineKeyboardButton(text="Check", callback_data="subchek")]
])

def create_markap_kb(name, url):
    if name == "None" or url== "None":
        return None
    ads_channel = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, url=url)]
    ])
    return ads_channel