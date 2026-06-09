from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def main_menu(auto_accept):
    b = ReplyKeyboardBuilder()
    b.button(text="📖 История")
    b.button(text="🔄 Рестарт")
    # Используем минималистичные индикаторы
    status = "🟢 ON" if auto_accept else "🔴 OFF"
    b.button(text=f"Автопринятие: {status}")
    b.adjust(2, 1)
    return b.as_markup(resize_keyboard=True)

def call_menu(ch_id, msg_id):
    b = InlineKeyboardBuilder()
    b.button(text="Принять (10-4)", callback_data=f"ok_{ch_id}_{msg_id}")
    return b.as_markup()

def manage_menu(th_id, msg_id):
    b = InlineKeyboardBuilder()
    # Компактные кнопки управления
    b.button(text="📍 10-20?", callback_data=f"m20_{th_id}_{msg_id}")
    b.button(text="❌ 10-0", callback_data=f"m00_{th_id}_{msg_id}")
    b.adjust(2)
    return b.as_markup()