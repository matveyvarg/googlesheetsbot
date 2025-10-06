from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel

EXPENSE = "Expense"


class Transaction(BaseModel):
    is_expense: bool | None = None
    category: str | None = None
    amount: float | None = None
    description: str | None = None


class Form(StatesGroup):
    type = State()
    category = State()
    amount = State()
    description = State()
