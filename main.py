import logging
from aiogram import Bot, Dispatcher, executor, types
from os import getenv
from sys import exit

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")
bot = Bot(token=bot_token) #Take token from secret variable in env

dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


async def cmd_start(message: types.Message):
    await message.answer_sticker(r'CAACAgIAAxkBAAFYGUBhWrh0nCeLdcIZ793Qu3dCuYdu2gAC0xIAApO10Uo5iAjOswKGUSEE')
    await message.reply("Да я та самая строгая училка, я слежу за дисциплиной "
                        "в группе. Матерщинники и хулиганы будут наказаны!")


async def cmd_help(message: types.Message):
    await message.answer_sticker(r'CAACAgIAAxkBAAFYGUxhWrh5wLM4NEo6KIbzetwu2N9RewACKhIAAlnE0EpdSCjExXw-BSEE')
    await message.reply("Добавьте бота в администраторы группы. "
                        "После этого, бот будет отслеживать диалоги "
                        "в группе и банить нарушителей. ")



#Function registrations in handler
dp.register_message_handler(cmd_help, commands="help")
dp.register_message_handler(cmd_start, commands="start")


restricted_messages = ["я веган", "i am vegan"]


# Выдаём Read-only за определённые фразы
@dp.message_handler(lambda message: message.text.lower() in
                                          restricted_messages)
async def set_ro(message: types.Message):
    await bot.restrict_chat_member(message.chat.id, message.from_user.id)


@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(message.text)



if __name__ == '__main__':
    executor.start_polling(dp)
    # executor.start_polling(dp, skip_updates=True)

