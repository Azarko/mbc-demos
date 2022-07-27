import dataclasses
import os


@dataclasses.dataclass(frozen=True)
class ApplicationConfig:
    port: int

    @classmethod
    def from_env(cls):
        return cls(
            port=os.getenv('PORT', 8080),
        )
