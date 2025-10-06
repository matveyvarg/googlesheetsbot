import json

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from redis import asyncio as aioredis

from googlesheetsbot.config import settings
from googlesheetsbot.google_client import google_client

redis = aioredis.from_url(settings.redis_dsn, decode_responses=True)


class KeyboardCache:
    categories: list = []

    async def init(self) -> None:
        keyboard = await self.get_category_keyboard_json()
        print(self, keyboard)

        if not keyboard:
            self.categories = google_client.get_categories()
            await redis.set(
                settings.keyboard_key, json.dumps({"items": self.categories})
            )

    async def get_category_keyboard_json(self) -> dict | None:
        keyboard_str = await redis.get("keyboard")
        if not keyboard_str:
            return keyboard_str
        keyboard_json = json.loads(keyboard_str)
        return keyboard_json["items"]

    async def get_category_keyboard(self) -> ReplyKeyboardMarkup:
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

        return ReplyKeyboardMarkup(keyboard=keyboard)

    async def update_cache(self, value: str) -> None:
        if value not in self.categories:
            self.categories.append(value)
            await redis.set(
                settings.keyboard_key, json.dumps({"items": self.categories})
            )
