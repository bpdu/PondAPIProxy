from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )

    POND_API_BASE_URL: str
    POND_API_TIMEOUT: int = 30

    ALLOWED_TOKENS: str
    IP_WHITELIST_PATH: str = '/app/config/whitelist.txt'

    VAULT_ADDR: str
    VAULT_TOKEN: str
    VAULT_KV_PATH: str = 'pondmobile'
    VAULT_TOKEN_FIELD: str = 'token'

    APP_VERSION: str = '1.0.0'
    LOG_LEVEL: str = 'info'
    HOST: str = '0.0.0.0'
    PORT: int = 8000

    @property
    def tokens(self) -> list[str]:
        return [t.strip() for t in self.ALLOWED_TOKENS.split(',')]


settings = Settings()
