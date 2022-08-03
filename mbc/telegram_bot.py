import asyncio
import concurrent.futures
import contextlib
import io
import logging
import os
import uuid

import aiogram
import aiogram.types
import imaginator.entry as imaginator_entry


logger = logging.getLogger(__name__)


MAX_TEXT_SIZE = 150


class Bot:
    def __init__(self, token: str, webhook_url: str):
        self.token = token
        self.webhook_url = webhook_url
        self.bot = aiogram.Bot(token=self.token, validate_token=False)
        self.dispatcher = aiogram.Dispatcher(self.bot)

    async def on_startup(self):
        self.dispatcher.register_message_handler(
            self.start_handler,
            commands=['start'],
        )
        self.dispatcher.register_message_handler(
            self.video_text_handler,
            commands=['video_text'],
        )
        if self.webhook_url:
            await self._setup_webhook()
        else:
            logger.warning('webhook is not configured, skip')

    async def _setup_webhook(self):
        webhook = await self.bot.get_webhook_info()
        if webhook.url != self.webhook_url:
            # TODO: ssl
            logger.info(
                f'webhook is different, change it to: {self.webhook_url}',
            )
            await self.bot.delete_webhook()
            await self.bot.set_webhook(
                self.webhook_url,
                drop_pending_updates=True,
            )
            logger.info('webhook successfully changed')
        else:
            logger.info(f'webhook already set: {self.webhook_url}')

    async def on_shutdown(self, *args, **kwargs):
        # if self.webhook_url:
        #     logger.info('webhook deleted')
        #     await self.bot.delete_webhook()
        pass

    async def start_handler(self, message: aiogram.types.Message):
        return await message.reply('started')

    async def video_text_handler(self, message: aiogram.types.Message):
        if message.chat.type != aiogram.types.ChatType.PRIVATE:
            return await message.reply(
                'this function available only in private chat',
            )
        command, command_argument = message.get_full_command()
        if not command_argument:
            logger.info(f'got {command} without arguments')
            return await message.reply('input text after command, please')
        if len(command_argument) > MAX_TEXT_SIZE:
            logger.info('len of received text for animation too long')
            return await message.reply(
                f'Your message too long! Max message size is {MAX_TEXT_SIZE}',
            )
        logger.info(f'generate video for text: {command_argument}')
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            content = await loop.run_in_executor(
                pool,
                generate_video,
                command_argument,
            )
        await message.answer_chat_action(action='upload_video')
        with io.BytesIO(content) as stream:
            stream.name = 'animation.mp4'
            return await message.answer_animation(animation=stream)


def generate_video(text: str) -> bytes:
    logger.info(f'start generating video for text "{text}')
    filename = f'{uuid.uuid4().hex}.mp4'
    try:
        imaginator = imaginator_entry.Imaginator()
        imaginator_entry.create_video(
            imaginator=imaginator,
            name=filename,
            text_line=text,
        )
        return _load_result(filename)
    finally:
        with contextlib.suppress(OSError):
            os.remove(filename)


def _load_result(path: str) -> bytes:
    with open(path, 'rb') as stream:
        return stream.read()
