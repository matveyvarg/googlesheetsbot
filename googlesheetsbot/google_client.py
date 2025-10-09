from datetime import datetime
import logging
import gspread

from googlesheetsbot.config import settings
from googlesheetsbot.models import Transaction

HEADER_ROWS = 2

logger = logging.getLogger(__name__)

def _get_worksheet_name() -> str:
    MONTHES = [
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
    ]
    now = datetime.now()
    return f"{MONTHES[now.month - 1]} {now.year}"


class GoogleClient:
    client: gspread.Client
    sheet: gspread.Spreadsheet
    worksheet: gspread.Worksheet

    def __init__(self) -> None:
        self.client = gspread.service_account(filename=settings.service_account_file)
        self.sheet = self.client.open(settings.sheet_name)
        self.worksheet = self.sheet.worksheet(_get_worksheet_name())

    def get_last_empty_row(self, is_expense: bool | None) -> int:
        column_number = (
            settings.transactions_column if is_expense else settings.income_column
        )
        values_list = self.worksheet.col_values(col=column_number)
        return len(values_list)

    def add_transaction(self, transaction: Transaction) -> None:
        row = self.get_last_empty_row(transaction.is_expense)
        if transaction.is_expense:
            self.add_expense(row, transaction)

    def add_expense(self, row: int, transaction: Transaction) -> None:
        logger.debug(f"Adding expense {transaction} at row {row}")
        col_cursor = settings.transactions_column

        # Add category
        category = transaction.category or "Unknown"
        self.worksheet.update_cell(row=row, col=col_cursor, value=category)
        col_cursor += 1

        # Add amount
        amount = transaction.amount or 0
        self.worksheet.update_cell(row=row, col=col_cursor, value=amount)
        col_cursor += 1

        # Add description
        description = transaction.description or ""
        self.worksheet.update_cell(row=row, col=col_cursor, value=description)

    def get_categories(self) -> list[str]:
        logger.debug("Getting categories")
        values = self.worksheet.col_values(col=settings.transactions_column)
        result = []
        for value in values[2:]:  # exclude headers
            if not isinstance(value, str):
                continue

            trimmed_value = value.strip()
            if trimmed_value in result or not trimmed_value:
                continue

            result.append(trimmed_value)
        logger.debug("Categories: %s", result)
        return result


google_client = GoogleClient()
