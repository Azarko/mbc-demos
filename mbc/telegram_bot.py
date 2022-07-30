import logging

import aiogram
import aiogram.types


logger = logging.getLogger(__name__)


class Bot:
    def __init__(self, token: str, webhook_url: str):
        self.token = token
        self.webhook_url = webhook_url
        self.bot = aiogram.Bot(token=self.token, validate_token=False)
        self.dispatcher = aiogram.Dispatcher(self.bot)

    async def on_startup(self):
        self.dispatcher.register_message_handler(
            self.start_handler, commands=['start'],
        )
        if self.webhook_url:
            webhook = await self.bot.get_webhook_info()
            if webhook.url != self.webhook_url:
                # TODO: ssl
                logger.info(
                    f'webhook is different, change it to: {self.webhook_url}',
                )
                await self.bot.delete_webhook()
                await self.bot.set_webhook(
                    self.webhook_url, drop_pending_updates=True,
                )
                logger.info('webhook successfully changed')
            else:
                logger.info(f'webhook already set: {self.webhook_url}')
        else:
            logger.info('webhook is not configured, skip')

    async def on_shutdown(self, *args, **kwargs):
        if self.webhook_url:
            logger.info('webhook deleted')
            await self.bot.delete_webhook()

    async def start_handler(self, message: aiogram.types.Message):
        return await message.reply('started')
