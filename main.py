import sqlite3 as sq

#from webserver import keep_alive
from aiogram import types, executor, Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from check_price import get_price
import asyncio
from asgiref.sync import sync_to_async


bot = Bot("2052601286:AAFBSpENQibU8mkPclqEvXHLM8-7d6vMwJ8")
dp = Dispatcher(bot, storage=MemoryStorage())
baseMain = sq.connect('bybit.db', check_same_thread = False)

class AwaitMessages(StatesGroup):
    message_limit_items = State()
    send_penis = State()

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_settings = types.KeyboardButton("⚙️Настройки")
    btn_start = types.KeyboardButton("Запуск")
    keyboard_markup.add(btn_start, btn_settings)
    try:
        check_user_base = baseMain.execute(f'SELECT user_id FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
        print(check_user_base)
        if check_user_base is None:
            baseMain.execute(f'INSERT INTO users (user_id, rub_count) VALUES ("{message.from_user.id}", {float(10)});')
            baseMain.commit()
    except Exception as e:
        print(e)
        pass
    await message.delete()
    await message.answer("👨‍👨‍👦GAY Bot", reply_markup=keyboard_markup)
    

#ГЛАВНОЕ МЕНЮ CALLBACK
@dp.callback_query_handler(text_startswith="start", state="*")
async def start_callback(call: types.CallbackQuery):
    await call.message.delete()
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_settings = types.KeyboardButton("⚙️Настройки")
    btn_start = types.KeyboardButton("Запуск")
    keyboard_markup.add(btn_start, btn_settings)
    await bot.send_message(text="👨‍👨‍👦GAY Bot", chat_id=call.from_user.id, reply_markup=keyboard_markup)

#МЕНЮ Запуск
@dp.message_handler(lambda message: message.text == "Запуск")
async def parser(message: types.Message):
    userinfo = baseMain.execute(f'SELECT * FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
    await message.answer(f"Запуск\nСтоимость в рублях: {userinfo[1]}")

    good_links = await sync_to_async(get_price)(userinfo[1])
    send_message = f"Завершил работу.\n\n{good_links}"
    if len(send_message) > 4096:
        for x in range(0, len(send_message), 4096):
            await message.answer(send_message[x:x+4096])
    else:
        await message.answer(send_message)

#МЕНЮ НАСТРОЕК
@dp.message_handler(lambda message: message.text == "⚙️Настройки")
async def parser(message: types.Message):
    await message.delete()
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    markup.add(InlineKeyboardButton(text="Стоимость руб", callback_data="limit_items"))
    markup.add(InlineKeyboardButton(text="❌Закрыть", callback_data="start"))

    userinfo = baseMain.execute(f'SELECT * FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
    await message.answer(f"⚙️Меню настроек пользоваетеля {userinfo[0]} \n\nСтоимость руб: {userinfo[1]}", reply_markup=markup)

#ДЛЯ ВАДИМА
@dp.message_handler(commands=['penis'])
async def process_start_command(message: types.Message):
    
    await message.delete()
    await message.answer("Введи сообщение:")
    await AwaitMessages.send_penis.set()

#ДЛЯ ВАДИМА МАШИНА СОСТОЯНИЙ
@dp.message_handler(state=AwaitMessages.send_penis)  # Принимаем состояние
async def started(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:  # Устанавливаем состояние ожидания
        proxy['send_penis'] = message.text
        await message.delete()
    if proxy["send_penis"] != "/stop":
        users = baseMain.execute(f'SELECT user_id FROM users').fetchall()
        for user in users:
            await bot.send_message(user[0], proxy["send_penis"])
        await state.finish()  # Выключаем состояние
    else:
        await state.finish()  # Выключаем состояние

    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    markup.add(InlineKeyboardButton(text="Стоимость руб", callback_data="limit_items"))
    markup.add(InlineKeyboardButton(text="❌Закрыть", callback_data="start"))

    await message.answer(f"Сообщение ушло", reply_markup=markup)

#ЛИМИТ ТОВАРОВ
@dp.callback_query_handler(text_startswith="limit_items", state="*")
async def start_callback(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    markup.add(InlineKeyboardButton(text="❌Закрыть", callback_data="start"))
    await call.message.delete()
    await AwaitMessages.message_limit_items.set()

#ЛИМИТ ТОВАРОВ МАШИНА СОСТОЯНИЙ
@dp.message_handler(state=AwaitMessages.message_limit_items)  # Принимаем состояние
async def started(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:  # Устанавливаем состояние ожидания
        proxy['message_limit_items'] = message.text
    if proxy["message_limit_items"] != "/messages":
        baseMain.execute(f'UPDATE users SET rub_count = {float(message.text)} WHERE user_id = "{message.from_user.id}"')
        baseMain.commit()
        await state.finish()  # Выключаем состояние
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    markup.add(InlineKeyboardButton(text="Стоимость руб", callback_data="limit_items"))
    markup.add(InlineKeyboardButton(text="❌Закрыть", callback_data="start"))

    userinfo = baseMain.execute(f'SELECT * FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
    await message.answer(f"⚙️Меню настроек пользоваетеля {userinfo[0]} \n\nСтоимость руб: {userinfo[1]}", reply_markup=markup)

if __name__ == '__main__':
    executor.start_polling(dp)
    loop = asyncio.get_event_loop()