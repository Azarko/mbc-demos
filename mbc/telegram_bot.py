import asyncio
import concurrent.futures
import contextlib
import io
import logging

import aiogram
from aiogram.contrib.fsm_storage import memory
from aiogram.dispatcher.filters import state
import aiogram.types

from mbc.utils import party_calculator
from mbc.utils import video_generator


logger = logging.getLogger(__name__)


MAX_TEXT_SIZE = 150


class Form(state.StatesGroup):
    data = state.State()


def _drop_chat_storage_info(func):
    """Drops chat_id from bot storage after function call."""

    async def wrapper(self: 'Bot', message: aiogram.types.Message, **kwargs):
        try:
            return await func(self, message, **kwargs)
        finally:
            logger.info(f'drop chat {message.chat.id} from storage')
            with contextlib.suppress(KeyError):
                self.storage.data.pop(str(message.chat.id))

    return wrapper


class Bot:
    def __init__(self, token: str, webhook_url: str):
        self.token = token
        self.webhook_url = webhook_url
        self.storage = memory.MemoryStorage()
        self.bot = aiogram.Bot(token=self.token, validate_token=False)
        self.dispatcher = aiogram.Dispatcher(self.bot, storage=self.storage)

    async def on_startup(self):
        self.dispatcher.register_message_handler(
            self.start_handler,
            commands=['start'],
        )
        self.dispatcher.register_message_handler(
            self.video_text_handler,
            commands=['video_text'],
        )
        self.dispatcher.register_message_handler(
            self.party_calc,
            commands=['party'],
        )
        self.dispatcher.register_message_handler(
            self.process_calc_data,
            state=Form.data,
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
        await self.storage.close()

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
                video_generator.generate_video,
                command_argument,
            )
        await message.answer_chat_action(action='upload_video')
        with io.BytesIO(content) as stream:
            stream.name = 'animation.mp4'
            return await message.answer_animation(animation=stream)

    async def party_calc(self, message: aiogram.types.Message):
        await Form.data.set()
        await message.reply(
            'input members and payments separated by space, one member per '
            'line, for example: \n\nperson_one 1000\nperson_two 2000',
        )

    @_drop_chat_storage_info
    async def process_calc_data(
        self,
        message: aiogram.types.Message,
        **kwargs,
    ):
        logger.info(f'process calc data for {message.chat.id}')
        await Form.next()
        text = message.text
        members = []
        for index, string in enumerate(text.split('\n'), start=1):
            try:
                member = party_calculator.PartyMember.from_string(string)
            except party_calculator.ValidationError:
                logger.exception(f'failed to parse string "{string}"')
                return await message.reply(
                    f'can\'t parse string {index} ("{string}"): '
                    'invalid string format',
                )
            members.append(member)
        total_sum = sum(member.payment for member in members)
        avg = total_sum / len(members)
        result = [f'each member must pay: {avg:.2f}\n']
        for member in members:
            result.append(f'{member.name}: {avg - member.payment:.2f}')
        # TODO: format numbers to x.xx e.g. 100.23 or 0.00
        return await message.reply('\n'.join(result))
