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

from googlesheetsbot import google_client
from googlesheetsbot.config import settings
from googlesheetsbot.google_client import GoogleClient
from googlesheetsbot.keyboards.cache import KeyboardCache
from googlesheetsbot.keyboards.static import TYPE_KEYBOARD
from googlesheetsbot.models import EXPENSE, Form, Transaction


logger = logging.getLogger(__name__)

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
    logger.debug("Sending webhook to telegram: %s", f"{settings.base_webhook_url}{settings.webhook_path}")
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
        logger.info("STARTING APP...")

        await self.keyboard_cache.init()
        logger.debug("Keyboard initialized")

        dp.startup.register(on_startup)
        logger.debug("Startup hook registred")

        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=self.bot,
            secret_token=settings.secret_token,
            keyboard_cache=self.keyboard_cache,
            google_client=google_client,
            transaction=Transaction(),
        )
        # Register webhook handler on application
        webhook_requests_handler.register(app, path=settings.webhook_path)
        logger.debug("Handler registred")

        # Mount dispatcher startup and shutdown hooks to aiohttp application
        setup_application(app, dp, bot=self.bot)
        logger.debug("Application mounted")

        # And finally start webserver
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, settings.server.host, settings.server.port)
        await site.start()


if __name__ == "__main__":
    app = App()
    logging.basicConfig(level=settings.loglevel, stream=sys.stdout)
    asyncio.run(app.run())
