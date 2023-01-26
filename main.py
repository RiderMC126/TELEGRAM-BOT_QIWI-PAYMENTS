from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random

import config
import keyboard

bot = Bot(token=config.telegram_token) # Токен
dp = Dispatcher(bot)

async def get_history(phone, token):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + token 

    parameters = {
    'rows': 4, 'operation': 'IN'
    }

    h = s.get(f'https://edge.qiwi.com/payment-history/v2/persons/{phone}/payments', params = parameters)

    return h.json()

@dp.message_handler(commands=['start'])
async def handler(message: types.Message):
    await bot.send_message(message.from_user.id, 'Добро пожаловать!\nЧтобы приобрести доступ, воспользуйтесь клавиатурой.', reply_markup=keyboard.buy_lic)

@dp.message_handler(text='🔒 Приобрести доступ 🔒')
async def handler(message: types.Message):
    random_code = random.randint(1, 1000000)

    if config.pay_to_nick:
        link = f"https://qiwi.com/payment/form/99999?extra%5B%27account%27%5D={config.nick}&amountInteger={config.cost}&amountFraction=0&extra%5B%27comment%27%5D={random_code}&currency=643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"

        payment = InlineKeyboardMarkup()
        payment.add(InlineKeyboardButton('Проверить оплату', callback_data = f'check_payment_{random_code}'), InlineKeyboardButton('Перейти к оплате', url=link))

        await message.reply(f'💵 Оплатите доступ 💵\n\n📱 Никнейм: {config.nick}\n🔐 Комментарий: {random_code} (ОБЯЗАТЕЛЬНО УКАЖИТЕ)\n💰 Цена: {config.cost}р\n\n🚀 Для удобства перейдите по ссылке', reply=False, reply_markup=payment)
    else:
        link = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={config.number}&amountInteger={config.cost}&amountFraction=0&extra%5B%27comment%27%5D={random_code}&currency=643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"

        payment = InlineKeyboardMarkup()
        payment.add(InlineKeyboardButton('Проверить оплату', callback_data = f'check_payment_{random_code}'), InlineKeyboardButton('Перейти к оплате', url=link))

        await message.reply(f'💵 Оплатите доступ 💵\n\n📱 Номер: {config.number}\n🔐 Комментарий: {random_code}\n💰 Цена: {config.cost}р\n\n🚀 Для удобства перейдите по ссылке', reply=False, reply_markup=payment)

@dp.callback_query_handler(text_contains='check_payment_')
async def menu(call: types.CallbackQuery):
    code = call.data[14:]
    result_pay = False
    try:
        qiwi_history = await get_history(config.number, config.qiwi)

        for i in range(4):
            if qiwi_history['data'][i]['comment'] == str(code) and qiwi_history['data'][i]['sum']['amount'] == int(config.cost):
                result_pay = True
                await call.message.edit_text(f'🔐 Оплата найдена 🔐')
        if not result_pay:
            payment = InlineKeyboardMarkup()
            payment.add(InlineKeyboardButton('Проверить оплату', callback_data = f'check_payment_{code}'))
            await bot.send_message(call.from_user.id, 'Платеж не найден.', reply_markup=payment)
    except Exception as e:
        payment = InlineKeyboardMarkup()
        payment.add(InlineKeyboardButton('Проверить оплату', callback_data = f'check_payment_{code}'))
        await bot.send_message(call.from_user.id, "Администратор не настроил оплату, уведомите его об этом")
        print(e)

executor.start_polling(dp)
