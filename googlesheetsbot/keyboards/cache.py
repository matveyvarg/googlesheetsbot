import json
import logging
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from redis import asyncio as aioredis

from googlesheetsbot.config import settings
from googlesheetsbot.google_client import google_client

redis = aioredis.from_url(settings.redis_dsn, decode_responses=True)

logger = logging.getLogger(__name__)

class KeyboardCache:
    categories: list = []

    async def init(self) -> None:
        logger.debug("Initializing keyboard cache") 
        keyboard = await self.get_category_keyboard_json()

        if not keyboard:
            logger.debug("Keyboard not found in cache, getting from google")
            self.categories = google_client.get_categories()
            await redis.set(
                settings.keyboard_key, json.dumps({"items": self.categories})
            )

    async def get_category_keyboard_json(self) -> dict | None:
        logger.debug("Getting keyboard from cache")
        keyboard_str = await redis.get("keyboard")
        if not keyboard_str:
            return keyboard_str
        keyboard_json = json.loads(keyboard_str)
        return keyboard_json["items"]

    async def get_category_keyboard(self) -> ReplyKeyboardMarkup:
        logger.debug("Making keyboard instance")
        if not self.categories:
            await self.init()
        keyboard_json = self.categories
        keyboard: list[list[KeyboardButton]] = []
        row: list[KeyboardButton] = []
        for item in keyboard_json:
            button = KeyboardButton(text=item)
            if len(row) < 3:
                row.append(button)
            else:
                keyboard.append(row)
                row = [button]
        if len(row) > 0:
            keyboard.append(row)
        logger.debug(f"Keyboard: %s", keyboard)
        return ReplyKeyboardMarkup(keyboard=keyboard)

    async def update_cache(self, value: str) -> None:
        logger.debug("Updating keyboard cache")
        if value not in self.categories:
            self.categories.append(value)
            await redis.set(
                settings.keyboard_key, json.dumps({"items": self.categories})
            )
