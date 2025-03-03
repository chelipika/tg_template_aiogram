import os
from aiogram import F, Bot
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery, FSInputFile, ChatJoinRequest
from aiogram.exceptions import TelegramBadRequest
from aiogram import Router
from config import TOKEN, CHANNEL_ID, CHANNEL_LINK
from datetime import datetime, timedelta
from collections import defaultdict
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import database.requests as rq
bot = Bot(token=TOKEN)
import logic.keyboards as kb
# File to store chat history


class AdvMsg(StatesGroup):
    img = State()
    audio = State()
    txt = State()
    inline_link_name = State()
    inline_link_link = State()
    
    

class Gen(StatesGroup):
    wait = State()
# --- Load and Save Voice Settings ---
pending_requests = set()
async def sub_chek(user_id):
    if user_id in pending_requests or await is_subscribed(user_id=user_id):
        return True
    else:
        return False


async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False
    



router = Router()

@router.chat_join_request()
async def handle_join_request(update: ChatJoinRequest):
    pending_requests.add(update.from_user.id)
    # Optionally notify admins or log the request


@router.message(Command("test"))
async def test(message: Message):
    await message.answer("test")
    await message.answer(str(pending_requests))

@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    await rq.set_user(tg_id=user_id)

    if not await sub_chek(message.from_user.id):
        await message.answer(f"Send request first, Киньте запрос на подписку: \n{CHANNEL_LINK}", reply_markup=kb.subscribe_channel)
        return
    await message.answer("your text is here")

    
@router.message(Command("narrator")) #// /narrator 123456, all users will recieve 123456
async def narrator(message: Message, command: CommandObject):
    for user in await rq.get_all_user_ids():
        await bot.send_message(chat_id=user, text=command.args)



@router.callback_query(F.data == "subchek")
async def subchek(callback: CallbackQuery):
    if not await sub_chek(callback.from_user.id):
        await callback.answer("Your not subscribed yet",)
        return
    await callback.answer("Your are okay to go")
    
@router.message(Command("send_to_all_users"))
async def start_send_to_all(message: Message, state: FSMContext):
    await state.set_state(AdvMsg.img)
    await message.answer("send your img🖼️")


@router.message(AdvMsg.img)
async def ads_img(message: Message, state: FSMContext):
    photo_data = { "photo": message.photo }  # Ensure it's in dictionary format
    await state.update_data(img=message.photo[-1].file_id)
    await state.set_state(AdvMsg.txt)
    await message.answer("send your text🗄️")

@router.message(AdvMsg.txt)
async def ads_txt(message: Message, state: FSMContext):
    await state.update_data(txt=message.text)
    await state.set_state(AdvMsg.inline_link_name)
    await message.answer("send your inline_link name📛")

@router.message(AdvMsg.inline_link_name)
async def ads_lk_name(message: Message, state: FSMContext):
    await state.update_data(inline_link_name=message.text)
    await state.set_state(AdvMsg.inline_link_link)
    await message.answer("send your inline_link LINK🔗")

@router.message(AdvMsg.inline_link_link)
async def ads_final(message: Message, state: FSMContext):
    await state.update_data(inline_link_link=message.text)
    data = await state.get_data()
    new_inline_kb = kb.create_markap_kb(name=data['inline_link_name'], url=data['inline_link_link'])
    if new_inline_kb == None:
        for user in await rq.get_all_user_ids():
            if data['img']:
                await bot.send_photo(chat_id=user, photo=data['img'],caption=data['txt'])
            elif data['audio']:
                await bot.send_voice(chat_id=user, voice=data['audio'], caption=data["txt"])

    else:
        for user in await rq.get_all_user_ids():
            if data['img']:
                await bot.send_photo(chat_id=user, photo=data['img'],caption=data['txt'], reply_markup=new_inline_kb)
            elif data['audio']:
                await bot.send_voice(chat_id=user, voice=data['audio'], caption=data["txt"], reply_markup=new_inline_kb)


    await state.clear()


@router.message(Gen.wait)
async def stop_flood(message: Message):
    await message.answer("Wait one requests at a time \nПодождите ваш запрос генерируется.")
