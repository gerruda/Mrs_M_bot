import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.utils import exceptions
from aiogram.dispatcher.filters.state import State, StatesGroup
from os import getenv
from sys import exit
from aiogram.contrib.fsm_storage.memory import MemoryStorage


bot_token = getenv("BOT_TOKEN")
storage = MemoryStorage()
if not bot_token:
    exit("Error: no token provided")
bot = Bot(token=bot_token) #Take token from secret variable in env

dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

available_settings = ['Mute', 'Ban', 'Warning', 'Second Mute', 'Second Ban']
available_parametr = [1, 15, 60, 360]


#State params for FSM
class Bot_settings(StatesGroup):
    waiting_bot_settings_joice = State()
    waitint_bot_settings_parametr = State()
    waiting_user_choise = State()
    msg_id = str()


#Startin to change Bot settings.
async def settings(message: types.Message, state: FSMContext):
    if message.chat.type not in ('supergroup', 'group'):
        await message.answer('Запустите настройки из группы.')
        return
    keyboard = types.InlineKeyboardMarkup()
    for name in available_settings:
        keyboard.add(types.InlineKeyboardButton(text=name, callback_data=name))
    await Bot_settings.waiting_bot_settings_joice.set()
    await message.answer("Для отмены /cancel .Выберите виды наказания, которые хотели бы отредактировать. "
                         "Прошу обратить внимание что обычно стоит наказание за мат - предупреждение. "
                         "За три предупреждения дается мьют на 15 минут.  при повторном нарушении мьют на час."
                         " Далее бан.",
                         reply_markup=keyboard)
    await state.update_data(msg_id=message.message_id + 1)



#Joice the punishment.
async def settings_joice(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data(chosen_settings=call.data)
    await state.update_data(chat_id=call.from_user.id)
    await state.update_data(msg_id=call.message.message_id + 1)

    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    for parametr in available_parametr:
        keyboard.add(types.InlineKeyboardButton(text=str(parametr) + ' min', callback_data=str(parametr)))
    await Bot_settings.next()
    await call.message.answer('Для отмены /cancel Выберете длительность наказания или введите числовое значение'
                              ' с клавиатуры.  Число должно быть целое и указывать на колличество минут.',
                              reply_markup=keyboard)


#Joice the time of punishment.
async def settings_parametr(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await call.message.answer(f"Вы выбрали наказание {user_data['chosen_settings']} на {call.data} минут. "
                         f"Хулиганы, должны быть наказаны! :-)")
    await call.message.delete()


#Cansel making setting.
async def cancel(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await state.finish()
    await bot.delete_message(message.chat.id, user_data['msg_id'])
    await message.answer('Настройка отмененна')


async def cmd_start(message: types.Message):
    await message.answer_sticker(r'CAACAgIAAxkBAAFYGUBhWrh0nCeLdcIZ793Qu3dCuYdu2gAC0xIAApO10Uo5iAjOswKGUSEE')
    await message.reply("Да я та самая строгая училка, я слежу за дисциплиной "
                        "в группе. Матерщинники и хулиганы будут наказаны!")


async def cmd_help(message: types.Message):
    await message.answer_sticker(r'CAACAgIAAxkBAAFYGUxhWrh5wLM4NEo6KIbzetwu2N9RewACKhIAAlnE0EpdSCjExXw-BSEE')
    await message.reply("Добавьте бота в администраторы группы. "
                        "После этого, бот будет отслеживать диалоги "
                        "в группе и банить нарушителей. ")


#Trying to work with errors.
async def error_bot_blocked(update: types.Update, exception: exceptions.BotBlocked):
    # Update: объект события от Telegram. Exception: объект исключения
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")

    # Такой хэндлер должен всегда возвращать True,
    # если дальнейшая обработка не требуется.
    return True


#Function registrations in handler
dp.register_message_handler(cmd_help, commands="help")
dp.register_message_handler(cmd_start, commands="start")
dp.register_message_handler(settings, state='*', commands='settings')
dp.register_callback_query_handler(settings_joice, lambda c: c.data != 'user_choise',
state=Bot_settings.waiting_bot_settings_joice)
dp.register_callback_query_handler(settings_parametr, lambda c: c.data, state=Bot_settings.waitint_bot_settings_parametr)
dp.register_message_handler(cancel, state='*', commands="cancel")
dp.errors_handler(error_bot_blocked, exception=exceptions.BotBlocked)

restricted_messages = ["я веган", "i am vegan"]


# Make the punishment
@dp.message_handler(lambda message: message.text.lower() in
                                          restricted_messages)
async def set_ro(message: types.Message):
    await bot.restrict_chat_member(message.chat.id, message.from_user.id)

#Echo message
# @dp.message_handler()
# async def echo(message: types.Message):
#     await message.reply(message.text)



if __name__ == '__main__':
    executor.start_polling(dp)
    # executor.start_polling(dp, skip_updates=True)

