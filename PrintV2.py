# -*- coding: utf-8 -*-

import asyncio
import logging
from hikkatl.types import Message
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class TypingSimulatorMod(loader.Module):
    """Simulates typing text word by word."""

    strings = {
        "name": "TypingSimulator",
        "args_needed": "<b>Text is required after the command. Optionally, provide a delay multiplier per character (e.g., .type 0.1 Hello).</b>",
        "error_editing": "⚠️ <b>Error editing message:</b>\n{}",
        "text_too_short": "<b>Text must contain at least one word.</b>",
    }

    strings_ru = {
        "args_needed": "<b>После команды требуется текст. Опционально, укажите множитель задержки на символ (например, .type 0.1 Привет).</b>",
        "error_editing": "⚠️ <b>Ошибка при редактировании сообщения:</b>\n{}",
        "text_too_short": "<b>Текст должен содержать хотя бы одно слово.</b>",
        "_cls_doc": "Имитирует печать текста по словам.",
        "_cmd_doc_type": "[delay_multiplier] <text> - Type out the text word by word with a configurable delay.",
    }

    @loader.command(
        alias="tsim",
        ru_doc="[множитель_задержки] <текст> - Напечатать текст по словам с настраиваемой задержкой.",
    )
    async def typecmd(self, message: Message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args_needed"))
            return

        parts = args.split(maxsplit=1)
        base_delay_per_char = 0.05  # Default multiplier for delay per character
        text_segment = args

        if len(parts) > 1:
            try:
                custom_multiplier = float(parts[0])
                if custom_multiplier >= 0:
                    base_delay_per_char = custom_multiplier
                    text_segment = parts[1]
            except ValueError:
                pass # Not a float, use default multiplier and full text

        # Split the remaining text into words
        words = text_segment.split()

        if not words:
             # This handles cases like ".type 0.1   " or just ".type   "
             await utils.answer(message, self.strings("text_too_short"))
             return

        current_text = ""

        # Send the initial placeholder or clear the message to start typing over it
        # Keeping the original behavior of showing a placeholder first
        message = await utils.answer(message, self.strings("typing_process"))


        first_word = True
        for word in words:
            if not first_word:
                current_text += " "  # Add space before the next word (except the first)
            current_text += word
            first_word = False

            try:
                # Edit the message, adding the next word
                # utils.answer edits the original message for incoming commands
                message = await utils.answer(message, current_text)
            except Exception as e:
                logger.exception("Failed to edit message for typing effect")
                # If an error occurs (e.g., message deleted), attempt to report it
                await utils.answer(message, self.strings("error_editing").format(utils.escape_html(str(e))))
                return # Stop execution on error

            # Calculate delay based on the word length and the base delay per character multiplier
            delay = len(word) * base_delay_per_char
            # Use asyncio.sleep for asynchronous pause
            await asyncio.sleep(delay)

        # After the loop, the message contains the full text.
        # The initial placeholder "✍️ Печатаю..." will be replaced by the final text.
