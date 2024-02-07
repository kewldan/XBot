import math
import time
import traceback

from aiogram import Router, F
from aiogram.types import Message, ErrorEvent, BufferedInputFile, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..config import config

message_limit = 3970


def get_support_markup(url: str):
    builder = InlineKeyboardBuilder()

    builder.button(text='🆘 Поддержка', url=url)
    builder.adjust(1)

    return builder.as_markup()


def get_user_markup(user_url: str):
    builder = InlineKeyboardBuilder()

    builder.button(text='👤 Пользователь', url=user_url)
    builder.adjust(1)

    return builder.as_markup()


async def report(exception: ErrorEvent, object_name: str, text: str, username: str, user_id: int, user_url: str):
    for admin in config['bot']['owners']:
        traceback_log = BufferedInputFile(traceback.format_exc().encode(),
                                          filename=f"Traceback{math.floor(time.time())}.txt")
        await exception.bot.send_document(admin, traceback_log,
                                          caption=f'⚠️ Произошла ошибка при обработке {object_name} от @{username} [<code>{user_id}</code>]!\n'
                                                  f'<pre>{text}</pre>',
                                          reply_markup=get_user_markup(user_url))


def add_to_router(main_router: Router, url: str):
    error_handler_router = Router()

    @error_handler_router.error(F.update.message.as_("message"))
    async def error_handler(exception: ErrorEvent, message: Message):
        await message.reply('❌ Похоже, что-то пошло не так, репорт отправлен', reply_markup=get_support_markup(url))

        await report(exception, 'сообщения', message.text, message.from_user.username, message.from_user.id,
                     message.from_user.url)

    @error_handler_router.error(F.update.callback_query.as_("query"))
    async def error_handler(exception: ErrorEvent, query: CallbackQuery):
        await query.answer('❌ Похоже, что-то пошло не так, репорт отправлен', show_alert=True)

        await report(exception, 'кнопки', query.data, query.from_user.username, query.from_user.id, query.from_user.url)

    main_router.include_router(error_handler_router)
