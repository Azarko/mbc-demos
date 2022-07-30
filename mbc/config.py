import dataclasses
import os


@dataclasses.dataclass(frozen=True)
class ApplicationConfig:
    port: int
    telegram_token: str
    telegram_webhook_url: str
    is_test: bool = False

    @classmethod
    def from_env(cls):
        return cls(
            port=int(os.getenv('PORT', '8080')),
            telegram_token=os.getenv('TG_TOKEN', ''),
            telegram_webhook_url=os.getenv('TG_WEBHOOK_URL', ''),
            is_test=bool(os.getenv('TEST')),
        )
