from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🆕 Новый случай"),
                KeyboardButton(text="✅ Закрыть случай"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Опишите проблему или отправьте фото",
    )