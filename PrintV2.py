#-*- coding: utf-8 -*-

import asyncio
from hikka import loader, utils
from hikka.types import Message

@loader.tds
class PrinterMod(loader.Module):
    """Модуль для создания эффекта 'пишущей машинки' в Telegram."""

    strings = {
        "name": "Printer",
        "usage": (
            "<b>🚫 Неверное использование.</b>\n"
            "Пример: <code>.prt 0.1 Текст для анимации</code>"
        ),
        "no_text": "<b>🚫 Нет текста для вывода.</b>",
        "invalid_delay": "<b>🚫 Неверный формат задержки. Укажите число."
    }

    @loader.command(
        alias="prt",
        ru_doc="<задержка> <текст> - Анимирует печать текста по словам",
    )
    async def prtcmd(self, message: Message):
        """<delay> <text> - Animates text printing word by word."""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("usage"))
            return

        parts = args.split()
        
        try:
            delay_per_char = float(parts[0])
        except (ValueError, IndexError):
            await utils.answer(message, self.strings("invalid_delay"))
            return

        text_to_print = " ".join(parts[1:])
        if not text_to_print:
            await utils.answer(message, self.strings("no_text"))
            return

        words = text_to_print.split()
        
        current_words_window = []
        window_size = 5

        # \u2060 - это невидимый символ, чтобы '[' не ломал форматирование
        await utils.answer(message, "|[\u2060...]|")

        for word in words:
            current_words_window.append(word)

            if len(current_words_window) > window_size:
                current_words_window.pop(0)

            # ✨ Вот здесь мы добавили обрамление текста
            text = " ".join(current_words_window)
            output_text = f"|[\u2060{text}]|"
            
            current_delay = delay_per_char * len(word)
            
            await utils.answer(message, output_text)
            
            await asyncio.sleep(current_delay)