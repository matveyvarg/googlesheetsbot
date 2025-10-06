import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from googlesheetsbot.config import settings
from googlesheetsbot.google_client import GoogleClient
from googlesheetsbot.keyboards.cache import KeyboardCache
from googlesheetsbot.keyboards.static import TYPE_KEYBOARD
from googlesheetsbot.models import EXPENSE, Form, Transaction

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.set_state(Form.type)
    await message.answer("Выберите тип", reply_markup=TYPE_KEYBOARD)


@dp.message(Form.type)
async def handle_type(
    message: Message,
    state: FSMContext,
    transaction: Transaction,
    keyboard_cache: KeyboardCache,
):
    transaction.is_expense = message.text == EXPENSE
    await state.set_state(Form.category)
    await message.answer(
        "Выберите категорию", reply_markup=await keyboard_cache.get_category_keyboard()
    )


@dp.message(Form.category)
async def handle_category(
    message: Message,
    state: FSMContext,
    transaction: Transaction,
    keyboard_cache: KeyboardCache,
):
    transaction.category = message.text
    if transaction.category:
        await keyboard_cache.update_cache(transaction.category)

    await state.set_state(Form.amount)
    await message.answer("Введите сумму", reply_markup=ReplyKeyboardRemove())


@dp.message(Form.amount)
async def handle_amount(message: Message, state: FSMContext, transaction: Transaction):
    if message.text is not None and message.text.isdigit():
        transaction.amount = float(message.text)
        await state.set_state(Form.description)
        await message.answer("Введите описание")
        return
        
    await message.answer("Введите сумму")




@dp.message(Form.description)
async def handle_description(
    message: Message,
    state: FSMContext,
    transaction: Transaction,
    google_client: GoogleClient,
):
    google_client.add_transaction(transaction=transaction)
    await state.set_state(Form.type)
    await message.answer("Выберите тип", reply_markup=TYPE_KEYBOARD)


async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(
        f"{settings.base_webhook_url}{settings.webhook_path}",
        secret_token=settings.secret_token,
    )


class App:
    bot: Bot

    def __init__(self) -> None:
        self.bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self.keyboard_cache = KeyboardCache()

    async def run(self):
        await self.keyboard_cache.init()
        dp.startup.register(on_startup)
        app = web.Application()

        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=self.bot,
            secret_token=settings.secret_token,
        )
        # Register webhook handler on application
        webhook_requests_handler.register(app, path=settings.webhook_path)

        # Mount dispatcher startup and shutdown hooks to aiohttp application
        setup_application(app, dp, bot=self.bot)

        # And finally start webserver
        web.run_app(app, host=settings.server.host, port=settings.server.port)


if __name__ == "__main__":
    app = App()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(app.run())
